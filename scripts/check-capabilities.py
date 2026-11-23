#!/usr/bin/env python3
"""Validate the capability progress registry against modules, domains and roadmap.

Rules (strategy ``module-packages`` only; ``none``/missing layout and
``footprint`` skip):

- required CSV headers present, unique, and exactly the ten documented columns;
- every ``capability_slug`` appears on exactly one row, and one capability has
  exactly one owner module (conflicting owners across rows are an error);
- ``status`` is one of PLANNED / ACTIVE / DELIVERED / DEPRECATED;
- every ``domain_id`` exists as a ``DOM-xxx`` row in ``domain-boundaries.md``
  (a missing/unreadable file fails closed);
- ``owner_module`` is non-blank, exists in ``modules.csv``, and that module's
  ``capabilities`` column lists this capability;
- every ``related_modules`` slug exists in ``modules.csv``;
- a capability whose Change in ``active_changes`` has roadmap
  ``Slice Coverage=partial`` must declare non-empty ``remaining_slices``
  (empty / ``N/A`` / ``PENDING`` count as blank); partial Changes present only
  in ``delivered_slices`` are historical and impose no remaining-work
  requirement;
- ``--completed <change-id>`` requires the Change in ``delivered_slices`` and
  absent from ``active_changes``.

WARN-only: an ACTIVE capability with blank ``remaining_slices`` but no linked
active partial Change, and a missing/unreadable roadmap. Registry rows that are
still the template ``PENDING`` row produce warnings, not errors.

Code paths and module cards are checked by ``check-modules.py``, not here.
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

REGISTRY_REL = "docs/product/capabilities.csv"
MODULES_REL = "docs/product/modules.csv"
DOMAINS_REL = "docs/architecture/domain-boundaries.md"
ROADMAP_REL = "docs/product/proposal-roadmap.md"

REQUIRED_HEADERS = (
    "capability_slug",
    "capability_name",
    "domain_id",
    "owner_module",
    "related_modules",
    "status",
    "delivered_slices",
    "remaining_slices",
    "active_changes",
    "notes",
)
STATUSES = {"PLANNED", "ACTIVE", "DELIVERED", "DEPRECATED"}
PLACEHOLDER = "PENDING"
DOM_ROW_RE = re.compile(r"DOM-[0-9]+", re.I)
TOKEN_SPLIT_RE = re.compile(r"[;,]")
COVERAGE_KEYS = {"slice coverage", "切片覆盖", "切片覆盖范围"}


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


def _read_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        try:
            return [cell.strip() for cell in next(reader)]
        except StopIteration:
            return []


def _domain_ids(path: Path) -> set[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeError(f"cannot read {_rel(path)}: {exc}") from exc
    ids = set()
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip().strip("*` ").strip() for cell in stripped.strip("|").split("|")]
        if cells and DOM_ROW_RE.fullmatch(cells[0]):
            ids.add(cells[0].upper())
    return ids


def _coverage_for(roadmap: dict | None, change_id: str) -> str | None:
    """Return the roadmap ``Slice Coverage`` cell for ``change_id``, if any."""
    if roadmap is None:
        return None
    row = gm.find_change(roadmap, change_id)
    if row is None:
        return None
    for key, value in row.items():
        normalized = " ".join((key or "").strip().casefold().split())
        if normalized in COVERAGE_KEYS:
            return (value or "").strip()
    return None


def _linked_changes(
    entries: list[tuple[int, dict]],
    fields: tuple[str, ...] = ("active_changes",),
) -> list[str]:
    """Exact Change-ID tokens from the requested registry fields."""
    linked: list[str] = []
    seen: set[str] = set()
    for _, row in entries:
        for field in fields:
            for token in _tokens(row.get(field) or ""):
                if token.upper() == PLACEHOLDER or token in seen:
                    continue
                seen.add(token)
                linked.append(token)
    return linked


def _module_index(modules: list[dict]) -> dict[str, list[dict]]:
    """Map a module slug to every modules.csv row that declares it."""
    index: dict[str, list[dict]] = defaultdict(list)
    for row in modules:
        slug = (row.get("module_slug") or "").strip()
        if slug:
            index[slug].append(row)
    return index


def _module_capabilities(rows: list[dict]) -> set[str]:
    """Capability slugs a module lists, split on semicolons and commas."""
    result: set[str] = set()
    for row in rows:
        for item in row.get("capabilities") or []:
            result.update(_tokens(item))
    return result


def _owner_conflict(entries: list[tuple[int, dict]]) -> list[str]:
    owners = sorted(
        {
            (row.get("owner_module") or "").strip()
            for _, row in entries
            if not _is_blank(row.get("owner_module") or "")
        }
    )
    return owners


def _validate_rows(
    rows: list[dict],
    module_index: dict[str, list[dict]],
    domain_ids: set[str] | None,
    roadmap: dict | None,
) -> tuple[list[str], list[str], int]:
    """Return (errors, warnings, unique capability count)."""
    errors: list[str] = []
    warnings: list[str] = []
    by_slug: dict[str, list[tuple[int, dict]]] = defaultdict(list)

    for index, row in enumerate(rows, start=1):
        slug = (row.get("capability_slug") or "").strip()
        if _is_placeholder_slug(slug):
            warnings.append(
                f"{REGISTRY_REL} row {index}: placeholder row {slug!r} skipped"
            )
            continue
        if not slug:
            errors.append(f"{REGISTRY_REL} row {index}: missing capability_slug")
            continue
        by_slug[slug].append((index, row))

    for slug, entries in by_slug.items():
        first_index = entries[0][0]
        if len(entries) > 1:
            row_numbers = ", ".join(str(index) for index, _ in entries)
            owners = _owner_conflict(entries)
            detail = (
                f"; capability declares multiple owner modules: {', '.join(owners)}"
                if len(owners) > 1
                else ""
            )
            errors.append(
                f"{REGISTRY_REL}: duplicate capability_slug {slug!r} on rows "
                f"{row_numbers} (first at row {first_index}){detail}"
            )
        for index, row in entries:
            status_raw = (row.get("status") or "").strip()
            status = status_raw.upper()
            if status not in STATUSES:
                errors.append(
                    f"{REGISTRY_REL} row {index}: invalid status {status_raw!r}; "
                    "expected PLANNED|ACTIVE|DELIVERED|DEPRECATED"
                )

            domain_raw = (row.get("domain_id") or "").strip()
            if domain_ids is not None and domain_raw.upper() not in domain_ids:
                errors.append(
                    f"{REGISTRY_REL} row {index}: domain_id {domain_raw!r} not found as a "
                    f"DOM-xxx row in {DOMAINS_REL}"
                )

            owner = (row.get("owner_module") or "").strip()
            if _is_blank(owner):
                errors.append(
                    f"{REGISTRY_REL} row {index}: capability {slug!r} has a blank "
                    "owner_module"
                )
            elif owner not in module_index:
                errors.append(
                    f"{REGISTRY_REL} row {index}: owner_module {owner!r} not found in "
                    f"{MODULES_REL}"
                )
            elif slug not in _module_capabilities(module_index[owner]):
                errors.append(
                    f"{REGISTRY_REL} row {index}: owner module {owner!r} does not list "
                    f"capability {slug!r} in its capabilities column"
                )

            for item in row.get("related_modules") or []:
                for related in _tokens(item):
                    if _is_blank(related):
                        continue
                    if related not in module_index:
                        errors.append(
                            f"{REGISTRY_REL} row {index}: related module {related!r} not "
                            f"found in {MODULES_REL}"
                        )

        statuses = {(row.get("status") or "").strip().upper() for _, row in entries}
        has_remaining = any(
            not _is_blank(row.get("remaining_slices") or "") for _, row in entries
        )
        active_changes = _linked_changes(entries, ("active_changes",))
        partial_changes = [
            change_id
            for change_id in active_changes
            if (_coverage_for(roadmap, change_id) or "").casefold().startswith("partial")
        ]
        if partial_changes and not has_remaining:
            errors.append(
                f"{REGISTRY_REL}: capability {slug!r} links partial active Change(s) "
                f"{', '.join(partial_changes)} but remaining_slices is blank"
            )
        elif "ACTIVE" in statuses and not has_remaining:
            warnings.append(
                f"{REGISTRY_REL}: capability {slug!r} is ACTIVE with blank "
                "remaining_slices but no active Change is marked Slice Coverage=partial"
            )

    return errors, warnings, len(by_slug)


def _completed_errors(rows: list[dict], change_id: str) -> list[str]:
    errors: list[str] = []
    delivered = False
    active_hits: list[tuple[int, str]] = []
    for index, row in enumerate(rows, start=1):
        if change_id in _tokens(row.get("delivered_slices") or ""):
            delivered = True
        if change_id in _tokens(row.get("active_changes") or ""):
            active_hits.append((index, (row.get("capability_slug") or "").strip()))
    if not delivered:
        errors.append(
            f"--completed {change_id}: not found in delivered_slices of {REGISTRY_REL}"
        )
    for index, slug in active_hits:
        errors.append(
            f"--completed {change_id}: still listed in active_changes of capability "
            f"{slug!r} (row {index})"
        )
    return errors


def _header_errors(header: list[str]) -> tuple[list[str], bool]:
    errors: list[str] = []
    if not header:
        return [f"{REGISTRY_REL}: empty or missing header row"], False
    missing = [name for name in REQUIRED_HEADERS if name not in header]
    unexpected = [
        name for name in header if name and name not in REQUIRED_HEADERS
    ]
    duplicated = sorted(
        {name for name in REQUIRED_HEADERS if header.count(name) > 1}
    )
    if missing:
        errors.append(
            f"{REGISTRY_REL}: missing required header(s): {', '.join(missing)}"
        )
    if unexpected:
        errors.append(
            f"{REGISTRY_REL}: unexpected header(s): {', '.join(unexpected)}"
        )
    if duplicated:
        errors.append(
            f"{REGISTRY_REL}: duplicate header(s): {', '.join(duplicated)}"
        )
    return errors, not (missing or unexpected or duplicated)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check-capabilities.py",
        description="Check the capability registry (docs/product/capabilities.csv).",
    )
    parser.add_argument("--completed", metavar="CHANGE-ID", default=None)
    args = parser.parse_args(argv)

    root = _root()
    try:
        strategy = gm.strategy(root=root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        print("Capabilities check failed: 1 error(s), 0 warning(s).")
        return 1
    if strategy != "module-packages":
        print(f"CAPABILITIES_CHECK=SKIPPED (strategy {strategy})")
        return 0

    errors: list[str] = []
    warnings: list[str] = []

    registry_path = root / REGISTRY_REL
    header_ok = False
    rows: list[dict] = []
    if not registry_path.is_file():
        errors.append(
            f"{REGISTRY_REL}: missing capability registry "
            "(required by strategy module-packages)"
        )
    else:
        try:
            header = _read_header(registry_path)
        except OSError as exc:
            errors.append(f"cannot read {REGISTRY_REL}: {exc}")
            header = []
        header_errors, header_ok = _header_errors(header)
        errors.extend(header_errors)
        if header_ok:
            try:
                rows = gm.load_capabilities(root=root)
            except RuntimeError as exc:
                errors.append(str(exc))
                rows = []
            if not rows:
                errors.append(
                    f"{REGISTRY_REL}: registry has no data rows "
                    "(required by strategy module-packages)"
                )

    modules_path = root / MODULES_REL
    modules: list[dict] = []
    if not modules_path.is_file():
        errors.append(
            f"{MODULES_REL}: missing module registry "
            "(required by strategy module-packages)"
        )
    else:
        try:
            modules = gm.load_modules(root=root)
        except RuntimeError as exc:
            errors.append(str(exc))
    module_index = _module_index(modules)

    domain_ids: set[str] | None = None
    domains_path = root / DOMAINS_REL
    if not domains_path.is_file():
        errors.append(f"{DOMAINS_REL}: missing domain boundaries file")
    else:
        try:
            domain_ids = _domain_ids(domains_path)
        except RuntimeError as exc:
            errors.append(str(exc))
        if domain_ids is not None and not domain_ids:
            errors.append(f"{DOMAINS_REL}: no DOM-xxx table rows found")

    roadmap: dict | None = None
    roadmap_path = root / ROADMAP_REL
    if not roadmap_path.is_file():
        warnings.append(
            f"ROADMAP_UNAVAILABLE: {ROADMAP_REL} is missing; "
            "Slice Coverage partiality is not checked"
        )
    else:
        try:
            roadmap = gm.parse_roadmap(root=root)
        except RuntimeError as exc:
            warnings.append(f"ROADMAP_UNAVAILABLE: {exc}")
            roadmap = None
        if roadmap is not None and not roadmap.get("rows") and not roadmap.get("amendments"):
            warnings.append(
                f"ROADMAP_UNAVAILABLE: {ROADMAP_REL} has no Candidate Changes table "
                "rows; Slice Coverage partiality is not checked"
            )
            roadmap = None

    if header_ok and rows:
        row_errors, row_warnings, capability_count = _validate_rows(
            rows, module_index, domain_ids, roadmap
        )
        errors.extend(row_errors)
        warnings.extend(row_warnings)
    else:
        capability_count = 0

    if args.completed:
        errors.extend(_completed_errors(rows, args.completed))

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(
            f"Capabilities check failed: {len(errors)} error(s), "
            f"{len(warnings)} warning(s)."
        )
        return 1
    print(f"Capabilities check passed: {capability_count} capability(ies).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
