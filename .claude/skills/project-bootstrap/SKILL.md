---
name: project-bootstrap
description: Initialize a project repository's workflow state, AGENTS.md project sections, toolchain report, and initial baseline status.
---

# Stage 01: Project Bootstrap and Toolchain Check

## Role
Inventory the repository and local toolchain, then initialize project-level governance files so Stage 02 can begin cleanly.

## Execution Flow
1. Run `python scripts/workflow.py check-entry --step 01-project-bootstrap` and `python scripts/agent-context.py --stage 01`.
2. Inspect the repository directory layout, git state, installed CLIs (`python`, `node`/`npm`/`pnpm`, `git`, `openspec`, `playwright`/headless browser, language runtimes), and existing `AGENTS.md`.
3. Ask for explicit user approval before modifying any existing `AGENTS.md` or repository configuration.
4. Create or update the declared outputs:
   - `AGENTS.md`: project-owned sections only (Goal, project conventions). Never edit inside `<!-- toolkit:begin -->` … `<!-- toolkit:end -->`.
   - `workflow-state.json`: initialized via `scripts/workflow.py` (never hand-edited).
   - `docs/project/toolchain-report.md` (from `templates/project-baseline/toolchain-report.md`): record actual versions, commands, exit codes, and real blockers; replace `PENDING` with `N/A + reason` for unused stacks.
   - `docs/architecture/baseline-status.md` (from `templates/project-baseline/baseline-status.md`): initial `DRAFT` baseline status register.
5. Run `python scripts/check-package.py` and verify all outputs exist on disk.

## Input/Output/Handoff Contract
- **Inputs**: User-provided project goal and repository location; existing repository layout/config/`AGENTS.md` (if present).
- **Outputs**: `AGENTS.md` (project-owned sections), `workflow-state.json`, `docs/project/toolchain-report.md`, `docs/architecture/baseline-status.md`.
- **Downstream Handoff**: Repository conventions, toolchain report, and initialized `workflow-state.json` for Stage 02.
- **Review & Boundaries**:
  - Generate `workflow/evidence/project/01-project-bootstrap.json` and run:
    `python scripts/workflow.py request-review --step 01-project-bootstrap --evidence workflow/evidence/project/01-project-bootstrap.json --summary "<summary>"`
  - Present `templates/workflow/step-handoff-report.md` and end the turn.
  - Under `standard` policy, run `approve` and `transition` only after explicit user approval. Under `risk-based` policy (`STATUS=RISK_BASED_FAST_TRACK`), `transition` may run after gates pass. Follow `AGENTS.md` for all other boundary rules.
