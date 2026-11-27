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
CONTRACTS = ROOT / 'process/STEP-ARTIFACT-CONTRACTS.json'

RESIDENT = {
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
    '10': [
        'docs/product/BASELINE-BRIEF.md',
        'docs/product/change-sizing.md',
        'docs/product/lessons.md',
        'docs/product/acceptance-policy.md',
    ],
}

PATH_RE = re.compile(r'(?:docs|openspec|scripts|prompts|templates|workflow|\.claude)/[A-Za-z0-9_\-./<>*#]+')


def load_stage(stage):
    data = json.loads(CONTRACTS.read_text(encoding='utf-8'))
    for row in data.get('steps', []):
        if row.get('step', '').lstrip('0') == stage.lstrip('0'):
            return row
    return None


def check_path(raw, change_id):
    token = raw.split('#', 1)[0].rstrip('。，、；:：)')
    if token.startswith('design/') or token.startswith('specs/'):
        return token, None
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
    root_arg = None
    while args:
        arg = args.pop(0)
        if arg == '--stage' and args:
            stage = args.pop(0)
        elif arg == '--change' and args:
            change_id = args.pop(0)
        elif arg == '--root' and args:
            root_arg = args.pop(0)
        elif arg == '--full':
            pass
        else:
            print(f'Unknown argument: {arg}', file=sys.stderr)
            sys.exit(2)
    if not stage:
        print('Usage: agent-context.py --stage <02|05> [--change <change-id>] [--full] [--root <dir>]', file=sys.stderr)
        sys.exit(2)
    global ROOT, CONTRACTS
    if root_arg:
        ROOT = Path(root_arg).resolve()
        CONTRACTS = ROOT / 'process/STEP-ARTIFACT-CONTRACTS.json'
    row = load_stage(stage.split('-')[0])
    if not row:
        print(f'Unknown stage: {stage}', file=sys.stderr)
        sys.exit(2)

    contract = json.loads(CONTRACTS.read_text(encoding='utf-8'))
    profile = (contract.get('input_policy') or {}).get('stage_profiles', {}).get(row['step'])
    full = '--full' in sys.argv
    missing = []

    print(f'# Agent Context Bundle: {row["step"]} {row["title"]}')
    print(f'- Skill: `{row["skill"]}`')
    print(f'- Scope: {row.get("scope", "—")}')
    print('')

    if profile:
        lean = profile.get('lean') or []
        max_files = profile.get('max_files', 8)
        print('## 0. Lean inputs (default reads, within budget)')
        for item in lean:
            print(f'- {item}')
            optional = bool(re.search(r'\b(?:if|when) present\b', str(item), re.I))
            for raw in PATH_RE.findall(str(item)):
                token, exists = check_path(raw, change_id)
                if exists is False:
                    if optional:
                        print(f'  - `{token}` [OPTIONAL; absent]')
                    else:
                        missing.append(token)
                        print(f'  - `{token}` [MISSING]')
                elif exists is True:
                    print(f'  - `{token}` [OK]')
        print(f'- Budget (advisory): {len(lean)}/{max_files} lean read groups; if exceeded, narrow the scope or record why the extra reads are needed.')
        if len(lean) > max_files:
            print(f'CONTEXT_BUDGET_WARNING: lean {len(lean)} > advisory max_files {max_files}; over-budget is advisory, not a gate.')
        print('')
        print('## 1. On-demand inputs (read only after a trigger; not counted in the default budget)')
        for item in profile.get('on_demand') or []:
            print(f'- {item}')
        print('')
        if full:
            print('## 2. Full contract inputs (for audit)')
            for item in row.get('inputs', []):
                print(f'- {item}')
            print('')
        else:
            print('## 2. Full contract inputs (audit-only; not read by default; add --full when needed)')
            print(f'- {len(row.get("inputs", []))} items; read the lean/on-demand lists above by default.')
            print('')
    else:
        print('## 0. Resident reads (read first)')
        for path in RESIDENT.get(row['step'].lstrip('0'), []):
            token, exists = check_path(path, change_id)
            print(f'- `{token}` [{"OK" if exists else "MISSING"}]')
            if exists is False:
                missing.append(token)
        print('')
        print('## 1. Contract inputs')
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

    print('## 3. Contract outputs')
    for item in row.get('outputs', []):
        print(f'- {item.replace("<change-id>", change_id or "<change-id>")}')

    print('')
    print('## 4. Gates')
    print(row.get('gate', '—'))
    print('')
    print('## 5. Approval and next-stage inputs')
    print(f'- Approval: {row.get("approval", "—")}')
    for item in row.get('next_inputs', []):
        print(f'- {item}')

    if missing:
        print('')
        print(f'MISSING inputs: {len(missing)}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
