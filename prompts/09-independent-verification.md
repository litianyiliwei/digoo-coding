# Prompt 09: Independent Verification and Acceptance Evidence

- Stage ID: `09-independent-verification` (Change-scoped, read-only independent Verifier)
- Skill: `.claude/skills/independent-verifier/SKILL.md`
- Required method skills: `verification-before-completion`

## User Input

- Change ID: `<change-id>`
- Test directory / running UI base URL (if UI): `<test-dir / url>`

## Entry Commands (Run First)

1. `python scripts/workflow.py check-entry --step 09-independent-verification --change-id <change-id>`
2. `python scripts/agent-context.py --stage 09 --change <change-id>`

## Execution Rules

Follow `.claude/skills/independent-verifier/SKILL.md` in an independent read-only context (distinct from the Builder). Never modify business code or `baseline-binding.json`. Independently re-run tests, static analysis (`--independent`), UI checks (`independent-figma-layout-check.json` + `check-design-tokens.py`), and `check-change-footprint.py <change-id> --verify`, and output `independent-verification-report.md` and `independent-verification.json`.

## Mandatory Deliverable Handoff

- Write all declared outputs to disk and run: `python scripts/check-independent-verification.py --report openspec/changes/<change-id>/design/evidence/independent-verification-report.md --evidence openspec/changes/<change-id>/design/evidence/independent-verification.json`, `python scripts/check-static-analysis.py --change <change-id> --expect-independent` (when quality gates exist), and `python scripts/check-method-evidence.py --step 09-independent-verification --evidence workflow/evidence/<change-id>/09-independent-verification.json`.
- Run `python scripts/workflow.py request-review --step 09-independent-verification --change-id <change-id> --evidence workflow/evidence/<change-id>/09-independent-verification.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves this stage (only `PASS` may enter Stage 10). Never edit `workflow-state.json` directly.
