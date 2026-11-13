#!/usr/bin/env python3
"""PreToolUse hook: stop writes that cross the current review boundary.

Reads Claude Code hook JSON on stdin. Denies Write/Edit/MultiEdit/NotebookEdit
when the target is:
  - workflow-state.json (state may only be written by scripts/workflow.py), or
  - an artifact declared as an output of a stage after the current stage while
    a review request is pending.
All other writes are allowed (no output, exit 0).

Deliberately conservative: unknown tools, missing state, unreadable contracts
and paths outside the project are left to the normal permission system.
"""
import json
import re
import sys
from pathlib import Path

PATH_TOKEN = re.compile(r'(?:docs|templates|openspec|workflow|prompts|scripts|design)/[A-Za-z0-9_\-./<>*]+')


def deny(reason: str) -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))
    return 0


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
    try:
        state = json.loads((root / 'workflow-state.json').read_text(encoding='utf-8'))
    except Exception:
        return 0

    target = Path(raw)
    target = (root / target).resolve() if not target.is_absolute() else target.resolve()
    try:
        rel = target.relative_to(root).as_posix()
    except ValueError:
        return 0

    if rel == 'workflow-state.json':
        return deny('workflow-state.json 只能由 scripts/workflow.py 命令写入；禁止直接编辑状态文件。')

    pending = state.get('pending_approvals') or []
    current = state.get('current_step')
    try:
        stages = json.loads((root / 'docs/WORKFLOW-STAGES.json').read_text(encoding='utf-8'))['stages']
        contracts = json.loads((root / 'docs/STEP-ARTIFACT-CONTRACTS.json').read_text(encoding='utf-8'))['steps']
    except Exception:
        return 0
    order = [s['id'] for s in stages]
    if current not in order:
        return 0

    cid = state.get('active_change_id') or ''
    by_step = {str(row.get('step')): row for row in contracts}

    def declared_outputs(sid):
        row = by_step.get(sid.split('-')[0])
        if not row:
            return []
        paths = []
        for entry in row.get('outputs', []):
            match = PATH_TOKEN.search(str(entry))
            if not match:
                continue
            path = match.group(0)
            if '<change-id>' in path:
                if cid:
                    path = path.replace('<change-id>', cid)
                else:
                    # No active change yet: block the whole Change workspace.
                    path = path.split('<change-id>')[0] or 'openspec/changes/'
            paths.append(path)
        return paths

    current_index = order.index(current)
    allowed = {path for sid in order[:current_index + 1] for path in declared_outputs(sid)}
    future_only = {path for sid in order[current_index + 1:] for path in declared_outputs(sid)} - allowed

    def matches(declared: str) -> bool:
        if declared.endswith('/'):
            return rel.startswith(declared)
        return rel == declared

    if any(matches(path) for path in future_only):
        if pending:
            waiting = ', '.join(str(item.get('step_id') if isinstance(item, dict) else item) for item in pending)
            reason = f'阶段 {current} 处于待评审（{waiting}），禁止写入后续阶段产物：{rel}。'
        else:
            reason = f'阶段 {current} 尚未完成或尚未推进，禁止提前写入后续阶段产物：{rel}。'
        return deny(
            reason
            + f'请先完成当前阶段并运行 workflow.py request-review，结束回合等待用户评审；'
            f'只有用户明确回复“评审通过 {current}”、运行 approve 与 transition 后，下一阶段产物才可写入。'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
