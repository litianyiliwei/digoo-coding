#!/usr/bin/env python3
"""Check the proposal roadmap structure (``docs/product/proposal-roadmap.md``).

CLI: ``python scripts/check-roadmap.py [--strict]``.

The rule set follows the project's code-layout strategy:

- ``none`` / missing layout: legacy checks only (Change-ID format, duplicates
  and unresolved placeholder rows); new columns are not required.
- ``footprint``: the roadmap must carry a ``Code Target`` column; each target is
  a ``;`` list of repo-relative paths that must stay under a ``code-layout.json``
  root when roots are declared. Module/capability registries are not required.
- ``module-packages``: the main table must carry ``Primary Capability``,
  ``Owner Module``, ``Related Modules``, ``Slice Type``, ``Slice Coverage``,
  ``Code Target``, ``Demo Path`` and ``Slice Budget``. Rows are checked against
  ``docs/product/capabilities.csv`` and ``docs/product/modules.csv``:

  * ``Primary Capability`` exists; ``Owner Module`` equals that capability's
    registered ``owner_module``;
  * ``Related Modules`` is ``N/A`` or a ``;``/``,`` list of registered module
    slugs;
  * ``Code Target`` paths must descend from the owner/related modules' paths
    (backend resource level is allowed);
  * ``Slice Type`` is ``initial|extend``; ``extend`` needs a capability whose
    status is ``ACTIVE``/``DELIVERED`` (``initial`` only needs registration);
  * ``Slice Coverage`` is ``partial|full``; ``partial`` needs a non-blank
    ``remaining_slices`` (empty/``N/A``/``PENDING`` count as blank);
  * amendment rows must fill ``Reason``/``Requester``/``Approver``/``Date``/
    ``Baseline Impact`` and obey the same capability/owner/related/code-target
    and enum rules; a Change may not appear in both tables;
  * every ``openspec/changes/*`` directory except ``archive`` must be in the
    main table or an approved amendment;
  * every Change ID in a capability's ``active_changes`` cell must be in the
    main table or an approved amendment (ERROR, not a warning).

``--strict`` turns warnings (including placeholder rows) into a failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import gate_common as gm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

ROADMAP_REL = "docs/product/proposal-roadmap.md"
CAPABILITIES_REL = "docs/product/capabilities.csv"
MODULES_REL = "docs/product/modules.csv"
CHANGES_REL = "openspec/changes"

LEGACY_MAIN_HEADINGS = (
    "## 1. 路线图总表",
    "## 1. Roadmap Overview",
    "## Roadmap Overview",
    "## 1. Roadmap",
)

MAIN_REQUIRED = (
    "Change ID",
    "Primary Capability",
    "Owner Module",
    "Related Modules",
    "Slice Type",
    "Slice Coverage",
    "Code Target",
    "Demo Path",
    "Slice Budget",
)
AMENDMENT_REQUIRED = (
    "Change ID",
    "Primary Capability",
    "Owner Module",
    "Related Modules",
    "Slice Type",
    "Slice Coverage",
    "Code Target",
    "Reason",
    "Requester",
    "Approver",
    "Date",
    "Baseline Impact",
)
AMENDMENT_APPROVAL_FIELDS = ("Reason", "Requester", "Approver", "Date", "Baseline Impact")

# Content cells scanned for placeholder warnings. ``Related Modules`` is
# excluded because ``N/A[...]`` is a legitimate value there; extra template
# columns (Dependencies, Value, ...) are excluded because free text may be N/A.
MAIN_CONTENT_FIELDS = (
    "Primary Capability",
    "Owner Module",
    "Slice Type",
    "Slice Coverage",
    "Code Target",
    "Demo Path",
    "Slice Budget",
)
AMENDMENT_CONTENT_FIELDS = (
    "Primary Capability",
    "Owner Module",
    "Slice Type",
    "Slice Coverage",
    "Code Target",
) + AMENDMENT_APPROVAL_FIELDS
# Footprint has no registries; only Code Target is a required content column, so
# optional columns that legitimately hold ``N/A`` never trigger a placeholder
# warning (and never fail ``--strict``).
FOOTPRINT_CONTENT_FIELDS = ("Code Target",)

CHANGE_ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
TOKEN_SPLIT_RE = re.compile(r"[;,]")
ABSOLUTE_PATH_RE = re.compile(r"^(?:/|[A-Za-z]:)")
WILDCARD_PATH_RE = re.compile(r"[*?]")
SEPARATOR_CELL_RE = re.compile(r":?-{3,}:?")

SLICE_TYPES = {"initial", "extend"}
SLICE_COVERAGES = {"partial", "full"}
BASELINE_IMPACTS = {"CHANGE_ONLY", "BASELINE_CHANGE_REQUIRED"}
EXTEND_STATUSES = {"ACTIVE", "DELIVERED"}
PLACEHOLDER = "PENDING"


def _root() -> Path:
    return Path(ROOT)


# -- small helpers ------------------------------------------------------------
def _norm(value: str) -> str:
    return " ".join((value or "").strip().casefold().split())


def _cell(row: dict, label: str) -> str:
    target = _norm(label)
    for key, value in row.items():
        if _norm(key) == target:
            return (value or "").strip()
    return ""


def _row_change_id(row: dict) -> str:
    for key, value in row.items():
        if _norm(key) in gm.CHANGE_ID_KEYS:
            return (value or "").strip()
    return ""


def _is_placeholder_id(change_id: str) -> bool:
    change_id = (change_id or "").strip()
    upper = change_id.upper()
    return (
        not change_id
        or upper == PLACEHOLDER
        or "TODO" in upper
        or (change_id.startswith("<") and change_id.endswith(">"))
    )


def _is_placeholder_slug(slug: str) -> bool:
    slug = (slug or "").strip()
    return slug.upper() == PLACEHOLDER or (slug.startswith("<") and slug.endswith(">"))


def _placeholder_cell(value: str) -> bool:
    """One placeholder definition: blank, ``N/A...``, ``PENDING``, TODO, ``<...>``."""
    value = (value or "").strip()
    upper = value.upper()
    return (
        not value
        or upper.startswith("N/A")
        or upper == PLACEHOLDER
        or "TODO" in upper
        or (value.startswith("<") and value.endswith(">"))
    )


def _is_blank(value: str) -> bool:
    """Empty / ``N/A...`` / ``PENDING`` all count as blank."""
    value = (value or "").strip()
    upper = value.upper()
    return not value or upper.startswith("N/A") or upper == PLACEHOLDER


def _tokens(value: str) -> list[str]:
    return [item.strip() for item in TOKEN_SPLIT_RE.split(value or "") if item.strip()]


def _norm_path(value: str) -> str:
    value = str(value or "").strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    value = re.sub(r"/+", "/", value)
    return value.strip("/")


def _path_problem(value: str) -> str:
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


def _within(path_norm: str, allowed: list[str]) -> bool:
    folded = path_norm.casefold()
    return any(
        folded == candidate.casefold() or folded.startswith(candidate.casefold() + "/")
        for candidate in allowed
    )


def _root_state(path_norm: str, roots: list[str]) -> str:
    folded = path_norm.casefold()
    for root in roots:
        root_folded = root.casefold()
        if folded == root_folded:
            return "equals"
        if folded.startswith(root_folded + "/"):
            return "under"
    return "outside"


def _layout_roots(layout) -> list[str]:
    roots = layout.get("roots") if isinstance(layout, dict) else None
    if isinstance(roots, dict):
        values = list(roots.values())
    elif isinstance(roots, list):
        values = roots
    else:
        return []
    normalized = []
    for value in values:
        if isinstance(value, str):
            norm = _norm_path(value)
            if norm:
                normalized.append(norm)
    return normalized


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(SEPARATOR_CELL_RE.fullmatch(cell) for cell in cells)


# -- table line mapping -------------------------------------------------------
def _scan_table(lines: list[str], heading_index: int) -> dict | None:
    index = heading_index + 1
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("|"):
            break
        if stripped.startswith("## "):
            return None
        index += 1
    table: list[tuple[int, list[str]]] = []
    while index < len(lines) and lines[index].strip().startswith("|"):
        row = lines[index].strip()
        table.append((index + 1, [cell.strip() for cell in row.strip("|").split("|")]))
        index += 1
    if not table:
        return None
    header_line, header = table[0]
    data = [
        (lineno, cells) for lineno, cells in table[1:] if not _is_separator(cells)
    ]
    return {"header_line": header_line, "header": header, "data": data}


def _scan_sections(text: str) -> tuple[dict | None, dict | None]:
    lines = text.splitlines()
    main = None
    amendments = None
    for index, line in enumerate(lines):
        heading = line.strip().casefold()
        if heading in gm.MAIN_ROADMAP_HEADINGS and main is None:
            main = _scan_table(lines, index)
        elif heading in gm.AMENDMENT_ROADMAP_HEADINGS and amendments is None:
            amendments = _scan_table(lines, index)
    return main, amendments


def _missing_columns(header: list[str], required: tuple[str, ...]) -> list[str]:
    present = {_norm(cell) for cell in header}
    return [label for label in required if _norm(label) not in present]


def _pair_rows(rows: list[dict], table: dict | None) -> list[tuple[int, dict]]:
    data = (table or {}).get("data") or []
    return [
        (data[index][0] if index < len(data) else 0, row)
        for index, row in enumerate(rows)
    ]


# -- legacy strategy ----------------------------------------------------------
def _legacy_check(text: str) -> tuple[list[str], list[str], int]:
    rows = []
    in_roadmap = False
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("## "):
            if stripped in LEGACY_MAIN_HEADINGS:
                in_roadmap = True
                continue
            if in_roadmap:
                break
        if not in_roadmap:
            continue
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and cells[0].lower() in {"change id", "change-id"}:
            continue
        if len(cells) >= 3:
            rows.append((line_no, cells))
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()
    if not rows:
        warnings.append("Roadmap table has no data rows yet")
    for line_no, cells in rows:
        change_id = cells[0]
        if not change_id or "TODO" in change_id.upper() or change_id.startswith("<"):
            warnings.append(f"line {line_no}: unresolved Change ID: {change_id!r}")
            continue
        if not CHANGE_ID_RE.fullmatch(change_id):
            errors.append(
                f"line {line_no}: invalid change-id {change_id!r}; use lowercase kebab-case"
            )
        if change_id in seen:
            errors.append(f"line {line_no}: duplicate change-id {change_id!r}")
        seen.add(change_id)
        if any((not cell or "TODO" in cell.upper()) for cell in cells[1:]):
            warnings.append(
                f"line {line_no}: placeholder remains in roadmap row {change_id!r}"
            )
    return errors, warnings, len(seen)


# -- shared ID rules ----------------------------------------------------------
def _check_ids(
    pairs: list[tuple[int, dict]],
    errors: list[str],
    warnings: list[str],
) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for line_no, row in pairs:
        change_id = _row_change_id(row)
        if _is_placeholder_id(change_id):
            if change_id:
                warnings.append(
                    f"line {line_no}: placeholder row {change_id!r} skipped"
                )
            else:
                warnings.append(f"line {line_no}: unresolved Change ID: {change_id!r}")
            continue
        if not CHANGE_ID_RE.fullmatch(change_id):
            errors.append(
                f"line {line_no}: invalid change-id {change_id!r}; use lowercase kebab-case"
            )
        if change_id in seen:
            errors.append(f"line {line_no}: duplicate change-id {change_id!r}")
        seen.add(change_id)
        ids.append(change_id)
    return ids


def _amendment_approved(row: dict) -> bool:
    change_id = _row_change_id(row)
    if _is_placeholder_id(change_id):
        return False
    return all(
        not _placeholder_cell(_cell(row, label))
        for label in AMENDMENT_APPROVAL_FIELDS
    )


# -- module-packages strategy -------------------------------------------------
def _capability_index(registry: list[dict]) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for row in registry:
        slug = (row.get("capability_slug") or "").strip()
        if not slug or _is_placeholder_slug(slug):
            continue
        index.setdefault(slug, row)
    return index


def _module_slugs(registry: list[dict]) -> set[str]:
    return {
        (row.get("module_slug") or "").strip()
        for row in registry
        if (row.get("module_slug") or "").strip()
        and not _is_placeholder_slug((row.get("module_slug") or "").strip())
    }


def _validate_slice_row(
    line_no: int,
    row: dict,
    *,
    amendment: bool,
    cap_index: dict[str, dict],
    module_slugs: set[str],
    modules: list[dict],
    caps_available: bool,
    modules_available: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    tag = f"line {line_no}"
    change_id = _row_change_id(row)
    primary = _cell(row, "Primary Capability")
    owner = _cell(row, "Owner Module")
    related_raw = _cell(row, "Related Modules")
    slice_type_raw = _cell(row, "Slice Type")
    coverage_raw = _cell(row, "Slice Coverage")
    code_target_raw = _cell(row, "Code Target")

    fields = AMENDMENT_CONTENT_FIELDS if amendment else MAIN_CONTENT_FIELDS
    if any(_placeholder_cell(_cell(row, label)) for label in fields):
        warnings.append(
            f"{tag}: placeholder remains in roadmap row {change_id!r}"
        )

    if amendment:
        for label in AMENDMENT_APPROVAL_FIELDS:
            value = _cell(row, label)
            if not value:
                errors.append(
                    f"{tag}: amendment Change {change_id!r} has a blank {label}"
                )
            elif _placeholder_cell(value):
                errors.append(
                    f"{tag}: amendment Change {change_id!r} has a placeholder "
                    f"{label} {value!r}"
                )
        baseline_raw = _cell(row, "Baseline Impact")
        if baseline_raw and baseline_raw.upper() not in BASELINE_IMPACTS:
            errors.append(
                f"{tag}: invalid Baseline Impact {baseline_raw!r}; "
                "expected CHANGE_ONLY|BASELINE_CHANGE_REQUIRED"
            )

    capability = None
    if caps_available:
        if _is_blank(primary):
            errors.append(
                f"{tag}: Change {change_id!r} has a blank Primary Capability"
            )
        elif primary not in cap_index:
            errors.append(
                f"{tag}: Primary Capability {primary!r} not found in {CAPABILITIES_REL}"
            )
        else:
            capability = cap_index[primary]
            cap_owner = (capability.get("owner_module") or "").strip()
            if _is_blank(owner):
                errors.append(f"{tag}: Change {change_id!r} has a blank Owner Module")
            elif owner != cap_owner:
                errors.append(
                    f"{tag}: Owner Module {owner!r} does not match capability "
                    f"{primary!r} owner_module {cap_owner!r} in {CAPABILITIES_REL}"
                )

    related_slugs: list[str] = []
    if modules_available:
        if not related_raw:
            errors.append(
                f"{tag}: Change {change_id!r} has a blank Related Modules; "
                "use N/A or a ; list"
            )
        else:
            for token in _tokens(related_raw):
                if token.upper().startswith("N/A"):
                    continue
                if token not in module_slugs:
                    errors.append(
                        f"{tag}: related module {token!r} not found in {MODULES_REL}"
                    )
                else:
                    related_slugs.append(token)
    else:
        related_slugs = [
            token for token in _tokens(related_raw) if not token.upper().startswith("N/A")
        ]

    if slice_type_raw.casefold() not in SLICE_TYPES:
        errors.append(
            f"{tag}: invalid Slice Type {slice_type_raw!r}; expected initial|extend"
        )
    if coverage_raw.casefold() not in SLICE_COVERAGES:
        errors.append(
            f"{tag}: invalid Slice Coverage {coverage_raw!r}; expected partial|full"
        )

    if not code_target_raw:
        errors.append(f"{tag}: Change {change_id!r} has a blank Code Target")
    else:
        allowed: list[str] | None = None
        if modules_available:
            slugs = ([owner] if owner and not _is_blank(owner) else []) + related_slugs
            allowed = [_norm_path(path) for path in gm.module_paths(modules, slugs)]
        for raw_path in [token.strip() for token in code_target_raw.split(";") if token.strip()]:
            problem = _path_problem(raw_path)
            if problem:
                errors.append(f"{tag}: Code Target {raw_path!r} {problem}")
                continue
            norm = _norm_path(raw_path)
            if not norm:
                errors.append(f"{tag}: empty Code Target entry {raw_path!r}")
                continue
            if allowed is None:
                continue
            if not allowed:
                errors.append(
                    f"{tag}: Code Target {raw_path!r} cannot be matched; "
                    "owner/related modules have no registered module paths"
                )
            elif not _within(norm, allowed):
                errors.append(
                    f"{tag}: Code Target {raw_path!r} is outside owner/related "
                    f"module paths ({', '.join(allowed)})"
                )

    if capability is None:
        return

    if coverage_raw.casefold() == "partial" and _is_blank(
        capability.get("remaining_slices") or ""
    ):
        errors.append(
            f"{tag}: capability {primary!r} has Slice Coverage=partial but "
            f"remaining_slices is blank in {CAPABILITIES_REL}"
        )
    if slice_type_raw.casefold() == "extend":
        status = (capability.get("status") or "").strip().upper()
        if status not in EXTEND_STATUSES:
            found = status or "blank"
            errors.append(
                f"{tag}: Slice Type 'extend' requires capability {primary!r} status "
                f"ACTIVE|DELIVERED in {CAPABILITIES_REL}, found {found!r}"
            )


def _run_module_packages(
    root: Path, roadmap: dict, main_table, amend_table, strict: bool
) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    main_missing: list[str] = []
    if main_table is None or not roadmap.get("rows"):
        warnings.append("Roadmap table has no data rows yet")
    else:
        main_missing = _missing_columns(main_table["header"], MAIN_REQUIRED)
        if main_missing:
            errors.append(
                f"line {main_table['header_line']}: roadmap table missing required "
                f"column(s): {', '.join(main_missing)}"
            )

    amend_missing: list[str] = []
    if amend_table is not None:
        amend_missing = _missing_columns(amend_table["header"], AMENDMENT_REQUIRED)
        if amend_missing:
            errors.append(
                f"line {amend_table['header_line']}: roadmap amendments table "
                f"missing required column(s): {', '.join(amend_missing)}"
            )

    main_pairs = _pair_rows(roadmap.get("rows", []), main_table)
    amend_pairs = _pair_rows(roadmap.get("amendments", []), amend_table)

    main_ids = _check_ids(main_pairs, errors, warnings)
    amend_ids: list[str] = []
    amend_seen: set[str] = set()
    for line_no, row in amend_pairs:
        change_id = _row_change_id(row)
        if _is_placeholder_id(change_id):
            if change_id:
                warnings.append(f"line {line_no}: placeholder row {change_id!r} skipped")
            else:
                warnings.append(f"line {line_no}: unresolved Change ID: {change_id!r}")
            continue
        if not CHANGE_ID_RE.fullmatch(change_id):
            errors.append(
                f"line {line_no}: invalid change-id {change_id!r}; use lowercase kebab-case"
            )
        if change_id in amend_seen:
            errors.append(f"line {line_no}: duplicate amendment change-id {change_id!r}")
        if change_id in set(main_ids):
            errors.append(
                f"line {line_no}: change-id {change_id!r} appears in both the main "
                "roadmap and an amendment"
            )
        amend_seen.add(change_id)
        amend_ids.append(change_id)

    caps_available = (root / CAPABILITIES_REL).is_file()
    modules_available = (root / MODULES_REL).is_file()
    capability_registry: list[dict] = []
    module_registry: list[dict] = []
    if not caps_available:
        errors.append(
            f"{CAPABILITIES_REL}: missing capability registry "
            "(required by strategy module-packages)"
        )
    else:
        try:
            capability_registry = gm.load_capabilities(root=root)
        except RuntimeError as exc:
            errors.append(str(exc))
            caps_available = False
    if not modules_available:
        errors.append(
            f"{MODULES_REL}: missing module registry (required by strategy module-packages)"
        )
    else:
        try:
            module_registry = gm.load_modules(root=root)
        except RuntimeError as exc:
            errors.append(str(exc))
            modules_available = False

    cap_index = _capability_index(capability_registry)
    module_slug_set = _module_slugs(module_registry)

    if not main_missing:
        for line_no, row in main_pairs:
            if _is_placeholder_id(_row_change_id(row)):
                continue
            _validate_slice_row(
                line_no,
                row,
                amendment=False,
                cap_index=cap_index,
                module_slugs=module_slug_set,
                modules=module_registry,
                caps_available=caps_available,
                modules_available=modules_available,
                errors=errors,
                warnings=warnings,
            )
    if not amend_missing:
        for line_no, row in amend_pairs:
            if _is_placeholder_id(_row_change_id(row)):
                continue
            _validate_slice_row(
                line_no,
                row,
                amendment=True,
                cap_index=cap_index,
                module_slugs=module_slug_set,
                modules=module_registry,
                caps_available=caps_available,
                modules_available=modules_available,
                errors=errors,
                warnings=warnings,
            )

    registered = set(main_ids)
    approved = {
        _row_change_id(row)
        for row in roadmap.get("amendments", [])
        if _amendment_approved(row)
    }
    registered |= approved

    changes_dir = root / CHANGES_REL
    if changes_dir.is_dir():
        for entry in sorted(changes_dir.iterdir(), key=lambda path: path.name):
            if not entry.is_dir() or entry.name == "archive":
                continue
            if entry.name not in registered:
                errors.append(
                    f"{CHANGES_REL}/{entry.name}: active Change directory is not "
                    "registered in the main roadmap or an approved amendment"
                )

    if caps_available:
        for index, row in enumerate(capability_registry, start=1):
            slug = (row.get("capability_slug") or "").strip()
            if not slug or _is_placeholder_slug(slug):
                continue
            for token in _tokens(row.get("active_changes") or ""):
                if _is_blank(token):
                    continue
                if token not in registered:
                    errors.append(
                        f"{CAPABILITIES_REL} row {index}: capability {slug!r} lists "
                        f"active Change {token!r} but it is not registered in the "
                        "main roadmap or an approved amendment"
                    )

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors or (strict and warnings):
        print(
            f"Roadmap check failed: {len(errors)} error(s), {len(warnings)} warning(s)."
        )
        return 1
    print(
        f"Roadmap check passed: {len(set(main_ids))} Change(s), "
        f"{len(set(amend_ids))} amendment(s)."
    )
    return 0


# -- footprint strategy -------------------------------------------------------
def _footprint_rows(
    pairs: list[tuple[int, dict]],
    *,
    roots: list[str],
    modules: list[dict],
    modules_available: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    for line_no, row in pairs:
        change_id = _row_change_id(row)
        if _is_placeholder_id(change_id):
            continue
        if any(
            _placeholder_cell(_cell(row, label)) for label in FOOTPRINT_CONTENT_FIELDS
        ):
            warnings.append(
                f"line {line_no}: placeholder remains in roadmap row {change_id!r}"
            )
        code_target = _cell(row, "Code Target")
        if not code_target:
            errors.append(
                f"line {line_no}: Change {change_id!r} has a blank Code Target"
            )
            continue
        slugs: list[str] = []
        if modules_available:
            owner = _cell(row, "Owner Module")
            if owner and not _is_blank(owner):
                slugs.append(owner)
            slugs.extend(
                token
                for token in _tokens(_cell(row, "Related Modules"))
                if not token.upper().startswith("N/A")
            )
        allowed = (
            [_norm_path(path) for path in gm.module_paths(modules, slugs)]
            if slugs
            else []
        )
        for raw_path in [
            token.strip() for token in code_target.split(";") if token.strip()
        ]:
            problem = _path_problem(raw_path)
            if problem:
                errors.append(f"line {line_no}: Code Target {raw_path!r} {problem}")
                continue
            norm = _norm_path(raw_path)
            if roots:
                state = _root_state(norm, roots)
                roots_text = ", ".join(root_value + "/" for root_value in roots)
                if state == "equals":
                    errors.append(
                        f"line {line_no}: Code Target {raw_path!r} equals a "
                        "code-layout root; name the changed code below the root"
                    )
                    continue
                if state == "outside":
                    errors.append(
                        f"line {line_no}: Code Target {raw_path!r} does not start "
                        f"with any code-layout.json roots value ({roots_text})"
                    )
                    continue
            if allowed and not _within(norm, allowed):
                errors.append(
                    f"line {line_no}: Code Target {raw_path!r} is outside "
                    f"owner/related module paths ({', '.join(allowed)})"
                )


def _run_footprint(
    root: Path, roadmap: dict, main_table, amend_table, strict: bool
) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    main_missing: list[str] = []
    if main_table is None or not roadmap.get("rows"):
        warnings.append("Roadmap table has no data rows yet")
    else:
        main_missing = _missing_columns(
            main_table["header"], ("Change ID", "Code Target")
        )
        if main_missing:
            errors.append(
                f"line {main_table['header_line']}: roadmap table missing required "
                f"column(s): {', '.join(main_missing)}"
            )

    amend_missing: list[str] = []
    if amend_table is not None:
        amend_missing = _missing_columns(
            amend_table["header"], ("Change ID", "Code Target")
        )
        if amend_missing:
            errors.append(
                f"line {amend_table['header_line']}: roadmap amendments table "
                f"missing required column(s): {', '.join(amend_missing)}"
            )

    main_pairs = _pair_rows(roadmap.get("rows", []), main_table)
    amend_pairs = _pair_rows(roadmap.get("amendments", []), amend_table)
    ids = _check_ids(main_pairs, errors, warnings)

    amend_seen: set[str] = set()
    for line_no, row in amend_pairs:
        change_id = _row_change_id(row)
        if _is_placeholder_id(change_id):
            if change_id:
                warnings.append(f"line {line_no}: placeholder row {change_id!r} skipped")
            else:
                warnings.append(f"line {line_no}: unresolved Change ID: {change_id!r}")
            continue
        if not CHANGE_ID_RE.fullmatch(change_id):
            errors.append(
                f"line {line_no}: invalid change-id {change_id!r}; use lowercase kebab-case"
            )
        if change_id in amend_seen:
            errors.append(f"line {line_no}: duplicate amendment change-id {change_id!r}")
        amend_seen.add(change_id)

    roots: list[str] = []
    try:
        layout = gm.load_code_layout(root=root) or {}
        roots = _layout_roots(layout)
    except RuntimeError as exc:
        errors.append(str(exc))

    modules_available = (root / MODULES_REL).is_file()
    modules: list[dict] = []
    if modules_available:
        try:
            modules = gm.load_modules(root=root)
        except RuntimeError as exc:
            errors.append(str(exc))
            modules_available = False

    if not main_missing:
        _footprint_rows(
            main_pairs,
            roots=roots,
            modules=modules,
            modules_available=modules_available,
            errors=errors,
            warnings=warnings,
        )
    if not amend_missing:
        _footprint_rows(
            amend_pairs,
            roots=roots,
            modules=modules,
            modules_available=modules_available,
            errors=errors,
            warnings=warnings,
        )

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors or (strict and warnings):
        print(
            f"Roadmap check failed: {len(errors)} error(s), {len(warnings)} warning(s)."
        )
        return 1
    print(f"Roadmap footprint check passed: {len(set(ids))} Change(s).")
    return 0


# -- entry point --------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args != ["--strict"]:
        print("Usage: check-roadmap.py [--strict]", file=sys.stderr)
        return 2
    strict = "--strict" in args

    root = _root()
    path = root / ROADMAP_REL
    if not path.is_file():
        print(f"MISSING: {path}", file=sys.stderr)
        return 1
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"MISSING: {path} ({exc})", file=sys.stderr)
        return 1

    try:
        strategy = gm.strategy(root=root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        print("Roadmap check failed: 1 error(s), 0 warning(s).")
        return 1

    if strategy == "none":
        errors, warnings, count = _legacy_check(text)
        for warning in warnings:
            print(f"WARN: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        if errors or (strict and warnings):
            print(
                f"Roadmap check failed: {len(errors)} error(s), "
                f"{len(warnings)} warning(s)."
            )
            return 1
        print(f"Roadmap structure check passed: {count} named Change(s).")
        return 0

    try:
        roadmap = gm.parse_roadmap(root=root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        print("Roadmap check failed: 1 error(s), 0 warning(s).")
        return 1

    main_table, amend_table = _scan_sections(text)
    if strategy == "module-packages":
        return _run_module_packages(root, roadmap, main_table, amend_table, strict)
    return _run_footprint(root, roadmap, main_table, amend_table, strict)


if __name__ == "__main__":
    raise SystemExit(main())
