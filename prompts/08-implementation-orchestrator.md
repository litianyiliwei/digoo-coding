# Prompt 08: Implementation, TDD, Verification, and Code Review

- Stage ID: `08-implementation-orchestrator` (Change-scoped)
- Skill: `.claude/skills/implementation-orchestrator/SKILL.md`
- Required method skills: `test-driven-development`, `verification-before-completion`

## User Input
- Change ID: `<change-id>`
- Test directory / command scope: `<test-dir>`
- Running UI base URL (when UI is involved): `<url or N/A>`

## Entry Commands (Run First)
1. `python scripts/workflow.py check-entry --step 08-implementation-orchestrator --change-id <change-id>`
2. `python scripts/agent-context.py --stage 08 --change <change-id>`
3. `python scripts/implementation-snapshot.py <change-id>`
4. `python scripts/code-context.py <change-id>` (use `design/context-manifest.json` `read_set` as default code/contract read list)

## Execution Rules
Follow the 4-phase linear pipeline in `.claude/skills/implementation-orchestrator/SKILL.md` (Entry & Setup → Implement & TDD → Verify & Evidence → Freeze Footprint & Submit). Port `design/figma-code/` directly for UI pages without rewriting styles/layout/copy.

## Mandatory Deliverable Handoff
- After all code, tests, `tasks.md`, `MODULE.md`, `code-review.md`, and `baseline-binding.json` are written, run `STATIC_IDENTITY=<builder> bash scripts/verify-before-completion.sh <change-id> --test-dir <dir>`, UI checks (`check-figma-layout.py`, `check-design-tokens.py` if UI), `python scripts/check-code-review.py --change <change-id> --strict`, `baseline-governance.py check-change --phase implementation`, `check-change-footprint.py <change-id>`, and `check-method-evidence.py`.
- Run `python scripts/workflow.py request-review --step 08-implementation-orchestrator --change-id <change-id> --evidence workflow/evidence/<change-id>/08-implementation-orchestrator.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves this stage. Never run Stage 09 in the Builder session or edit `workflow-state.json` directly.
