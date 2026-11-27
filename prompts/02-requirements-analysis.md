# Prompt 02: Requirements Business Analysis

- Stage ID: `02-requirements-analysis` (project-level)
- Skill: `.claude/skills/requirements-analysis/SKILL.md`
- Required method skills: `brainstorming`, `internet-research`, `competitor-research` (`.claude/skills/competitor-research/SKILL.md`)
- Question coverage guide: `process/QUESTION-COVERAGE-CHECKLIST.md`

## User Input
- Business goals, users, roles, constraints, pain points, success criteria: `<provide materials>`
- Reference / same-category products (or `NONE + reason`): `<links / names / NONE + reason>`

## Entry Commands (Run First)
1. `python scripts/workflow.py check-entry --step 02-requirements-analysis`
2. `python scripts/agent-context.py --stage 02`

## Execution Rules
Follow `.claude/skills/requirements-analysis/SKILL.md` and `.claude/skills/competitor-research/SKILL.md` for discovery, target-platform inventory, business workflows (`FLOW`/`NODE`), data objects (`DO`), `RD` matrix, business rules (`BR`), reference research (with user-confirmed major deviations), and baseline brief/index generation. Use `process/QUESTION-COVERAGE-CHECKLIST.md` (`02-*`) to avoid blind spots.

## Mandatory Deliverable Handoff
- Write all declared outputs to disk and run: `python scripts/check-requirements.py --strict`, `python scripts/gen-baseline-index.py --check`, `python scripts/check-reference-research.py --strict`, and `python scripts/check-method-evidence.py --step 02-requirements-analysis --evidence workflow/evidence/project/02-requirements-analysis.json`.
- Run `python scripts/workflow.py request-review --step 02-requirements-analysis --evidence workflow/evidence/project/02-requirements-analysis.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves this stage. Never edit `workflow-state.json` directly.
