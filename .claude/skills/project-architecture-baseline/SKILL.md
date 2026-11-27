---
name: project-architecture-baseline
description: Design and freeze the project-level architecture baseline, shared contracts, code layout, optional static quality gates, and constraint registry.
---

# Stage 03: Project Architecture Baseline

## Role
Conduct the technology and boundary interview with the user/tech lead, author the project architecture baseline, and prepare the frozen baseline manifest and constraint registry.

## Required Methods & Guidance
- Use `brainstorming` for architecture options and trade-offs.
- Consult `process/QUESTION-COVERAGE-CHECKLIST.md` (`03-*`) to cover platform, integration, NFR, security, and ops topics.

## Execution Flow
1. Run `python scripts/workflow.py check-entry --step 03-project-architecture-baseline` and `python scripts/agent-context.py --stage 03`.
2. **Mandatory Architecture Interview (never assume defaults)**:
   - Confirm target tech stack per declared platform (web/h5/mini-program/app/desktop/pda), native/bridge/offline capabilities, and record in `technology-decisions.md` (`## Interview Record` & `## Platform and Integration Boundary Interview Record`).
   - If extending an existing system: read the actual repository/branch/commit and record `## Existing System Secondary-Development Constraints` (`LEGACY-*` constraints). Otherwise write `N/A + reason`.
   - Record all third-party interfaces in `## Third-Party Interface Dependency List` (`EXT-*` constraints, auth, SLA, sandbox, owner) or `NONE + reason`.
   - Confirm static-analysis adoption: if adopted, create `docs/architecture/quality-gates.json` (structure/selection only; installation happens in Stage 08) and set `QUALITY-STATIC-001` to `ACTIVE`; if not adopted, omit `quality-gates.json`, leave `QUALITY-STATIC-001` `RETIRED`, and write `N/A + reason` in `test-strategy.md` and `technology-decisions.md`.
   - Confirm `docs/architecture/code-layout.json` strategy (`module-packages` default for new projects, `footprint`, or `none`), roots, `package_pattern`, `integration_paths`, `frozen_paths`, and `dependency_rules`.
3. **Author Architecture Baseline** (using `templates/project-baseline/*`, reference-style, no duplication of `docs/product/*`):
   - `docs/architecture/system-context.md`, `domain-boundaries.md`, `containers-and-deployment.md`, `data-flows.md`, `logical-erd.md`
   - `docs/architecture/technology-decisions.md`, `api-conventions.md`, `frontend-conventions.md` (with `## Visual Conventions` for Stage 06/07), `test-strategy.md`
   - `docs/architecture/code-layout.json`, optional `docs/architecture/quality-gates.json`, `docs/adr/README.md`
4. **Governance & Freeze Audit**:
   - Populate `docs/architecture/baseline-manifest.json` and `docs/architecture/constraint-registry.json`, update `docs/architecture/baseline-status.md`, and write `docs/project/baseline-audit-report.md` (cross-check boundaries ↔ data flows ↔ ERD ↔ shared contracts ↔ glossary).
   - Validate `code-layout.json` structure before freeze so invalid layouts are never frozen.
5. **Stage-End Gates**:
   - `bash scripts/check-required-files.sh --strict`
   - `python scripts/check-architecture-baseline.py --strict`
   - `python scripts/check-quality-gates.py --root . --strict`
   - `python scripts/check-method-evidence.py --step 03-project-architecture-baseline --evidence workflow/evidence/project/03-project-architecture-baseline.json`
   - `python scripts/baseline-governance.py audit --require-frozen` (after owner freeze approval)

## Input/Output/Handoff Contract
- **Inputs**: Run `python scripts/agent-context.py --stage 03` for the lean read set (`BASELINE-BRIEF.md`, `reference-research.md`, `toolchain-report.md`, `open-questions.md`, matched IDs).
- **Outputs**: All declared `docs/architecture/*`, `docs/adr/README.md`, and `docs/project/baseline-audit-report.md` in `STEP-ARTIFACT-CONTRACTS.json` step `03`.
- **Downstream Handoff**: Frozen architecture baseline, `baseline-manifest.json`, `constraint-registry.json`, `code-layout.json`, optional `quality-gates.json`, and `baseline-audit-report.md` for Stage 04.
- **Review & Boundaries**:
  - Generate `workflow/evidence/project/03-project-architecture-baseline.json` and run:
    `python scripts/workflow.py request-review --step 03-project-architecture-baseline --evidence workflow/evidence/project/03-project-architecture-baseline.json --summary "<summary>"`
  - Present `templates/workflow/step-handoff-report.md` and end the turn. Advance (`approve` → `transition`) only after explicit user approval. Follow `AGENTS.md`.
