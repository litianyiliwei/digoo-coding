---
name: detailed-design
description: Author unified detailed design, implementation slice, OpenAPI/IO/interface catalogs, UI action bindings, test cases, and traceability.
---

# Stage 07: Detailed Design, Interface, and Test Design

## Role
Produce the single unified `design.md` (using `templates/change-assets/design/design.md`), complete interface/API/IO/UI/test contracts, update design-phase baseline evidence, and declare the `### Implementation Slice` that governs Stage 08.

## Required Methods & Guidance
- Load `.claude/skills/existing-code-impact-analysis/SKILL.md` (`existing-code-impact-analysis`) when modifying existing code, and use `brainstorming` + `writing-plans`.
- Consult `process/QUESTION-COVERAGE-CHECKLIST.md` (`07-*`) for technical, contract, security, and failure-path blind spots.

## Execution Flow
1. **Entry**: Run `python scripts/workflow.py check-entry --step 07-detailed-design --change-id <change-id>` and `python scripts/agent-context.py --stage 07 --change <change-id>`.
2. **Unified `design.md`** (copy skeleton from `templates/change-assets/design/design.md`; keep reference-style—point to CSV/YAML by ID instead of duplicating full tables):
   - **`## Design Decisions`**: Fill `### Implementation Slice` (`Primary capability`, `Owner module`, `Related modules`, `Slice type/coverage`, `Code packages`, `Owned paths`, `Integration paths`, `Module card`; optional `Frozen approvals`, `Out of context`) and `### Existing Code Change Impact` (via `existing-code-impact-analysis` or `N/A + reason`).
   - **`## Interface Design`**: Reference `api/openapi.yaml` (`x-api-scope: none` when no HTTP API) and `design/interface-catalog.csv` (cross-boundary interfaces; avoid duplicating internal DB/cache calls already in `io-catalog.csv`).
   - **`## Frontend Detailed Design`** (or `N/A + reason`):
     - Finalize `route` and `dom_selector` in `design/figma-layout.csv` (keep geometry/text/font faithful to Stage 06).
     - Create `design/ui-actions.csv` mapping every functional control to `navigate` (route + `route_params`), `api` (`operationId` in `openapi.yaml`), `local-ui` (pure presentation state such as expand/collapse, tab switch, dialog toggle, or local sort/filter — record reason in `notes`, no user approval needed), or user-confirmed `local-only` (business meaning without navigation/API, with `approver` + `confirmed_at`).
     - Reference real `element_id` values from `design/ui-actions.csv` in `### Event Handling`. Never redesign styles/layout/copy; routine states (loading/empty/error/toast/skeleton) may be filled with project tokens and recorded as `UI-DERIVED (routine)` without approver, while non-routine `UI-DERIVED` / `UI-DEVIATION` items still require an approver.
   - **`## Backend Detailed Design`** (or `N/A + reason`):
     - When APIs exist, author `api/openapi.yaml`, `design/api-io-mapping.csv` (every `operationId` → ≥ 1 real IO), and `design/io-catalog.csv` (contracts, timeouts, retries, idempotency, errors).
   - **`## Test Design`**:
     - Author `design/test-cases.csv` (every AC/PAGE/operationId/IO/interface → ≥ 1 `TEST` ID; failure injection & test doubles explicit).
     - Include `### Static Analysis` referencing `docs/architecture/quality-gates.json` (or `N/A + reason`) and `design/static-waivers.json` (only when approved Change-scoped waivers are needed).
3. **Traceability & Baseline Evidence**:
   - Build `openspec/changes/<change-id>/traceability.csv` (single traceability aggregate; use `scripts/gen-traceability.py` if available or verify closure).
   - Update `design/baseline-impact.md` (design review conclusion `NO_IMPACT`/`REBASE_REQUIRED`) and write design evidence per constraint in `design/baseline-binding.json`.
   - Refine `tasks.md` with small, verifiable `- [ ]` tasks aligned to the slice.
4. **Stage-End Gates**:
   - `bash scripts/check-design-assets.sh <change-id>`
   - `python scripts/check-design-sections.py --change <change-id>`
   - UI (when applicable): `python scripts/check-ui-actions.py --change <change-id> --strict`
   - API/Interface (when applicable): `bash scripts/validate-openapi.sh openspec/changes/<change-id>/api/openapi.yaml`, `python scripts/check-api-io-mapping.py openspec/changes/<change-id>/api/openapi.yaml openspec/changes/<change-id>/design/api-io-mapping.csv openspec/changes/<change-id>/design/io-catalog.csv`, `python scripts/check-interface-catalog.py --change <change-id> --strict`
   - Tests & Traceability: `python scripts/check-test-cases.py --change <change-id>`, `python scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict`, `python scripts/check-api-traceability.py --change <change-id> --strict`
   - Baseline & Slice: `python scripts/check-baseline-impact.py <change-id> --strict`, `python scripts/baseline-governance.py check-change --change-id <change-id> --phase design`, `python scripts/check-change-footprint.py <change-id> --declaration-only`
   - Method evidence: `python scripts/check-method-evidence.py --step 07-detailed-design --evidence workflow/evidence/<change-id>/07-detailed-design.json`

## Input/Output/Handoff Contract
- **Inputs**: Run `python scripts/agent-context.py --stage 07 --change <change-id>` for the lean read set.
- **Outputs**: `design.md`, `design/figma-layout.csv` (completed), `design/ui-actions.csv`, `design/baseline-impact.md`, `design/baseline-binding.json`, `design/test-cases.csv`, `traceability.csv`, and conditional `api/openapi.yaml`, `design/api-io-mapping.csv`, `design/io-catalog.csv`, `design/interface-catalog.csv`, `design/static-waivers.json`.
- **Downstream Handoff**: Approved detailed design, contracts, implementation slice declaration, and test matrix for Stage 08 (07→08 transition acquires the implementation lease).
- **Review & Boundaries**:
  - Generate `workflow/evidence/<change-id>/07-detailed-design.json` and run:
    `python scripts/workflow.py request-review --step 07-detailed-design --change-id <change-id> --evidence workflow/evidence/<change-id>/07-detailed-design.json --summary "<summary>"`
  - Present `templates/workflow/step-handoff-report.md` and end the turn. Advance (`approve` → `transition`) only after explicit user approval. Follow `AGENTS.md`.
