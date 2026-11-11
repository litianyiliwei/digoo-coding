#!/usr/bin/env python3
"""Fail-closed structural check for human acceptance evidence."""
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)!=2:
    print('Usage: check-acceptance.py <change-id>', file=sys.stderr); sys.exit(2)
change_id=sys.argv[1]
if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',change_id):
    print('Invalid change-id; use lowercase kebab-case.',file=sys.stderr); sys.exit(2)
path=ROOT/'openspec/changes'/change_id/'design/evidence/acceptance.md'
if not path.is_file():
    print(f'MISSING: {path.relative_to(ROOT)}',file=sys.stderr); sys.exit(1)
text=path.read_text(encoding='utf-8')
errors=[]
match=re.search(r'(?im)^-\s*Overall result:\s*(.+?)\s*$',text)
accepted={'accepted','accepted with approved deviations'}
if not match or match.group(1).strip().lower() not in accepted:
    errors.append('Overall result must be ACCEPTED or ACCEPTED WITH APPROVED DEVIATIONS.')
for marker in ('TODO','TBD','待确认','Pending','pending','NOT ACCEPTED'):
    if marker in text:
        errors.append(f'Unresolved marker remains in acceptance evidence: {marker}')
rows=[]
for line_no,line in enumerate(text.splitlines(),1):
    s=line.strip()
    if not s.startswith('|') or '---' in s: continue
    cells=[x.strip() for x in s.strip('|').split('|')]
    if cells and cells[0].lower()=='ac id': continue
    if cells and re.fullmatch(r'AC-\d+',cells[0]): rows.append((line_no,cells))
if not rows: errors.append('At least one AC-### result row is required.')
allowed={'pass','passed','accepted','n/a','approved deviation'}
for line_no,cells in rows:
    while len(cells)<5: cells.append('')
    result=cells[1].lower()
    evidence=cells[2]
    reviewer=cells[4]
    if result not in allowed:
        errors.append(f'Line {line_no}: AC result {cells[1]!r} is not an accepted status.')
    if not evidence or evidence.lower() in {'todo','tbd','pending','n/a'}:
        errors.append(f'Line {line_no}: AC evidence must identify an actual test/report/manual evidence.')
    if not reviewer or reviewer.lower() in {'todo','tbd','pending'}:
        errors.append(f'Line {line_no}: reviewer is required.')
if errors:
    for e in errors: print('ERROR:',e)
    print(f'Acceptance check failed: {len(errors)} issue(s).')
    sys.exit(1)
print(f'Acceptance evidence structurally passed: {len(rows)} AC row(s). Human judgment is still required.')
