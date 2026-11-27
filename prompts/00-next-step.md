# Prompt 00: Next-Step Workflow Orchestration

- Skill: `.claude/skills/workflow-orchestrator/SKILL.md`
- Scope: Project-level and feature-level (non-DAG orchestration entry point)

## User Input
- Current goal or target Change ID (optional): `<none / change-id>`

## Entry Commands (Run First)
1. `python scripts/next-step.py`
2. `python scripts/workflow.py list-changes`
3. Verify actual disk artifacts, approvals, and OpenSpec state (`openspec list`, `openspec list --specs` when initialized). Do not read full `STEP-ARTIFACT-CONTRACTS.md/.json` by default.

## Execution Rules
Follow `.claude/skills/workflow-orchestrator/SKILL.md` for all stage selection, multi-lane scheduling, and safety rules. Select **exactly one** safe next stage (or report the exact blocker) and print its `python scripts/agent-context.py --stage <NN> [--change <id>]` command.

## Mandatory Deliverable Handoff
- Before starting any selected stage, run `python scripts/workflow.py check-entry --step <step-id> [--change-id <id>]`.
- Stage completion is not approval: at stage end run checks, generate `workflow/evidence/<scope>/<step-id>.json`, run `python scripts/workflow.py request-review --step <step-id> [--change-id <id>] --evidence <path> --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn immediately.
- Run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves the pending stage (or when `risk-based` fast-track applies to a low-risk stage). Never edit `workflow-state.json` directly.
