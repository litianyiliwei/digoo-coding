#!/usr/bin/env python3
"""Validate the Change test-case matrix: AC/page/API/IO coverage and TEST IDs."""
from pathlib import Path
import csv, re, sys

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
strict = '--strict' in args
change = None
if '--change' in args:
    idx = args.index('--change')
    if idx + 1 >= len(args):
        print('Usage: check-test-cases.py --change <change-id> [--strict]', file=sys.stderr)
        sys.exit(2)
    change = args[idx + 1]
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', change):
        print('Invalid change-id', file=sys.stderr); sys.exit(2)
    args = args[:idx] + args[idx + 2:]
args = [a for a in args if a != '--strict']
if args or not change:
    print('Usage: check-test-cases.py --change <change-id> [--strict]', file=sys.stderr)
    sys.exit(2)

change_dir = ROOT / 'openspec/changes' / change
base = change_dir / 'design'
TEST = base / 'test-cases.csv'
US = base / 'user-stories.md'
AUDIT = base / 'figma-audit.md'
OPENAPI = change_dir / 'api' / 'openapi.yaml'
IO = base / 'io-catalog.csv'
TRACE = change_dir / 'traceability.csv'

errors, warnings = [], []
required_cols = ['test_id', 'level', 'ac_ids', 'page_ids', 'block_ids', 'api_ids', 'io_ids',
                 'preconditions', 'data', 'steps', 'expected', 'failure_injection', 'fakes_env',
                 'manual_reason', 'automation', 'status', 'notes']
if not TEST.is_file():
    print(f'ERROR: missing test-case matrix: {TEST.relative_to(ROOT)}')
    print('Stage 07 must produce design/test-cases.csv (TEST IDs mapped to AC/PAGE/BLOCK/API/IO).')
    sys.exit(1)
with TEST.open(newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames or []
    missing = [c for c in required_cols if c not in headers]
    if missing:
        print('ERROR: test-cases.csv missing columns: ' + ', '.join(missing))
        sys.exit(1)
    rows = list(reader)
if not rows:
    print('ERROR: test-cases.csv is header-only; at least one test case is required.')
    sys.exit(1)

VALID_STATUS = {'planned', 'covered', 'passed', 'failed', 'n/a', 'gap', 'blocked'}
required_fields = ['test_id', 'level', 'ac_ids', 'preconditions', 'steps', 'expected', 'failure_injection', 'fakes_env', 'automation', 'status']
seen = {}
def split_ids(value):
    return [x.strip() for x in re.split(r'[;,，；、\s]+', value or '') if x.strip() and x.strip().upper() != 'N/A']

for line, row in enumerate(rows, 2):
    tid = (row.get('test_id') or '').strip()
    if not tid.startswith('TEST-'):
        errors.append(f'line {line}: test_id must use TEST- prefix, got {tid!r}')
    if tid in seen:
        errors.append(f'line {line}: duplicate TEST ID {tid} (first at line {seen[tid]})')
    else:
        seen[tid] = line
    for field in required_fields:
        if not (row.get(field) or '').strip():
            errors.append(f'line {line}: {field} is required; use N/A + reason when not applicable')
    status = (row.get('status') or '').strip().lower()
    if status not in VALID_STATUS:
        errors.append(f'line {line}: status must be one of {", ".join(sorted(VALID_STATUS))}; got {status!r}')
    if status == 'n/a' and not (row.get('notes') or '').strip():
        errors.append(f'line {line}: n/a requires a reason in notes')
    manual_reason = (row.get('manual_reason') or '').strip()
    automation = (row.get('automation') or '').strip()
    if (row.get('level') or '').strip().lower() == 'manual' or automation.lower().startswith('manual'):
        if not manual_reason or manual_reason.upper() == 'N/A':
            errors.append(f'line {line}: manual test requires a concrete manual_reason')
    if status in {'gap', 'blocked'}:
        warnings.append(f'line {line}: unresolved test gap/blocked status for {tid or "row"}')
    if re.search(r'TODO|TBD|PENDING|\[填充\]|待确认|待补充', '\n'.join(str(v or '') for v in row.values()), re.I):
        warnings.append(f'line {line}: unresolved placeholder remains in {tid or "row"}')

# AC coverage: every AC declared in user-stories.md must appear in at least one test case.
if US.is_file():
    acs = set(re.findall(r'AC-\d{3}', US.read_text(encoding='utf-8')))
else:
    acs = set()
covered_acs = set()
for row in rows:
    covered_acs.update(split_ids(row.get('ac_ids')))
for ac in sorted(acs - covered_acs):
    errors.append(f'AC coverage: {ac} has no test case (add a test row, or a manual row with status n/a + reason)')

# Page coverage: every PAGE frozen in 06 figma-audit.md must appear in at
# least one test case.
pages = set()
if AUDIT.is_file():
    pages = set(re.findall(r'PAGE-\d{3}', AUDIT.read_text(encoding='utf-8')))
covered_pages = set()
for row in rows:
    covered_pages.update(split_ids(row.get('page_ids')))
for pid in sorted(pages - covered_pages):
    errors.append(f'UI coverage: {pid} has no test case/page_ids entry')

# Block coverage: every BLOCK in block-inventory.csv must appear in at least one test case.
BLOCK = base / 'block-inventory.csv'
blocks = set()
if BLOCK.is_file():
    with BLOCK.open(newline='', encoding='utf-8-sig') as f:
        blocks = { (r.get('block_id') or '').strip() for r in csv.DictReader(f) if (r.get('block_id') or '').strip() }
covered_blocks = set()
for row in rows:
    covered_blocks.update(split_ids(row.get('block_ids')))
for bid in sorted(blocks - covered_blocks):
    errors.append(f'Block coverage: {bid} has no test case/block_ids entry')

# API coverage: every operationId in OpenAPI must appear in at least one test case.
operation_ids = set()
if OPENAPI.is_file():
    text = OPENAPI.read_text(encoding='utf-8')
    if not re.search(r'x-api-scope:\s*none', text, re.I):
        operation_ids = set(re.findall(r'operationId:\s*([A-Za-z0-9_.-]+)', text))
covered_apis = set()
for row in rows:
    covered_apis.update(split_ids(row.get('api_ids')))
for op in sorted(operation_ids - covered_apis):
    errors.append(f'API coverage: operationId {op} has no test case/api_ids entry')

# IO coverage: every IO in io-catalog.csv must be referenced by at least one test case.
io_ids = set()
if IO.is_file():
    with IO.open(newline='', encoding='utf-8-sig') as f:
        io_ids = { (r.get('io_id') or '').strip() for r in csv.DictReader(f) if (r.get('io_id') or '').strip() }
covered_ios = set()
for row in rows:
    covered_ios.update(split_ids(row.get('io_ids')))
for ioid in sorted(io_ids - covered_ios):
    errors.append(f'IO coverage: {ioid} has no test case/io_ids entry')

# Interface coverage: every cross-boundary interface must have at least one test.
INTERFACE = base / 'interface-catalog.csv'
interface_ids = set()
covered_interfaces = set()
if INTERFACE.is_file():
    if 'interface_ids' not in headers:
        errors.append('test-cases.csv missing interface_ids column while interface-catalog.csv exists')
    with INTERFACE.open(newline='', encoding='utf-8-sig') as f:
        interface_ids = { (r.get('interface_id') or '').strip() for r in csv.DictReader(f) if (r.get('interface_id') or '').strip() }
    for row in rows:
        covered_interfaces.update(split_ids(row.get('interface_ids')))
    for iid in sorted(interface_ids - covered_interfaces):
        errors.append(f'Interface coverage: {iid} has no test case/interface_ids entry')
    for iid in sorted(covered_interfaces - interface_ids):
        errors.append(f'Interface coverage: test case references unknown interface {iid}')


# Traceability: TEST IDs must appear in the single aggregate traceability.csv.
if TRACE.is_file():
    trace_ids = set()
    with TRACE.open(newline='', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            trace_ids.add((r.get('source_id') or '').strip())
            trace_ids.add((r.get('target_id') or '').strip())
    for tid in sorted(seen):
        if tid not in trace_ids:
            errors.append(f'traceability: {tid} is not linked in traceability.csv')
else:
    errors.append('missing traceability.csv; TEST IDs must be linked in the aggregate traceability')

if errors:
    for e in errors: print('ERROR:', e)
for w in warnings: print('WARN:', w)
if errors or (strict and warnings):
    print(f'Test-case matrix check failed: {len(errors)} error(s), {len(warnings)} warning(s).')
    sys.exit(1)
print(f'Test-case matrix passed: {len(rows)} case(s), AC coverage {len(covered_acs)}/{len(acs)}, pages {len(covered_pages)}/{len(pages)}, blocks {len(covered_blocks)}/{len(blocks)}, APIs {len(covered_apis)}/{len(operation_ids)}, IO {len(covered_ios)}/{len(io_ids)}, interfaces {len(covered_interfaces)}/{len(interface_ids)}.')
