# Prompt 08: Implementation, TDD, Verification, and Code Review

- Stage ID: `08-implementation-orchestrator` (Change-scoped)
- Skill: `.claude/skills/implementation-orchestrator/SKILL.md`
- Recommended method skills (advisory): `test-driven-development`, `verification-before-completion`

## User Input
- Change ID: `<change-id>`
- Test directory / command scope: `<test-dir>`
- Running UI base URL (when UI is involved): `<url or N/A>`

## Entry Commands (Run First)
1. `python scripts/workflow.py check-entry --step 08-implementation-orchestrator --change-id <change-id>`
2. `python scripts/agent-context.py --stage 08 --change <change-id>`
3. `python scripts/implementation-snapshot.py <change-id>`
4. `python scripts/code-context.py <change-id>` (use `design/context-manifest.json` `read_set` as recommended starting point)

## Execution Rules
Follow `.claude/skills/implementation-orchestrator/SKILL.md` (Entry & Setup → Implement & Test → Verify & Evidence → Freeze Footprint & Submit; `check-change-footprint.py` must run after the last edit). Read `tasks.md`, `design.md` structure, and the `context-manifest.json` `read_set` path list first; for multi-platform or multi-capability Changes, you may autonomously split Phase 2 into scoped batches or sub-agents (by platform/stack, and by capability when needed) instead of preloading all stacks into one context, then converge in the main session for Phase 3–4 verification and footprint freeze. Port `design/figma-code/` directly for UI pages without rewriting styles/layout/copy.

## Mandatory Deliverable Handoff
- After all code, tests, `tasks.md`, `MODULE.md` (when new module or external contract changes), `code-review.md`, and `baseline-binding.json` are written, run `STATIC_IDENTITY=<builder> bash scripts/verify-before-completion.sh <change-id> --test-dir <dir>`, UI checks (`check-figma-layout.py`, `check-design-tokens.py` if UI), `python scripts/check-code-review.py --change <change-id> --strict`, `baseline-governance.py check-change --phase implementation`, `check-change-footprint.py <change-id>`, and `check-method-evidence.py`.
- Run `python scripts/workflow.py request-review --step 08-implementation-orchestrator --change-id <change-id> --evidence workflow/evidence/<change-id>/08-implementation-orchestrator.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Under `standard` policy, run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves this stage; under `risk-based` policy (`STATUS=RISK_BASED_FAST_TRACK`), `transition` may run after all gates pass. Never run Stage 09 in the Builder session or edit `workflow-state.json` directly.
