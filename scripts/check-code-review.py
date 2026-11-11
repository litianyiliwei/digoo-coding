#!/usr/bin/env python3
"""Validate code-review evidence content for stage 08."""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
strict = '--strict' in args
change = None
if '--change' in args:
    idx = args.index('--change')
    if idx + 1 >= len(args):
        print('Usage: check-code-review.py --change <change-id> [--strict]', file=sys.stderr)
        sys.exit(2)
    change = args[idx + 1]
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', change):
        print('Invalid change-id', file=sys.stderr)
        sys.exit(2)
    args = args[:idx] + args[idx + 2:]
args = [a for a in args if a != '--strict']
if args or not change:
    print('Usage: check-code-review.py --change <change-id> [--strict]', file=sys.stderr)
    sys.exit(2)

path = ROOT / 'openspec/changes' / change / 'design/evidence/code-review.md'
if not path.is_file() or not path.stat().st_size:
    print(f'ERROR: missing code-review evidence: {path.relative_to(ROOT)}')
    print('Stage 08 must record the code review in design/evidence/code-review.md.')
    sys.exit(1)

text = path.read_text(encoding='utf-8')
errors = []
markers = ('TODO', 'TBD', 'PENDING', '待确认', '待补充')
for marker in markers:
    if marker.lower() in text.lower():
        errors.append(f'unresolved marker remains: {marker}')

for field in ('Change ID', 'Reviewer/tool', 'Review date/commit'):
    m = re.search(rf'^-\s*{re.escape(field)}\s*[:：]\s*(.+?)\s*$', text, re.M)
    if not m or not m.group(1).strip() or m.group(1).strip().upper() in {'TODO', 'TBD', 'PENDING', 'N/A', '待确认', '待补充'}:
        errors.append(f'{field} must be filled with a real value')

conclusion = re.search(r'^-\s*Review conclusion\s*[:：]\s*(.+?)\s*$', text, re.M)
allowed_conclusions = {'pass', 'passed', 'approved', 'no blocking findings', 'no-blocking-findings'}
if not conclusion or conclusion.group(1).strip().lower() not in allowed_conclusions:
    errors.append('Review conclusion must be PASS/APPROVED/NO_BLOCKING_FINDINGS; unresolved findings block stage 08')

required_sections = ['## Findings by severity', '## Spec compliance, security, data consistency, failure paths']
for section in required_sections:
    if section not in text:
        errors.append(f'missing section: {section}')

findings_section = ''
start = text.find('## Findings by severity')
if start >= 0:
    end = text.find('\n## ', start + len('## Findings by severity'))
    findings_section = text[start:end if end >= 0 else len(text)]
rows = [line.strip() for line in findings_section.splitlines()
        if line.strip().startswith('|')
        and 'Severity' not in line
        and not re.match(r'^\|[\s:|-]+\|$', line.strip())]
no_findings = re.search(r'^-\s*Findings\s*[:：]\s*(none|no findings|无)\s*$', text, re.M | re.I)
if not rows and not no_findings:
    errors.append('Findings must list at least one row, or declare "- Findings: none"')

allowed_status = {'fixed', 'resolved', 'closed', 'accepted', 'risk-accepted', 'n/a', 'none'}
for row in rows:
    cells = [c.strip() for c in row.strip('|').split('|')]
    if len(cells) < 5 or any(not c for c in cells[:5]):
        errors.append(f'finding row is incomplete: {row}')
        continue
    status = cells[4].lower()
    if status not in allowed_status:
        errors.append(f'finding status must be one of {sorted(allowed_status)}; got {cells[4]!r}')
    if any(c.lower() in {'todo', 'tbd', 'pending', 'open'} for c in cells):
        errors.append(f'finding row contains unresolved placeholder: {row}')

if errors:
    for e in errors:
        print('ERROR:', e)
    print(f'Code review check failed: {len(errors)} issue(s).')
    sys.exit(1)
print(f'Code review check passed: {len(rows)} finding row(s), conclusion approved.')
