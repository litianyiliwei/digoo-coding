# Unified Detailed Design

- Change ID: `<change-id>`
- Status: DRAFT
- Source baseline: `docs/architecture/baseline-status.md` (`vX.Y.Z`), `openspec/changes/<change-id>/design/user-stories.md`
- Related US / AC / FLOW / BR / PAGE: `<IDs>`
- Generated date/version: `<YYYY-MM-DD>`

> Keep this file concise and reference-style: point to `openapi.yaml`, `figma-audit.md`, `figma-layout.csv`, `ui-actions.csv`, `api-io-mapping.csv`, `io-catalog.csv`, `interface-catalog.csv`, `test-cases.csv`, and `traceability.csv` by ID instead of duplicating full tables. Write `N/A + reason` for inapplicable sections.

## Design Decisions

### Implementation Slice
- Primary capability: `<capability_slug>`
- Owner module: `<module_slug>`
- Related modules: `<module_slugs or N/A + reason>`
- Slice type/coverage: `<initial|extend> / <partial|full>`
- Code packages: `<package paths>`
- Owned paths: `<glob/paths>`
- Integration paths: `<paths or N/A + reason>`
- Module card: `<create|update> <module_path>/MODULE.md`

### Scope and Non-Goals
- In scope: `<...>`
- Non-goals: `<...>`

### Key Decisions and Trade-offs
- `<Decision, rationale, alternatives rejected, and baseline constraint IDs>`

### Existing Code Change Impact
> Load `.claude/skills/existing-code-impact-analysis/SKILL.md` when modifying existing code; write `N/A + reason` for greenfield features.
- Affected modules/files, compatibility/migration impact, and rollback notes: `<...>`

### Design Task Breakdown and Interface Scope
- Summary of implementation tasks (synced to `tasks.md`) and cross-boundary interface scope.

### Design Gaps and Entry Conclusion
- Blocking gaps: `<none or Q-xxx>`
- Entry conclusion for Stage 08: `<READY / BLOCKED>`

## Interface Design

### Interface Inventory
- Reference `api/openapi.yaml` (`x-api-scope: none` if no HTTP API).

### Interface Boundary Inventory
- Reference `design/interface-catalog.csv` (or `N/A + reason` if no cross-boundary interfaces).

### Contracts and Error Semantics
- Auth, error mapping, idempotency, timeout/retry conventions (referencing `docs/architecture/api-conventions.md`).

### Interface Traceability
- Reference `traceability.csv` linking `AC → operationId / interface_id → TEST`.

## Frontend Detailed Design

> Write `N/A + reason` for no-UI Changes. For UI Changes, keep `figma-layout.csv`, `check-figma-layout.py`, `ui-actions.csv`, and `check-ui-actions.py` referenced explicitly.

### Routing and Component Tree
- Routes per declared platform and component hierarchy derived from `design/figma-code/`.

### Design Tokens and Implementation Mapping
- Token → CSS variable / component library theme mapping (referencing `design/figma-audit.md` and `docs/architecture/frontend-conventions.md`).

### PAGE→BLOCK→Figma Specifications
- Reference `design/figma-audit.md` and `design/figma-layout.csv`; list only `UI-DEVIATION` or `UI-DERIVED` notes with approver.

### PAGE→BLOCK→Component Mapping
- Map each `PAGE-00N` in `design/figma-code/` to target runtime component paths and business adapters.

### Component Responsibilities and States
- Local/server state ownership and component responsibilities.

### Event Handling
- Handler behavior notes referencing `design/ui-actions.csv` by `element_id`; verified by `python scripts/check-ui-actions.py --change <change-id> --strict`.

### State Coverage
- Default, loading, empty, error, permission-denied, and platform-specific states (consistent with `design/figma-audit.md`).

### Test Mapping
- Reference `design/test-cases.csv` for frontend unit/component/e2e coverage.

### Responsive and Viewport Rules
- Per-platform viewports and breakpoints matching `design/figma-layout.csv`.

### Page Geometry and Fidelity Assertions
- Runtime geometry/text/font assertions executed via `python scripts/check-figma-layout.py --change <change-id> --base-url <url>` against `design/figma-layout.csv` and `python scripts/check-design-tokens.py`.

## Backend Detailed Design

> Write `N/A + reason` when the Change has no backend work.

### API Execution Chain
- Request validation → authz → domain service → persistence/external calls → response mapping.

### API→IO Mapping
- Reference `design/api-io-mapping.csv` (every OpenAPI `operationId` maps to ≥ 1 real IO ID).

### IO Contracts
- Reference `design/io-catalog.csv` (transaction boundaries, timeouts, retries, idempotency, error mapping).

### Data Model and Migration
- Physical schema changes, indexes, backward-compatible migration and rollback plan.

### Non-Database IO
- Cache, MQ, object storage, third-party HTTP/RPC calls (or `N/A + reason`).

### Domain Types and Methods
- Core domain types, invariants, and service entry points.

### Errors and Consistency
- Transaction scope, compensation, concurrency control, and failure paths.

### Shared Concerns
- Auth, audit logging, metrics/tracing, rate limiting, and privacy/masking.

### Test Coverage
- Reference `design/test-cases.csv` for unit/integration/contract/failure-injection tests.

### Open Decisions
- Unresolved technical questions (`none` or `Q-xxx` in `docs/product/open-questions.md`).

## Test Design

### Test Strategy
- Unit, integration, contract, UI layout/token, and e2e test plan referencing `design/test-cases.csv` and `docs/architecture/test-strategy.md`.

### Test Environment and Doubles
- Required fixtures, sandboxes, and test doubles for external/IO dependencies.

### Manual Verification
- Items requiring human verification with explicit reason (or `N/A + reason`).

### Static Analysis
- Reference `docs/architecture/quality-gates.json` (or `N/A + reason` if static analysis is not adopted) and `design/static-waivers.json` (if any waivers apply).
