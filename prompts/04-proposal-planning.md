# Prompt 04: Proposal Breakdown, Dependency Ordering, and Roadmap

- Stage ID: `04-proposal-planning` (project-level to feature-level)
- Skill: `.claude/skills/proposal-planning/SKILL.md`
- Required method skills: `brainstorming`

## User Input
- Delivery priorities, milestone constraints, or known technical debt: `<optional>`

## Entry Commands (Run First)
1. `python scripts/workflow.py check-entry --step 04-proposal-planning`
2. `python scripts/agent-context.py --stage 04`

## Execution Rules
Follow `.claude/skills/proposal-planning/SKILL.md` to slice the project into independently deliverable Changes, establish the dependency DAG and target platforms in `docs/product/proposal-roadmap.md`, and initialize `docs/product/capabilities.csv` and `docs/product/modules.csv`.

## Mandatory Deliverable Handoff
- Write all declared outputs to disk and run: `python scripts/check-capabilities.py`, `python scripts/check-modules.py`, `python scripts/check-roadmap.py --strict`, and `python scripts/check-method-evidence.py --step 04-proposal-planning --evidence workflow/evidence/project/04-proposal-planning.json`.
- Run `python scripts/workflow.py request-review --step 04-proposal-planning --evidence workflow/evidence/project/04-proposal-planning.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Under `standard` policy, run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves this stage. Under `risk-based` policy (`STATUS=RISK_BASED_FAST_TRACK`), `transition` may run after gates pass. Never edit `workflow-state.json` directly.
