#!/usr/bin/env python3
"""Validate a Change's Implementation Slice declaration and its code footprint.

Usage:
  python scripts/check-change-footprint.py <change-id> --declaration-only
  python scripts/check-change-footprint.py <change-id>
  python scripts/check-change-footprint.py <change-id> --verify

``--declaration-only`` is the stage-07 gate: it reads ``design.md`` and validates
the ``### Implementation Slice`` against ``docs/product/modules.csv``,
``docs/product/capabilities.csv`` and ``docs/architecture/code-layout.json``.

Diff mode (stage 08) additionally diffs the current workspace against
``openspec/changes/<change-id>/design/evidence/implementation-base.json``
(written by ``implementation-snapshot.py``), classifies every added/modified/
deleted path, and writes ``design/evidence/implementation-diff.json``.
``--verify`` (stage 09) recomputes the same diff, compares the sorted path set
and ``diff_sha256`` with the stored file, and re-runs the classification.

Path rules (shared with ``check-design-sections.py``): paths are repository
relative, must not be absolute or contain ``.``/``..`` segments, and may only
use a strictly trailing ``/**`` subtree marker (normalized to its directory
prefix). Owned paths and code packages must stay under the owner/related module
roots (resource-level descent is allowed). Every owner/related module path's
``code-layout.json.module_card`` (default ``MODULE.md``) is implicitly owned,
so stage 08 can create or update module cards without listing the card file in
``Owned paths``. Integration paths may be empty or ``N/A`` (no integration
entries) but every declared entry must match
``code-layout.json.integration_paths`` and carry a reason plus ``task <ID>``.
Changes inside a module ``shared_paths`` directory need an owned entry inside
that shared path that also contains the changed file. Changes under a layout
``frozen_paths`` pattern need an approved BCR in ``Frozen approvals``.

``strategy=none`` (or a missing layout) skips the gate with
``FOOTPRINT_CHECK=SKIPPED (strategy none)`` and exit code 0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import gate_common as gm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_VERSION = "1.0"
BASE_REL = "openspec/changes/{change_id}/design/evidence/implementation-base.json"
DIFF_REL = "openspec/changes/{change_id}/design/evidence/implementation-diff.json"
DESIGN_REL = "openspec/changes/{change_id}/design.md"

ABSOLUTE_PATH_RE = re.compile(r"^(?:/|[A-Za-z]:)")
WILDCARD_PATH_RE = re.compile(r"[*?]")
PLACEHOLDER_SEGMENT_RE = re.compile(r"<[^/>]+>")

# Approved design §5.3: frozen paths are ``code-layout.json.frozen_paths`` plus
# the architecture baseline. The volatile baseline files in
# ``gate_common.EXCLUDED_EXACT`` never enter the diff, so they need no BCR.
BASELINE_FROZEN_PATTERN = "docs/architecture/**"

REQUIRED_SLICE_FIELDS = {
    "module-packages": (
        ("primary", "Primary capability"),
        ("owner_module", "Owner module"),
        ("related_modules", "Related modules"),
        ("packages", "Code packages"),
        ("owned", "Owned paths"),
        ("integration", "Integration paths"),
        ("module_card", "Module card"),
    ),
    "footprint": (
        ("owned", "Owned paths"),
        ("integration", "Integration paths"),
    ),
}


def _root(root: Path | None) -> Path:
    return Path(root) if root is not None else Path(ROOT)


def _rel(path: Path, root: Path | None) -> str:
    try:
        return path.relative_to(_root(root)).as_posix()
    except ValueError:
        return path.as_posix()


def _validate_change_id(change_id: str) -> str:
    value = (change_id or "").strip()
    if not value or "/" in value or "\\" in value or ".." in value:
        raise RuntimeError(
            f"invalid change-id {change_id!r}; expected a single directory name "
            "without path separators"
        )
    return value


# -- path helpers (mirror check-design-sections.py) ---------------------------------
def _is_na(value: str) -> bool:
    return (value or "").strip().upper().startswith("N/A")


def _norm_path(value: str) -> str:
    value = str(value or "").strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    value = re.sub(r"/+", "/", value)
    return value.strip("/")


def _slice_path_prefix(value: str) -> str:
    """Return the concrete prefix of a path; only a trailing ``/**`` is accepted."""
    raw = str(value or "").strip().replace("\\", "/")
    if len(raw) > len("/**") and raw.endswith("/**"):
        raw = raw[: -len("/**")]
    return _norm_path(raw)


def _path_problem(value: str) -> str:
    """Return why a path is unsafe, or ``""`` when it is acceptable."""
    raw = str(value or "").strip().replace("\\", "/")
    if ABSOLUTE_PATH_RE.match(raw):
        return "is an absolute path"
    segments = raw.split("/")
    if any(segment == "." for segment in segments):
        return "contains a '.' segment"
    if any(segment == ".." for segment in segments):
        return "contains a '..' segment"
    if WILDCARD_PATH_RE.search(raw):
        return "contains a wildcard character"
    return ""


def _inside(path: str, container: str) -> bool:
    """True when ``path`` equals ``container`` or descends into it.

    ``<org>``-style placeholder segments in the container match exactly one path
    segment, so module roots written with package patterns still contain concrete
    resource paths.
    """
    path = _slice_path_prefix(path)
    container = _slice_path_prefix(container)
    if not path or not container:
        return False
    if PLACEHOLDER_SEGMENT_RE.search(container):
        pattern = PLACEHOLDER_SEGMENT_RE.sub("*", container)
        return gm.path_matches(path, pattern) or gm.path_matches(path, pattern + "/**")
    folded = path.casefold()
    prefix = container.casefold()
    return folded == prefix or folded.startswith(prefix + "/")


def _within(path: str, roots: list[str]) -> bool:
    return any(_inside(path, root) for root in roots)


def _pattern_matches(relpath: str, pattern: str) -> bool:
    """Match a layout glob, treating ``<org>`` segments as one segment."""
    if gm.path_matches(relpath, pattern):
        return True
    expanded = PLACEHOLDER_SEGMENT_RE.sub("*", pattern)
    return expanded != pattern and gm.path_matches(relpath, expanded)


def _real_values(items: list[str]) -> list[str]:
    return [item.strip() for item in items if item.strip() and not _is_na(item)]


# -- declaration gate ---------------------------------------------------------
def load_design(change_id: str, root: Path | None = None) -> str:
    path = _root(root) / DESIGN_REL.format(change_id=change_id)
    if not path.is_file():
        raise RuntimeError(f"missing {_rel(path, root)}")
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"cannot read {_rel(path, root)}: {exc}") from exc


def _layout_patterns(layout: dict, key: str) -> list[str]:
    raw = layout.get(key) if isinstance(layout, dict) else None
    return [item for item in raw if isinstance(item, str)] if isinstance(raw, list) else []


def _module_card(layout: dict) -> str:
    """Return the normalized module card path from ``code-layout.json``."""
    card = layout.get("module_card") if isinstance(layout, dict) else None
    if isinstance(card, str) and card.strip():
        return _norm_path(card) or "MODULE.md"
    return "MODULE.md"


def validate_declaration(
    design_text: str, root: Path | None = None
) -> tuple[dict, list[str]]:
    """Validate the slice declaration and return ``(context, errors)``."""
    base = _root(root)
    parsed = gm.parse_slice(design_text)
    try:
        strategy = gm.strategy(root=base)
    except RuntimeError as exc:
        return {"strategy": "none", "parsed": parsed}, [str(exc)]
    if strategy == "none":
        return {"strategy": "none", "parsed": parsed}, []

    errors: list[str] = []
    present = set(parsed["present"])
    required = REQUIRED_SLICE_FIELDS[strategy]
    required_fields = {field for field, _ in required}
    for field, label in required:
        if field not in present:
            errors.append(
                f"### Implementation Slice missing required field: {label}"
            )

    capabilities = gm.load_capabilities(root=base)
    modules = gm.load_modules(root=base)
    layout = gm.load_code_layout(root=base) or {}
    integration_patterns = _layout_patterns(layout, "integration_paths")
    frozen_patterns = _layout_patterns(layout, "frozen_paths")
    if BASELINE_FROZEN_PATTERN not in frozen_patterns:
        frozen_patterns.append(BASELINE_FROZEN_PATTERN)

    primary = ""
    if "primary" in present:
        value = (parsed["primary"] or "").strip()
        if not value or _is_na(value):
            if "primary" in required_fields:
                errors.append(
                    "### Implementation Slice field Primary capability "
                    "must not be empty or N/A"
                )
        else:
            primary = value
            if not gm.capability_rows(capabilities, primary):
                errors.append(
                    f"### Implementation Slice Primary capability {primary!r} "
                    "is not in docs/product/capabilities.csv"
                )

    owner = ""
    if "owner_module" in present:
        value = (parsed["owner_module"] or "").strip()
        if _is_na(value):
            # Under ``footprint`` an owner of N/A simply means no module ownership.
            if strategy == "module-packages":
                errors.append(
                    "### Implementation Slice field Owner module "
                    "must not be empty or N/A"
                )
        elif not value:
            if strategy == "module-packages":
                errors.append(
                    "### Implementation Slice field Owner module "
                    "must not be empty or N/A"
                )
        else:
            owner = value
            if not gm.module_rows(modules, owner):
                errors.append(
                    f"### Implementation Slice Owner module {owner!r} "
                    "is not in docs/product/modules.csv"
                )

    related: list[str] = []
    if "related_modules" in present:
        for slug in parsed["related_modules"]:
            if gm.module_rows(modules, slug):
                related.append(slug)
            else:
                errors.append(
                    f"### Implementation Slice Related module {slug!r} "
                    "is not in docs/product/modules.csv"
                )

    if strategy == "module-packages" and primary and owner:
        expected = {
            (row.get("owner_module") or "").strip()
            for row in gm.capability_rows(capabilities, primary)
            if (row.get("owner_module") or "").strip()
        }
        if expected and owner not in expected:
            errors.append(
                f"### Implementation Slice Owner module {owner!r} must equal "
                f"capability {primary!r} owner_module "
                f"{', '.join(sorted(expected))!r} in docs/product/capabilities.csv"
            )

    module_slugs = ([owner] if owner else []) + related
    roots = gm.module_paths(modules, module_slugs)
    card = _module_card(layout)
    card_paths: list[str] = []
    for root in roots:
        prefix = _norm_path(root)
        if not prefix:
            continue
        card_path = f"{prefix}/{card}"
        if card_path not in card_paths:
            card_paths.append(card_path)

    shared_paths: list[str] = []
    for slug in module_slugs:
        for row in gm.module_rows(modules, slug):
            for shared in row.get("shared_paths") or []:
                if shared and not _is_na(shared) and shared not in shared_paths:
                    shared_paths.append(shared)

    owned: list[str] = []
    for field, label in (("packages", "Code packages"), ("owned", "Owned paths")):
        if field not in present:
            continue
        values = _real_values(parsed[field])
        if not values:
            if field in required_fields:
                errors.append(
                    f"### Implementation Slice field {label} "
                    "must not be empty or N/A"
                )
            continue
        for raw in values:
            prefix = _slice_path_prefix(raw)
            problem = _path_problem(prefix)
            if problem:
                errors.append(
                    f"### Implementation Slice {label} path {raw!r} {problem}"
                )
                continue
            if roots and not _within(prefix, roots):
                errors.append(
                    f"### Implementation Slice {label} path {raw!r} is outside "
                    f"the owner/related module paths ({', '.join(roots)})"
                )
            if field == "owned":
                owned.append(prefix)
    # Module cards are implicitly owned for every owner/related module path so
    # stage 08 can create or update them without declaring the card file.
    for card_path in card_paths:
        if card_path not in owned:
            owned.append(card_path)

    integration: list[dict] = []
    if "integration" in present:
        entries = parsed["integration"]
        # Empty or N/A integration paths mean no integration entries; the design
        # requires only that declared values match layout patterns.
        for entry in entries:
            path = (entry.get("path") or "").strip()
            reason = (entry.get("reason") or "").strip()
            task = (entry.get("task") or "").strip()
            problem = _path_problem(path)
            if problem:
                errors.append(
                    f"### Implementation Slice integration path {path!r} {problem}"
                )
            elif not any(
                _pattern_matches(path, pattern)
                for pattern in integration_patterns
            ):
                errors.append(
                    f"### Implementation Slice integration path {path!r} does not "
                    "match code-layout.json integration_paths"
                )
            if not reason:
                errors.append(
                    f"### Implementation Slice integration path {path!r} "
                    "must state a reason"
                )
            if not task:
                errors.append(
                    f"### Implementation Slice integration path {path!r} "
                    "must end with '; task <TASK-ID>'"
                )
            integration.append({"path": _slice_path_prefix(path)})

    if strategy == "module-packages" and "module_card" in present:
        if not (parsed["module_card"] or "").strip():
            errors.append(
                "### Implementation Slice field Module card must not be empty"
            )

    frozen_approvals: list[dict] = []
    for entry in parsed["frozen"]:
        path = (entry.get("path") or "").strip()
        if not path:
            errors.append(
                "Frozen approvals entry must be '- <BCR-ID> — <path or prefix>'"
            )
            continue
        prefix = _slice_path_prefix(path)
        problem = _path_problem(prefix)
        if problem:
            errors.append(
                f"### Implementation Slice Frozen approvals path {path!r} {problem}"
            )
            continue
        frozen_approvals.append(
            {"id": (entry.get("id") or "").strip(), "path": prefix}
        )

    context = {
        "strategy": strategy,
        "parsed": parsed,
        "owner": owner,
        "related": related,
        "module_roots": roots,
        "shared_paths": shared_paths,
        "owned": owned,
        "module_card": card,
        "module_card_paths": card_paths,
        "integration": integration,
        "frozen_approvals": frozen_approvals,
        "integration_patterns": integration_patterns,
        "frozen_patterns": frozen_patterns,
    }
    return context, errors


def check_declaration(
    change_id: str, root: Path | None = None
) -> tuple[dict, list[str]]:
    """Load ``design.md`` and validate its Implementation Slice."""
    change_id = _validate_change_id(change_id)
    return validate_declaration(load_design(change_id, root), root)


# -- diff gate ----------------------------------------------------------------
def load_base(change_id: str, root: Path | None = None) -> tuple[dict, str]:
    """Load ``implementation-base.json`` plus its verified fingerprint."""
    path = _root(root) / BASE_REL.format(change_id=change_id)
    relpath = _rel(path, root)
    if not path.is_file():
        raise RuntimeError(
            f"missing {relpath}; run "
            f"scripts/implementation-snapshot.py {change_id} at the start of 08"
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid {relpath}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"invalid {relpath}: top level must be an object")
    files = data.get("files")
    if not isinstance(files, dict):
        raise RuntimeError(f"invalid {relpath}: 'files' must be an object")
    if data.get("change_id") and data["change_id"] != change_id:
        raise RuntimeError(
            f"{relpath} belongs to change {data['change_id']!r}, not {change_id!r}"
        )
    computed = gm.fingerprint(files)
    stored = data.get("fingerprint")
    if stored and stored != computed:
        raise RuntimeError(
            f"{relpath} fingerprint does not match its files; re-capture with "
            f"scripts/implementation-snapshot.py {change_id} --force --reason <text>"
        )
    return data, computed


def load_stored_diff(change_id: str, root: Path | None = None) -> dict:
    path = _root(root) / DIFF_REL.format(change_id=change_id)
    relpath = _rel(path, root)
    if not path.is_file():
        raise RuntimeError(
            f"missing {relpath}; run scripts/check-change-footprint.py {change_id} "
            "at the end of 08"
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid {relpath}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"invalid {relpath}: top level must be an object")
    return data


def compute_changes(
    base_files: dict[str, str], current_files: dict[str, str]
) -> list[dict]:
    """Return sorted ``[{"path","status","sha256"}]`` for added/modified/deleted files.

    ``sha256`` pins the content of the diff: for added/modified paths it is the
    current file hash, for deleted paths the base snapshot hash. This lets
    ``--verify`` detect a content-only re-edit of a path that was already
    ``modified`` at stage 08.
    """
    changed: list[dict] = []
    for path in sorted(set(base_files) | set(current_files)):
        if path not in base_files:
            status, digest = "added", current_files[path]
        elif path not in current_files:
            status, digest = "deleted", base_files[path]
        elif base_files[path] != current_files[path]:
            status, digest = "modified", current_files[path]
        else:
            continue
        changed.append({"path": path, "status": status, "sha256": digest})
    return changed


def diff_hash(changed_paths: list[dict]) -> str:
    """SHA-256 of the canonical JSON of the sorted changed paths.

    Each entry is ``{path,status,sha256}``; ``sort_keys`` makes the serialization
    canonical regardless of dict construction order.
    """
    canonical = json.dumps(changed_paths, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def diff_document(
    change_id: str, base_fingerprint: str, changed_paths: list[dict]
) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "change_id": change_id,
        "base_fingerprint": base_fingerprint,
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "changed_paths": changed_paths,
        "diff_sha256": diff_hash(changed_paths),
    }


def classify_path(relpath: str, context: dict) -> list[str]:
    """Return the footprint errors for one changed path (empty when allowed)."""
    problems: list[str] = []

    owned = any(_inside(relpath, entry) for entry in context["owned"])
    integration = any(
        _inside(relpath, entry["path"]) for entry in context["integration"]
    )

    shared_hits = [
        shared for shared in context["shared_paths"] if _inside(relpath, shared)
    ]
    shared_ok = True
    for shared in shared_hits:
        # The changed file itself must be inside an owned entry that is inside
        # this shared path; an owned entry under a sibling resource does not
        # narrow a change in another resource of the same shared directory.
        narrowed = any(
            _inside(relpath, entry) and _inside(entry, shared)
            for entry in context["owned"]
        )
        if not narrowed:
            shared_ok = False
            problems.append(
                f"changed path {relpath!r} is inside module shared path {shared!r}; "
                "add an Owned paths entry that contains the changed file and is "
                "inside that shared path"
            )

    frozen_hits = [
        pattern
        for pattern in context["frozen_patterns"]
        if _pattern_matches(relpath, pattern)
    ]
    approved = any(
        _inside(relpath, entry["path"]) for entry in context["frozen_approvals"]
    )
    if frozen_hits and not approved:
        problems.append(
            f"changed path {relpath!r} is under frozen path {frozen_hits[0]!r}; "
            "add an approved BCR to Frozen approvals"
        )

    allowed = (
        owned
        or integration
        or (bool(shared_hits) and shared_ok)
        or (bool(frozen_hits) and approved)
    )
    if not allowed and not problems:
        problems.append(
            f"changed path {relpath!r} is not owned, integration, explicitly "
            "narrowed shared, or BCR-approved frozen"
        )
    return problems


def check_diff(
    change_id: str, root: Path | None = None, verify: bool = False
) -> tuple[dict, list[str], Path | None, list[dict]]:
    """Diff the workspace against the base snapshot, classify, and write/verify."""
    change_id = _validate_change_id(change_id)
    base_root = _root(root)

    context, errors = check_declaration(change_id, base_root)
    if errors:
        return context, errors, None, []

    base, base_fingerprint = load_base(change_id, base_root)
    current = gm.enumerate_files(base_root, change_id)
    changed = compute_changes(base["files"], current)

    if verify:
        stored = load_stored_diff(change_id, base_root)
        stored_paths = [
            item.get("path")
            for item in stored.get("changed_paths") or []
            if isinstance(item, dict)
        ]
        if sorted(stored_paths) != [item["path"] for item in changed]:
            errors.append(
                "implementation-diff.json path set does not match the recomputed "
                f"diff (stored {len(stored_paths)} path(s), recomputed {len(changed)})"
            )
        if stored.get("diff_sha256") != diff_hash(changed):
            errors.append(
                "implementation-diff.json diff_sha256 does not match the "
                "recomputed diff"
            )
        if stored.get("base_fingerprint") != base_fingerprint:
            errors.append(
                "implementation-diff.json base_fingerprint does not match "
                "implementation-base.json"
            )
        if stored.get("change_id") != change_id:
            errors.append(
                "implementation-diff.json change_id does not match the Change"
            )

    for item in changed:
        for problem in classify_path(item["path"], context):
            errors.append(f"{item['status']}: {problem}")

    if errors or verify:
        return context, errors, None, changed

    target = base_root / DIFF_REL.format(change_id=change_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    document = diff_document(change_id, base_fingerprint, changed)
    target.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return context, errors, target, changed


# -- CLI ----------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check-change-footprint.py",
        description="Validate the Implementation Slice declaration and code footprint.",
    )
    parser.add_argument("change_id", metavar="change-id")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--declaration-only",
        action="store_true",
        help="validate the design.md slice only (stage 07)",
    )
    group.add_argument(
        "--verify",
        action="store_true",
        help="recompute the diff from the base and compare with implementation-diff.json",
    )
    args = parser.parse_args(argv)

    try:
        change_id = _validate_change_id(args.change_id)
        strategy = gm.strategy(root=ROOT)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if strategy == "none":
        print("FOOTPRINT_CHECK=SKIPPED (strategy none)")
        return 0

    try:
        if args.declaration_only:
            _context, errors = check_declaration(change_id, ROOT)
            written = None
            changed: list[dict] = []
        else:
            _context, errors, written, changed = check_diff(
                change_id, ROOT, verify=args.verify
            )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1

    if args.declaration_only:
        print("FOOTPRINT_CHECK=PASSED (declaration)")
    elif args.verify:
        print(f"FOOTPRINT_CHECK=PASSED (verify, {len(changed)} changed path(s))")
    else:
        print(f"Wrote {_rel(written, ROOT)} ({len(changed)} changed path(s))")
        print("FOOTPRINT_CHECK=PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
