# OpenSpec + Superpowers AI R&D Workflow Toolkit

[中文版本 (Chinese Version)](README-zh.md)

This toolkit breaks down 16 workflow stages (including sub-stages 10b, 13a–13e, 14b, and next-step orchestration) into independently loadable Skills, reproducible Prompts, baseline templates, and deterministic verification scripts. It is designed for `pen.dev` + Figma MCP + OpenSpec + Superpowers + OpenCode/compatible Agent workflows.

---

## Contents

- `.claude/skills/<skill-id>/SKILL.md`: 17 project workflow skills (plus 6 OpenSpec auxiliary skills). Claude Code reads from `.claude/skills/`; other agents such as OpenCode can migrate or symlink them to `.agents/skills/` per their specification. Verification scripts support both paths.
- `prompts/`: Prompts corresponding 1:1 with each stage skill; `prompts/00-next-step.md` serves as the universal entry point for determining the "next step".
- `workflow-state.json`: Cross-stage state index. Real artifacts and approval statuses must be validated prior to proceeding.
- `.claude/skills/workflow-orchestrator/SKILL.md`: Orchestrator responsible for next-step determination, prerequisite verification, and quality gates.
- `scripts/next-step.py`: Read-only state reader that prints suggested next stages without mutating state.
- `docs/WORKFLOW-STAGES.json`: The single source of truth for the state machine DAG definition; `scripts/workflow.py` provides status tracking, stage entry guards, evidence validation, atomic state transitions, and SHA-256 handoffs.
- `templates/workflow/stage-evidence.schema.json`: Machine-readable evidence contract for every stage transition; automated checks require real commands, exit codes, and execution logs.
- `independent-verifier` / `prompts/14b-independent-verification.md`: Independent, read-only verification executed after builder completion. A `PASS` status is mandatory prior to manual user acceptance testing (UAT).
- `scripts/check-independent-verification.py`: Structured gate validator for independent verification reports.
- `docs/product/`, `docs/architecture/`, `docs/design/`, `docs/adr/`: Project-level baselines and design inventory templates.
- `openspec/config.yaml`: Example project context and artifact rules. **Compare against existing files before merging; do not overwrite existing OpenSpec configurations blindly.**
- `scripts/`: Structural, traceability, OpenAPI, testing, and pre-completion verification scripts, as well as non-destructive template initializers for Change assets.
- `docs/SUPERPOWERS-MAPPING.md`: Mapping between workflow stages and official Superpowers skills.
- `docs/REVIEW-REPORT.md`: Self-inspection report and known limitations of this toolkit release.
- `docs/TEMPLATE-POLICY.md` & `docs/OUTPUT-TEMPLATE-MATRIX.csv`: Defines mandatory output templates, template locations, and validation gates.
- `docs/STEP-ARTIFACT-CONTRACTS.md` / `.json`: Authoritative contracts defining inputs, outputs, downstream consumers, approval checkpoints, and quality gates per skill.
- `docs/STAGE-IO-OVERVIEW.md`: Auto-generated per-stage input/output matrix generated from contracts and the DAG. Re-generate using `python3 scripts/stage-io-report.py --out docs/STAGE-IO-OVERVIEW.md` after modifying contracts; verified by `check-package.py`.
- `docs/BASELINE-FEATURE-INTERACTION.md`: Governs how project baselines constrain feature development and when feature-level decisions feed back into the baseline.
- `templates/change-assets/design/baseline-impact.md`: Mandatory baseline applicability and impact checklist required for every feature Change.
- `templates/project-baseline/baseline-status.md` / `baseline-change-request.md`: Human-readable baseline status and revision request templates.
- `docs/architecture/baseline-manifest.json` / `constraint-registry.json`: Machine-authoritative baseline manifest and stable constraint registry; frozen states are guarded via SHA-256 checksums.
- `templates/change-assets/design/baseline-binding.json`: Per-change machine binding tracking inheritance of all `ACTIVE` constraints, approved exceptions, design/implementation evidence, and rebase records.
- `scripts/baseline-governance.py`: Baseline governance engine invoked by `workflow.py` during stage gating.
- `templates/workflow/step-handoff-report.md`: Mandatory handoff summary report template displayed upon completion of each stage.
- `scripts/check-step-contracts.py`: Verifies that every Skill/Prompt has matching input, output, and handoff contracts.
- `scripts/check-output-template-matrix.py`: Verifies that all template files registered in the template matrix actually exist on disk.

---

## Installation & Merging into Existing Projects

1. Extract the package ZIP to a temporary directory to inspect differences. Avoid overwriting identical existing files directly.
2. Merge `.claude/skills/`, `prompts/`, and `scripts/` into your project root. Preserve existing skills of the same name and review differences manually.
3. Review `docs/TEMPLATE-POLICY.md` and `docs/OUTPUT-TEMPLATE-MATRIX.csv` to determine stage-specific templates and gates. Merge `docs/` templates into your existing project documentation without overwriting production docs with boilerplate.
4. Merge `context` and `rules` from `openspec/config.yaml` into your active configuration, adapting schemas and rules to your domain.
5. If OpenSpec is not yet initialized, run `openspec init` in your repository root (run `openspec init --help` for options). Do not overwrite active `openspec/specs/` or `openspec/changes/` directories.
6. Run health checks (replace `python3` with `python` on Windows if necessary; repository `.sh` scripts detect both automatically):

   ```bash
   python3 scripts/check-package.py
   python3 scripts/next-step.py
   python3 scripts/workflow.py status
   python3 scripts/check-package.py
   bash scripts/check-required-files.sh
   ```

7. Update test commands for your repository structure, then execute on a target Change:

   ```bash
   openspec new change <change-id>
   bash scripts/new-change-assets.sh <change-id>
   # Fill out design/baseline-impact.md, conduct review, and run structure check:
   python3 scripts/check-baseline-impact.py <change-id>
   # Baseline-binding.json is automatically generated when initializing Change assets (requires frozen baseline).
   # Stage 10 requirement/binding gate:
   python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement
   # Design/implementation/acceptance gates are called by workflow.py or executed manually:
   python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase design
   python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase implementation
   python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase acceptance
   # Once proposal/specs/design/tasks are authored via prompts/ and skills, validate:
   bash scripts/check-change.sh <change-id>
   bash scripts/check-design-assets.sh <change-id> --strict --lint-api
   bash scripts/validate-openapi.sh openspec/changes/<change-id>/api/openapi.yaml
   bash scripts/test-all.sh <frontend-dir> <backend-dir>
   ```

---

## Key Design Conventions

- **Baseline vs. Feature Separation**: Project-level baselines reside in `docs/`; feature changes are defined via OpenSpec Changes. Every feature Change must read baselines and document its impact in `design/baseline-impact.md`. Modifying frozen baselines during feature execution is prohibited; only approved cross-functional decisions may be backported upon completion.
- **Specification Scope**: OpenSpec `specs/**/spec.md` files must capture observable behavior exclusively—avoid class names, framework details, or procedural implementation minutiae.
- **Artifact Standards**: In this spec-driven workflow, standard artifacts are `proposal.md`, `specs/<capability>/spec.md`, `design.md`, and `tasks.md`. Other detailed design assets are supplementary files within the Change directory; file presence alone does not imply OpenSpec validation.
- **Task Tracking**: `tasks.md` must strictly use `- [ ]` and `- [x]` syntax for OpenSpec to accurately parse progress.
- **Change Archival**: Archiving in OpenSpec updates the main spec and moves the entire Change to `archive/`. Ensure deltas are correct and all tasks and acceptance criteria are satisfied before archiving.
- **Next-Step Orchestration**: When asking for the "next step", invoke `@workflow-orchestrator` or use `prompts/00-next-step.md`. The Agent must have access to repository files, terminal, and skills. New chats must inspect current state files and real disk artifacts rather than relying on session memory.
- **Superpowers Alignment**: Skill names evolve across releases. Verify your installed Superpowers versions. This package references official skills: `brainstorming`, `writing-plans`, `test-driven-development`, `systematic-debugging`, `requesting-code-review`, `receiving-code-review`, and `verification-before-completion`. Missing skills must be reported transparently.
- **External Tool Verification**: External tools (`pen.dev`, Figma MCP) must be validated against real accessible capabilities. Unreadable links or inaccessible fields must never be marked as reviewed.
- **UI Inventory Hierarchy**: UI pages must be cataloged in three strict tiers: `PAGE` $\to$ `BLOCK` $\to$ `ELEM/EVT`. `page-inventory.csv` tracks pages, `block-inventory.csv` tracks functional blocks per page, and `interaction-map.csv` maps interactive elements/buttons to their enclosing `block_id`. Consistency and closure are enforced by `scripts/check-inventory.py`.
- **Template Policy**: Not every AI response requires a template; however, formal, traceable artifacts consumed downstream must strictly adhere to `docs/OUTPUT-TEMPLATE-MATRIX.csv`.
- **Contract Enforcement**: Every stage must validate inputs and emit outputs conforming to `docs/STEP-ARTIFACT-CONTRACTS.json`, concluding with a handoff report. Unapproved drafts must not be used as inputs for downstream stages.
- **API & I/O Integrity**: Every OpenAPI `operationId` must explicitly map to one or more `io_id` records in `design/api-io-mapping.csv`, and each `io_id` must have a complete contract in `design/io-catalog.csv`. Databases, files, HTTP/Feign calls, Redis, MQ, object storage, and search queries are all treated as explicit I/O operations. Pure computation or health check endpoints without I/O require an explicit exception approved by an authorized owner.

### Bi-directional Baseline Governance

- Before beginning a feature, baselines must pass freezing and SHA-256 verification via `baseline-manifest.json`, generating a machine-readable `design/baseline-binding.json` bound to all current `ACTIVE` constraints.
- Every Change must contain both `design/baseline-impact.md` (human impact analysis) and `design/baseline-binding.json` (machine constraint tracking); neither replaces the other.
- Constraints must specify applicability, design evidence, and implementation verification item by item. Exceptions must be explicitly approved by assigned owners and scoped strictly to the current Change.
- Modifying frozen baselines during implementation is forbidden. If conflicts arise, halt affected tasks and submit a Baseline Change Request or ADR.
- During acceptance, only approved, implemented, verified, and cross-feature reusable decisions are written back to the baseline. OpenSpec change archival and project baseline updates remain independent decisions.

---

## Suggested Workflow Flow

1. **Requirements & Domain Modeling**: Business workflow nodes, data objects, and RD matrix.
2. **System Architecture Design**: Data flows, domain/shared contracts, audit checkpoints, and baseline freeze.
3. **Proposal Breakdown**: Decomposing initiatives into individual change proposals.
4. **Proposal Requirements Analysis**: User stories (US), use cases (UC), and acceptance criteria (AC).
5. **Prototype & Review**: Generating UI prototypes via AI with `pen.dev` MCP and conducting review.
6. **UI Cataloging**: Page, block, and interaction inventories (`page-inventory.csv`, `block-inventory.csv`, `interaction-map.csv`).
7. **Figma Audit**: Design fidelity and contract audit.
8. **Technical Design**: API, frontend, backend, and test architecture.
9. **Implementation (TDD)**: Test-Driven Development with Superpowers.
10. **Automated Verification**: Linting, integration, and contract tests.
11. **Independent Verification**: Read-only verification by an independent verifier.
12. **Manual Acceptance**: Final human stakeholder sign-off.
13. **Archival & Baseline Sync**: OpenSpec archival and baseline write-back.

---

## Automated Guardrails: What NOT to Do Automatically

By default, this toolkit intentionally **will not**:
- Automatically install external dependencies.
- Commit or push code to version control.
- Alter CI/CD pipelines.
- Automatically archive or release changes.
- Approve pending business, architecture, or design decisions on behalf of human leads.

---

## P0 Runtime Governance

The runtime governance system provides an explicit state machine, stage guards, SHA-256 verified handoff bundles, and an independent Verifier. See `docs/P0-RUNTIME-GOVERNANCE.md` for full documentation. Common commands:

```bash
python3 scripts/workflow.py status
python3 scripts/workflow.py check-entry --step 01-project-bootstrap
python3 scripts/workflow.py transition --step 01-project-bootstrap --evidence workflow/evidence/01-project-bootstrap.json
python3 scripts/workflow.py handoff-verify --manifest workflow/handoffs/project/01-project-bootstrap--02-requirements-analysis.json
```

### Baseline Governance Engine

**Initial Freeze Procedure** (must not bypass human stakeholder sign-off):
1. Complete `docs/architecture/baseline-manifest.json` and `constraint-registry.json`.
2. Confirm artifacts and approval evidence across all six baseline domains are complete, then set each domain to `FROZEN`.
3. Review constraints individually: mark approved rules as `ACTIVE` and deprecated rules as `RETIRED` (no `DRAFT` constraints permitted).
4. Run the following commands:

```bash
python3 scripts/baseline-governance.py refresh-hashes
python3 scripts/baseline-governance.py freeze --approved-by <owner> --approved-at <ISO-date> --evidence <approval-evidence-path>
python3 scripts/baseline-governance.py audit --require-frozen
```

Initializing Change assets automatically derives `design/baseline-binding.json` from the frozen registry. `workflow.py check-entry/transition` enforces fail-closed baseline validation at stages 05, 09, and across all feature phases.

Modifications to baselines require opening an amendment via `open-amendment`. Following updates, increment both the global and domain-specific versions, recalculate hashes, and obtain approval to close the amendment. When global status is `UNDER_AMENDMENT`, all feature development stages are blocked. Checksum drift, missing `ACTIVE` constraint bindings, unapproved exceptions, missing design/implementation evidence, or unresolved rebases will fail gate validation. For complete rules and constraints, refer to Section 9 of `docs/BASELINE-FEATURE-INTERACTION.md`.