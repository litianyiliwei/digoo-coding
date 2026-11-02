#!/usr/bin/env python3
"""Check that requirements artifacts declare stable FLOW/UC/US/AC/BR identifiers."""
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
strict='--strict' in sys.argv[1:]
if len(sys.argv)>1 and sys.argv[1:] != ['--strict']:
    print('Usage: check-requirements.py [--strict]',file=sys.stderr); sys.exit(2)
checks=[
  ('docs/product/workflows.md', r'^##\s+(FLOW-\d+)\b', 'FLOW'),
  ('docs/product/use-cases.md', r'^##\s+(UC-\d+)\b', 'UC'),
  ('docs/product/user-stories.md', r'^\|\s*(US-\d+)\s*\|', 'US'),
  ('docs/product/user-stories.md', r'^###\s+(AC-\d+)\b', 'AC'),
  ('docs/product/business-rules.md', r'^\|\s*(BR-\d+)\s*\|', 'BR'),
]
errors=[]; warnings=[]; seen_by_kind={}
for rel, pattern, kind in checks:
    path=ROOT/rel
    if not path.is_file(): errors.append(f'Missing artifact: {rel}'); continue
    lines=path.read_text(encoding='utf-8').splitlines()
    ids=[]
    rx=re.compile(pattern)
    for line_no,line in enumerate(lines,1):
        m=rx.search(line)
        if m: ids.append((m.group(1),line_no))
    if not ids: warnings.append(f'{rel}: no declared {kind}-IDs found')
    seen={}
    for item,line_no in ids:
        if item in seen: errors.append(f'{rel}:{line_no}: duplicate declared {kind}-ID {item} (first at line {seen[item]})')
        else: seen[item]=line_no
    seen_by_kind[kind]=len(seen)
    if any(re.search(r'\bTODO\b|\bTBD\b|\[填充\]',line,re.I) for line in lines):
        warnings.append(f'{rel}: unresolved template placeholders remain')
if errors:
    for e in errors: print('ERROR:',e)
for w in warnings: print('WARN:',w)
if errors or (strict and warnings):
    print(f'Requirements check failed: {len(errors)} error(s), {len(warnings)} warning(s).')
    sys.exit(1)
print('Declared IDs:', ', '.join(f'{k}={v}' for k,v in sorted(seen_by_kind.items())))
print('Requirements artifact structure check passed.')
