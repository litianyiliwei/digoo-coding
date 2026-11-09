#!/usr/bin/env python3
"""Print the minimal context bundle for a workflow stage.

Usage:
  python scripts/agent-context.py --stage 02
  python scripts/agent-context.py --stage 05 --change <change-id>
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / 'docs/STEP-ARTIFACT-CONTRACTS.json'

RESIDENT = {
    '02': [
        'docs/TEMPLATE-POLICY.md',
        'docs/OUTPUT-TEMPLATE-MATRIX.csv',
        'docs/STEP-ARTIFACT-CONTRACTS.md',
        'docs/STEP-ARTIFACT-CONTRACTS.json',
    ],
    '03': [
        'docs/product/BASELINE-BRIEF.md',
        'docs/product/role-permission-matrix.csv',
        'docs/product/change-sizing.md',
        'docs/product/decisions.md',
        'docs/product/assumptions.md',
        'docs/product/id-conventions.md',
    ],
    '04': [
        'docs/product/BASELINE-BRIEF.md',
        'docs/product/change-sizing.md',
        'docs/product/decisions.md',
        'docs/product/assumptions.md',
        'docs/product/lessons.md',
        'docs/product/id-conventions.md',
    ],
    '05': [
        'docs/product/BASELINE-BRIEF.md',
        'docs/product/change-sizing.md',
        'docs/product/role-permission-matrix.csv',
        'docs/product/decisions.md',
        'docs/product/assumptions.md',
        'docs/product/lessons.md',
        'docs/product/id-conventions.md',
    ],
    '16': [
        'docs/product/BASELINE-BRIEF.md',
        'docs/product/change-sizing.md',
        'docs/product/lessons.md',
        'docs/product/acceptance-policy.md',
    ],
}

PATH_RE = re.compile(r'(?:docs|openspec|scripts|prompts|templates|\.claude)/[^\s，、；（）<>]+')


def load_stage(stage):
    data = json.loads(CONTRACTS.read_text(encoding='utf-8'))
    for row in data.get('steps', []):
        if row.get('step', '').lstrip('0') == stage.lstrip('0'):
            return row
    return None


def check_path(raw, change_id):
    token = raw.rstrip('。，、；:：)')
    if '<change-id>' in token:
        if not change_id:
            return token, None
        token = token.replace('<change-id>', change_id)
    if '*' in token or token.startswith('openspec/specs'):
        return token, None
    target = ROOT / token
    return token, target.is_file()


def main():
    args = sys.argv[1:]
    stage = None
    change_id = None
    while args:
        arg = args.pop(0)
        if arg == '--stage' and args:
            stage = args.pop(0)
        elif arg == '--change' and args:
            change_id = args.pop(0)
        else:
            print(f'Unknown argument: {arg}', file=sys.stderr)
            sys.exit(2)
    if not stage:
        print('Usage: agent-context.py --stage <02|05> [--change <change-id>]', file=sys.stderr)
        sys.exit(2)
    row = load_stage(stage)
    if not row:
        print(f'Unknown stage: {stage}', file=sys.stderr)
        sys.exit(2)

    missing = []
    print(f'# Agent Context Bundle: {row["step"]} {row["title"]}')
    print(f'- Skill: `{row["skill"]}`')
    print(f'- Scope: {row.get("scope", "—")}')
    print('')
    print('## 0. 常驻读取（先读）')
    for path in RESIDENT.get(row['step'].lstrip('0'), []):
        token, exists = check_path(path, change_id)
        print(f'- `{token}` [{"OK" if exists else "MISSING"}]')
        if exists is False:
            missing.append(token)

    print('')
    print('## 1. 契约输入')
    for item in row.get('inputs', []):
        print(f'- {item}')
        for raw in PATH_RE.findall(item):
            token, exists = check_path(raw, change_id)
            if exists is False:
                missing.append(token)
                print(f'  - `{token}` [MISSING]')
            elif exists is True:
                print(f'  - `{token}` [OK]')

    print('')
    print('## 2. 契约输出')
    for item in row.get('outputs', []):
        print(f'- {item.replace("<change-id>", change_id or "<change-id>")}')

    print('')
    print('## 3. 门禁')
    print(row.get('gate', '—'))
    print('')
    print('## 4. 审批与下一步输入')
    print(f'- 审批：{row.get("approval", "—")}')
    for item in row.get('next_inputs', []):
        print(f'- {item}')

    if missing:
        print('')
        print(f'MISSING inputs: {len(missing)}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
