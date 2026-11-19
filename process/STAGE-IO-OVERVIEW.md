# Stage Input/Output Overview

> Language: English | [简体中文](STAGE-IO-OVERVIEW-zh.md)

> Status: DERIVED (auto-generated from the authoritative contracts; do not edit by hand)
> Change ID: N/A (project-level process overview)
> Source baseline: `process/STEP-ARTIFACT-CONTRACTS.json` (inputs/outputs/approval/gates), `process/WORKFLOW-STAGES.json` (dependency DAG)
> Related requirements/AC: N/A (process document)
> Generation version: `src-sha256:baf995ad68f6`

> This file summarizes only the stage handoff surface. Field-level artifact templates are in `process/OUTPUT-TEMPLATE-MATRIX.csv`; the process entry point is `prompts/00-next-step.md`.
> To change stage handoffs, first change the two JSON source files, then regenerate with `python scripts/stage-io-report.py --out process/STAGE-IO-OVERVIEW.md`; `scripts/check-package.py` verifies that this file is current.

11 contract stages: 10 DAG stages + 00 next-step orchestration (non-DAG stage).

## Stage Groups

| Group | Stage chain | Description |
|---|---|---|
| Project baseline chain | 00 → 01 → 02 → 03 → 04 | Initialization → requirements business analysis → architecture/baseline freeze → roadmap |
| Proposal delivery chain | 04 → 05 → 06 → 07 → 08 → 09 → 10 | Proposal requirements → Figma design/review → detailed design (incl. interfaces/tests) → implementation → independent verification → acceptance |

## Overview

> The overview merges inputs and outputs; per-stage details further split them into "content/material" and "documents/files".
> The "Lean inputs" column is each stage's default read set; the full contract audit set and on-demand inputs are listed in the per-stage details.

| Stage | Name | Scope | Skill | Dependencies (DAG) | Lean inputs (default reads) | Outputs | On-demand inputs (when triggered) |
|---|---|---|---|---|---|---|---|
| 00 | Next-step orchestration | Applies to project-level and feature-level | `workflow-orchestrator` | N/A (orchestration entry point; not a DAG stage) | workflow-state.json<br>process/PROCESS-MAP.md<br>process/STEP-ARTIFACT-CONTRACTS.json<br>process/WORKFLOW-STAGES.json<br>process/BASELINE-FEATURE-INTERACTION.md<br>process/OUTPUT-TEMPLATE-MATRIX.csv<br>actual artifacts and approval records<br>current OpenSpec CLI state (if initialized) | next-stage determination report (shown in the conversation; persistent storage not mandatory)<br>workflow-state.json (updated only when real state changes) | N/A |
| 01 | Project initialization and toolchain check | project-level | `project-bootstrap` | none (process start) | project goals and repository location provided by the user<br>existing repository directories/configuration/AGENTS.md (if present) | AGENTS.md (project-owned sections only; the toolkit-managed block is maintained by the toolkit sync tool)<br>workflow-state.json<br>docs/architecture/baseline-status.md (based on the project baseline-status template)<br>docs/project/toolchain-report.md (based on the toolchain-report template) | N/A |
| 02 | Requirements business analysis | project-level | `requirements-analysis` | `01-project-bootstrap` | User-provided interviews, business/legacy materials, project goals, users, roles, constraints, pain points, and success criteria; do not scan unrelated locations.<br>Stage 02 contract and required template rows: process/STEP-ARTIFACT-CONTRACTS.json step 02; process/OUTPUT-TEMPLATE-MATRIX.csv Requirements business analysis rows.<br>Stage 02 discovery and output rules: prompts/02-requirements-analysis.md; .claude/skills/requirements-analysis/SKILL.md<br>docs/product/BASELINE-BRIEF.md (when present; Stage 02 creates or refreshes it).<br>docs/product/open-questions.md (open questions and only relevant confirmed decisions, when present).<br>Existing requirements, flow, data, rule, role, glossary, and acceptance artifacts: matched IDs or sections only; do not load all of docs/product/* by default.<br>User-selected reference products or official sources matched to each research question; record actual queries, URLs, access dates, and findings.<br>docs/product/change-sizing.md and docs/product/id-conventions.md (relevant rules only, when present). | docs/product/requirements-analysis.md<br>docs/product/workflows.md (each FLOW must include a complete node table: node role, input/output data objects, preconditions, processing actions, exceptions/branches, next node)<br>docs/product/data-objects.csv (business data object catalog)<br>docs/product/rd-matrix.csv (requirement-data object matrix: requirement/rule → process node → role → data object)<br>docs/product/business-rules.md<br>docs/product/glossary.md<br>docs/product/acceptance-policy.md<br>docs/product/open-questions.md<br>docs/product/BASELINE-BRIEF.md (one-page baseline entry point, about one page; resident context for stages 03–05)<br>docs/product/role-permission-matrix.csv (role / capability / data scope / access level)<br>docs/product/change-sizing.md (Change slicing budget and definition of done)<br>docs/product/decisions.md (DEC decision log)<br>docs/product/assumptions.md (ASM assumption register)<br>docs/product/lessons.md (lessons/anti-patterns; appended by stage 10 after acceptance)<br>docs/product/id-conventions.md (project-level/Change-level IDs and parallel allocation rules)<br>docs/product/BASELINE-INDEX.md (resident baseline index generated by scripts/gen-baseline-index.py)<br>docs/product/reference-research.md (reference products and internet research: research questions/reference products/source records/comparison/conclusions/impact mapping) | 6 items (see details) |
| 03 | Project overall architecture design | project-level | `project-architecture-baseline` | `02-requirements-analysis` | docs/product/BASELINE-BRIEF.md (read first, about one page)<br>docs/product/reference-research.md (technology selection/third-party decisions)<br>docs/product/open-questions.md (relevant items only)<br>docs/project/toolchain-report.md (toolchain/test commands)<br>docs/architecture/baseline-status.md (initial baseline)<br>existing system code repository location/third-party interface list (provided by the user)<br>matched FLOW/NODE/DO/RD/BR rows (read by ID on demand) | docs/architecture/system-context.md<br>docs/architecture/domain-boundaries.md<br>docs/architecture/containers-and-deployment.md<br>docs/architecture/data-flows.md (data flows: DF ID, sync/async, transaction boundaries, failures and compensation)<br>docs/architecture/logical-erd.md (logical entities, relationships, data ownership, domain invariants)<br>docs/architecture/technology-decisions.md (including technology selection interview records, candidate comparison, user confirmer and date)<br>docs/architecture/api-conventions.md<br>docs/architecture/frontend-conventions.md<br>docs/architecture/test-strategy.md<br>docs/architecture/quality-gates.json (conditionally applicable: when the project adopts static analysis; machine-readable stack roots, tool commands, config paths, severity and waiver policy; structure only at 03 because a from-scratch repository may not have stack directories yet; approval comes from the frozen test_quality baseline domain, not from the file; omit the file, mark the evidence output n/a, and record the adoption decision when not adopted)<br>docs/adr/README.md<br>docs/architecture/baseline-manifest.json (machine-authoritative versions/freeze status/domain file SHA-256)<br>docs/architecture/constraint-registry.json (stable constraint IDs and approval status)<br>docs/project/baseline-audit-report.md (end-of-stage audit report) | 13 items (see details) |
| 04 | Proposal breakdown, dependency ordering, and roadmap | project-level to feature-level | `proposal-planning` | `03-project-architecture-baseline` | docs/product/BASELINE-BRIEF.md<br>docs/product/change-sizing.md<br>docs/architecture/baseline-manifest.json<br>docs/architecture/constraint-registry.json<br>docs/architecture/baseline-status.md<br>docs/project/baseline-audit-report.md<br>docs/product/open-questions.md (relevant items only)<br>matched FLOW/NODE/DO/BR rows | docs/product/proposal-roadmap.md (including scope/dependencies/value/baseline applicability domains and potential amendment summary for each candidate Change) | 6 items (see details) |
| 05 | Proposal-level requirements analysis | single feature Change | `feature-requirements` | `04-proposal-planning` | docs/product/BASELINE-BRIEF.md<br>docs/product/change-sizing.md, id-conventions.md<br>docs/product/proposal-roadmap.md (current row)<br>docs/architecture/baseline-status.md, baseline-manifest.json, constraint-registry.json<br>matched FLOW/NODE/DO/RD/BR/ROLE/CAP rows<br>openspec/specs/** (relevant capability only)<br>docs/product/open-questions.md (relevant items only)<br>docs/product/reference-research.md (only when scope/scenarios require it) | openspec/changes/<change-id>/proposal.md<br>openspec/changes/<change-id>/specs/<capability>/spec.md (when applicable)<br>openspec/changes/<change-id>/tasks.md (initial tasks; 08 updates checkboxes)<br>openspec/changes/<change-id>/design/user-stories.md (user stories and AC; AC is the sole anchor for testing and verification)<br>openspec/changes/<change-id>/design/baseline-impact.md (based on the baseline-impact template; 07 updates the design review conclusions)<br>openspec/changes/<change-id>/design/baseline-binding.json (generated automatically from the current frozen baseline, binding the constraints required by the manifest governance profile: all ACTIVE in standard, critical only in lite; 07 writes design evidence) | 9 items (see details) |
| 06 | Figma design and review (Figma-only) | single feature Change | `figma-design-review` | `05-feature-requirements` | current Change's proposal/specs/design/user-stories<br>current Change's design/baseline-impact.md, baseline-binding.json<br>docs/architecture/frontend-conventions.md section 9, technology-decisions.md<br>docs/architecture/baseline-status.md<br>docs/product/BASELINE-BRIEF.md, id-conventions.md<br>matched FLOW/NODE/DO/RD/BR/ROLE/PAGE rows<br>docs/product/open-questions.md (page-related only)<br>Figma MCP accessibility | openspec/changes/<change-id>/design/figma-audit.md (the sole UI contract (single file): Figma file/version, target framework/transcoding notes, PAGE list, actual token values, text styles, block specs for each PAGE, design code notes, assertion scope, state coverage and decisions, asset list, MCP read records, deviations and pending confirmations, UI review APPROVED; N/A + reason when there is no UI)<br>openspec/changes/<change-id>/design/figma-code/ (README.md + one PAGE-00N.vue per PAGE (.tsx for a React stack); target-framework design code transcoded in 06 according to the overall technology selection; 08 ports it directly and only adds business logic)<br>openspec/changes/<change-id>/design/figma-layout.csv (compact assertion table: page_id/route/element_id/figma_node_id/x/y/width/height/dom_selector/assert_geometry/assert_text/tolerance_px/text_content/font_size/font_weight/notes; 06 may leave route/dom_selector as PENDING, 07 fills them in)<br>openspec/changes/<change-id>/design/figma-assets/README.md (generated only when there are real image/SVG assets; reference screenshots are not saved) | 11 items (see details) |
| 07 | Detailed design, interface and test design | single feature Change | `detailed-design` | `06-figma-design-review` | openspec/changes/<change-id>/proposal.md, specs/<capability>/spec.md, design/user-stories.md, tasks.md, design.md<br>openspec/changes/<change-id>/design/baseline-impact.md, baseline-binding.json<br>existing functionality code location/third-party interface list (provided by the user)<br>when UI is involved: openspec/changes/<change-id>/design/figma-audit.md, figma-code/, figma-layout.csv, Figma review file<br>docs/architecture/technology-decisions.md, docs/architecture/api-conventions.md, docs/architecture/frontend-conventions.md#9, docs/architecture/test-strategy.md (by design domain)<br>docs/architecture/baseline-status.md<br>docs/product/BASELINE-BRIEF.md, docs/product/id-conventions.md<br>matched FLOW/NODE/DO/RD/BR/ROLE/CAP/PAGE rows (read by ID on demand) | openspec/changes/<change-id>/design.md (unified design: five sections for design decisions, interfaces, frontend, backend, and tests)<br>openspec/changes/<change-id>/design/figma-layout.csv (07 fills route/dom_selector in every row and defines responsive rules accordingly; geometry/text/font values follow the target-framework design code and metadata)<br>the ### PAGE→BLOCK→component mapping in openspec/changes/<change-id>/design.md (based on the figma-code target-framework design code, registering only business adaptations and UI-DEVIATION; do not redesign styles/layout/copy)<br>openspec/changes/<change-id>/design/baseline-impact.md (07 updates the design review conclusion: NO_IMPACT/REBASE_REQUIRED and design evidence)<br>openspec/changes/<change-id>/design/baseline-binding.json (07 writes design evidence for each constraint)<br>openspec/changes/<change-id>/design/test-cases.csv (test case matrix mapping TEST ID → AC/PAGE/API/IO, including failure injection/test-double environment/manual reason; BLOCK is optional, write N/A when not applicable)<br>openspec/changes/<change-id>/api/openapi.yaml (applicable conditionally: when there is an API)<br>openspec/changes/<change-id>/design/api-io-mapping.csv (applicable conditionally: when there is an API)<br>openspec/changes/<change-id>/design/io-catalog.csv (applicable conditionally: when there is an API)<br>openspec/changes/<change-id>/design/interface-catalog.csv (cross-boundary interface catalog: HTTP/native bridge/device/third-party/async/file; applicable conditionally: when there are cross-boundary interfaces)<br>openspec/changes/<change-id>/design/static-waivers.json (applicable conditionally: when static analysis waivers are needed; Change-scoped file+rule waivers with reason/owner/approver/approval date/expiry; never stored in the frozen gates file; omit the file or keep an empty list when none are needed)<br>openspec/changes/<change-id>/traceability.csv (merges API and test mappings; the sole traceability aggregate file) | 14 items (see details) |
| 08 | Implementation, TDD, verification, and code review | single feature Change | `implementation-orchestrator` | `07-detailed-design` | current Change's tasks.md, design.md, specs, user-stories, test-cases.csv, traceability.csv<br>when applicable: api/openapi.yaml, api-io-mapping.csv, io-catalog.csv, interface-catalog.csv<br>figma-audit.md, figma-code/, figma-layout.csv when UI is involved<br>current Change's design/baseline-impact.md, baseline-binding.json, baseline-status.md<br>architecture sections matched by design domain: system-context/domain-boundaries/logical-erd/data-flows/technology-decisions/api-conventions/frontend-conventions/test-strategy<br>docs/product/BASELINE-BRIEF.md<br>docs/product/open-questions.md (relevant items only)<br>existing functionality code location (if modifying existing functionality) | actual source code/migrations/configuration<br>automated test code and run results<br>openspec/changes/<change-id>/design/evidence/code-review.md (when UI is involved, includes a ## UI fidelity per-PAGE numeric table: Figma node/asserted element count/max deviation/layout evidence/deviations/conclusion/approver; numbers are taken directly from figma-layout-check.json; only deviation/UI-DERIVED PAGEs require manual explanation and approval; when quality gates are adopted, includes a ## Static analysis table copied verbatim from static-analysis.json: per stack/tool command, config path @ SHA-256, result, literal exit 0, and applied waivers with approver)<br>openspec/changes/<change-id>/design/evidence/static-analysis.json (when quality gates are adopted; produced by scripts/run-quality-gates.py: per blocking stack/tool command, cwd, exit code, config SHA-256, gates SHA-256, source revision, applied waivers, verdict)<br>openspec/changes/<change-id>/design/evidence/static-analysis-logs/ (when quality gates are adopted; one captured log per blocking stack/tool; the log filename derives from the sanitized stack root plus the tool id)<br>openspec/changes/<change-id>/design/evidence/figma-layout-check.json (per-element expected/actual/delta evidence from scripts/check-figma-layout.py)<br>openspec/changes/<change-id>/tasks.md (checkbox status updated by implementation; MUTABLE by 08)<br>openspec/changes/<change-id>/design/evidence/implementation-diff.json (commit/diff SHA-256 and changed paths at the verified revision)<br>implementation/verification evidence<br>conditionally applicable: baseline change request/ADR draft (when conflicts are found; do not update the frozen baseline without approval) | 10 items (see details) |
| 09 | Independent verification and acceptance evidence | feature-level | `independent-verifier` | `08-implementation-orchestrator` | implemented code and revision/diff fingerprint<br>current Change's proposal/specs/design/user-stories/tasks<br>when applicable: api/openapi.yaml, api-io-mapping.csv, io-catalog.csv, interface-catalog.csv<br>figma-audit.md, figma-layout.csv, figma-layout-check.json when UI is involved<br>test-cases.csv, traceability.csv, code-review.md, Builder test evidence<br>docs/product/BASELINE-BRIEF.md<br>docs/product/acceptance-policy.md<br>current Change's baseline-impact.md, baseline-binding.json, baseline-status.md | openspec/changes/<change-id>/design/evidence/independent-verification-report.md<br>openspec/changes/<change-id>/design/evidence/independent-verification.json<br>openspec/changes/<change-id>/design/evidence/static-analysis-independent.json (when quality gates are adopted; independent rerun evidence with distinct verifier and builder identities; produced by scripts/run-quality-gates.py --independent) | 10 items (see details) |
| 10 | Human acceptance, archive, and baseline write-back | single feature Change | `acceptance-audit` | `09-independent-verification` | independent-verification-report.md and independent-verification.json<br>current Change's specs, user-stories, traceability.csv, design.md, code-review.md<br>figma-audit.md, figma-layout.csv, figma-layout-check.json when UI is involved<br>test-cases.csv, interface-catalog.csv<br>current Change's baseline-impact.md, baseline-binding.json, baseline-status.md<br>docs/product/acceptance-policy.md, BASELINE-BRIEF.md, change-sizing.md<br>docs/product/decisions.md, assumptions.md, id-conventions.md<br>running acceptance environment entry point | openspec/changes/<change-id>/design/evidence/acceptance.md (when UI is involved, includes ## UI acceptance per-PAGE sign-off: Figma node/running system entry/deviation approval/acceptance method (machine evidence/side-by-side check)/reviewer; when quality gates are adopted, includes ## Static analysis reconciled from static-analysis.json and static-analysis-independent.json: per stack/tool command, result, literal exit 0, and every applied waiver with approver)<br>shared mutable write-back: lessons/decisions/assumptions registries (owned by Stage 02; Stage 10 appends/updates them without re-declaring them as outputs)<br>acceptance report and approval records<br>OpenSpec archive results and updated main specs (only after approval) | 7 items (see details) |

## Per-Stage Details

### 00 Next-step orchestration

- Scope: Applies to project-level and feature-level
- Skill: `workflow-orchestrator`
- Prompt: `prompts/00-next-step.md`
- Dependencies (DAG): N/A (orchestration entry point; not a DAG stage)

**Full contract inputs (content/material, audit set)**

- actual artifacts and approval records
- current OpenSpec CLI state (if initialized)

**Full contract inputs (documents/files, audit set)**

- workflow-state.json
- process/PROCESS-MAP.md
- process/STEP-ARTIFACT-CONTRACTS.json
- process/WORKFLOW-STAGES.json
- process/BASELINE-FEATURE-INTERACTION.md
- process/OUTPUT-TEMPLATE-MATRIX.csv

**Outputs (content/material)**

- next-stage determination report (shown in the conversation; persistent storage not mandatory)

**Outputs (documents/files)**

- workflow-state.json (updated only when real state changes)

**Output consumers**

- workflow-state.json → SYSTEM

**Downstream handoff**

- all files in the Input Contract of the selected stage

**Approval and gates**

- Approval: must not bypass pending_approvals, blocked_items, missing inputs, or failed gates
- Gate: verify actual files/approvals/CLI; select exactly one stage

---

### 01 Project initialization and toolchain check

- Scope: project-level
- Skill: `project-bootstrap`
- Prompt: `prompts/01-project-bootstrap.md`
- Dependencies (DAG): none (process start)

**Full contract inputs (content/material, audit set)**

- project goals and repository location provided by the user

**Full contract inputs (documents/files, audit set)**

- existing repository directories/configuration/AGENTS.md (if present)

**Outputs (content/material)**

- N/A

**Outputs (documents/files)**

- AGENTS.md (project-owned sections only; the toolkit-managed block is maintained by the toolkit sync tool)
- workflow-state.json
- docs/architecture/baseline-status.md (based on the project baseline-status template)
- docs/project/toolchain-report.md (based on the toolchain-report template)

**Output consumers**

- AGENTS.md → ALL
- workflow-state.json → SYSTEM
- docs/architecture/baseline-status.md → 03, 04, 05, 06, 07, 08, 09, 10
- docs/project/toolchain-report.md → 03

**Downstream handoff**

- repository conventions and toolchain report
- workflow-state.json

**Approval and gates**

- Approval: approval required before overwriting/modifying existing AGENTS.md or configuration
- Gate: repository inventory, Skill/CLI availability check, basic file check

---

### 02 Requirements business analysis

- Scope: project-level
- Skill: `requirements-analysis`
- Prompt: `prompts/02-requirements-analysis.md`
- Dependencies (DAG): `01-project-bootstrap`

**Lean inputs (default reads, advisory budget)**

- User-provided interviews, business/legacy materials, project goals, users, roles, constraints, pain points, and success criteria; do not scan unrelated locations.
- Stage 02 contract and required template rows: process/STEP-ARTIFACT-CONTRACTS.json step 02; process/OUTPUT-TEMPLATE-MATRIX.csv Requirements business analysis rows.
- Stage 02 discovery and output rules: prompts/02-requirements-analysis.md; .claude/skills/requirements-analysis/SKILL.md
- docs/product/BASELINE-BRIEF.md (when present; Stage 02 creates or refreshes it).
- docs/product/open-questions.md (open questions and only relevant confirmed decisions, when present).
- Existing requirements, flow, data, rule, role, glossary, and acceptance artifacts: matched IDs or sections only; do not load all of docs/product/* by default.
- User-selected reference products or official sources matched to each research question; record actual queries, URLs, access dates, and findings.
- docs/product/change-sizing.md and docs/product/id-conventions.md (relevant rules only, when present).

> Budget (advisory): 8/8 items; when exceeded, narrow the scope or record why the extra reads are needed.

**On-demand inputs (read after a trigger; not counted in the default budget)**

- Complete existing docs/product/* only when a conflict or baseline-wide re-evaluation requires it; record the trigger and sections read.
- docs/product/reference-research.md when prior research exists and the current scope needs it refreshed or reconciled.
- Run openspec list --specs; read relevant specs only and read-only. If no specs are found, record N/A instead of searching unrelated Changes.
- docs/project/toolchain-report.md when checking build, test, or research feasibility.
- docs/architecture/* and docs/adr/* only when existing approved architecture or decisions constrain a requirement.
- Legacy, regulatory, and business materials only from locations or sources provided for this project.

**Full contract inputs (content/material, audit set)**

- interviews/business materials/legacy system materials
- project goals, users, roles, constraints
- reference products provided by the user (name/link/screenshot/account; NONE + reason if none)
- internet research tools and real sources (WebSearch/WebFetch or host-equivalent capability; record query, URL, access date)

**Full contract inputs (documents/files, audit set)**

- existing docs/product/* (if present)
- existing OpenSpec specs (read-only)

**Outputs (content/material)**

- N/A

**Outputs (documents/files)**

- docs/product/requirements-analysis.md
- docs/product/workflows.md (each FLOW must include a complete node table: node role, input/output data objects, preconditions, processing actions, exceptions/branches, next node)
- docs/product/data-objects.csv (business data object catalog)
- docs/product/rd-matrix.csv (requirement-data object matrix: requirement/rule → process node → role → data object)
- docs/product/business-rules.md
- docs/product/glossary.md
- docs/product/acceptance-policy.md
- docs/product/open-questions.md
- docs/product/BASELINE-BRIEF.md (one-page baseline entry point, about one page; resident context for stages 03–05)
- docs/product/role-permission-matrix.csv (role / capability / data scope / access level)
- docs/product/change-sizing.md (Change slicing budget and definition of done)
- docs/product/decisions.md (DEC decision log)
- docs/product/assumptions.md (ASM assumption register)
- docs/product/lessons.md (lessons/anti-patterns; appended by stage 10 after acceptance)
- docs/product/id-conventions.md (project-level/Change-level IDs and parallel allocation rules)
- docs/product/BASELINE-INDEX.md (resident baseline index generated by scripts/gen-baseline-index.py)
- docs/product/reference-research.md (reference products and internet research: research questions/reference products/source records/comparison/conclusions/impact mapping)

**Output consumers**

- docs/product/requirements-analysis.md → 03, 04, 05
- docs/product/reference-research.md → 03, 04, 05, 06
- docs/product/workflows.md → 03, 04, 05, 06, 07
- docs/product/data-objects.csv → 03, 04, 05, 06, 07
- docs/product/rd-matrix.csv → 03, 04, 05, 06, 07
- docs/product/business-rules.md → 03, 04, 05, 06, 07
- docs/product/glossary.md → 03, 04, 05
- docs/product/acceptance-policy.md → 03, 04, 05, 07, 09, 10
- docs/product/open-questions.md → 03, 04, 05, 06, 07, 08, 09, 10
- docs/product/BASELINE-BRIEF.md → 03, 04, 05, 07, 10
- docs/product/role-permission-matrix.csv → 03, 04, 05, 06, 07
- docs/product/change-sizing.md → 03, 04, 05, 10
- docs/product/decisions.md → 03, 04, 05, 10
- docs/product/assumptions.md → 03, 04, 05, 10
- docs/product/lessons.md → 04, 05, 10
- docs/product/id-conventions.md → 03, 04, 05, 06, 07, 10
- docs/product/BASELINE-INDEX.md → 03

**Downstream handoff**

- business processes and node-level roles/data objects, business data object catalog, RD matrix, business rules, glossary and acceptance policy, open questions
- resident baseline brief, role-permission matrix, Change sizing rules, decision/assumption registers, ID conventions and baseline index

**Approval and gates**

- Approval: business/product owner confirms process completeness, node data objects and roles, and RD matrix coverage
- Gate: scripts/check-requirements.py --strict (FLOW/NODE/DO/RD/BR structure, reference closure, and node coverage); scripts/gen-baseline-index.py --check (resident baseline index not stale); python scripts/check-reference-research.py --strict (reference products and internet research: ≥3 research questions, ≥3 sources, ≥2 comparisons, impact mapping and approval)

---

### 03 Project overall architecture design

- Scope: project-level
- Skill: `project-architecture-baseline`
- Prompt: `prompts/03-project-architecture-baseline.md`
- Dependencies (DAG): `02-requirements-analysis`

**Lean inputs (default reads, advisory budget)**

- docs/product/BASELINE-BRIEF.md (read first, about one page)
- docs/product/reference-research.md (technology selection/third-party decisions)
- docs/product/open-questions.md (relevant items only)
- docs/project/toolchain-report.md (toolchain/test commands)
- docs/architecture/baseline-status.md (initial baseline)
- existing system code repository location/third-party interface list (provided by the user)
- matched FLOW/NODE/DO/RD/BR rows (read by ID on demand)

> Budget (advisory): 7/8 items; when exceeded, narrow the scope or record why the extra reads are needed.

**On-demand inputs (read after a trigger; not counted in the default budget)**

- docs/product/requirements-analysis.md
- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/rd-matrix.csv
- docs/product/business-rules.md
- docs/product/glossary.md
- docs/product/acceptance-policy.md
- docs/product/role-permission-matrix.csv
- docs/product/change-sizing.md
- docs/product/decisions.md
- docs/product/assumptions.md
- docs/product/id-conventions.md
- docs/adr/*

**Full contract inputs (content/material, audit set)**

- existing repository structure/technical constraints
- existing system code repository location and accessibility (if extending an existing system; including repository/local path/branch/commit)
- third-party interface list confirmed by the user (provider/purpose/protocol/authentication/SLA/sandbox/approval; NONE + reason if none)
- non-functional requirements
- explicit technology selection preferences from the user/technical lead (must be explicitly asked and recorded in this stage; never assume defaults)

**Full contract inputs (documents/files, audit set)**

- approved docs/product/requirements-analysis.md, workflows.md, data-objects.csv, rd-matrix.csv, business-rules.md, glossary.md, acceptance-policy.md
- docs/product/BASELINE-BRIEF.md, role-permission-matrix.csv, change-sizing.md, decisions.md, assumptions.md, id-conventions.md, BASELINE-INDEX.md (resident baseline; read the brief first, load details on demand)
- docs/product/reference-research.md (reference product and internet research conclusions; used for technology selection, boundaries, and third-party decisions)
- docs/product/open-questions.md (read-only; unresolved questions must not be closed unilaterally by the architecture stage)
- docs/project/toolchain-report.md (toolchain, test commands, and environment constraints)
- docs/architecture/baseline-status.md (initial baseline and template status from stage 01; this stage updates it to a freeze candidate)

**Outputs (content/material)**

- N/A

**Outputs (documents/files)**

- docs/architecture/system-context.md
- docs/architecture/domain-boundaries.md
- docs/architecture/containers-and-deployment.md
- docs/architecture/data-flows.md (data flows: DF ID, sync/async, transaction boundaries, failures and compensation)
- docs/architecture/logical-erd.md (logical entities, relationships, data ownership, domain invariants)
- docs/architecture/technology-decisions.md (including technology selection interview records, candidate comparison, user confirmer and date)
- docs/architecture/api-conventions.md
- docs/architecture/frontend-conventions.md
- docs/architecture/test-strategy.md
- docs/architecture/quality-gates.json (conditionally applicable: when the project adopts static analysis; machine-readable stack roots, tool commands, config paths, severity and waiver policy; structure only at 03 because a from-scratch repository may not have stack directories yet; approval comes from the frozen test_quality baseline domain, not from the file; omit the file, mark the evidence output n/a, and record the adoption decision when not adopted)
- docs/adr/README.md
- docs/architecture/baseline-manifest.json (machine-authoritative versions/freeze status/domain file SHA-256)
- docs/architecture/constraint-registry.json (stable constraint IDs and approval status)
- docs/project/baseline-audit-report.md (end-of-stage audit report)

**Output consumers**

- docs/architecture/system-context.md → 07, 08
- docs/architecture/domain-boundaries.md → 07, 08
- docs/architecture/containers-and-deployment.md → 07
- docs/architecture/data-flows.md → 07, 08
- docs/architecture/logical-erd.md → 07, 08
- docs/architecture/technology-decisions.md → 06, 07, 08
- docs/architecture/api-conventions.md → 07, 08
- docs/architecture/frontend-conventions.md → 06, 07, 08
- docs/architecture/test-strategy.md → 07, 08
- docs/architecture/quality-gates.json → 05, 07, 08, 09, 10
- docs/adr/README.md → 07, 08, 09, 10
- docs/architecture/baseline-manifest.json → 04, 05
- docs/architecture/constraint-registry.json → 04, 05
- docs/project/baseline-audit-report.md → 04

**Downstream handoff**

- frozen project architecture baseline, data flows, logical ERD, shared contracts/test strategy, ACTIVE constraint catalog, audit report, and approval records

**Approval and gates**

- Approval: product/architecture/technical leads jointly confirm system boundaries, data flows, and shared contracts, and approve the baseline freeze
- Gate: scripts/check-required-files.sh --strict; cross-document consistency audit (system boundaries/data flows/ERD/shared contracts/glossary); python scripts/check-quality-gates.py --root . --strict (when quality-gates.json exists: structure/selection, not materialized at 03; when the file is absent it reports QUALITY_GATES_NOT_ADOPTED and passes); python scripts/check-method-evidence.py --step 03-project-architecture-baseline --evidence <evidence> (required method skills, a real evidence path, and a landing section); python scripts/check-architecture-baseline.py --strict (existing system extension constraints/third-party interface dependency list/LEGACY-*/EXT-*); docs/architecture/technology-decisions.md must contain existing system extension constraints and third-party interface dependency list; scripts/baseline-governance.py audit --require-frozen (end-of-stage freeze audit, which is also the approval of the gates file when adopted)

---

### 04 Proposal breakdown, dependency ordering, and roadmap

- Scope: project-level to feature-level
- Skill: `proposal-planning`
- Prompt: `prompts/04-proposal-planning.md`
- Dependencies (DAG): `03-project-architecture-baseline`

**Lean inputs (default reads, advisory budget)**

- docs/product/BASELINE-BRIEF.md
- docs/product/change-sizing.md
- docs/architecture/baseline-manifest.json
- docs/architecture/constraint-registry.json
- docs/architecture/baseline-status.md
- docs/project/baseline-audit-report.md
- docs/product/open-questions.md (relevant items only)
- matched FLOW/NODE/DO/BR rows

> Budget (advisory): 8/8 items; when exceeded, narrow the scope or record why the extra reads are needed.

**On-demand inputs (read after a trigger; not counted in the default budget)**

- docs/product/requirements-analysis.md
- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/rd-matrix.csv
- docs/product/business-rules.md
- docs/adr/*

**Full contract inputs (content/material, audit set)**

- known technical debt and dependencies
- related architecture/data/API/frontend/test baseline versions and approval information

**Full contract inputs (documents/files, audit set)**

- approved and frozen project architecture and baseline: docs/architecture/baseline-manifest.json, constraint-registry.json, baseline-status.md, docs/project/baseline-audit-report.md
- docs/product/requirements-analysis.md, workflows.md, data-objects.csv, rd-matrix.csv, business-rules.md, glossary.md, acceptance-policy.md (full requirements business analysis input)
- docs/product/BASELINE-BRIEF.md, role-permission-matrix.csv, change-sizing.md, decisions.md, assumptions.md, lessons.md, id-conventions.md (resident baseline layer and lessons write-back)
- docs/product/reference-research.md (reference product and internet research conclusions; used for Change breakdown and dependency decisions)
- docs/architecture/baseline-status.md
- docs/product/open-questions.md (open questions and blocking conditions)
- docs/project/baseline-audit-report.md (gaps, pending approvals, and freeze conclusions from the stage 03 audit)

**Outputs (content/material)**

- N/A

**Outputs (documents/files)**

- docs/product/proposal-roadmap.md (including scope/dependencies/value/baseline applicability domains and potential amendment summary for each candidate Change)

**Output consumers**

- docs/product/proposal-roadmap.md → 05

**Downstream handoff**

- approved Change list, priorities, dependency order

**Approval and gates**

- Approval: product and technical leads approve the roadmap and the first Change
- Gate: scripts/check-roadmap.py --strict; do not fabricate Change validation in this stage

**Baseline interaction**

- Read-only: docs/architecture/baseline-status.md; related product/architecture/data/shared contract/test baselines; openspec/specs/**
- Produce/review: baseline applicability domains and candidate amendments for each Change in docs/product/proposal-roadmap.md

---

### 05 Proposal-level requirements analysis

- Scope: single feature Change
- Skill: `feature-requirements`
- Prompt: `prompts/05-feature-requirements.md`
- Dependencies (DAG): `04-proposal-planning`

**Lean inputs (default reads, advisory budget)**

- docs/product/BASELINE-BRIEF.md
- docs/product/change-sizing.md, id-conventions.md
- docs/product/proposal-roadmap.md (current row)
- docs/architecture/baseline-status.md, baseline-manifest.json, constraint-registry.json
- matched FLOW/NODE/DO/RD/BR/ROLE/CAP rows
- openspec/specs/** (relevant capability only)
- docs/product/open-questions.md (relevant items only)
- docs/product/reference-research.md (only when scope/scenarios require it)

> Budget (advisory): 8/8 items; when exceeded, narrow the scope or record why the extra reads are needed.

**On-demand inputs (read after a trigger; not counted in the default budget)**

- docs/product/requirements-analysis.md
- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/rd-matrix.csv
- docs/product/business-rules.md
- docs/product/glossary.md
- docs/product/acceptance-policy.md
- docs/product/role-permission-matrix.csv
- docs/adr/*

**Full contract inputs (content/material, audit set)**

- N/A

**Full contract inputs (documents/files, audit set)**

- docs/product/proposal-roadmap.md (the row for the current Change and its dependencies), current Change scope
- docs/product/BASELINE-BRIEF.md (read first, about one page), change-sizing.md (slicing budget and DoD), role-permission-matrix.csv, decisions.md, assumptions.md, lessons.md, id-conventions.md
- docs/product/reference-research.md (reference product and internet research conclusions; used for proposal scope and scenario completeness)
- docs/architecture/baseline-status.md and related architecture/data/shared contract/test baselines
- docs/product/requirements-analysis.md, workflows.md, data-objects.csv, rd-matrix.csv, business-rules.md, glossary.md, acceptance-policy.md (related FLOW/BR/AC and RD matrix; AC aligned with acceptance policy)
- openspec/specs/** (read-only)
- docs/architecture/baseline-manifest.json and docs/architecture/constraint-registry.json (machine-authoritative sources)
- docs/architecture/quality-gates.json (when adopted; applicable static analysis gates referenced from the Change baseline impact list)
- docs/product/open-questions.md (read-only; proposal requirements must not decide on the user's behalf)

**Outputs (content/material)**

- N/A

**Outputs (documents/files)**

- openspec/changes/<change-id>/proposal.md
- openspec/changes/<change-id>/specs/<capability>/spec.md (when applicable)
- openspec/changes/<change-id>/tasks.md (initial tasks; 08 updates checkboxes)
- openspec/changes/<change-id>/design/user-stories.md (user stories and AC; AC is the sole anchor for testing and verification)
- openspec/changes/<change-id>/design/baseline-impact.md (based on the baseline-impact template; 07 updates the design review conclusions)
- openspec/changes/<change-id>/design/baseline-binding.json (generated automatically from the current frozen baseline, binding the constraints required by the manifest governance profile: all ACTIVE in standard, critical only in lite; 07 writes design evidence)

**Output consumers**

- openspec/changes/<change-id>/proposal.md → 06, 07, 09
- openspec/changes/<change-id>/specs/<capability>/spec.md → 06, 07, 08, 09, 10
- openspec/changes/<change-id>/tasks.md → 07, 08, 09
- openspec/changes/<change-id>/design/user-stories.md → 06, 07, 08, 09, 10
- openspec/changes/<change-id>/design/baseline-impact.md → 06, 07, 08, 09, 10
- openspec/changes/<change-id>/design/baseline-binding.json → 06, 07, 08, 09, 10

**Downstream handoff**

- approved proposal-level US/AC, scenarios and business rules, scope boundaries, requirement traceability IDs, baseline snapshot, and constraint bindings
- specs are the single source of normative behavior; user-stories retain only scenarios, AC, and traceability IDs

**Approval and gates**

- Approval: product owner approves proposal-level requirements and acceptance criteria; technical lead confirms scope and baseline impact
- Gate: scripts/check-requirements.py --change <change-id> --strict (US/AC structure and reference closure); openspec validate <change-id> --strict; scripts/check-baseline-impact.py <change-id>; scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement

**Baseline interaction**

- Read-only: docs/architecture/baseline-status.md; related product/architecture/data/API/frontend/test baselines; related openspec/specs/**
- Produce/review: openspec/changes/<change-id>/design/baseline-impact.md
- Gate: if feature design depends on unapproved architecture/data/shared contract/quality baseline changes, block entry into detailed design/implementation

---

### 06 Figma design and review (Figma-only)

- Scope: single feature Change
- Skill: `figma-design-review`
- Prompt: `prompts/06-figma-design-review.md`
- Dependencies (DAG): `05-feature-requirements`

**Lean inputs (default reads, advisory budget)**

- current Change's proposal/specs/design/user-stories
- current Change's design/baseline-impact.md, baseline-binding.json
- docs/architecture/frontend-conventions.md section 9, technology-decisions.md
- docs/architecture/baseline-status.md
- docs/product/BASELINE-BRIEF.md, id-conventions.md
- matched FLOW/NODE/DO/RD/BR/ROLE/PAGE rows
- docs/product/open-questions.md (page-related only)
- Figma MCP accessibility

> Budget (advisory): 8/8 items; when exceeded, narrow the scope or record why the extra reads are needed.

**On-demand inputs (read after a trigger; not counted in the default budget)**

- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/rd-matrix.csv
- docs/product/business-rules.md
- docs/product/role-permission-matrix.csv
- docs/product/reference-research.md
- docs/architecture/system-context.md
- docs/architecture/domain-boundaries.md
- docs/architecture/api-conventions.md
- docs/architecture/test-strategy.md
- docs/adr/*

**Full contract inputs (content/material, audit set)**

- actual Figma MCP accessibility (required to generate and read back the real Figma design; block if unavailable or unable to read real files/nodes; never fabricate)

**Full contract inputs (documents/files, audit set)**

- openspec/changes/<change-id>/proposal.md, specs/<capability>/spec.md, design/user-stories.md (approved proposal-level requirements and AC; initial design decisions are in proposal.md)
- docs/product/workflows.md, data-objects.csv, rd-matrix.csv, business-rules.md, role-permission-matrix.csv, id-conventions.md (business processes/data objects/RD matrix/role permissions/ID conventions); docs/architecture/frontend-conventions.md (UI/frontend conventions, section 9 is the visual authority); docs/architecture/technology-decisions.md (overall technology selection, determines the target frontend framework/component library)
- docs/product/open-questions.md (read-only; do not decide unilaterally during generation)
- docs/product/reference-research.md (reference product and internet research conclusions; used for page and state reference)
- docs/architecture/baseline-status.md (current version)
- openspec/changes/<change-id>/design/baseline-impact.md (approved baseline snapshot)
- openspec/changes/<change-id>/design/baseline-binding.json (constraint bindings approved in stage 05; this stage inherits them read-only)

**Outputs (content/material)**

- N/A

**Outputs (documents/files)**

- openspec/changes/<change-id>/design/figma-audit.md (the sole UI contract (single file): Figma file/version, target framework/transcoding notes, PAGE list, actual token values, text styles, block specs for each PAGE, design code notes, assertion scope, state coverage and decisions, asset list, MCP read records, deviations and pending confirmations, UI review APPROVED; N/A + reason when there is no UI)
- openspec/changes/<change-id>/design/figma-code/ (README.md + one PAGE-00N.vue per PAGE (.tsx for a React stack); target-framework design code transcoded in 06 according to the overall technology selection; 08 ports it directly and only adds business logic)
- openspec/changes/<change-id>/design/figma-layout.csv (compact assertion table: page_id/route/element_id/figma_node_id/x/y/width/height/dom_selector/assert_geometry/assert_text/tolerance_px/text_content/font_size/font_weight/notes; 06 may leave route/dom_selector as PENDING, 07 fills them in)
- openspec/changes/<change-id>/design/figma-assets/README.md (generated only when there are real image/SVG assets; reference screenshots are not saved)

**Output consumers**

- openspec/changes/<change-id>/design/figma-audit.md → 07, 08, 09, 10
- openspec/changes/<change-id>/design/figma-assets/README.md → evidence-only
- openspec/changes/<change-id>/design/figma-code/ → 07, 08, 09, 10
- openspec/changes/<change-id>/design/figma-layout.csv → 07, 08, 09, 10

**Downstream handoff**

- design/figma-audit.md (target framework/transcoding notes, actual token values, PAGE specs, state decisions), design/figma-code/ (target-framework design code transcoded in 06 according to the overall technology selection), and design/figma-layout.csv (runtime assertion table) are the sole UI inputs for 07/08/09/10; 07/08 consume them offline by default and re-read Figma in page batches only when the file version changes or a page is ambiguous (serially, to avoid rate limiting)
- PAGE IDs and the page set are frozen in 06; 07 initializes PAGE→AC in traceability.csv; 08–10 are read-only and do not add or rename PAGEs
- Visual conventions come from section 9 of docs/architecture/frontend-conventions.md and the actual token values in figma-audit.md; the Figma review file and figma-code/ are the final reference for visuals/components/variables; do not maintain design-tokens.json or scattered token/contract JSON; screenshots are not gate evidence

**Approval and gates**

- Approval: UI Changes: the user (design owner) completes UI review on the real Figma review file and marks it APPROVED, and the Figma MCP audit passes. No-UI Changes may skip the stage with a machine-verified no-UI check.
- Gate: scripts/check-figma-audit.py --change <change-id> --strict --require-framework (target framework/transcoding + actual token values + per-PAGE specs + per-PAGE code in figma-code/ + geometry/text/selector completeness of the figma-layout.csv assertion table + state decisions + UI review APPROVED); workflow.py automatically rechecks baseline-binding.json (requirement phase)

---

### 07 Detailed design, interface and test design

- Scope: single feature Change
- Skill: `detailed-design`
- Prompt: `prompts/07-detailed-design.md`
- Dependencies (DAG): `06-figma-design-review`

**Lean inputs (default reads, advisory budget)**

- openspec/changes/<change-id>/proposal.md, specs/<capability>/spec.md, design/user-stories.md, tasks.md, design.md
- openspec/changes/<change-id>/design/baseline-impact.md, baseline-binding.json
- existing functionality code location/third-party interface list (provided by the user)
- when UI is involved: openspec/changes/<change-id>/design/figma-audit.md, figma-code/, figma-layout.csv, Figma review file
- docs/architecture/technology-decisions.md, docs/architecture/api-conventions.md, docs/architecture/frontend-conventions.md#9, docs/architecture/test-strategy.md (by design domain)
- docs/architecture/baseline-status.md
- docs/product/BASELINE-BRIEF.md, docs/product/id-conventions.md
- matched FLOW/NODE/DO/RD/BR/ROLE/CAP/PAGE rows (read by ID on demand)

> Budget (advisory): 8/8 items; when exceeded, narrow the scope or record why the extra reads are needed.

**On-demand inputs (read after a trigger; not counted in the default budget)**

- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/rd-matrix.csv
- docs/product/business-rules.md
- docs/product/acceptance-policy.md
- docs/product/role-permission-matrix.csv
- docs/product/open-questions.md
- docs/architecture/system-context.md
- docs/architecture/domain-boundaries.md
- docs/architecture/containers-and-deployment.md
- docs/architecture/data-flows.md
- docs/architecture/logical-erd.md
- docs/adr/*
- docs/product/reference-research.md

**Full contract inputs (content/material, audit set)**

- existing functionality code location and accessibility (if modifying existing functionality code; including repository/path/branch/commit)
- third-party interface list and sandbox/contract/test-double requirements from the 03 baseline

**Full contract inputs (documents/files, audit set)**

- openspec/changes/<change-id>/proposal.md, specs/<capability>/spec.md, design/user-stories.md (proposal requirements, AC, and initial design decisions recorded in proposal.md; 07 is the single writer of design.md)
- openspec/changes/<change-id>/tasks.md (task scope)
- openspec/changes/<change-id>/design/figma-audit.md (target framework/transcoding notes, actual token values, text styles, block specs for each PAGE, state decisions; consume offline by default and re-read page by page only on version changes/ambiguity), design/figma-code/ (target-framework design code transcoded in 06 according to the overall technology selection), and design/figma-layout.csv (assertion mapping; 07 fills in route/dom_selector)
- the Figma review file (authority for visuals/components/variables) and section 9 of docs/architecture/frontend-conventions.md (visual conventions); do not maintain design-tokens.json; actual token values are in figma-audit.md
- docs/product/workflows.md, data-objects.csv, rd-matrix.csv, business-rules.md, acceptance-policy.md, role-permission-matrix.csv, id-conventions.md, open-questions.md (related FLOW/NODE/DO/BR, acceptance criteria, permissions, and ID conventions; open-questions is read-only)
- docs/architecture/system-context.md, domain-boundaries.md, containers-and-deployment.md, data-flows.md, logical-erd.md, technology-decisions.md, api-conventions.md, frontend-conventions.md, test-strategy.md, docs/adr/README.md and docs/adr/* (read on demand by design domain); docs/product/BASELINE-BRIEF.md (read first)
- docs/architecture/quality-gates.json (when adopted; frozen static analysis gates and waiver policy to plan against)
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md (current version)
- openspec/changes/<change-id>/design/baseline-binding.json (each constraint, design evidence, and exception approval)

**Outputs (content/material)**

- N/A

**Outputs (documents/files)**

- openspec/changes/<change-id>/design.md (unified design: five sections for design decisions, interfaces, frontend, backend, and tests)
- openspec/changes/<change-id>/design/figma-layout.csv (07 fills route/dom_selector in every row and defines responsive rules accordingly; geometry/text/font values follow the target-framework design code and metadata)<br>the ### PAGE→BLOCK→component mapping in openspec/changes/<change-id>/design.md (based on the figma-code target-framework design code, registering only business adaptations and UI-DEVIATION; do not redesign styles/layout/copy)
- openspec/changes/<change-id>/design/baseline-impact.md (07 updates the design review conclusion: NO_IMPACT/REBASE_REQUIRED and design evidence)
- openspec/changes/<change-id>/design/baseline-binding.json (07 writes design evidence for each constraint)
- openspec/changes/<change-id>/design/test-cases.csv (test case matrix mapping TEST ID → AC/PAGE/API/IO, including failure injection/test-double environment/manual reason; BLOCK is optional, write N/A when not applicable)
- openspec/changes/<change-id>/api/openapi.yaml (applicable conditionally: when there is an API)
- openspec/changes/<change-id>/design/api-io-mapping.csv (applicable conditionally: when there is an API)
- openspec/changes/<change-id>/design/io-catalog.csv (applicable conditionally: when there is an API)
- openspec/changes/<change-id>/design/interface-catalog.csv (cross-boundary interface catalog: HTTP/native bridge/device/third-party/async/file; applicable conditionally: when there are cross-boundary interfaces)
- openspec/changes/<change-id>/design/static-waivers.json (applicable conditionally: when static analysis waivers are needed; Change-scoped file+rule waivers with reason/owner/approver/approval date/expiry; never stored in the frozen gates file; omit the file or keep an empty list when none are needed)
- openspec/changes/<change-id>/traceability.csv (merges API and test mappings; the sole traceability aggregate file)

**Output consumers**

- openspec/changes/<change-id>/design/baseline-impact.md → 08, 09, 10
- openspec/changes/<change-id>/design/baseline-binding.json → 08, 09, 10
- openspec/changes/<change-id>/design.md → 08, 09, 10
- openspec/changes/<change-id>/api/openapi.yaml → 08, 09
- openspec/changes/<change-id>/design/api-io-mapping.csv → 08, 09
- openspec/changes/<change-id>/design/io-catalog.csv → 08, 09
- openspec/changes/<change-id>/design/interface-catalog.csv → 08, 09, 10
- openspec/changes/<change-id>/design/static-waivers.json → 08, 09, 10
- openspec/changes/<change-id>/traceability.csv → 08, 09, 10
- openspec/changes/<change-id>/design/test-cases.csv → 08, 09, 10
- openspec/changes/<change-id>/design/figma-layout.csv → 08, 09, 10

**Downstream handoff**

- unified design decisions, interface contracts, frontend/backend implementation constraints, test case matrix, figma-layout.csv assertion mapping, and the sole traceability matrix

**Approval and gates**

- Approval: technical lead confirms design scope, interfaces, and test approach
- Gate: scripts/check-change.sh <change-id>; scripts/check-design-assets.sh <change-id> --strict --lint-api (also validates figma-audit when UI is involved); scripts/check-design-sections.py --change <change-id> (including ### existing code change impact, figma-layout.csv route/dom_selector completion, and responsive rules); scripts/check-test-cases.py --change <change-id> --strict; scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict; when there is an API: scripts/check-api-traceability.py --change <change-id>; when there are cross-boundary interfaces: scripts/check-interface-catalog.py --change <change-id> --strict; python scripts/check-method-evidence.py --step 07-detailed-design --evidence <evidence> (required method skills, real evidence paths, and landing sections); python3 scripts/baseline-governance.py check-change --change-id <id> --phase design

**Baseline interaction**

- Read-only: current Change's design/baseline-impact.md; docs/architecture/baseline-status.md; project baselines applicable to this design domain
- Produce/review: update the review conclusion/affected domains/NO_IMPACT or REBASE_REQUIRED in baseline-impact.md
- Gate: conflicts must trigger a baseline amendment proposal; affected designs must not be frozen before approval

---

### 08 Implementation, TDD, verification, and code review

- Scope: single feature Change
- Skill: `implementation-orchestrator`
- Prompt: `prompts/08-implementation-orchestrator.md`
- Dependencies (DAG): `07-detailed-design`

**Lean inputs (default reads, advisory budget)**

- current Change's tasks.md, design.md, specs, user-stories, test-cases.csv, traceability.csv
- when applicable: api/openapi.yaml, api-io-mapping.csv, io-catalog.csv, interface-catalog.csv
- figma-audit.md, figma-code/, figma-layout.csv when UI is involved
- current Change's design/baseline-impact.md, baseline-binding.json, baseline-status.md
- architecture sections matched by design domain: system-context/domain-boundaries/logical-erd/data-flows/technology-decisions/api-conventions/frontend-conventions/test-strategy
- docs/product/BASELINE-BRIEF.md
- docs/product/open-questions.md (relevant items only)
- existing functionality code location (if modifying existing functionality)

> Budget (advisory): 8/8 items; when exceeded, narrow the scope or record why the extra reads are needed.

**On-demand inputs (read after a trigger; not counted in the default budget)**

- docs/product/acceptance-policy.md
- docs/architecture/system-context.md
- docs/architecture/domain-boundaries.md
- docs/architecture/logical-erd.md
- docs/architecture/data-flows.md
- docs/architecture/technology-decisions.md
- docs/architecture/api-conventions.md
- docs/architecture/frontend-conventions.md
- docs/architecture/test-strategy.md
- docs/adr/*

**Full contract inputs (content/material, audit set)**

- N/A

**Full contract inputs (documents/files, audit set)**

- openspec/changes/<change-id>/tasks.md, design.md (approved)
- openspec/changes/<change-id>/specs/<capability>/spec.md, design/user-stories.md (AC)
- openspec/changes/<change-id>/api/openapi.yaml, design/api-io-mapping.csv, design/io-catalog.csv, design/interface-catalog.csv (when applicable)
- openspec/changes/<change-id>/design/test-cases.csv (implement and run tests by TEST ID)
- openspec/changes/<change-id>/design/figma-audit.md (when UI is involved, read the target framework/transcoding notes, actual token values/PAGE specs/state decisions; 06 freezes the PAGE list), design/figma-code/ (target-framework design code transcoded in 06 according to the overall technology selection), and design/figma-layout.csv (assertion mapping)
- openspec/changes/<change-id>/traceability.csv
- docs/architecture/quality-gates.json (when adopted; frozen static analysis gates) and openspec/changes/<change-id>/design/static-waivers.json (when present; Change-scoped waivers applied by the runner and checker)
- docs/architecture/system-context.md, domain-boundaries.md, logical-erd.md, data-flows.md, technology-decisions.md, api-conventions.md, frontend-conventions.md, test-strategy.md, docs/adr/README.md (implementation constraints); docs/product/open-questions.md (read-only; implementation must not close unresolved questions unilaterally)
- openspec/changes/<change-id>/design/baseline-impact.md (approved baseline snapshot)
- docs/architecture/baseline-status.md (current version)
- openspec/changes/<change-id>/design/baseline-binding.json (approved constraint bindings)

**Outputs (content/material)**

- actual source code/migrations/configuration
- automated test code and run results
- implementation/verification evidence
- conditionally applicable: baseline change request/ADR draft (when conflicts are found; do not update the frozen baseline without approval)

**Outputs (documents/files)**

- openspec/changes/<change-id>/design/evidence/code-review.md (when UI is involved, includes a ## UI fidelity per-PAGE numeric table: Figma node/asserted element count/max deviation/layout evidence/deviations/conclusion/approver; numbers are taken directly from figma-layout-check.json; only deviation/UI-DERIVED PAGEs require manual explanation and approval; when quality gates are adopted, includes a ## Static analysis table copied verbatim from static-analysis.json: per stack/tool command, config path @ SHA-256, result, literal exit 0, and applied waivers with approver)
- openspec/changes/<change-id>/design/evidence/static-analysis.json (when quality gates are adopted; produced by scripts/run-quality-gates.py: per blocking stack/tool command, cwd, exit code, config SHA-256, gates SHA-256, source revision, applied waivers, verdict)
- openspec/changes/<change-id>/design/evidence/static-analysis-logs/ (when quality gates are adopted; one captured log per blocking stack/tool; the log filename derives from the sanitized stack root plus the tool id)
- openspec/changes/<change-id>/design/evidence/figma-layout-check.json (per-element expected/actual/delta evidence from scripts/check-figma-layout.py)
- openspec/changes/<change-id>/tasks.md (checkbox status updated by implementation; MUTABLE by 08)
- openspec/changes/<change-id>/design/evidence/implementation-diff.json (commit/diff SHA-256 and changed paths at the verified revision)

**Output consumers**

- openspec/changes/<change-id>/design/evidence/code-review.md → 09, 10
- openspec/changes/<change-id>/tasks.md → 09
- openspec/changes/<change-id>/design/evidence/implementation-diff.json → 09, 10
- openspec/changes/<change-id>/design/evidence/static-analysis.json → 09, 10
- openspec/changes/<change-id>/design/evidence/static-analysis-logs/ → evidence-only
- openspec/changes/<change-id>/design/evidence/figma-layout-check.json → 09, 10

**Downstream handoff**

- code diff, test report, review conclusion, unresolved issues, figma-layout-check.json, and token check results
- when quality gates are adopted: openspec/changes/<change-id>/design/evidence/static-analysis.json, openspec/changes/<change-id>/design/evidence/static-analysis-logs/, and the ## Static analysis section in design/evidence/code-review.md

**Approval and gates**

- Approval: code review blockers closed; merging is approved separately according to project permissions
- Gate: TDD; scripts/test-all.sh; scripts/verify-before-completion.sh; when docs/architecture/quality-gates.json exists: python scripts/check-quality-gates.py --root . --strict --require-materialized; python scripts/run-quality-gates.py <change-id> --output openspec/changes/<change-id>/design/evidence/static-analysis.json --identity <builder>; python scripts/check-static-analysis.py --change <change-id> --strict (the authoritative 08 static-analysis transition command); scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900; scripts/check-design-tokens.py --change <change-id> --tokens <token.css>; scripts/check-code-review.py --change <change-id> --strict (UI Change ## UI fidelity numbers are taken directly from figma-layout-check.json; only deviation/UI-DERIVED PAGEs require manual explanation; ## Static analysis rows are copied from static-analysis.json when gates are adopted); baseline-governance.py check-change --phase implementation

**Baseline interaction**

- Read-only: approved design/baseline-impact.md; current docs/architecture/baseline-status.md version
- Produce/review: records of baseline conflicts found during implementation, and baseline change requests/ADRs when applicable
- Gate: do not modify the frozen baseline directly; pause affected tasks while unapproved; after approval, refresh the Change snapshot and re-verify

---

### 09 Independent verification and acceptance evidence

- Scope: feature-level
- Skill: `independent-verifier`
- Prompt: `prompts/09-independent-verification.md`
- Dependencies (DAG): `08-implementation-orchestrator`

**Lean inputs (default reads, advisory budget)**

- implemented code and revision/diff fingerprint
- current Change's proposal/specs/design/user-stories/tasks
- when applicable: api/openapi.yaml, api-io-mapping.csv, io-catalog.csv, interface-catalog.csv
- figma-audit.md, figma-layout.csv, figma-layout-check.json when UI is involved
- test-cases.csv, traceability.csv, code-review.md, Builder test evidence
- docs/product/BASELINE-BRIEF.md
- docs/product/acceptance-policy.md
- current Change's baseline-impact.md, baseline-binding.json, baseline-status.md

> Budget (advisory): 8/8 items; when exceeded, narrow the scope or record why the extra reads are needed.

**On-demand inputs (read after a trigger; not counted in the default budget)**

- docs/architecture/system-context.md
- docs/architecture/domain-boundaries.md
- docs/architecture/logical-erd.md
- docs/architecture/data-flows.md
- docs/architecture/technology-decisions.md
- docs/architecture/api-conventions.md
- docs/architecture/frontend-conventions.md
- docs/architecture/test-strategy.md
- docs/adr/*
- docs/product/open-questions.md

**Full contract inputs (content/material, audit set)**

- implemented code and revision/diff fingerprint

**Full contract inputs (documents/files, audit set)**

- openspec/changes/<change-id>/proposal.md, specs/<capability>/spec.md, design.md, tasks.md, design/user-stories.md (approved requirements, design, and AC)
- openspec/changes/<change-id>/api/openapi.yaml, design/api-io-mapping.csv, design/io-catalog.csv, design/interface-catalog.csv (when applicable)
- openspec/changes/<change-id>/design/figma-audit.md (when UI is involved, compare against the target framework/transcoding notes, actual token values/PAGE specs/state decisions), design/figma-code/ (target-framework design code transcoded in 06 according to the overall technology selection), and design/figma-layout.csv (assertion mapping)
- docs/product/acceptance-policy.md (project-level acceptance criteria)
- openspec/changes/<change-id>/design/test-cases.csv (test cases and execution result verification)
- openspec/changes/<change-id>/design/evidence/code-review.md, Builder test and verification evidence; docs/product/open-questions.md (read-only; verification must not close unresolved questions unilaterally)
- openspec/changes/<change-id>/traceability.csv (traceability matrix)
- docs/architecture/quality-gates.json and openspec/changes/<change-id>/design/static-waivers.json (when adopted; frozen gates and Change-scoped waivers independently re-checked)
- openspec/changes/<change-id>/design/evidence/static-analysis.json (when quality gates are adopted; 08 builder evidence and builder identity; 09 independently re-runs the gates)
- approved baseline snapshot and baseline-impact.md
- openspec/changes/<change-id>/design/baseline-binding.json (approved constraint bindings)
- docs/architecture/baseline-status.md (current version)
- openspec/changes/<change-id>/design/evidence/figma-layout-check.json (measured in 08; 09 must independently rerun check-figma-layout.py)
- openspec/changes/<change-id>/design/evidence/implementation-diff.json (commit/diff SHA-256 and changed paths at the verified revision)
- docs/adr/README.md and docs/adr/* (read approved architecture decisions on demand)

**Outputs (content/material)**

- N/A

**Outputs (documents/files)**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md
- openspec/changes/<change-id>/design/evidence/independent-verification.json
- openspec/changes/<change-id>/design/evidence/static-analysis-independent.json (when quality gates are adopted; independent rerun evidence with distinct verifier and builder identities; produced by scripts/run-quality-gates.py --independent)

**Output consumers**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md → 10
- openspec/changes/<change-id>/design/evidence/independent-verification.json → 10
- openspec/changes/<change-id>/design/evidence/static-analysis-independent.json → 10

**Downstream handoff**

- independent verification report and JSON evidence (including static_checks when quality gates are adopted)
- static-analysis-independent.json when quality gates are adopted
- per-AC verification results
- test commands and exit codes
- layout_checks (per-PAGE asserted element count/max deviation/tolerance/missing elements/result/evidence)
- findings and items not executed

**Approval and gates**

- Approval: independent verification PASS; the Verifier must not be the same execution context as the Builder for this change; failures/blockers return to the implementation stage
- Gate: scripts/check-independent-verification.py; all applicable AC PASS, test exit codes 0, revision stable, read-only, no BLOCKER/CRITICAL; when docs/architecture/quality-gates.json exists: python scripts/run-quality-gates.py <change-id> --independent --identity <verifier> --builder-identity <08 builder> --output openspec/changes/<change-id>/design/evidence/static-analysis-independent.json; python scripts/check-static-analysis.py --change <change-id> --expect-independent (all static_checks PASS, no gates drift, no expired/invalid waivers); when UI is involved, all layout_checks PASS and test_runs include an independent rerun of check-figma-layout.py exit 0 and check-design-tokens.py exit 0; manual visual spot checks only on deviation/UI-DERIVED/unasserted PAGEs; baseline-governance.py check-change --phase implementation

---

### 10 Human acceptance, archive, and baseline write-back

- Scope: single feature Change
- Skill: `acceptance-audit`
- Prompt: `prompts/10-acceptance-audit.md`
- Dependencies (DAG): `09-independent-verification`

**Lean inputs (default reads, advisory budget)**

- independent-verification-report.md and independent-verification.json
- current Change's specs, user-stories, traceability.csv, design.md, code-review.md
- figma-audit.md, figma-layout.csv, figma-layout-check.json when UI is involved
- test-cases.csv, interface-catalog.csv
- current Change's baseline-impact.md, baseline-binding.json, baseline-status.md
- docs/product/acceptance-policy.md, BASELINE-BRIEF.md, change-sizing.md
- docs/product/decisions.md, assumptions.md, id-conventions.md
- running acceptance environment entry point

> Budget (advisory): 8/8 items; when exceeded, narrow the scope or record why the extra reads are needed.

**On-demand inputs (read after a trigger; not counted in the default budget)**

- design/figma-code/
- docs/adr/*
- docs/product/requirements-analysis.md
- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/business-rules.md
- docs/product/lessons.md

**Full contract inputs (content/material, audit set)**

- implemented code and test evidence
- running acceptance environment entry point (URL/route; for manual UI acceptance, sign off PAGEs with no deviations from machine evidence and check deviation/UI-DERIVED PAGEs side by side; do not use screenshots)

**Full contract inputs (documents/files, audit set)**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md and independent-verification.json (must PASS; revision must match the current acceptance code)
- openspec/changes/<change-id>/specs/<capability>/spec.md, design/user-stories.md, traceability.csv (approved AC/specs/traceability)
- openspec/changes/<change-id>/design.md (design basis)
- openspec/changes/<change-id>/design/evidence/code-review.md
- openspec/changes/<change-id>/design/evidence/implementation-diff.json (verified revision fingerprint)
- docs/architecture/quality-gates.json and openspec/changes/<change-id>/design/static-waivers.json (when adopted; gates file and Change-scoped waivers checked for expiry/validity)
- openspec/changes/<change-id>/design/evidence/static-analysis.json and openspec/changes/<change-id>/design/evidence/static-analysis-independent.json (when quality gates are adopted; acceptance reconciles ## Static analysis with these evidence files and rejects a non-PASS verdict, gates drift, or expired/invalid waivers)
- openspec/changes/<change-id>/design/figma-audit.md (when UI is involved, verify the target framework/transcoding notes, actual token values/PAGE specs/state consistency with the Figma review file), design/figma-code/ (target-framework design code transcoded in 06 according to the overall technology selection), design/figma-layout.csv (assertion mapping), and design/evidence/figma-layout-check.json (must PASS)
- openspec/changes/<change-id>/design/test-cases.csv (acceptance test coverage evidence)
- openspec/changes/<change-id>/design/interface-catalog.csv (cross-boundary interface acceptance evidence)
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md (current version)
- openspec/changes/<change-id>/design/baseline-binding.json (all applicable constraints have final verification evidence)
- docs/product/acceptance-policy.md (project-level acceptance criteria)
- docs/product/BASELINE-BRIEF.md, change-sizing.md (DoD), lessons.md, open-questions.md (resident baseline, definition of done, historical lessons, and open questions; open-questions is read-only)
- docs/product/decisions.md, assumptions.md (decision and assumption registers to be updated with acceptance results)
- docs/product/id-conventions.md (allocation rules for write-back baseline and Change IDs)
- docs/adr/README.md and docs/adr/* (read approved architecture decisions on demand)

**Outputs (content/material)**

- shared mutable write-back: lessons/decisions/assumptions registries (owned by Stage 02; Stage 10 appends/updates them without re-declaring them as outputs)
- acceptance report and approval records
- OpenSpec archive results and updated main specs (only after approval)

**Outputs (documents/files)**

- openspec/changes/<change-id>/design/evidence/acceptance.md (when UI is involved, includes ## UI acceptance per-PAGE sign-off: Figma node/running system entry/deviation approval/acceptance method (machine evidence/side-by-side check)/reviewer; when quality gates are adopted, includes ## Static analysis reconciled from static-analysis.json and static-analysis-independent.json: per stack/tool command, result, literal exit 0, and every applied waiver with approver)

**Output consumers**

- openspec/changes/<change-id>/design/evidence/acceptance.md → evidence-only

**Downstream handoff**

- accepted and archived capability specs, acceptance evidence, and dependencies of subsequent Changes

**Approval and gates**

- Approval: archive only after explicit approval by the product owner; do not bypass with -y
- Gate: scripts/check-acceptance.py (UI Changes validate ## UI acceptance per-PAGE running entry/sign-off and figma-layout-check.json PASS; PAGEs with no deviations may be signed off in bulk from machine evidence; deviation/UI-DERIVED PAGEs are checked side by side); when docs/architecture/quality-gates.json exists: verify-before-completion.sh (static gates run by default) and static-analysis evidence reconciled in ## Static analysis; non-PASS verdict, gates drift, or expired/invalid waivers block acceptance; actually run openspec validate/archive; stage 09 independent verification must PASS and the revision must be unchanged; baseline-governance.py check-change --phase acceptance

**Baseline interaction**

- Read-only: design/baseline-impact.md; current baseline status; approved ADRs/baseline change requests
- Produce/review: update docs/product/lessons.md, decisions.md, assumptions.md (write back only cross-feature decisions that are approved, implemented, and verified); impact review checklist for in-flight Changes; when the frozen baseline must be updated, submit a baseline amendment request and follow the open-amendment/close-amendment process; do not write baseline files directly
- Gate: write back only approved/implemented/verified cross-feature decisions; feature details stay in the Change

---
