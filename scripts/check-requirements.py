#!/usr/bin/env python3
"""Validate project requirement-business artifacts or a Change's proposal-level US/AC.

CLI: ``python scripts/check-requirements.py [--change <change-id>] [--strict]``.

Without ``--change`` the project-level requirement business artifacts
(workflows, data objects, RD matrix, business rules) are checked.

With ``--change`` the legacy US/AC structure and project-ID reference checks
always run. The code-layout strategy decides which proposal/slice rules apply:

- ``none`` / missing layout: legacy checks only.
- ``footprint``: Scenario -> AC tracing, ``Slice position``, the
  ``Acceptance Walkthrough`` coverage and the AC budget exception.
- ``module-packages``: additionally the proposal ``New/Modified Capabilities``
  must exist in ``docs/product/capabilities.csv`` and agree with the Change's
  ``Primary Capability`` / ``Slice Type`` roadmap row (main table or an approved
  amendment).

Missing or unknown references are errors. ``--strict`` turns warnings into a
failure.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import gate_common as gm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

ERRORS: list[str] = []
WARNINGS: list[str] = []

CAPABILITIES_REL = "docs/product/capabilities.csv"
ROADMAP_REL = "docs/product/proposal-roadmap.md"
AMENDMENT_APPROVAL_FIELDS = ("Reason", "Requester", "Approver", "Date", "Baseline Impact")

SCENARIO_HEADING_RE = re.compile(r"^####\s+Scenario:\s*(.+?)\s*$", re.I)
AC_SECTION_RE = re.compile(r"^###\s+(AC-\d{3})\b")
SCENARIO_LINE_RE = re.compile(r"^-\s*Scenario:\s*(.+?)\s*$", re.I)
SLICE_POSITION_RE = re.compile(r"^-\s*Slice position:\s*(.+?)\s*$", re.I)
WALKTHROUGH_HEADING_RE = re.compile(
    r"^##\s+(Acceptance Walkthrough|验收走查)\s*$", re.I
)
BUDGET_EXCEPTION_RE = re.compile(
    r"^(?:-\s*)?Budget exception:\s*(.+?)\s*$", re.I
)
BUDGET_SEPARATOR_RE = re.compile(r"^(.+?)\s+[—–-]\s+(.+)$")
PROPOSAL_CAP_BULLET_RE = re.compile(r"^-\s+`([^`]+)`")
HEADING_TITLE_RE = re.compile(r"^#+\s+(.*?)\s*$")

SLICE_POSITIONS = {"entry", "behavior", "result"}
AC_BUDGET = 12


def read_lines(path):
    if not path.is_file():
        ERRORS.append(f'Missing artifact: {path.relative_to(ROOT)}')
        return []
    return path.read_text(encoding='utf-8').splitlines()


def read_csv(path, required):
    if not path.is_file():
        ERRORS.append(f'Missing artifact: {path.relative_to(ROOT)}')
        return []
    with path.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing = [h for h in required if h not in headers]
        if missing:
            ERRORS.append(f'{path.name}: missing columns: {", ".join(missing)}')
            return []
        rows = list(reader)
    if not rows:
        WARNINGS.append(f'{path.name}: header only; no rows yet')
    return rows


def ids_from(lines, pattern):
    rx = re.compile(pattern)
    out = []
    for n, line in enumerate(lines, 1):
        m = rx.search(line)
        if m:
            out.append((m.group(1), n))
    return out


def report_duplicates(pairs, label):
    seen = {}
    for value, line_no in pairs:
        if value in seen:
            ERRORS.append(f'{label}: duplicate ID {value} (first at line {seen[value]})')
        else:
            seen[value] = line_no
    return set(seen)


def placeholders(lines, label):
    if any(re.search(r'\bTODO\b|\bTBD\b|\[填充\]|PENDING', line) for line in lines):
        WARNINGS.append(f'{label}: unresolved template placeholders remain')


def project_context():
    workflows = read_lines(ROOT / 'docs/product/workflows.md')
    objects = read_lines(ROOT / 'docs/product/data-objects.csv')
    rd = read_lines(ROOT / 'docs/product/rd-matrix.csv')
    rules = read_lines(ROOT / 'docs/product/business-rules.md')
    reqs = read_lines(ROOT / 'docs/product/requirements-analysis.md')
    flows = report_duplicates(ids_from(workflows, r'^##\s+(FLOW-\d{3})\b'), 'workflows.md')
    nodes = ids_from(workflows, r'^\|\s*(NODE-\d{3}-\d{2})\s*\|')
    node_ids = report_duplicates(nodes, 'workflows.md')
    node_flow = {}
    for nid, _ in nodes:
        node_flow[nid] = 'FLOW-' + nid.split('-')[1]
    brs = report_duplicates(ids_from(rules, r'^\|\s*(BR-\d{3})\s*\|'), 'business-rules.md')
    ras = set(re.findall(r'RA-\d{3}', '\n'.join(reqs)))
    do_rows = read_csv(ROOT / 'docs/product/data-objects.csv', [
        'data_object_id', 'data_object_name', 'definition', 'key_attributes',
        'owner_role', 'source_nodes', 'consumer_nodes', 'status'])
    rd_rows = read_csv(ROOT / 'docs/product/rd-matrix.csv', [
        'rd_id', 'requirement_id', 'requirement_type', 'flow_id', 'node_id', 'node_name',
        'role_ids', 'data_object_id', 'data_object_name', 'access_type',
        'business_rule_ids', 'acceptance_criteria', 'priority', 'status'])
    return workflows, objects, rd, flows, node_ids, node_flow, brs, ras, do_rows, rd_rows


def check_project():
    workflows, objects, rd, flows, node_ids, node_flow, brs, ras, do_rows, rd_rows = project_context()
    for label, lines in (('workflows.md', workflows), ('data-objects.csv', objects), ('rd-matrix.csv', rd)):
        placeholders(lines, label)
    if not flows:
        ERRORS.append('workflows.md: no FLOW-xxx headings found')
    if not node_ids:
        ERRORS.append('workflows.md: no NODE-xxx-xx table rows found; every FLOW must be decomposed into executable nodes')
    for flow in flows:
        if not any(nid.startswith('NODE-' + flow.split('-')[1]) for nid in node_ids):
            ERRORS.append(f'workflows.md: {flow} has no node rows')
    # Node table must expose role / input object / output object columns.
    header = [l for l in workflows if 'NODE ID' in l]
    for need, en in (('执行角色', 'executing role'), ('输入数据对象', 'input data object'), ('输出数据对象', 'output data object')):
        if not any(need in l or en.lower() in l.lower() for l in header):
            ERRORS.append(f'workflows.md: node table header missing column: {need} / {en}')
    do_ids = report_duplicates([(r['data_object_id'].strip(), n) for n, r in enumerate(do_rows, 2) if r.get('data_object_id')], 'data-objects.csv')
    for r in do_rows:
        doid = (r.get('data_object_id') or '').strip()
        if doid and not doid.startswith('DO-'):
            ERRORS.append(f'data-objects.csv: {doid} should use DO- prefix')
        for field in ('data_object_name', 'definition', 'key_attributes', 'owner_role', 'source_nodes', 'status'):
            if not (r.get(field) or '').strip():
                ERRORS.append(f'data-objects.csv: {doid or "row"}: {field} is required; use N/A + reason when not applicable')
    rd_ids = report_duplicates([(r['rd_id'].strip(), n) for n, r in enumerate(rd_rows, 2) if r.get('rd_id')], 'rd-matrix.csv')
    covered_nodes = set()
    for r in rd_rows:
        rid = (r.get('rd_id') or '').strip()
        if rid and not rid.startswith('RD-'):
            ERRORS.append(f'rd-matrix.csv: {rid} should use RD- prefix')
        node = (r.get('node_id') or '').strip()
        if node and node not in node_ids:
            ERRORS.append(f'rd-matrix.csv: {rid or "row"} references unknown node_id {node!r}')
        else:
            covered_nodes.add(node)
        flow = (r.get('flow_id') or '').strip()
        if flow and flow not in flows:
            ERRORS.append(f'rd-matrix.csv: {rid or "row"} references unknown flow_id {flow!r}')
        doid = (r.get('data_object_id') or '').strip()
        if doid and doid != 'N/A' and doid not in do_ids:
            ERRORS.append(f'rd-matrix.csv: {rid or "row"} references unknown data_object_id {doid!r}')
        req = (r.get('requirement_id') or '').strip()
        if req and req not in (flows | node_ids | brs | ras | do_ids) and req != 'N/A':
            WARNINGS.append(f'rd-matrix.csv: {rid or "row"} requirement_id {req!r} is not a declared FLOW/NODE/DO/BR/RA ID')
        for bid in [x.strip() for x in (r.get('business_rule_ids') or '').replace('；', ';').replace('，', ',').split(';') if x.strip()]:
            if bid != 'N/A' and bid not in brs:
                ERRORS.append(f'rd-matrix.csv: {rid or "row"} references unknown BR ID {bid!r}')
        for field in ('rd_id', 'requirement_id', 'requirement_type', 'flow_id', 'node_id', 'node_name',
                      'role_ids', 'data_object_id', 'access_type', 'status'):
            if not (r.get(field) or '').strip():
                ERRORS.append(f'rd-matrix.csv: {rid or "row"}: {field} is required; use N/A + reason when not applicable')
    for nid in node_ids:
        if nid not in covered_nodes:
            ERRORS.append(f'rd-matrix.csv: node {nid} has no RD row; every node must declare its data objects and roles')
    for doid in do_ids:
        if not any((r.get('data_object_id') or '').strip() == doid for r in rd_rows):
            WARNINGS.append(f'data-objects.csv: {doid} is not referenced by any RD row')
    counts = f'FLOW={len(flows)}, NODE={len(node_ids)}, DO={len(do_ids)}, RD={len(rd_ids)}, BR={len(brs)}'
    return counts


# -- Change-mode helpers ------------------------------------------------------
def _norm(value) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _cell(row: dict, label: str) -> str:
    target = _norm(label)
    for key, value in row.items():
        if _norm(key) == target:
            return str(value or "").strip()
    return ""


def _is_blank(value: str) -> bool:
    value = str(value or "").strip()
    upper = value.upper()
    return not value or upper.startswith("N/A") or upper == "PENDING"


def _row_change_id(row: dict) -> str:
    for key, value in row.items():
        if _norm(key) in gm.CHANGE_ID_KEYS:
            return str(value or "").strip()
    return ""


def _roadmap_lookup(roadmap: dict, change: str) -> tuple[dict | None, str]:
    if not gm.registered_change(roadmap, change):
        return None, ""
    row = gm.find_change(roadmap, change)
    in_main = any(
        _row_change_id(candidate) == change for candidate in roadmap.get("rows", [])
    )
    return row, "main" if in_main else "amendment"


def _amendment_approval_gap(row: dict) -> str:
    for label in AMENDMENT_APPROVAL_FIELDS:
        value = _cell(row, label)
        if _is_blank(value) or "TODO" in value.upper() or (
            value.startswith("<") and value.endswith(">")
        ):
            return label
    return ""


def _scenario_title(value: str) -> str:
    return value.strip().strip("`").strip()


def _proposal_capabilities(path: Path) -> dict:
    result = {
        "new": [],
        "modified": [],
        "new_heading": False,
        "modified_heading": False,
    }
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        heading = HEADING_TITLE_RE.match(stripped)
        if heading:
            title = _norm(heading.group(1))
            if title == "new capabilities":
                current = "new"
                result["new_heading"] = True
            elif title == "modified capabilities":
                current = "modified"
                result["modified_heading"] = True
            else:
                current = None
            continue
        if current is None:
            continue
        match = PROPOSAL_CAP_BULLET_RE.match(stripped)
        if match:
            slug = match.group(1).strip()
            if slug and slug not in result[current]:
                result[current].append(slug)
    return result


def _check_proposal(change: str) -> None:
    change_dir = ROOT / "openspec/changes" / change
    proposal_path = change_dir / "proposal.md"
    if not proposal_path.is_file():
        ERRORS.append(
            "Missing artifact: "
            + proposal_path.relative_to(ROOT).as_posix()
            + " (required by strategy module-packages)"
        )
        proposal = {"new": [], "modified": []}
    else:
        proposal = _proposal_capabilities(proposal_path)

    registry_path = ROOT / CAPABILITIES_REL
    registered: set[str] = set()
    if not registry_path.is_file():
        ERRORS.append(
            f"{CAPABILITIES_REL}: missing capability registry "
            "(required by strategy module-packages)"
        )
    else:
        try:
            rows = gm.load_capabilities(root=ROOT)
        except RuntimeError as exc:
            ERRORS.append(str(exc))
            rows = []
        registered = {
            slug
            for row in rows
            for slug in [(row.get("capability_slug") or "").strip()]
            if slug
            and slug.upper() != "PENDING"
            and not (slug.startswith("<") and slug.endswith(">"))
        }

    for kind, label in (("new", "New Capabilities"), ("modified", "Modified Capabilities")):
        for slug in proposal[kind]:
            if slug not in registered:
                ERRORS.append(
                    f"proposal.md: {label} capability {slug!r} not found in "
                    f"{CAPABILITIES_REL}"
                )

    roadmap_path = ROOT / ROADMAP_REL
    if not roadmap_path.is_file():
        ERRORS.append(f"Missing artifact: {ROADMAP_REL}")
        return
    try:
        roadmap = gm.parse_roadmap(root=ROOT)
    except RuntimeError as exc:
        ERRORS.append(str(exc))
        return

    row, source = _roadmap_lookup(roadmap, change)
    if row is None:
        ERRORS.append(
            f"proposal.md: Change {change!r} is not registered in {ROADMAP_REL}; "
            "a Change absent from the main table requires an approved amendment row"
        )
        return

    if source == "amendment":
        gap = _amendment_approval_gap(row)
        if gap:
            ERRORS.append(
                f"{ROADMAP_REL}: amendment for Change {change!r} is not approved; "
                f"{gap} is blank or a placeholder"
            )

    primary = _cell(row, "Primary Capability")
    slice_type = _cell(row, "Slice Type")
    if _is_blank(primary):
        ERRORS.append(
            f"{ROADMAP_REL}: Change {change!r} has a blank Primary Capability"
        )
    elif primary not in registered:
        ERRORS.append(
            f"{ROADMAP_REL}: Change {change!r} Primary Capability {primary!r} not "
            f"found in {CAPABILITIES_REL}"
        )

    normalized_type = slice_type.casefold()
    if normalized_type == "initial":
        if primary and primary not in proposal["new"]:
            ERRORS.append(
                f"proposal.md: roadmap Primary Capability {primary!r} for initial "
                "Change must be listed under ### New Capabilities"
            )
    elif normalized_type == "extend":
        if primary and primary not in proposal["modified"]:
            ERRORS.append(
                f"proposal.md: roadmap Primary Capability {primary!r} for extend "
                "Change must be listed under ### Modified Capabilities"
            )
    else:
        ERRORS.append(
            f"{ROADMAP_REL}: Change {change!r} has invalid or missing Slice Type "
            f"{slice_type!r}; expected initial|extend, so capability consistency "
            "cannot be verified"
        )


def _spec_scenarios(change: str) -> tuple[set[str], int]:
    specs_dir = ROOT / "openspec/changes" / change / "specs"
    titles: set[str] = set()
    files = 0
    if not specs_dir.is_dir():
        return titles, files
    for path in sorted(specs_dir.glob("*/spec.md")):
        files += 1
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            ERRORS.append(
                f"{path.relative_to(ROOT).as_posix()}: cannot read spec: {exc}"
            )
            continue
        for line in lines:
            match = SCENARIO_HEADING_RE.match(line)
            if match:
                title = _scenario_title(match.group(1))
                if title:
                    titles.add(title)
    return titles, files


def _ac_sections(lines: list[str]) -> list[dict]:
    sections: list[dict] = []
    current: dict | None = None
    for number, line in enumerate(lines, 1):
        match = AC_SECTION_RE.match(line)
        if match:
            current = {"id": match.group(1), "line": number, "body": []}
            sections.append(current)
            continue
        if line.startswith("#"):
            current = None
            continue
        if current is not None:
            current["body"].append((number, line))
    return sections


def _find_section(lines: list[str], heading_re) -> tuple[int, list[str]] | None:
    for index, line in enumerate(lines):
        if heading_re.match(line):
            body = []
            for number, inner in enumerate(lines[index + 1:], index + 2):
                if inner.startswith("## "):
                    break
                body.append((number, inner))
            return index + 1, body
    return None


def _check_walkthrough(
    lines: list[str], positions: dict[str, str], ac_ids: set[str]
) -> None:
    found = _find_section(lines, WALKTHROUGH_HEADING_RE)
    if found is None:
        ERRORS.append(
            "user-stories.md: missing ## Acceptance Walkthrough / ## 验收走查 section"
        )
        return
    line_no, body = found
    listed: list[str] = []
    for _, line in body:
        listed.extend(re.findall(r"AC-\d{3}", line))
    if not listed:
        ERRORS.append(
            f"user-stories.md:{line_no}: Acceptance Walkthrough lists no AC IDs"
        )
        return
    for ac in sorted(set(listed)):
        if ac not in ac_ids:
            ERRORS.append(
                f"user-stories.md:{line_no}: Acceptance Walkthrough references "
                f"undefined {ac}"
            )
    covered = {positions[ac] for ac in listed if ac in positions}
    missing = SLICE_POSITIONS - covered
    if missing:
        ERRORS.append(
            f"user-stories.md:{line_no}: Acceptance Walkthrough must cover at least "
            "one AC at each Slice position; missing "
            + ", ".join(sorted(missing))
        )


def _check_budget(lines: list[str], ac_count: int) -> None:
    if ac_count <= AC_BUDGET:
        return
    approved = False
    for line in lines:
        match = BUDGET_EXCEPTION_RE.match(line.strip())
        if not match:
            continue
        value = match.group(1).strip()
        if _is_blank(value):
            continue
        if "TODO" in value.upper() or (
            value.startswith("<") and value.endswith(">")
        ):
            continue
        if BUDGET_SEPARATOR_RE.match(value):
            approved = True
    if not approved:
        ERRORS.append(
            f"user-stories.md: AC count {ac_count} exceeds {AC_BUDGET}; add a line "
            '"Budget exception: <approver> — <reason>"'
        )


def _check_stories_and_scenarios(change: str, lines: list[str]) -> None:
    sections = _ac_sections(lines)
    scenario_titles, spec_files = _spec_scenarios(change)
    referenced: set[str] = set()
    positions: dict[str, str] = {}

    for section in sections:
        ac = section["id"]
        scenario_values = []
        position_value = None
        for number, line in section["body"]:
            match = SCENARIO_LINE_RE.match(line)
            if match:
                scenario_values.append((number, _scenario_title(match.group(1))))
            match = SLICE_POSITION_RE.match(line)
            if match:
                position_value = (number, match.group(1).strip())
        if not scenario_values:
            ERRORS.append(
                f'user-stories.md:{section["line"]}: {ac} is missing '
                '"- Scenario: <spec Scenario title>"'
            )
        for number, value in scenario_values:
            if not value:
                ERRORS.append(
                    f"user-stories.md:{number}: {ac} has a blank Scenario reference"
                )
                continue
            referenced.add(value)
            if spec_files and value not in scenario_titles:
                ERRORS.append(
                    f"user-stories.md:{number}: {ac} references unknown spec "
                    f"Scenario {value!r}"
                )
        if position_value is None:
            ERRORS.append(
                f'user-stories.md:{section["line"]}: {ac} is missing '
                '"- Slice position: entry|behavior|result"'
            )
        else:
            value = position_value[1].casefold()
            if value not in SLICE_POSITIONS:
                ERRORS.append(
                    f"user-stories.md:{position_value[0]}: {ac} has invalid Slice "
                    f"position {position_value[1]!r}; expected entry|behavior|result"
                )
            else:
                positions[ac] = value

    for title in sorted(scenario_titles - referenced):
        ERRORS.append(
            f"spec Scenario {title!r} is not referenced by any AC - Scenario: line"
        )

    _check_walkthrough(lines, positions, {section["id"] for section in sections})
    _check_budget(lines, len(sections))


def check_change(change):
    base = ROOT / 'openspec/changes' / change / 'design'
    us_lines = read_lines(base / 'user-stories.md')
    placeholders(us_lines, 'user-stories.md')
    uss = report_duplicates(ids_from(us_lines, r'^\|\s*(US-\d{3})\s*\|'), 'user-stories.md')
    acs = report_duplicates(ids_from(us_lines, r'^###\s+(AC-\d{3})\b'), 'user-stories.md')
    if not uss:
        ERRORS.append('user-stories.md: no US-xxx table rows found')
    if not acs:
        ERRORS.append('user-stories.md: no AC-xxx sections found')
    # US rows are markdown tables, not CSV; parse AC references directly.
    for n, line in enumerate(us_lines, 1):
        m = re.match(r'^\|\s*(US-\d{3})\s*\|', line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        refs = re.findall(r'AC-\d{3}', line)
        if not refs:
            ERRORS.append(f'user-stories.md:{n}: {m.group(1)} has no AC reference')
        for ac in refs:
            if ac not in acs:
                ERRORS.append(f'user-stories.md:{n}: {m.group(1)} references undefined {ac}')
        if len(cells) < 6:
            WARNINGS.append(f'user-stories.md:{n}: {m.group(1)} row has fewer than 6 columns')
    # Cross-check project IDs referenced by the proposal-level artifacts.
    workflows = read_lines(ROOT / 'docs/product/workflows.md')
    flows = set(re.findall(r'^##\s+(FLOW-\d{3})\b', '\n'.join(workflows), re.M))
    nodes = set(re.findall(r'NODE-\d{3}-\d{2}', '\n'.join(workflows)))
    rules = read_lines(ROOT / 'docs/product/business-rules.md')
    brs = set(re.findall(r'BR-\d{3}', '\n'.join(rules)))
    for ref in set(re.findall(r'FLOW-\d{3}', '\n'.join(us_lines))):
        if flows and ref not in flows:
            ERRORS.append(f'user-stories.md: references unknown {ref}')
    for ref in set(re.findall(r'NODE-\d{3}-\d{2}', '\n'.join(us_lines))):
        if nodes and ref not in nodes:
            ERRORS.append(f'user-stories.md: references unknown {ref}')
    for ref in set(re.findall(r'BR-\d{3}', '\n'.join(us_lines))):
        if brs and ref not in brs:
            ERRORS.append(f'user-stories.md: references unknown {ref}')

    try:
        strategy = gm.strategy(root=ROOT)
    except RuntimeError as exc:
        ERRORS.append(str(exc))
        strategy = 'none'
    if strategy != 'none':
        if strategy == 'module-packages':
            _check_proposal(change)
        _check_stories_and_scenarios(change, us_lines)
    return f'US={len(uss)}, AC={len(acs)}'


def _parse_args(argv):
    args = list(sys.argv[1:] if argv is None else argv)
    strict = '--strict' in args
    args = [a for a in args if a != '--strict']
    change = None
    if '--change' in args:
        idx = args.index('--change')
        if idx + 1 >= len(args):
            print('Usage: check-requirements.py [--change <change-id>] [--strict]', file=sys.stderr)
            return None, strict, 2
        change = args[idx + 1]
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', change):
            print('Invalid change-id', file=sys.stderr)
            return None, strict, 2
        args = args[:idx] + args[idx + 2:]
    if args:
        print('Usage: check-requirements.py [--change <change-id>] [--strict]', file=sys.stderr)
        return None, strict, 2
    return change, strict, 0


def main(argv=None):
    global ERRORS, WARNINGS
    ERRORS = []
    WARNINGS = []
    change, strict, code = _parse_args(argv)
    if code:
        return code
    counts = check_change(change) if change else check_project()
    for w in WARNINGS:
        print('WARN:', w)
    for e in ERRORS:
        print('ERROR:', e)
    if ERRORS or (strict and WARNINGS):
        print(f'Requirements check failed: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s).')
        return 1
    scope = f'Change {change}' if change else 'project requirement business'
    print(f'Declared IDs: {counts}')
    print(f'Requirements artifact structure check passed ({scope}).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
