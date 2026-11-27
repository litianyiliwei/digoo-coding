---
name: implementation-orchestrator
description: Execute TDD implementation inside the declared Change slice, run verification/UI/static gates, and produce code review and footprint evidence.
---

# Stage 08: Implementation, TDD, Verification, and Code Review

## Role
Implement the approved Change strictly inside its declared `### Implementation Slice`, verify behavior/UI/static quality gates, and hand off clean, reviewable code and footprint evidence to the independent Verifier (Stage 09).

## Recommended Methods
- `test-driven-development` (red → green → refactor) is recommended (advisory); the hard outcome gate is that every row in `design/test-cases.csv` has passing automated tests.
- `verification-before-completion`: never claim pass without fresh command exit codes.

## Execution Flow

### Phase 1: Entry & Setup
1. `python scripts/workflow.py check-entry --step 08-implementation-orchestrator --change-id <change-id>`
2. `python scripts/baseline-governance.py check-change --change-id <change-id> --phase design`
3. `python scripts/agent-context.py --stage 08 --change <change-id>`
4. `python scripts/implementation-snapshot.py <change-id>` (records entry `implementation-base.json`)
5. `python scripts/code-context.py <change-id>` (when `strategy != none`, use `design/context-manifest.json` `read_set` as the recommended starting point; reading additional files outside `read_set` requires no extra logging—write boundaries are enforced by the footprint gate). Read `tasks.md`, `design.md` structure, and the `read_set` path list first; for multi-platform or multi-capability Changes, avoid preloading all stacks' source files and `figma-code/` into the main session up front—load full contents on demand per active work slice.
6. If `docs/architecture/quality-gates.json` exists and starter rule-pack configs are not yet materialized, copy them with explicit authorization as defined in Stage 03.

### Phase 2: Implement & Test
- **Optional Context Splitting (Self-Managed, Non-Gating)**: For small or single-platform Changes, execute directly in one session. When a Change spans multiple platforms/stacks or multiple heavy capabilities, you may autonomously split Phase 2 into scoped batches or sub-agents—prefer splitting by **platform/stack** first (e.g., backend/contracts first, then each client platform loading only `openapi.yaml` plus its own `figma-code/`, `figma-layout.csv`, `ui-actions.csv`, and `Owned paths`), and further by **capability** if a single platform is still large. No extra approvals or sub-stage gates are required; keep the main session focused on task coordination, conflict resolution, and unified Phase 3–4 convergence.
7. Execute tasks in `openspec/changes/<change-id>/tasks.md` (TDD recommended), keeping every modified file inside `Owned paths` ∪ `Integration paths` (`frozen_paths` require an approved BCR).
8. Implement every row in `api/openapi.yaml`, `design/api-io-mapping.csv`, `design/io-catalog.csv`, and `design/interface-catalog.csv` with corresponding automated tests from `design/test-cases.csv`.
9. For UI Changes: port `design/figma-code/PAGE-00N.<ext>` directly as the page skeleton, wiring routes/APIs/events from `design/ui-actions.csv` without rewriting styles, layout, or copy.
10. Update `- [x]` checkboxes in `tasks.md`. Create/update `<module_path>/MODULE.md` when creating a new module or changing a module's external contract; for minor internal edits, update at your discretion.

### Phase 3: Verify & Evidence
> Execution order and intermediate re-runs (such as running `run-quality-gates.py` during debugging) are AI-owned; final submission relies on fresh `verify-before-completion.sh` results and running `check-change-footprint.py` **after the last edit**.
11. Run the completion verification script (final pass):
    `STATIC_IDENTITY=<builder-id> bash scripts/verify-before-completion.sh <change-id> --test-dir <dir>`
12. For UI Changes, run:
    - `python scripts/check-figma-layout.py --change <change-id> --base-url <url>` → produces `design/evidence/figma-layout-check.json`
    - `python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>`
13. Write `openspec/changes/<change-id>/design/evidence/code-review.md` (using `templates/change-assets/evidence/code-review.md`; reference JSON paths and explain only differing/`UI-DERIVED` PAGEs; never use screenshots) and run `python scripts/check-code-review.py --change <change-id> --strict`.
14. Update implementation evidence in `design/baseline-binding.json` and run `python scripts/baseline-governance.py check-change --change-id <change-id> --phase implementation`.

### Phase 4: Freeze Footprint & Submit (Footprint Must Run After Last Edit)
15. Run `python scripts/check-change-footprint.py <change-id>` **after your final file edit** (produces `design/evidence/implementation-diff.json` matching the final tree).
16. Run `python scripts/check-method-evidence.py --step 08-implementation-orchestrator --evidence workflow/evidence/<change-id>/08-implementation-orchestrator.json`.

## Input/Output/Handoff Contract
- **Inputs**: Run `python scripts/agent-context.py --stage 08 --change <change-id>` plus `design/context-manifest.json` `read_set`.
- **Outputs**: Source code/migrations/tests, updated `tasks.md`, `<module_path>/MODULE.md` (when new module or external contract changes), `design/evidence/code-review.md`, `implementation-base.json`, `implementation-diff.json`, `design/context-manifest.json`, and conditional `figma-layout-check.json`, `static-analysis.json`, `static-analysis-logs/`.
- **Downstream Handoff**: Verified code revision, diff fingerprint, and Builder evidence for independent verification (Stage 09).
- **Review & Boundaries**:
  - Generate `workflow/evidence/<change-id>/08-implementation-orchestrator.json` and run:
    `python scripts/workflow.py request-review --step 08-implementation-orchestrator --change-id <change-id> --evidence workflow/evidence/<change-id>/08-implementation-orchestrator.json --summary "<summary>"`
  - Present `templates/workflow/step-handoff-report.md` and end the turn. Under `standard` policy, advance (`approve` → `transition`) only after explicit user approval; under `risk-based` policy (`STATUS=RISK_BASED_FAST_TRACK`), `transition` may run after all gates pass. Never run Stage 09 in the Builder session. Follow `AGENTS.md`.
