# Prompt 01: Project Initialization and Toolchain Check

- Stage ID: `01-project-bootstrap` (project-level)
- Skill: `.claude/skills/project-bootstrap/SKILL.md`

## User Input
- Project goal: `<describe project goal>`
- Repository path / origin: `<repo path; greenfield or existing>`

## Entry Commands (Run First)
1. `python scripts/workflow.py check-entry --step 01-project-bootstrap`
2. `python scripts/agent-context.py --stage 01`

## Execution Rules
Follow `.claude/skills/project-bootstrap/SKILL.md` to inventory the repository/toolchain, initialize project-owned `AGENTS.md` sections (with user approval before modifying existing files), `workflow-state.json`, `docs/project/toolchain-report.md`, and initial `docs/architecture/baseline-status.md`.

## Mandatory Deliverable Handoff
- Write all declared outputs to disk, run `python scripts/check-package.py`, and generate `workflow/evidence/project/01-project-bootstrap.json`.
- Run `python scripts/workflow.py request-review --step 01-project-bootstrap --evidence workflow/evidence/project/01-project-bootstrap.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Under `standard` policy, run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves this stage. Under `risk-based` policy (`STATUS=RISK_BASED_FAST_TRACK`), `transition` may run after gates pass. Never edit `workflow-state.json` directly.
