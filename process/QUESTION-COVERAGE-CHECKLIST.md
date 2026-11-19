# Stage Question Coverage Checklist (02 / 03 / 05 / 07)

> Language: English | [简体中文](QUESTION-COVERAGE-CHECKLIST-zh.md)

> Status: RECOMMENDED (stage elicitation aid; not a hard gate; the evidence block is optional)
> Change ID: N/A (process document)
> Scope: 02 Requirements business analysis, 03 Overall project architecture design, 05 Proposal-level requirements analysis, 07 Detailed design/interface/test design
> Related requirements/AC: N/A (process document)
> Source basis: `process/STEP-ARTIFACT-CONTRACTS.md`, `process/STEP-ARTIFACT-CONTRACTS.json`, `prompts/02-requirements-analysis.md`, `prompts/03-project-architecture-baseline.md`, `prompts/05-feature-requirements.md`, `prompts/07-detailed-design.md`, and the matching Skills under `.claude/skills/`
> Generated: 2026-11-18

## 1. Purpose and Use

The prompts are strong at artifact structure but uneven at elicitation. This checklist turns "what downstream stages need" into a per-stage question list. It is a working aid for stage execution and review, not a machine gate: stages decide which items apply and are not required to record a row for every item.

Use it as follows:

1. At stage start, skim the table for the current stage and pick the questions that actually affect this project or Change.
2. Use the suggested questions to prepare interviews; skip items that genuinely do not apply rather than producing "n/a" compliance rows.
3. Write answers into the declared artifact section; unknown or unconfirmed items go to `docs/product/open-questions.md` with an owner and blocking condition.
4. At stage end, apply the downstream-consumption question: **can the next stage produce its declared artifacts without asking the user again?**
5. If it helps the stage record coverage, add an optional `question_coverage` block to the evidence; it is shape-checked but does not require a fixed item list.

When a stage does record `question_coverage`, the status vocabulary is:

| Status | Meaning | Required record |
|---|---|---|
| `ANSWERED` | The question has a real answer | Answer summary, source, landing point |
| `N/A` | The item genuinely does not apply | Reason |
| `OPEN` | The answer is unknown or unconfirmed | Owner, blocking condition, open-question file |
| `DEFERRED` | Deliberately postponed | Reason, approver, target stage/Change |

## 2. Current Coverage Snapshot

Legend: `Q` = an explicit question/interview exists in the current Prompt/Skill; `F` = a template field or output exists, but no elicitation question or hard validation; `-` = neither a question nor a field. This table is diagnostic, not the target state.

| ID | Information thread | 02 | 03 | 05 | 07 |
|---|---|---|---|---|---|
| T01 | Goal, scope, success metrics | Q | F | Q | F |
| T02 | Scale and capacity | - | - | - | - |
| T03 | Organization, roles, permissions, approval chain | F | F | Q | Q |
| T04 | Flows, exceptions, compensation | Q | Q | Q | Q |
| T05 | Data objects, rules, codes, units | Q | Q | F | Q |
| T06 | Data lifecycle, privacy, compliance | F | F | - | F |
| T07 | External systems, devices, terminals, offline | F | Q | Q | Q |
| T08 | Reports, printing, export, traceability certificates | - | - | - | - |
| T09 | Non-functional requirements | F | F | - | F |
| T10 | Migration, compatibility, rollback | F | F | - | F |
| T11 | Acceptance, pilot, UAT, training | F | F | F | F |
| T12 | Runtime, release, monitoring, operations, DR | - | F | - | F |
| T13 | Owners and RACI | - | F | - | - |
| T14 | Business calendar, seasonality, deadlines | F | - | - | - |
| T15 | Test strategy, environments, data, doubles | - | Q | F | Q |

The most visible broken threads are T02 (scale/capacity), T06 (data lifecycle/privacy), T08 (reports/printing), T09 (NFR), T10 (migration), T11 (acceptance), T13 (owners/RACI), and T14 (business calendar). None of them is owned end to end by one stage today.

## 3. Stage Checklists

### 3.1 Stage 02: Requirements Business Analysis

| ID | Must clarify | Suggested question | Landing point | Downstream consumer | Status |
|---|---|---|---|---|---|
| 02-T01-01 | Goal, scope, non-goals, KPI baseline and target | What is the project goal, the first-release scope, what is explicitly out of scope, and what measurable baseline/target defines success? | `docs/product/requirements-analysis.md` §1; `BASELINE-BRIEF.md` | 03 system context; 04 slicing; 05 AC; 10 acceptance | [ ] |
| 02-T02-01 | Expected scale and volume | How many users and roles, concurrent users, farms/plots/greenhouses, devices, batches/records, daily and peak transactions, data growth, and retention years? | `requirements-analysis.md` §6 NFR; `data-objects.csv`; `change-sizing.md` | 03 capacity/deployment; 04 slice size; 07 indexes/pagination; 08 load test | [ ] |
| 02-T03-01 | Organization, roles, permissions, approval chain | What is the organization hierarchy (company/cooperative/base/farmer), who approves for whom, who can see whose data, and are delegation/separation of duties required? | `role-permission-matrix.csv`; `business-rules.md`; `rd-matrix.csv` | 03 identity model; 05 permission AC; 06 page visibility; 07 permission design | [ ] |
| 02-T04-01 | Complete flow and node registration | Does every main, alternative, exception, and compensation flow have executable nodes with role, input/output DO, preconditions, actions, branches, and next node? | `workflows.md`; `rd-matrix.csv` | 03 data flows; 05 scenarios; 07 errors/compensation | [ ] |
| 02-T04-02 | Manual override, correction, rollback authority | When a human takes over, corrects, or rolls back a business action, who may do it, what is audited, and who is notified? | `workflows.md` exception nodes; `business-rules.md`; `open-questions.md` | 03 audit/control; 05 exception AC; 07 audit/error design | [ ] |
| 02-T05-01 | Business keys, codes, units, terms | What are the business keys and numbering rules for plots, batches, varieties, pesticides/fertilizers, and what units, precision, status dictionaries, synonyms, or local terms are used? | `data-objects.csv`; `glossary.md`; `id-conventions.md`; `business-rules.md` | 06 copy/terminology; 07 data model/API | [ ] |
| 02-T06-01 | Data lifecycle, privacy, retention | Where does data come from, who owns it, how long is it retained, when is it archived/deleted/exported, what is legally held, and which fields are personal or sensitive? | `business-rules.md`; `data-objects.csv`; NFR table; `open-questions.md` | 03 data governance; 05 privacy AC; 07 masking/retention | [ ] |
| 02-T07-01 | External systems and third-party inventory | Which external systems, regulators, traceability platforms, weather/map/payment/SMS/WeChat/ERP/logistics services are needed, for what purpose, with what data flow, account/sandbox, SLA, approval, and privacy terms? | `requirements-analysis.md` §6/§7; `reference-research.md`; `open-questions.md` | 03 third-party list; 05 scenarios; 07 interface catalog | [ ] |
| 02-T07-02 | Field terminals, network, offline, devices | What terminals (phone/PDA/tablet/PC) are used in the field, is there network coverage, is offline work required, and are scanning/camera/GPS/weighing/printing needed? | `workflows.md` node inputs; `requirements-analysis.md`; NFR table | 03 platform; 06 interaction; 07 interfaces | [ ] |
| 02-T08-01 | Reports, ledgers, certificates, export, print | Which reports, ledgers, traceability certificates, or regulatory submissions are required, with what dimensions, frequency, export format, print/signature/QR needs? | `requirements-analysis.md`; `workflows.md`; `acceptance-policy.md` | 06 print layout; 07 IO/export; 08/10 acceptance | [ ] |
| 02-T09-01 | Quantified NFR targets | What are the quantified targets for performance, availability, RPO/RTO, offline tolerance, security, privacy, audit retention, accessibility, and compliance (MLPS/xinchuang/industry rules)? | `requirements-analysis.md` §6 NFR table | 03 constraints; 05 NFR AC; 07 NFR tests; 08/09 verification | [ ] |
| 02-T10-01 | Legacy data source, volume, quality, migration | What legacy data exists (paper/Excel/old system), how much, how clean, who cleans it, how will it be migrated, how long will dual-run last, and when does the old system stop? | `workflows.md`; `requirements-analysis.md` §7; `open-questions.md` | 03 migration; 04 dependency; 07 backfill; 08 cutover | [ ] |
| 02-T11-01 | Acceptance, pilot, training | Who accepts, with which scenarios/data, at which pilot site/users, and who trains and supports users after go-live? | `acceptance-policy.md` | 04 acceptance direction; 05 verification; 10 acceptance | [ ] |
| 02-T13-01 | Owners, approvers, RACI | Who are the business/product/technical/design/acceptance owners and approvers, and what is the decision SLA? | `decisions.md`; `BASELINE-BRIEF.md`; `open-questions.md` | All stage approval gates | [ ] |
| 02-T14-01 | Business calendar, seasonality, deadlines | What are the planting/harvest/processing/sales windows, safety intervals, regulatory reporting deadlines, holidays, and blackout periods? | `business-rules.md`; `acceptance-policy.md`; `change-sizing.md` | 04 ordering; 05 time-window AC; 07 scheduling; 08 test data | [ ] |
| 02-T15-01 | Test and acceptance inputs | Which environments, real devices, third-party sandboxes, and sample data are available for acceptance and testing? | `acceptance-policy.md`; `open-questions.md` | 03 test strategy; 07 test design; 08 execution | [ ] |

### 3.2 Stage 03: Overall Project Architecture Design

| ID | Must clarify | Suggested question | Landing point | Downstream consumer | Status |
|---|---|---|---|---|---|
| 03-T01-01 | Architecture goals aligned with Stage 02 | Which business goals and success metrics must the architecture preserve, and which quality goals must be frozen as baseline constraints? | `system-context.md`; `technology-decisions.md`; `constraint-registry.json` | 04 slicing; 05 baseline impact; 07 design constraints | [ ] |
| 03-T02-01 | Capacity, HA/DR, RPO/RTO | What are the expected capacity, concurrency, peak load, growth, and retention, and what HA/DR, RPO, and RTO targets follow from them? | `containers-and-deployment.md`; `constraint-registry.json`; `test-strategy.md` | 05 NFR AC; 07 indexes/capacity; 08 load test; 10 ops acceptance | [ ] |
| 03-T02-02 | Performance, availability, SLO | What are the quantified performance/availability/SLO targets, and how will each be verified? | `technology-decisions.md`; `constraint-registry.json`; `test-strategy.md` | 05 AC; 07 tests; 08/09 verification | [ ] |
| 03-T03-01 | Identity and authorization model | Which authentication methods (SSO/AD/LDAP/WeChat/SMS), authorization model (RBAC/ABAC), multi-tenant isolation, account lifecycle, MFA, and session rules are required? | `technology-decisions.md`; `api-conventions.md`; `constraint-registry.json` | 05 permission AC; 06 page visibility; 07 permission design | [ ] |
| 03-T04-01 | Data flows, events, compensation | Do the DF records cover every FLOW/NODE/DO/RD entry, including sync/async, transaction boundaries, failures, compensation, ordering, DLQ, and replay semantics? | `data-flows.md`; `api-conventions.md` | 05 scenarios; 07 interface/error design; 08 implementation | [ ] |
| 03-T05-01 | Domain model, data ownership, conventions | Do domain boundaries, entities, lifecycle, ownership, and the logical ERD cover every DO, and are naming, IDs, audit fields, time, deletion, concurrency version, and retention conventions defined? | `domain-boundaries.md`; `logical-erd.md`; `constraint-registry.json` | 05 DO references; 07 data model/API | [ ] |
| 03-T06-01 | Data classification, privacy, compliance | What are the data classifications (public/internal/sensitive/PII), encryption (transit/at rest), key management, masking, retention, deletion/export, legal hold, and cross-border rules? | `technology-decisions.md`; `constraint-registry.json`; `api-conventions.md` | 05 privacy AC; 07 masking/retention; 08/09 audit | [ ] |
| 03-T07-01 | Platform and integration boundary inventory | Have client form, cross-platform approach, native plugins/JS Bridge, device/IoT protocols, third-party platforms, and every interface boundary been registered with protocol, auth, contract, errors, timeout/retry/idempotency, version, test, and owner? | `technology-decisions.md`; `api-conventions.md`; `frontend-conventions.md`; `data-flows.md`; `constraint-registry.json` | 05 scenarios; 06 design; 07 interface catalog; 08 implementation | [ ] |
| 03-T07-02 | Offline, degradation, push, deep links | What are the offline cache, sync-conflict, permission-denial/degradation, push/deep-link, hot-update, and app-store compliance rules? | `frontend-conventions.md`; `data-flows.md` | 05 offline AC; 06 interaction; 07 frontend/native design | [ ] |
| 03-T08-01 | Reporting, BI, print, export, read model | Are reports/BI/printing/export/read models in scope, and what are their data sources, refresh frequency, permissions, and export formats? | `system-context.md`; `containers-and-deployment.md`; `api-conventions.md`; `data-flows.md` | 05 report AC; 06 print layout; 07 IO/export design | [ ] |
| 03-T09-01 | NFR frozen as verifiable constraints | Are all NFRs quantified into verifiable constraints, each with an owner, verification method, and evidence path? | `constraint-registry.json`; `test-strategy.md` | 05 NFR AC; 07 NFR tests; 08/09 verification | [ ] |
| 03-T09-02 | Static analysis adoption and toolchain | Does this project adopt static-analysis gates? If not, record the decision and reason. If yes, per selected language, which tools (lint/format/type/style) are chosen, with what version pinning, package/plugin list, config landing paths, blocking severities and zero-finding policy, and what waiver policy (Change-scoped file, approver, expiry)? Can a from-scratch repository run them offline (no package fetch)? | `technology-decisions.md` `## Static Analysis Toolchain`; `test-strategy.md` `## Static Analysis and Quality Gates`; `docs/architecture/quality-gates.json` (when adopted); `constraint-registry.json` `QUALITY-STATIC-001` (ACTIVE when adopted, RETIRED otherwise) | 05 applicable constraints; 07 config/waiver plan; 08 gates; 09 independent rerun; 10 acceptance | [ ] |
| 03-T10-01 | Legacy migration and coexistence | What is the legacy data migration, dual-run, cutover, decommission, and rollback strategy, and what is the boundary between old and new systems? | `technology-decisions.md`; `containers-and-deployment.md`; `data-flows.md`; `constraint-registry.json` | 04 dependency; 05 migration AC; 07 backfill; 08 cutover | [ ] |
| 03-T11-01 | Test strategy and test inputs | What are the test levels, contract/integration/E2E/performance/security/UAT strategy, and who provides environments, real devices, third-party sandboxes, and test data? | `test-strategy.md`; `docs/project/toolchain-report.md` | 05 verification; 07 test design; 08 execution | [ ] |
| 03-T12-01 | Environments, release, observability, DR | What are the dev/test/staging/prod topology, network zones, domains/certificates/VPN, release/rollback/canary/feature flags, DB migration policy, logs/metrics/traces/alerts/SLO/on-call/runbook, and backup/DR? | `containers-and-deployment.md`; `test-strategy.md`; `constraint-registry.json` | 07 configs/release; 08 implementation; 10 acceptance environment | [ ] |
| 03-T13-01 | Baseline owners and approvals | Who owns and approves each baseline domain (product/architecture/data/API/frontend/test), and what are the constraint levels, exception flow, and approval evidence? | `baseline-manifest.json`; `constraint-registry.json`; `baseline-status.md` | 04/05 baseline gates; 07/08/09/10 constraint checks | [ ] |
| 03-T14-01 | Batch and scheduling windows | What are the batch/scheduled-job/report-generation windows and SLAs, and how do they relate to the business calendar and regulatory deadlines? | `containers-and-deployment.md`; `data-flows.md`; `test-strategy.md` | 05 time-window AC; 07 scheduling; 08 test data | [ ] |

### 3.3 Stage 05: Proposal-Level Requirements Analysis

| ID | Must clarify | Suggested question | Landing point | Downstream consumer | Status |
|---|---|---|---|---|---|
| 05-T01-01 | Change value, scope, non-goals, success metrics | What value does this Change deliver, what is explicitly out of scope, how is success measured, and which ACs block acceptance versus which may be deferred? | `proposal.md`; `design/user-stories.md`; `change-sizing.md` | 06 page scope; 07 design; 10 acceptance | [ ] |
| 05-T03-01 | Roles, capabilities, data scope, degradation | Which ROLE/CAP/data scopes does this Change touch, and what does the user see when permission is denied, degraded, delegated, or masked? | `design/user-stories.md` AC; `specs/<capability>/spec.md` Scenario; `baseline-impact.md` | 06 page visibility; 07 permission design; 09 verification | [ ] |
| 05-T04-01 | US and scenario completeness | Does every user story state trigger, role, preconditions, main/alternative/exception paths, postconditions, and associated FLOW/NODE/DO/BR, with Given/When/Then for each key path? | `design/user-stories.md`; `specs/<capability>/spec.md` Scenario | 06 pages; 07 tests; 09 verification | [ ] |
| 05-T05-01 | Field-level rules | What are the validation, calculation, unit, precision, state-transition, uniqueness, duplicate-submission, and concurrency rules for each field or data object? | `specs/<capability>/spec.md` Scenario; `design/user-stories.md` AC; `business-rules.md` | 07 data model/API; 08 implementation | [ ] |
| 05-T06-01 | PII and data-lifecycle behavior | Which PII/sensitive fields does this Change touch, and what are the observable retention, deletion, export, and audit behaviors? | `specs/<capability>/spec.md` Scenario; AC; `baseline-impact.md` | 07 masking/retention; 08/09 audit | [ ] |
| 05-T07-01 | Multi-platform, offline, third-party failure | What are the observable behaviors for multi-platform, device, offline/weak network, push/deep link, third-party failure/timeout/rate limit/degradation, and manual fallback? | `specs/<capability>/spec.md` Scenario; AC | 06 states; 07 interface/error design; 08 tests | [ ] |
| 05-T08-01 | Reports, printing, export, certificates | Does this Change produce reports, prints, exports, or traceability certificates, and what are their ACs? | `specs/<capability>/spec.md` Scenario; AC | 06 print layout; 07 IO/export; 10 acceptance | [ ] |
| 05-T09-01 | NFR converted to acceptance | Which NFRs does this Change inherit, and what threshold, evidence, environment, and acceptance method make each verifiable? | AC; `baseline-binding.json`; `acceptance-policy.md` | 07 NFR tests; 08/09 verification | [ ] |
| 05-T10-01 | Migration, compatibility, rollback | Does this Change touch legacy data, APIs, or pages, and what are the ACs for migration correctness, dual-run, rollback, and backward compatibility? | AC; `baseline-impact.md`; `proposal.md` Impact | 07 backfill; 08 cutover | [ ] |
| 05-T11-01 | AC verification and acceptance inputs | For every AC, what is the verification method, environment, data, and acceptance owner, and who provides the pilot users and acceptance data? | `design/user-stories.md` AC; `acceptance-policy.md`; `traceability.csv` | 07 test design; 09 verification; 10 acceptance | [ ] |
| 05-T14-01 | Business-calendar ACs | Is this Change constrained by planting/harvest/sales windows, safety intervals, or regulatory deadlines, and what time-window ACs follow? | AC; `proposal.md`; `change-sizing.md` | 07 scheduling; 08 test data | [ ] |
| 05-T15-01 | Testability inputs | Which test data, doubles, real devices, and sandboxes are needed, and is every AC observable and assertable? | `specs/<capability>/spec.md` Scenario; AC; `test-cases.csv` (Stage 07) | 07 test design; 08 execution | [ ] |
| 05-T13-01 | Change owners and open-item owners | Who are the product owner, technical owner, and acceptance owner for this Change, and who closes each open question? | `proposal.md`; `decisions.md`; `open-questions.md` | 06/07/08/09/10 approvals | [ ] |

### 3.4 Stage 07: Detailed Design, Interfaces, and Test Design

| ID | Must clarify | Suggested question | Landing point | Downstream consumer | Status |
|---|---|---|---|---|---|
| 07-T01-01 | Design scope, non-goals, trade-offs, gaps | What are the design scope, non-goals, key trade-offs, design gaps, and entry conclusion for this Change? | `design.md` `## Design Decisions` | 08 implementation; 09 verification | [ ] |
| 07-T04-01 | Existing-code impact | Which files/classes/functions/interfaces/tables/tests/migrations are changed, with what strategy, compatibility, rollback, risk, and verification? | `design.md` `### Existing Code Change Impact` | 08 implementation | [ ] |
| 07-T05-01 | Data model, volume, indexing | Does the data model cover every DO/AC, and what are the expected data volume, growth, index, pagination, archive, and partition strategy? | `design.md` `## Backend Detailed Design`; `api/openapi.yaml`; `design/io-catalog.csv` | 08 implementation; 08 performance test | [ ] |
| 07-T06-01 | Privacy implementation | Where are PII/sensitive fields classified, masked, encrypted, retained, deleted, exported, and audited across components, interfaces, and tables? | `design.md` `### Shared Concerns`; `design/io-catalog.csv`; `design/test-cases.csv` | 08 implementation; 09 audit verification | [ ] |
| 07-T07-01 | Cross-boundary interface catalog | Have all HTTP/native/device/third-party/IoT/async/file boundaries registered protocol, auth, contract, errors, timeout/retry/idempotency, version, tests, and owner? | `design/interface-catalog.csv`; `design.md` `## Interface Design` | 08 implementation; 09 interface verification | [ ] |
| 07-T08-01 | Report, print, export, file storage | Where do report/print/export/file-storage features land in interfaces, tables, and components, with format, permission, retention, and failure paths? | `design.md` Interface/Backend; `design/io-catalog.csv`; `design/test-cases.csv` | 08 implementation; 10 acceptance | [ ] |
| 07-T09-01 | NFR test design | For every NFR (performance, load, security, accessibility, audit), what threshold, environment, data volume, and evidence will be used? | `design.md` `## Test Design`; `design/test-cases.csv` | 08 tests; 09 independent verification | [ ] |
| 07-T10-01 | Data migration execution | What are the backfill, transformation, validation, reconciliation, dual-run, rollback, and deploy-order steps for data migration? | `design.md` `### Data Model and Migration`; `design/test-cases.csv` | 08 cutover; 09 verification | [ ] |
| 07-T11-01 | UAT and acceptance inputs | What are the UAT/pilot scenarios, acceptance environment, seed data, manual verification steps, and who executes and signs off? | `design.md` `### Manual Verification`; acceptance evidence | 10 acceptance | [ ] |
| 07-T12-01 | Config, secrets, flags, release | How are configuration, secrets, feature flags, environment promotion, release, rollback, and runbook handled? | `design.md` `### Shared Concerns`; baseline constraints | 08 release; 10 acceptance | [ ] |
| 07-T12-02 | Observability and SLO | Where do logs, metrics, traces, alerts, SLOs, and audit logs land, and what are the thresholds and owners? | `design.md` `### Shared Concerns`; `design/test-cases.csv` | 08 implementation; 09/10 evidence | [ ] |
| 07-T15-01 | Test coverage and evidence | Does the test strategy cover every AC/page/operationId/IO/boundary with data, doubles, cleanup, and failure injection? | `design.md` `## Test Design`; `design/test-cases.csv`; `traceability.csv` | 08 execution; 09 verification | [ ] |
| 07-T15-02 | Offline, sync, multi-platform, device | Where do offline cache, sync conflict, multi-platform differences, JS Bridge, and device capabilities land in components, events, and interfaces? | `design.md` `## Frontend Detailed Design`; `design/interface-catalog.csv`; `design/test-cases.csv` | 08 implementation; 09 device verification | [ ] |
| 07-T15-03 | Static analysis config and waiver plan | When static analysis is adopted: which config files will 08 copy/pin into each stack root from the approved rule packs, do they match `quality-gates.json` (or is the deviation recorded), and which blocking findings need a Change-scoped waiver with approver and expiry inside `policy.waiver.max_days`? When not adopted, record `N/A + reason`. | `design.md` `### Static Analysis`; `design/static-waivers.json` (conditional) | 08 gates; 09 independent verification; 10 acceptance | [ ] |
| 07-T13-01 | Design and execution owners | Who owns design, implementation, testing, and acceptance, and what are the deadlines/blocking conditions for open decisions? | `design.md` `### Key Decisions and Trade-offs`; `### Open Decisions` | 08/09/10 approvals | [ ] |
| 07-T03-01 | Permission and audit implementation | How are permissions, data scope, masking, and audit implemented for every page, API, and IO? | `api/openapi.yaml`; frontend/backend sections; `design/test-cases.csv` | 08 implementation; 09 verification | [ ] |

## 4. Recommended Stage-Exit Checks

These are review aids, not a machine gate:

1. Items the stage chose to address have an answer or an explicit `N/A`/`OPEN`/`DEFERRED` status.
2. Every `OPEN` item appears in `docs/product/open-questions.md` with an owner and blocking condition.
3. Every `ANSWERED` item names a real landing point in a declared artifact.
4. The stage review passes the downstream-consumption test: the next stage can produce its declared artifacts without asking the user for missing facts.
5. If an item was intentionally postponed, recording `DEFERRED` with an approver and target stage is recommended; skipping an inapplicable item needs no status row.

## 5. Evidence and Handoff

- `question_coverage` is optional in stage evidence for 02/03/05/07. If present, `python scripts/check-question-coverage.py --step <step-id> --evidence <json>` validates each entry's status and fields, rejects duplicate `item_id`s, and checks that `landing` and `open_question` paths exist. It does not require a fixed item list and allows additional item IDs; `workflow.py request-review` / `transition` re-check the same optional block automatically.
- Shape example (entries need not cover the whole checklist; `landing` is one real artifact path, optionally with `#heading`):

```json
"question_coverage": [
  {
    "item_id": "02-T02-01",
    "status": "answered",
    "landing": "docs/product/requirements-analysis.md#6. Non-Functional Requirements",
    "owner": "product-owner",
    "date": "2026-11-18"
  },
  {
    "item_id": "02-T11-01",
    "status": "open",
    "owner": "product-owner",
    "blocking": "Pilot site and acceptance data not confirmed",
    "open_question": "docs/product/open-questions.md"
  },
  {
    "item_id": "02-T08-01",
    "status": "n/a",
    "reason": "No reports or printed certificates in this release"
  },
  {
    "item_id": "03-T10-01",
    "status": "deferred",
    "reason": "No legacy data to migrate in this release",
    "approver": "technical-lead",
    "target_step": "07-detailed-design"
  },
  {
    "item_id": "CUSTOM-01",
    "status": "answered",
    "landing": "docs/product/open-questions.md#resolved"
  }
]
```

- Do not claim an item is `answered` based on an assumption or an unread document. An answer without a source is `open`.
- Attaching the checklist to the stage handoff report as an appendix or summary table is optional.

## 6. Maintenance

- When a stage Prompt, Skill, template, or contract changes, update the affected checklist rows in the same change.
- When a downstream stage discovers a missing input, add a row here and record the source stage; do not fix it only in the downstream artifact.
- This checklist is guidance and does not change the hard gates; the optional `question_coverage` block's shape is validated by the checker.
- This checklist does not change the current hard gates. Making it mandatory requires a separate change to the stage contracts, prompts, and validators, with the usual stage review and approval.
