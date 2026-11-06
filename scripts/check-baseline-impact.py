#!/usr/bin/env python3
"""Check the baseline impact record for a Change; --strict requires review approval."""
from pathlib import Path
import argparse, re, sys, subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('change_id', help='OpenSpec change-id or path to baseline-impact.md')
parser.add_argument('--strict', action='store_true', help='Require approved baseline decision and design gate')
args = parser.parse_args()
arg = Path(args.change_id)
path = arg if arg.is_file() else ROOT / 'openspec/changes' / args.change_id / 'design/baseline-impact.md'
if not path.is_file():
    print(f'ERROR: baseline impact record not found: {path}', file=sys.stderr)
    sys.exit(2)
text = path.read_text(encoding='utf-8')
required_sections = [
    '## 1. 基线状态快照', '## 2. 固定读取项核验', '## 3. 按影响读取项核验',
    '## 4. 复用与一致性映射', '## 5. 变化归属判定',
    '## 6. 基线冲突、缺口与候选修订', '## 7. 在途 Change 版本复核', '## 8. 结论与门禁'
]
missing = [s for s in required_sections if s not in text]
if missing:
    for item in missing: print(f'ERROR: missing section: {item}')
    sys.exit(1)
if args.strict:
    checks = {
        'approved review state': re.search(r'^- 状态：APPROVED\s*$', text, re.M),
        'current baseline version recorded': re.search(r'^- 当前基线版本：(?!\s*$|\s*TODO\s*$).+', text, re.M),
        'classification recorded': re.search(r'^- 本 Change 基线分类：(CHANGE_ONLY|BASELINE_CHANGE_REQUIRED|BASELINE_UPDATE_AFTER_ACCEPTANCE|N/A)\s*$', text, re.M),
        'final conclusion recorded': re.search(r'^- 总体结论：(COMPATIBLE|BLOCKED_PENDING_BASELINE_CHANGE|APPROVED_BASELINE_AMENDMENT)\s*$', text, re.M),
        'detailed design gate recorded': re.search(r'^- 是否允许进入详细设计：(YES|NO)\s*$', text, re.M),
        'Change ID recorded': re.search(r'^- Change ID：(?!<change-id>\s*$).+', text, re.M),
        'approval evidence recorded': re.search(r'^- 审批人及证据：(?!\s*$).+', text, re.M),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print('ERROR: strict baseline impact gate failed: ' + ', '.join(failed))
        sys.exit(1)
    conclusion = re.search(r'^- 总体结论：(\S+)\s*$', text, re.M).group(1)
    allow = re.search(r'^- 是否允许进入详细设计：(\S+)\s*$', text, re.M).group(1)
    if conclusion == 'BLOCKED_PENDING_BASELINE_CHANGE' or allow != 'YES':
        print('ERROR: baseline impact decision blocks detailed design.')
        sys.exit(1)
    # Markdown approval fields are not sufficient: the machine-readable binding must also pass.
    inferred_change_id = path.parent.parent.name if path.parent.name == 'design' else ''
    if not inferred_change_id or inferred_change_id.startswith('<'):
        print('ERROR: --strict requires a real openspec/changes/<change-id>/design/baseline-impact.md path.')
        sys.exit(1)
    gate = subprocess.run([sys.executable, str(ROOT/'scripts'/'baseline-governance.py'),
                           'check-change', '--change-id', inferred_change_id, '--phase', 'design'],
                          capture_output=True, text=True)
    if gate.returncode:
        print('ERROR: machine baseline binding gate failed:')
        print((gate.stdout + gate.stderr).strip())
        sys.exit(1)
print(f'Baseline impact record structure passed: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}')
if args.strict:
    print('Strict baseline impact gate passed: record approved and detailed design allowed.')
