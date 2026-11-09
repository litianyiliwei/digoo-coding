#!/usr/bin/env python3
"""Validate operationId → PAGE/EVT/AC links in the aggregate traceability.csv."""
from pathlib import Path
import csv, re, sys

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
change = None
if '--change' in args:
    idx = args.index('--change')
    if idx + 1 >= len(args):
        print('Usage: check-api-traceability.py --change <change-id> [--strict]', file=sys.stderr)
        sys.exit(2)
    change = args[idx + 1]
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', change):
        print('Invalid change-id', file=sys.stderr); sys.exit(2)
    args = args[:idx] + args[idx + 2:]
args = [a for a in args if a != '--strict']
if args or not change:
    print('Usage: check-api-traceability.py --change <change-id> [--strict]', file=sys.stderr)
    sys.exit(2)

change_dir = ROOT / 'openspec/changes' / change
OPENAPI = change_dir / 'api' / 'openapi.yaml'
TRACE = change_dir / 'traceability.csv'

operation_ids = set()
if OPENAPI.is_file():
    text = OPENAPI.read_text(encoding='utf-8')
    if not re.search(r'x-api-scope:\s*none', text, re.I):
        operation_ids = set(re.findall(r'operationId:\s*([A-Za-z0-9_.-]+)', text))
if not operation_ids:
    print('API traceability check skipped: no operationId in OpenAPI (x-api-scope: none).')
    sys.exit(0)

if not TRACE.is_file():
    print(f'ERROR: missing traceability.csv; operationIds must link to PAGE/EVT/AC')
    sys.exit(1)

with TRACE.open(newline='', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

def ids(row):
    return [(row.get('source_type') or '').strip(), (row.get('source_id') or '').strip(),
            (row.get('target_type') or '').strip(), (row.get('target_id') or '').strip()]

errors = []
for op in sorted(operation_ids):
    related = [r for r in rows if (r.get('source_id') or '').strip() == op or (r.get('target_id') or '').strip() == op]
    if not related:
        errors.append(f'{op}: operationId is not linked in traceability.csv')
        continue
    linked = False
    for r in related:
        other = [(r.get('source_id') or '').strip(), (r.get('target_id') or '').strip()]
        if any(re.match(r'(PAGE|EVT|AC|ELEM)-', x) for x in other):
            linked = True
    if not linked:
        errors.append(f'{op}: has traceability rows but none link to PAGE/EVT/ELEM/AC')

if errors:
    for e in errors:
        print('ERROR:', e)
    print(f'API traceability check failed: {len(errors)} issue(s).')
    sys.exit(1)
print(f'API traceability passed: {len(operation_ids)} operationId(s) linked to PAGE/EVT/AC in traceability.csv.')
