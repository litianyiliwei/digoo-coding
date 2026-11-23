#!/usr/bin/env python3
"""Generate the stage-08 implementation context manifest for a Change.

Usage:
  python scripts/code-context.py <change-id>

Reads ``openspec/changes/<change-id>/design.md`` (its ``### Implementation
Slice`` block), ``docs/product/capabilities.csv``, ``docs/product/modules.csv``
and ``docs/architecture/code-layout.json``, then writes
``openspec/changes/<change-id>/design/context-manifest.json`` — the retrieval
closure the implementer must read before starting stage 08. It is not a gate.

The manifest lists:

* ``read_set`` — every current file under the slice ``Owned paths`` prefixes
  (``owned``), the owner/related modules' module cards (``module-card``;
  ``code-layout.json.module_card``, default ``MODULE.md``), existing Change
  contracts (``contract``) and ``test-cases.csv`` (``test``), the slice
  integration paths (``integration``) and the product registries
  (``registry``);
* ``not_needed`` — package paths of registered modules that are neither owner
  nor related (``other module``);
* ``missing`` — required inputs that could not be located (missing module
  cards); this does not fail generation.

``strategy=none`` (or a missing layout) skips with
``CODE_CONTEXT=SKIPPED (strategy none)`` and exit code 0, writing nothing.
Missing required slice fields and unknown owner/related modules exit 1 with
path-bearing errors; no manifest is written in that case.

Path normalization is shared with ``check-change-footprint.py``: paths are
repository relative, must not be absolute or contain ``.``/``..`` segments, and
only a strictly trailing ``/**`` subtree marker is accepted (normalized to its
directory prefix).
"""
from __future__ import annotations

import argparse
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

MANIFEST_REL = "openspec/changes/{change_id}/design/context-manifest.json"
DESIGN_REL = "openspec/changes/{change_id}/design.md"
CHANGE_DIR_REL = "openspec/changes/{change_id}/"

# Change-scoped design/API assets, relative to the Change directory.
CONTRACT_ASSETS = (
    ("api/openapi.yaml", "OpenAPI contract"),
    ("design/interface-catalog.csv", "interface catalog"),
    ("design/io-catalog.csv", "IO operation catalog"),
    ("design/api-io-mapping.csv", "API-IO mapping"),
    ("design/ui-actions.csv", "UI action mapping"),
)
TEST_ASSETS = (("design/test-cases.csv", "test case matrix"),)
REGISTRY_ASSETS = (
    ("docs/product/capabilities.csv", "capability registry"),
    ("docs/product/modules.csv", "module registry"),
)

REQUIRED_SLICE_FIELDS = {
    "module-packages": (
        ("primary", "Primary capability"),
        ("owner_module", "Owner module"),
        ("related_modules", "Related modules"),
        ("owned", "Owned paths"),
        ("integration", "Integration paths"),
    ),
    "footprint": (
        ("owned", "Owned paths"),
        ("integration", "Integration paths"),
    ),
}

CATEGORIES = {
    "owned",
    "module-card",
    "contract",
    "test",
    "integration",
    "registry",
}

ABSOLUTE_PATH_RE = re.compile(r"^(?:/|[A-Za-z]:)")
WILDCARD_PATH_RE = re.compile(r"[*?]")
PLACEHOLDER_SEGMENT_RE = re.compile(r"<[^/>]+>")


def _root(root: Path | None = None) -> Path:
    return Path(root) if root is not None else Path(ROOT)


def _rel(path: Path, root: Path | None = None) -> str:
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


# -- path helpers (mirror check-change-footprint.py) ---------------------------------
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


def _module_card(layout: dict) -> str:
    """Return the normalized module card path from ``code-layout.json``."""
    card = layout.get("module_card") if isinstance(layout, dict) else None
    if isinstance(card, str) and card.strip():
        return _norm_path(card) or "MODULE.md"
    return "MODULE.md"


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


def _real_values(items: list[str]) -> list[str]:
    return [item.strip() for item in items if item.strip() and not _is_na(item)]


def _under(relpath: str, prefix: str) -> bool:
    """True when ``relpath`` equals ``prefix`` or descends into its subtree."""
    return gm.path_matches(relpath, prefix) or gm.path_matches(relpath, prefix + "/**")


def _change_asset(change_id: str, relpath: str) -> str:
    return CHANGE_DIR_REL.format(change_id=change_id) + relpath


# -- loading ------------------------------------------------------------------
def load_design(change_id: str, root: Path | None = None) -> str:
    path = _root(root) / DESIGN_REL.format(change_id=change_id)
    relpath = _rel(path, root)
    if not path.is_file():
        raise RuntimeError(f"missing {relpath}")
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"cannot read {relpath}: {exc}") from exc


def _read_set_entry(path: str, category: str, reason: str) -> dict:
    return {"path": path, "category": category, "reason": reason}


def _existing_asset(base: Path, relpath: str) -> bool:
    return (base / relpath).is_file()


# -- generation ---------------------------------------------------------------
def _validate_slice(
    change_id: str,
    strategy: str,
    parsed: dict,
    errors: list[str],
    root: Path | None = None,
) -> dict:
    """Validate the slice values and return the resolved context."""
    design_rel = DESIGN_REL.format(change_id=change_id)
    present = set(parsed["present"])
    for field, label in REQUIRED_SLICE_FIELDS[strategy]:
        if field not in present:
            errors.append(f"{design_rel}: missing required slice field {label}")

    capabilities = gm.load_capabilities(root=_root(root))
    modules = gm.load_modules(root=_root(root))

    primary = ""
    if "primary" in present:
        value = (parsed["primary"] or "").strip()
        if _is_na(value) or not value:
            if strategy == "module-packages":
                errors.append(
                    f"{design_rel}: field Primary capability "
                    "must not be empty or N/A"
                )
        else:
            primary = value
            if not gm.capability_rows(capabilities, primary):
                errors.append(
                    f"{design_rel}: Primary capability {primary!r} is not in "
                    "docs/product/capabilities.csv"
                )

    owner = ""
    if "owner_module" in present:
        value = (parsed["owner_module"] or "").strip()
        if _is_na(value) or not value:
            if strategy == "module-packages":
                errors.append(
                    f"{design_rel}: field Owner module "
                    "must not be empty or N/A"
                )
        else:
            owner = value
            if not gm.module_rows(modules, owner):
                errors.append(
                    f"{design_rel}: Owner module {owner!r} is not in "
                    "docs/product/modules.csv"
                )

    related: list[str] = []
    for slug in parsed["related_modules"]:
        if gm.module_rows(modules, slug):
            related.append(slug)
        else:
            errors.append(
                f"{design_rel}: Related module {slug!r} is not in "
                "docs/product/modules.csv"
            )

    layout = gm.load_code_layout(root=_root(root)) or {}
    module_card = _module_card(layout)
    module_slugs = ([owner] if owner else []) + related
    for path in gm.module_paths(modules, module_slugs):
        normalized = _norm_path(path)
        if not normalized:
            errors.append(f"{design_rel}: module path {path!r} is empty")
        elif PLACEHOLDER_SEGMENT_RE.search(normalized):
            errors.append(
                f"{design_rel}: module path {path!r} contains a '<...>' "
                "placeholder; declare concrete module paths in "
                "docs/product/modules.csv"
            )

    owned: list[str] = []
    owned_values = _real_values(parsed["owned"])
    if "owned" in present and not owned_values:
        errors.append(
            f"{design_rel}: field Owned paths must contain at least one real "
            "path (not empty or N/A)"
        )
    for raw in owned_values:
        prefix = _slice_path_prefix(raw)
        problem = _path_problem(prefix)
        if problem:
            errors.append(
                f"{design_rel}: Owned paths entry {raw!r} {problem}"
            )
            continue
        if not prefix:
            errors.append(
                f"{design_rel}: Owned paths entry {raw!r} resolves to an empty path"
            )
            continue
        owned.append(prefix)

    integration: list[dict] = []
    for entry in parsed["integration"]:
        path = (entry.get("path") or "").strip()
        prefix = _slice_path_prefix(path)
        problem = _path_problem(prefix)
        if problem:
            errors.append(
                f"{design_rel}: integration path {path!r} {problem}"
            )
            continue
        if not prefix:
            errors.append(
                f"{design_rel}: integration path {path!r} resolves to an empty path"
            )
            continue
        reason = (entry.get("reason") or "").strip() or "integration path"
        integration.append({"path": prefix, "reason": reason})

    return {
        "primary": primary,
        "owner": owner,
        "related": related,
        "owned": owned,
        "integration": integration,
        "module_card": module_card,
        "modules": modules,
        "capabilities": capabilities,
    }


def build_document(
    change_id: str, strategy: str, parsed: dict, root: Path | None = None
) -> tuple[dict | None, list[str]]:
    """Build the manifest document (no disk writes) and return ``(doc, errors)``."""
    base = _root(root)
    errors: list[str] = []
    context = _validate_slice(change_id, strategy, parsed, errors, base)

    read_set: list[dict] = []
    missing: list[dict] = []
    not_needed: list[dict] = []

    if not errors:
        # Owned files: every current file under an owned prefix.
        files = gm.enumerate_files(base, change_id)
        owned_prefixes = context["owned"]
        for relpath in sorted(files):
            for prefix in owned_prefixes:
                if _under(relpath, prefix):
                    read_set.append(
                        _read_set_entry(
                            relpath, "owned", f"matches owned path {prefix}"
                        )
                    )
                    break

        # Module cards for owner and related modules.
        slugs = ([context["owner"]] if context["owner"] else []) + context["related"]
        for path in gm.module_paths(context["modules"], slugs):
            prefix = _norm_path(path)
            if not prefix:
                continue
            card = f"{prefix}/{context['module_card']}"
            if _existing_asset(base, card):
                read_set.append(
                    _read_set_entry(card, "module-card", f"module card for {prefix}")
                )
            else:
                missing.append(
                    {
                        "path": card,
                        "category": "module-card",
                        "reason": f"module card not found for {prefix}",
                    }
                )

        # Existing change-scoped contracts and tests.
        for relpath, reason in CONTRACT_ASSETS:
            asset = _change_asset(change_id, relpath)
            if _existing_asset(base, asset):
                read_set.append(_read_set_entry(asset, "contract", reason))
        for relpath, reason in TEST_ASSETS:
            asset = _change_asset(change_id, relpath)
            if _existing_asset(base, asset):
                read_set.append(_read_set_entry(asset, "test", reason))

        # Slice integration paths.
        for entry in context["integration"]:
            read_set.append(
                _read_set_entry(entry["path"], "integration", entry["reason"])
            )

        # Registries.
        for relpath, reason in REGISTRY_ASSETS:
            if _existing_asset(base, relpath):
                read_set.append(_read_set_entry(relpath, "registry", reason))

        # Other registered modules are deliberately out of context.
        claimed = {
            _norm_path(path)
            for path in gm.module_paths(context["modules"], slugs)
        }
        others = []
        for row in context["modules"]:
            slug = (row.get("module_slug") or "").strip()
            if slug and slug not in slugs and slug not in others:
                others.append(slug)
        for path in gm.module_paths(context["modules"], others):
            prefix = _norm_path(path)
            if not prefix or prefix in claimed:
                continue
            not_needed.append({"path": prefix, "reason": "other module"})

    if errors:
        return None, errors

    capability = context["primary"] or "N/A"
    document = {
        "change_id": change_id,
        "capability": capability,
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "read_set": _sorted_unique(read_set),
        "not_needed": _sorted_unique(not_needed),
        "missing": _sorted_unique(missing),
    }
    problem = validate_manifest(document)
    if problem:
        raise RuntimeError(f"generated manifest failed schema validation: {problem}")
    return document, []


def _sorted_unique(items: list[dict]) -> list[dict]:
    """Sort by path (then category) and drop exact duplicate entries."""
    seen = set()
    unique = []
    for item in items:
        key = (item["path"], item.get("category", ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return sorted(unique, key=lambda item: (item["path"], item.get("category", "")))


def validate_manifest(document: dict) -> str:
    """Return a structural schema problem, or ``""`` when the document is valid."""
    if not isinstance(document, dict):
        return "top level must be an object"
    expected = {
        "change_id",
        "capability",
        "generated_at",
        "read_set",
        "not_needed",
        "missing",
    }
    if set(document) != expected:
        return f"top-level keys {sorted(document)} != {sorted(expected)}"
    for key in ("change_id", "capability", "generated_at"):
        if not isinstance(document[key], str) or not document[key]:
            return f"{key} must be a non-empty string"
    checks = {
        "read_set": ("path", "category", "reason"),
        "not_needed": ("path", "reason"),
        "missing": ("path", "category", "reason"),
    }
    for key, fields in checks.items():
        value = document[key]
        if not isinstance(value, list):
            return f"{key} must be an array"
        expect_category = "category" in fields
        for index, item in enumerate(value):
            if not isinstance(item, dict) or set(item) != set(fields):
                return f"{key}[{index}] must have exactly {list(fields)}"
            for field in fields:
                if not isinstance(item[field], str) or not item[field]:
                    return f"{key}[{index}].{field} must be a non-empty string"
            if expect_category and item["category"] not in CATEGORIES:
                return f"{key}[{index}].category {item['category']!r} is invalid"
    return ""


def write_manifest(
    change_id: str, root: Path | None = None
) -> tuple[Path | None, dict | None, list[str]]:
    """Generate and write the manifest; return ``(path, doc, errors)``."""
    base = _root(root)
    change_id = _validate_change_id(change_id)
    strategy = gm.strategy(root=base)
    if strategy == "none":
        return None, None, []
    parsed = gm.parse_slice(load_design(change_id, base))
    document, errors = build_document(change_id, strategy, parsed, base)
    if errors or document is None:
        return None, None, errors
    target = base / MANIFEST_REL.format(change_id=change_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return target, document, []


# -- CLI ----------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="code-context.py",
        description="Generate the stage-08 implementation context manifest.",
    )
    parser.add_argument("change_id", metavar="change-id")
    args = parser.parse_args(argv)

    try:
        change_id = _validate_change_id(args.change_id)
        strategy = gm.strategy(root=ROOT)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if strategy == "none":
        print("CODE_CONTEXT=SKIPPED (strategy none)")
        return 0

    try:
        target, document, errors = write_manifest(change_id, ROOT)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1

    assert target is not None and document is not None
    print(
        f"Wrote {_rel(target, ROOT)} "
        f"({len(document['read_set'])} read, "
        f"{len(document['not_needed'])} not needed, "
        f"{len(document['missing'])} missing)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
