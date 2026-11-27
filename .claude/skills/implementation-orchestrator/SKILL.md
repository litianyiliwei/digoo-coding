---
name: implementation-orchestrator
description: Execute TDD implementation inside the declared Change slice, run verification/UI/static gates, and produce code review and footprint evidence.
---

# Stage 08: Implementation, TDD, Verification, and Code Review

## Role
Implement the approved Change strictly inside its declared `### Implementation Slice`, verify behavior/UI/static quality gates, and hand off clean, reviewable code and footprint evidence to the independent Verifier (Stage 09).

## Required Methods
- Use `test-driven-development` (red → green → refactor) and `verification-before-completion` (never claim pass without fresh command exit codes).

## Execution Flow (4-Phase Linear Pipeline)

### Phase 1: Entry & Setup
1. `python scripts/workflow.py check-entry --step 08-implementation-orchestrator --change-id <change-id>`
2. `python scripts/baseline-governance.py check-change --change-id <change-id> --phase design`
3. `python scripts/agent-context.py --stage 08 --change <change-id>`
4. `python scripts/implementation-snapshot.py <change-id>` (records entry `implementation-base.json`)
5. `python scripts/code-context.py <change-id>` (when `strategy != none`, use `design/context-manifest.json` `read_set` as the default read list; log any justified extra read as `CONTEXT_EXPANSION`).
6. If `docs/architecture/quality-gates.json` exists and starter rule-pack configs are not yet materialized, copy them with explicit authorization as defined in Stage 03.

### Phase 2: Implement & TDD
7. Execute tasks in `openspec/changes/<change-id>/tasks.md` using TDD, keeping every modified file inside `Owned paths` ∪ `Integration paths` (`frozen_paths` require an approved BCR).
8. Implement every row in `api/openapi.yaml`, `design/api-io-mapping.csv`, `design/io-catalog.csv`, and `design/interface-catalog.csv` with corresponding automated tests from `design/test-cases.csv`.
9. For UI Changes: port `design/figma-code/PAGE-00N.<ext>` directly as the page skeleton, wiring routes/APIs/events from `design/ui-actions.csv` without rewriting styles, layout, or copy.
10. Update `- [x]` checkboxes in `tasks.md` and create/update `<module_path>/MODULE.md` cards for touched modules.

### Phase 3: Verify & Evidence (Fixed Order)
11. Run the unified completion script once (do **not** manually re-run `run-quality-gates.py` separately, as `verify-before-completion.sh` runs it and uses `STATIC_IDENTITY`):
    `STATIC_IDENTITY=<builder-id> bash scripts/verify-before-completion.sh <change-id> --test-dir <dir>`
12. For UI Changes, run:
    - `python scripts/check-figma-layout.py --change <change-id> --base-url <url>` → produces `design/evidence/figma-layout-check.json`
    - `python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>`
13. Write `openspec/changes/<change-id>/design/evidence/code-review.md` (using `templates/change-assets/evidence/code-review.md`; reference JSON paths and explain only differing/`UI-DERIVED` PAGEs; never use screenshots) and run `python scripts/check-code-review.py --change <change-id> --strict`.
14. Update implementation evidence in `design/baseline-binding.json` and run `python scripts/baseline-governance.py check-change --change-id <change-id> --phase implementation`.

### Phase 4: Freeze Footprint & Submit (Run Last After All Edits)
15. Run `python scripts/check-change-footprint.py <change-id>` (produces `design/evidence/implementation-diff.json` matching the final tree).
16. Run `python scripts/check-method-evidence.py --step 08-implementation-orchestrator --evidence workflow/evidence/<change-id>/08-implementation-orchestrator.json`.

## Input/Output/Handoff Contract
- **Inputs**: Run `python scripts/agent-context.py --stage 08 --change <change-id>` plus `design/context-manifest.json` `read_set`.
- **Outputs**: Source code/migrations/tests, updated `tasks.md`, `<module_path>/MODULE.md`, `design/evidence/code-review.md`, `implementation-base.json`, `implementation-diff.json`, `design/context-manifest.json`, and conditional `figma-layout-check.json`, `static-analysis.json`, `static-analysis-logs/`.
- **Downstream Handoff**: Verified code revision, diff fingerprint, and Builder evidence for independent verification (Stage 09).
- **Review & Boundaries**:
  - Generate `workflow/evidence/<change-id>/08-implementation-orchestrator.json` and run:
    `python scripts/workflow.py request-review --step 08-implementation-orchestrator --change-id <change-id> --evidence workflow/evidence/<change-id>/08-implementation-orchestrator.json --summary "<summary>"`
  - Present `templates/workflow/step-handoff-report.md` and end the turn. Advance (`approve` → `transition`) only after explicit user approval. Never run Stage 09 in the Builder session. Follow `AGENTS.md`.
