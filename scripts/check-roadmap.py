#!/usr/bin/env python3
"""Check Change roadmap table for duplicate IDs and unresolved placeholder rows."""
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'docs/product/proposal-roadmap.md'
strict='--strict' in sys.argv[1:]
if len(sys.argv)>1 and sys.argv[1:] != ['--strict']:
    print('Usage: check-roadmap.py [--strict]', file=sys.stderr); sys.exit(2)
if not path.is_file(): print(f'MISSING: {path}', file=sys.stderr); sys.exit(1)
text=path.read_text(encoding='utf-8')
rows=[]
for line_no,line in enumerate(text.splitlines(),1):
    s=line.strip()
    if not s.startswith('|') or '---' in s: continue
    cells=[c.strip() for c in s.strip('|').split('|')]
    if cells and cells[0].lower() in {'change id','change-id'}: continue
    if len(cells)>=3: rows.append((line_no,cells))
errors=[]; warnings=[]; seen=set()
if not rows: warnings.append('Roadmap table has no data rows yet')
for n,cells in rows:
    change_id=cells[0]
    if not change_id or 'TODO' in change_id.upper() or change_id.startswith('<'):
        warnings.append(f'line {n}: unresolved Change ID: {change_id!r}'); continue
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',change_id): errors.append(f'line {n}: invalid change-id {change_id!r}; use lowercase kebab-case')
    if change_id in seen: errors.append(f'line {n}: duplicate change-id {change_id!r}')
    seen.add(change_id)
    if any((not c or 'TODO' in c.upper()) for c in cells[1:]): warnings.append(f'line {n}: placeholder remains in roadmap row {change_id!r}')
for m in warnings: print('WARN:',m)
for m in errors: print('ERROR:',m)
if errors or (strict and warnings):
    print(f'Roadmap check failed: {len(errors)} error(s), {len(warnings)} warning(s).'); sys.exit(1)
print(f'Roadmap structure check passed: {len(seen)} named Change(s).')
