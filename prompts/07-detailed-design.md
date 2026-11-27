# Prompt 07: Detailed Design, Interface, and Test Design

- Stage ID: `07-detailed-design` (Change-scoped)
- Skill: `.claude/skills/detailed-design/SKILL.md`
- Required method skills: `brainstorming`, `writing-plans`, `existing-code-impact-analysis` (`.claude/skills/existing-code-impact-analysis/SKILL.md`)
- Question coverage guide: `process/QUESTION-COVERAGE-CHECKLIST.md`

## User Input
- Change ID: `<change-id>`
- Existing code paths (if modifying existing functionality): `<paths or N/A>`
- Third-party interfaces for this Change (if any): `<list or N/A>`

## Entry Commands (Run First)
1. `python scripts/workflow.py check-entry --step 07-detailed-design --change-id <change-id>`
2. `python scripts/agent-context.py --stage 07 --change <change-id>`

## Execution Rules
Follow `.claude/skills/detailed-design/SKILL.md` (using `templates/change-assets/design/design.md` as the skeleton) and `.claude/skills/existing-code-impact-analysis/SKILL.md` to produce `design.md` (including `### Implementation Slice`), API/IO/interface contracts, UI bindings (`figma-layout.csv`, `ui-actions.csv`), `test-cases.csv`, `traceability.csv`, and design evidence in `baseline-impact.md` / `baseline-binding.json`. Use `process/QUESTION-COVERAGE-CHECKLIST.md` (`07-*`) as guidance.

## Mandatory Deliverable Handoff
- Write all declared outputs to disk and run all applicable gates (`bash scripts/check-design-assets.sh <change-id>`, `check-design-sections.py`, `check-ui-actions.py`, `check-api-io-mapping.py`, `check-interface-catalog.py`, `check-test-cases.py`, `check-traceability.py`, `check-baseline-impact.py --strict`, `baseline-governance.py check-change --phase design`, `check-change-footprint.py --declaration-only`, `check-method-evidence.py`).
- Run `python scripts/workflow.py request-review --step 07-detailed-design --change-id <change-id> --evidence workflow/evidence/<change-id>/07-detailed-design.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves this stage (07→08 acquires the implementation lease). Never edit `workflow-state.json` directly.
