#!/usr/bin/env python3
"""PreToolUse hook: stop writes that cross the current review boundary.

Reads Claude Code hook JSON on stdin. Denies Write/Edit/MultiEdit/NotebookEdit
when the target is:
  - workflow-state.json (state may only be written by scripts/workflow.py),
  - an artifact declared as an output of a stage after the current stage,
  - an artifact declared by an already completed stage (unless it is explicitly
    volatile, e.g. machine-managed state or a generated index), or
  - an artifact of the current stage while its review is pending.

All other writes are allowed (no output, exit 0).
Deliberately conservative: unknown tools, missing state or unreadable contracts
are left to the normal permission system. Bash-driven writes are not intercepted.
"""
import json
import re
import sys
from pathlib import Path

PATH_TOKEN = re.compile(r'(?:docs|templates|openspec|workflow|prompts|scripts|design)/[A-Za-z0-9_\-./<>*]+')
FILE_TOKEN = re.compile(r'^[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{2,5}$')
DEFAULT_VOLATILE = {
    'workflow-state.json',
    'AGENTS.md',
    'docs/architecture/baseline-status.md',
    'docs/architecture/baseline-manifest.json',
    'docs/architecture/constraint-registry.json',
    'docs/product/BASELINE-INDEX.md',
    'docs/project/toolchain-report.md',
}


def deny(reason: str) -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))
    return 0


def norm(path: str) -> str:
    return str(path).replace('\\', '/').strip().rstrip('。.）)')


def declared_outputs(row, cid):
    paths = []
    for entry in row.get('outputs', []):
        text = str(entry)
        matches = list(PATH_TOKEN.finditer(text))
        if matches:
            for match in matches:
                path = match.group(0)
                if '<change-id>' in path:
                    path = path.replace('<change-id>', cid) if cid else path.split('<change-id>')[0] or 'openspec/changes/'
                paths.append(norm(path))
            continue
        token = text.strip().split()[0].strip('`（）(),')
        if FILE_TOKEN.match(token) and '/' not in token:
            paths.append(norm(token))
    return paths


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if payload.get('tool_name') not in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit'):
        return 0
    tool_input = payload.get('tool_input') or {}
    raw = tool_input.get('file_path') or tool_input.get('notebook_path') or ''
    if not raw:
        return 0

    root = Path(payload.get('cwd') or '.').resolve()
    state_path = root / 'workflow-state.json'
    if not state_path.is_file():
        return 0
    try:
        state = json.loads(state_path.read_text(encoding='utf-8'))
    except Exception:
        return deny('workflow-state.json 无法解析；在修复状态文件前禁止写入任何受治理产物。')

    target = Path(raw)
    target = (root / target).resolve() if not target.is_absolute() else target.resolve()
    try:
        rel = target.relative_to(root).as_posix()
    except ValueError:
        return 0

    if rel == 'workflow-state.json':
        return deny('workflow-state.json 只能由 scripts/workflow.py 命令写入；禁止直接编辑状态文件。')

    try:
        stages = json.loads((root / 'docs/WORKFLOW-STAGES.json').read_text(encoding='utf-8'))['stages']
        contract = json.loads((root / 'docs/STEP-ARTIFACT-CONTRACTS.json').read_text(encoding='utf-8'))
    except Exception:
        return 0
    order = [s['id'] for s in stages]
    current = state.get('current_step')
    if current not in order:
        return 0
    cid = state.get('active_change_id') or ''
    by_step = {str(row.get('step')): row for row in contract.get('steps', [])}
    volatile = set(DEFAULT_VOLATILE)
    volatile.update(norm(x) for x in (contract.get('handoff_policy') or {}).get('volatile_artifacts', []) if isinstance(x, str))
    completed = set(state.get('completed_steps') or [])
    pending_steps = {x.get('step_id') if isinstance(x, dict) else x for x in (state.get('pending_approvals') or [])}
    current_index = order.index(current)

    def matches(declared: str) -> bool:
        if declared.endswith('/'):
            return rel.startswith(declared)
        return rel == declared

    # 1. Never write a future stage's declared output ahead of its stage.
    future_only = set()
    for sid in order[current_index + 1:]:
        row = by_step.get(sid.split('-')[0])
        if row:
            future_only.update(declared_outputs(row, cid))
    if any(matches(path) for path in future_only):
        if pending_steps:
            waiting = ', '.join(str(x) for x in sorted(pending_steps))
            reason = f'阶段 {current} 处于待评审（{waiting}），禁止写入后续阶段产物：{rel}。'
        else:
            reason = f'阶段 {current} 尚未完成或尚未推进，禁止提前写入后续阶段产物：{rel}。'
        return deny(reason + ' 请先完成当前阶段并运行 workflow.py request-review，结束回合等待用户评审。')

    # 2. Approved stage artifacts are read-only until that stage is reopened.
    completed_outputs = set()
    for sid in order:
        if sid not in completed:
            continue
        row = by_step.get(sid.split('-')[0])
        if row:
            completed_outputs.update(declared_outputs(row, cid))
    if any(matches(path) for path in completed_outputs if path not in volatile):
        return deny(f'{rel} 属于已完成阶段 {current} 之前已批准的产物，不能直接改写；请先运行 workflow.py reopen --step <stage> --reason <reason> 并重新评审。')

    # 3. While a review is pending, the reviewed stage's artifacts are frozen.
    if current in pending_steps:
        current_outputs = set()
        row = by_step.get(current.split('-')[0])
        if row:
            current_outputs.update(declared_outputs(row, cid))
        if any(matches(path) for path in current_outputs if path not in volatile):
            return deny(f'阶段 {current} 正在等待用户评审，{rel} 已进入评审范围；如需修改，请先修改并重新运行 workflow.py request-review。')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
