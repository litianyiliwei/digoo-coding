#!/usr/bin/env python3
"""Validate the module registry (docs/product/modules.csv).

Rules (strategy ``module-packages`` only; ``none``/missing layout and
``footprint`` skip because the module registry is not required there):

- required CSV headers present, unique, and exactly the nine documented columns;
- ``module_slug`` is unique;
- ``status`` is one of PLANNED / ACTIVE / DELIVERED / DEPRECATED;
- every ``domain_id`` exists as a ``DOM-xxx`` row in ``domain-boundaries.md``
  (a missing/unreadable file fails closed);
- ``frontend_paths``/``backend_paths`` entries start with a
  ``code-layout.json`` roots value, are not the root itself, contain no
  ``<...>`` placeholder token, and are globally unique across every module and
  both lists (case-insensitive, so ``Server/X`` and ``server/x`` cannot both
  pass);
- ``shared_paths`` entries sit strictly under one of this module's own
  frontend/backend paths (case-insensitive);
- ``capabilities`` entries exist in ``capabilities.csv``; N/A and blank lists
  are allowed;
- every capability whose ``capabilities.csv.owner_module`` is this module is
  listed by the module; a non-owner module may also list it (hosting is
  allowed);
- ACTIVE/DELIVERED modules declare at least one frontend/backend path and a
  ``<path>/MODULE.md`` module card exists under each declared path;
- ``--completed <module-slug>`` requires the module to be DELIVERED and no
  capability owned by it to retain a non-blank ``active_changes``.

WARN-only: structurally valid ``PENDING`` placeholder rows and a module that
has no capabilities yet.

Reuses the shared parsers in ``gate_common`` (Task 2).
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import gate_common as gm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

MODULES_REL = "docs/product/modules.csv"
CAPABILITIES_REL = "docs/product/capabilities.csv"
DOMAINS_REL = "docs/architecture/domain-boundaries.md"
LAYOUT_REL = "docs/architecture/code-layout.json"

REQUIRED_HEADERS = (
    "module_slug",
    "module_name",
    "domain_id",
    "frontend_paths",
    "backend_paths",
    "shared_paths",
    "capabilities",
    "status",
    "notes",
)
STATUSES = {"PLANNED", "ACTIVE", "DELIVERED", "DEPRECATED"}
CARD_REQUIRED_STATUSES = {"ACTIVE", "DELIVERED"}
PLACEHOLDER = "PENDING"
DOM_ROW_RE = re.compile(r"DOM-[0-9]+", re.I)
TOKEN_SPLIT_RE = re.compile(r"[;,]")
ABSOLUTE_PATH_RE = re.compile(r"^(?:/|[A-Za-z]:)")
WILDCARD_PATH_RE = re.compile(r"[*?]")
PLACEHOLDER_TOKEN_RE = re.compile(r"<[^/>]+>")


def _root() -> Path:
    return Path(ROOT)


def _rel(path: Path) -> str:
    try:
        return path.relative_to(_root()).as_posix()
    except ValueError:
        return path.as_posix()


def _is_blank(value: str) -> bool:
    value = (value or "").strip()
    upper = value.upper()
    return not value or upper.startswith("N/A") or upper == PLACEHOLDER


def _tokens(value: str) -> list[str]:
    return [item.strip() for item in TOKEN_SPLIT_RE.split(value or "") if item.strip()]


def _is_placeholder_slug(slug: str) -> bool:
    slug = (slug or "").strip()
    return slug.upper() == PLACEHOLDER or (slug.startswith("<") and slug.endswith(">"))


def _split_values(value, *, capabilities: bool = False) -> list[str]:
    """Split a registry list cell; drop blanks, ``N/A`` and placeholder tokens."""
    values = value if isinstance(value, list) else _tokens(value or "")
    result: list[str] = []
    for item in values:
        for token in _tokens(item):
            token = token.strip()
            if not token or token.upper().startswith("N/A"):
                continue
            if capabilities and token.upper() == PLACEHOLDER:
                continue
            result.append(token)
    return result


def _norm_path(value: str) -> str:
    """Normalize a repo-relative path: POSIX separators, no ``./``, no edge slashes."""
    value = str(value or "").strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    value = re.sub(r"/+", "/", value)
    return value.strip("/")


def _path_problem(value: str) -> str:
    """Return why a module/shared path is unsafe, or ``""`` when it is acceptable."""
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
    match = PLACEHOLDER_TOKEN_RE.search(raw)
    if match:
        return (
            f"contains a placeholder token {match.group(0)!r}; declare a "
            "concrete repo-relative module path"
        )
    return ""


def _has_active_change(value: str) -> bool:
    """True when at least one ``;``/``,`` token is not blank/N/A/PENDING."""
    return any(not _is_blank(token) for token in _tokens(value or ""))


def _read_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        try:
            return [cell.strip() for cell in next(reader)]
        except StopIteration:
            return []


def _domain_ids(path: Path) -> set[str]:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise RuntimeError(f"cannot read {_rel(path)}: {exc}") from exc
    ids = set()
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [
            cell.strip().strip("*` ").strip()
            for cell in stripped.strip("|").split("|")
        ]
        if cells and DOM_ROW_RE.fullmatch(cells[0]):
            ids.add(cells[0].upper())
    return ids


def _layout_roots(layout: dict) -> list[str]:
    """Normalized root values from ``code-layout.json`` ``roots`` (dict or list)."""
    roots = layout.get("roots") if isinstance(layout, dict) else None
    if isinstance(roots, dict):
        values = list(roots.values())
    elif isinstance(roots, list):
        values = roots
    else:
        return []
    normalized: list[str] = []
    for value in values:
        if isinstance(value, str):
            norm = _norm_path(value)
            if norm:
                normalized.append(norm)
    return normalized


def _module_card(layout: dict) -> str:
    card = (layout or {}).get("module_card") if isinstance(layout, dict) else None
    if isinstance(card, str) and card.strip():
        return card.strip().replace("\\", "/").lstrip("/")
    return "MODULE.md"


def _root_state(path_norm: str, roots: list[str]) -> str:
    """Return ``equals``, ``under`` or ``outside`` for a module path against roots."""
    folded = path_norm.casefold()
    for root in roots:
        root_folded = root.casefold()
        if folded == root_folded:
            return "equals"
        if gm.path_matches(folded, root_folded + "/**"):
            return "under"
    return "outside"


def _header_errors(header: list[str]) -> tuple[list[str], bool]:
    errors: list[str] = []
    if not header:
        return [f"{MODULES_REL}: empty or missing header row"], False
    missing = [name for name in REQUIRED_HEADERS if name not in header]
    unexpected = [name for name in header if name and name not in REQUIRED_HEADERS]
    duplicated = sorted(
        {name for name in header if name and header.count(name) > 1}
    )
    if missing:
        errors.append(
            f"{MODULES_REL}: missing required header(s): {', '.join(missing)}"
        )
    if unexpected:
        errors.append(f"{MODULES_REL}: unexpected header(s): {', '.join(unexpected)}")
    if duplicated:
        errors.append(f"{MODULES_REL}: duplicate header(s): {', '.join(duplicated)}")
    return errors, not (missing or unexpected or duplicated)


def _validate_rows(
    rows: list[dict],
    roots: list[str],
    module_card: str,
    domain_ids: set[str] | None,
    capability_rows: list[dict] | None,
    capability_slugs: set[str] | None,
) -> tuple[list[str], list[str], int]:
    """Return (errors, warnings, unique module count)."""
    errors: list[str] = []
    warnings: list[str] = []
    by_slug: dict[str, list[int]] = defaultdict(list)
    module_caps: dict[str, set[str]] = defaultdict(set)
    path_map: dict[str, tuple[int, str, str, str]] = {}

    if not roots:
        errors.append(
            f"{LAYOUT_REL}: no roots defined; module paths cannot be validated"
        )

    for index, row in enumerate(rows, start=1):
        slug = (row.get("module_slug") or "").strip()
        if _is_placeholder_slug(slug):
            warnings.append(
                f"{MODULES_REL} row {index}: placeholder row {slug!r} skipped"
            )
            continue
        if not slug:
            errors.append(f"{MODULES_REL} row {index}: missing module_slug")
            continue
        by_slug[slug].append(index)

        status_raw = (row.get("status") or "").strip()
        status = status_raw.upper()
        if status not in STATUSES:
            errors.append(
                f"{MODULES_REL} row {index}: invalid status {status_raw!r}; "
                "expected PLANNED|ACTIVE|DELIVERED|DEPRECATED"
            )

        domain_raw = (row.get("domain_id") or "").strip()
        if domain_ids is not None and domain_raw.upper() not in domain_ids:
            errors.append(
                f"{MODULES_REL} row {index}: domain_id {domain_raw!r} not found as a "
                f"DOM-xxx row in {DOMAINS_REL}"
            )

        front = _split_values(row.get("frontend_paths"))
        back = _split_values(row.get("backend_paths"))
        shared = _split_values(row.get("shared_paths"))
        caps = _split_values(row.get("capabilities"), capabilities=True)
        module_caps[slug].update(caps)

        if capability_slugs is not None:
            for cap in caps:
                if cap not in capability_slugs:
                    errors.append(
                        f"{MODULES_REL} row {index} (module {slug!r}): capability "
                        f"{cap!r} not found in {CAPABILITIES_REL}"
                    )

        declared: list[tuple[str, str, str]] = []
        for field, values in (("frontend_paths", front), ("backend_paths", back)):
            for original in values:
                problem = _path_problem(original)
                if problem:
                    errors.append(
                        f"{MODULES_REL} row {index} (module {slug!r}): {field} "
                        f"path {original!r} {problem}; declare a repo-relative "
                        "module directory"
                    )
                    continue
                norm = _norm_path(original)
                if not norm:
                    errors.append(
                        f"{MODULES_REL} row {index} (module {slug!r}): empty {field} "
                        f"entry {original!r}"
                    )
                    continue
                declared.append((field, original, norm))
                key = norm.casefold()
                if key in path_map:
                    prev_index, prev_slug, prev_field, prev_original = path_map[key]
                    errors.append(
                        f"{MODULES_REL} row {index} (module {slug!r}): duplicate path "
                        f"{original!r} in {field} (already declared as {prev_original!r} "
                        f"in {prev_field} by module {prev_slug!r} at row {prev_index})"
                    )
                else:
                    path_map[key] = (index, slug, field, original)
                if roots:
                    state = _root_state(norm, roots)
                    if state == "equals":
                        errors.append(
                            f"{MODULES_REL} row {index} (module {slug!r}): {field} "
                            f"path {original!r} equals a code-layout root; declare a "
                            "module subdirectory"
                        )
                    elif state == "outside":
                        roots_text = ", ".join(root + "/" for root in roots)
                        errors.append(
                            f"{MODULES_REL} row {index} (module {slug!r}): {field} "
                            f"path {original!r} does not start with any "
                            f"code-layout.json roots value ({roots_text})"
                        )

        owns = [norm for _, _, norm in declared]
        for original in shared:
            problem = _path_problem(original)
            if problem:
                errors.append(
                    f"{MODULES_REL} row {index} (module {slug!r}): shared path "
                    f"{original!r} {problem}"
                )
                continue
            norm = _norm_path(original)
            folded = norm.casefold()
            if not any(
                folded.startswith(own.casefold() + "/") for own in owns
            ):
                errors.append(
                    f"{MODULES_REL} row {index} (module {slug!r}): shared path "
                    f"{original!r} is not under any of this module's "
                    "frontend_paths/backend_paths"
                )

        if status in CARD_REQUIRED_STATUSES:
            if not (front or back):
                errors.append(
                    f"{MODULES_REL} row {index} (module {slug!r}): status {status} "
                    "requires at least one frontend_paths or backend_paths"
                )
            for field, original, norm in declared:
                card_path = _root() / norm / module_card
                if not card_path.is_file():
                    errors.append(
                        f"{MODULES_REL} row {index} (module {slug!r}): missing module "
                        f"card {_rel(card_path)} for {field} path {original!r}"
                    )

    for slug, indices in by_slug.items():
        if len(indices) > 1:
            row_numbers = ", ".join(str(i) for i in indices)
            errors.append(
                f"{MODULES_REL}: duplicate module_slug {slug!r} on rows "
                f"{row_numbers} (first at row {indices[0]})"
            )
        if not module_caps.get(slug):
            warnings.append(
                f"{MODULES_REL} row {indices[0]} (module {slug!r}): "
                "no capabilities listed yet"
            )

    if capability_rows is not None:
        cap_owners: dict[str, dict[str, list[int]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for cap_index, cap_row in enumerate(capability_rows, start=1):
            cap_slug = (cap_row.get("capability_slug") or "").strip()
            if _is_placeholder_slug(cap_slug) or not cap_slug:
                continue
            owner = (cap_row.get("owner_module") or "").strip()
            if _is_blank(owner):
                continue
            cap_owners[cap_slug][owner].append(cap_index)
            if owner not in by_slug:
                continue
            if cap_slug not in module_caps.get(owner, set()):
                errors.append(
                    f"{MODULES_REL} row {by_slug[owner][0]} (module {owner!r}): does "
                    f"not list owned capability {cap_slug!r} "
                    f"(owner_module in {CAPABILITIES_REL} row {cap_index})"
                )
        for cap_slug, owners in sorted(cap_owners.items()):
            if len(owners) > 1:
                detail = ", ".join(
                    f"{owner!r} (row {indices[0]})"
                    for owner, indices in sorted(owners.items())
                )
                errors.append(
                    f"{CAPABILITIES_REL}: capability {cap_slug!r} has multiple owner "
                    f"modules: {detail}"
                )

    return errors, warnings, len(by_slug)


def _completed_errors(
    rows: list[dict], capability_rows: list[dict] | None, slug: str
) -> list[str]:
    errors: list[str] = []
    matches = gm.module_rows(rows, slug)
    if not matches:
        return [f"--completed {slug}: module not found in {MODULES_REL}"]
    statuses = [(row.get("status") or "").strip().upper() for row in matches]
    if any(status != "DELIVERED" for status in statuses):
        listing = ", ".join(sorted(set(statuses))) or "blank"
        errors.append(
            f"--completed {slug}: module status is {listing}; expected DELIVERED"
        )
    if capability_rows is not None:
        for index, row in enumerate(capability_rows, start=1):
            cap_slug = (row.get("capability_slug") or "").strip()
            if _is_placeholder_slug(cap_slug) or not cap_slug:
                continue
            if (row.get("owner_module") or "").strip() != slug:
                continue
            active = row.get("active_changes") or ""
            if _has_active_change(active):
                errors.append(
                    f"--completed {slug}: capability {cap_slug!r} (row {index}) still "
                    f"lists active_changes {active!r}"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check-modules.py",
        description="Check the module registry (docs/product/modules.csv).",
    )
    parser.add_argument("--completed", metavar="MODULE-SLUG", default=None)
    args = parser.parse_args(argv)

    root = _root()
    try:
        strategy = gm.strategy(root=root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        print("Modules check failed: 1 error(s), 0 warning(s).")
        return 1
    if strategy != "module-packages":
        print(f"MODULES_CHECK=SKIPPED (strategy {strategy})")
        return 0

    try:
        layout = gm.load_code_layout(root=root) or {}
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        print("Modules check failed: 1 error(s), 0 warning(s).")
        return 1

    roots = _layout_roots(layout)
    module_card = _module_card(layout)

    errors: list[str] = []
    warnings: list[str] = []

    modules_path = root / MODULES_REL
    header_ok = False
    rows: list[dict] = []
    if not modules_path.is_file():
        errors.append(
            f"{MODULES_REL}: missing module registry "
            "(required by strategy module-packages)"
        )
    else:
        try:
            header = _read_header(modules_path)
        except OSError as exc:
            errors.append(f"cannot read {MODULES_REL}: {exc}")
            header = []
        header_errors, header_ok = _header_errors(header)
        errors.extend(header_errors)
        if header_ok:
            try:
                rows = gm.load_modules(root=root)
            except RuntimeError as exc:
                errors.append(str(exc))
                rows = []
            if not rows:
                errors.append(
                    f"{MODULES_REL}: module registry has no data rows "
                    "(required by strategy module-packages)"
                )

    domain_ids: set[str] | None = None
    domains_path = root / DOMAINS_REL
    if not domains_path.is_file():
        errors.append(f"{DOMAINS_REL}: missing domain boundaries file")
    else:
        try:
            domain_ids = _domain_ids(domains_path)
        except RuntimeError as exc:
            errors.append(str(exc))
            domain_ids = None
        else:
            if not domain_ids:
                errors.append(f"{DOMAINS_REL}: no DOM-xxx table rows found")
                domain_ids = None

    capability_rows: list[dict] | None = None
    capability_slugs: set[str] | None = None
    capabilities_path = root / CAPABILITIES_REL
    if not capabilities_path.is_file():
        errors.append(f"{CAPABILITIES_REL}: missing capability registry")
    else:
        try:
            capability_rows = gm.load_capabilities(root=root)
        except RuntimeError as exc:
            errors.append(str(exc))
            capability_rows = None
        else:
            capability_slugs = {
                (row.get("capability_slug") or "").strip()
                for row in capability_rows
                if (row.get("capability_slug") or "").strip()
                and not _is_placeholder_slug(row.get("capability_slug") or "")
            }

    module_count = 0
    path_count = 0
    if header_ok and rows:
        row_errors, row_warnings, module_count = _validate_rows(
            rows,
            roots,
            module_card,
            domain_ids,
            capability_rows,
            capability_slugs,
        )
        errors.extend(row_errors)
        warnings.extend(row_warnings)
        slugs: list[str] = []
        seen: set[str] = set()
        for row in rows:
            slug = (row.get("module_slug") or "").strip()
            if not slug or _is_placeholder_slug(slug) or slug in seen:
                continue
            seen.add(slug)
            slugs.append(slug)
        path_count = sum(len(gm.module_paths(rows, [slug])) for slug in slugs)

    if args.completed and header_ok and rows:
        errors.extend(_completed_errors(rows, capability_rows, args.completed))

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(
            f"Modules check failed: {len(errors)} error(s), "
            f"{len(warnings)} warning(s)."
        )
        return 1
    print(f"Modules check passed: {module_count} module(s), {path_count} path(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
