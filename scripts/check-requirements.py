#!/usr/bin/env python3
"""Validate project requirement-business artifacts or a Change's proposal-level UC/US/AC."""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
STRICT = '--strict' in args
CHANGE = None
if '--change' in args:
    idx = args.index('--change')
    if idx + 1 >= len(args):
        print('Usage: check-requirements.py [--change <change-id>] [--strict]', file=sys.stderr); sys.exit(2)
    CHANGE = args[idx + 1]
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', CHANGE):
        print('Invalid change-id', file=sys.stderr); sys.exit(2)
    args = args[:idx] + args[idx + 2:]
args = [a for a in args if a != '--strict']
if args:
    print('Usage: check-requirements.py [--change <change-id>] [--strict]', file=sys.stderr); sys.exit(2)

ERRORS, WARNINGS = [], []

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
    for need in ('执行角色', '输入数据对象', '输出数据对象'):
        if not any(need in l for l in header):
            ERRORS.append(f'workflows.md: node table header missing column: {need}')
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

def check_change(change):
    base = ROOT / 'openspec/changes' / change / 'design'
    uc_lines = read_lines(base / 'use-cases.md')
    us_lines = read_lines(base / 'user-stories.md')
    placeholders(uc_lines, 'use-cases.md')
    placeholders(us_lines, 'user-stories.md')
    ucs = report_duplicates(ids_from(uc_lines, r'^##\s+(UC-\d{3})\b'), 'use-cases.md')
    uss = report_duplicates(ids_from(us_lines, r'^\|\s*(US-\d{3})\s*\|'), 'user-stories.md')
    acs = report_duplicates(ids_from(us_lines, r'^###\s+(AC-\d{3})\b'), 'user-stories.md')
    if not ucs:
        ERRORS.append('use-cases.md: no UC-xxx sections found')
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
    for label, lines in (('use-cases.md', uc_lines), ('user-stories.md', us_lines)):
        for ref in set(re.findall(r'FLOW-\d{3}', '\n'.join(lines))):
            if flows and ref not in flows:
                ERRORS.append(f'{label}: references unknown {ref}')
        for ref in set(re.findall(r'NODE-\d{3}-\d{2}', '\n'.join(lines))):
            if nodes and ref not in nodes:
                ERRORS.append(f'{label}: references unknown {ref}')
        for ref in set(re.findall(r'BR-\d{3}', '\n'.join(lines))):
            if brs and ref not in brs:
                ERRORS.append(f'{label}: references unknown {ref}')
    return f'UC={len(ucs)}, US={len(uss)}, AC={len(acs)}'

counts = check_change(CHANGE) if CHANGE else check_project()
for w in WARNINGS:
    print('WARN:', w)
for e in ERRORS:
    print('ERROR:', e)
if ERRORS or (STRICT and WARNINGS):
    print(f'Requirements check failed: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s).')
    sys.exit(1)
scope = f'Change {CHANGE}' if CHANGE else 'project requirement business'
print(f'Declared IDs: {counts}')
print(f'Requirements artifact structure check passed ({scope}).')
