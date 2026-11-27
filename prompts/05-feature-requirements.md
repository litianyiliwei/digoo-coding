# Prompt 05: Proposal-Level Requirements Analysis

- Stage ID: `05-feature-requirements` (Change-scoped)
- Skill: `.claude/skills/feature-requirements/SKILL.md`
- Required method skills: `brainstorming`, `baseline-impact-classification` (`.claude/skills/baseline-impact-classification/SKILL.md`)
- Question coverage guide: `process/QUESTION-COVERAGE-CHECKLIST.md`

## User Input
- Change ID: `<change-id>`
- Additional business scope or constraints for this Change: `<optional>`

## Entry Commands (Run First)
1. If not started yet: `python scripts/workflow.py start-change --change-id <change-id>`
2. `python scripts/workflow.py check-entry --step 05-feature-requirements --change-id <change-id>`
3. `python scripts/agent-context.py --stage 05 --change <change-id>`

## Execution Rules
Follow `.claude/skills/feature-requirements/SKILL.md` and `.claude/skills/baseline-impact-classification/SKILL.md` to create `proposal.md`, delta `specs/<capability>/spec.md`, initial `tasks.md`, `design/user-stories.md`, `design/baseline-impact.md`, and `design/baseline-binding.json` (do **not** create `design.md` here), and update `capabilities.csv` / `modules.csv` (plus `proposal-roadmap.md` amendment if off-roadmap). Use `process/QUESTION-COVERAGE-CHECKLIST.md` (`05-*`) as guidance.

## Mandatory Deliverable Handoff
- Write all declared outputs to disk and run: `python scripts/check-requirements.py --change <change-id> --strict`, `openspec validate <change-id> --strict`, `python scripts/check-capabilities.py`, `python scripts/check-modules.py`, `python scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`, and `python scripts/check-method-evidence.py --step 05-feature-requirements --evidence workflow/evidence/<change-id>/05-feature-requirements.json`.
- Run `python scripts/workflow.py request-review --step 05-feature-requirements --change-id <change-id> --evidence workflow/evidence/<change-id>/05-feature-requirements.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves this stage. Never edit `workflow-state.json` directly.
