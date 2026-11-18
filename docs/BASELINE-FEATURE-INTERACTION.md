# Bidirectional Governance Rules Between the Project Baseline and Feature Changes

> Language: English | [简体中文](BASELINE-FEATURE-INTERACTION-zh.md)

> This document defines the responsibility boundary between the project-level baseline and feature-level OpenSpec Changes and is a mandatory rule for all feature development stages. Flow diagrams, Skills, Prompts, and stage contracts must not conflict with this document.

## 1. Core Principles

1. **The baseline constrains features first; features then feed back into the baseline.** Before requirements refinement, every feature Change must read the currently effective baseline and produce a baseline applicability/impact record.
2. **The baseline is shared rules, not a copy of feature design.** Feature Changes reference the baseline through file paths, versions, sections, and stable IDs, and do not copy the entire baseline.
3. **A feature Change is the authoritative change vehicle for the behavior of a single feature.** The current feature's behavior, pages, endpoints, local data migrations, IO, tests, and implementation details remain in that Change.
4. **Do not automatically modify the baseline just because "new implementation" is added.** Only cross-feature reuse, changes to shared rules, changes to system-level constraints, or evolution of project shared models are elevated to baseline changes.
5. **Baseline changes must be explicitly reviewed, approved, and versioned.** A frozen baseline must not be silently rewritten during feature development; unapproved candidate decisions cannot become constraints for other Changes.
6. **Baseline updates must not retroactively and silently change in-flight Changes.** After the baseline version changes, in-flight Changes must re-check applicability and record whether rebase / re-review is required.

## 2. What Authoritative Content the Project Baseline Contains

| Baseline domain | Authoritative files | Constraint type for features |
|---|---|---|
| Product baseline | `docs/product/requirements-analysis.md`, `workflows.md`, `data-objects.csv`, `rd-matrix.csv`, `business-rules.md`, `glossary.md`, `acceptance-policy.md` | Global business goals, shared flows and nodes, roles/data objects, RD matrix, business rules, terminology, acceptance criteria |
| Architecture baseline | `docs/architecture/system-context.md`, `domain-boundaries.md`, `containers-and-deployment.md`, `data-flows.md`, `technology-decisions.md`, `docs/adr/` | System/module boundaries, responsibilities and dependency direction, technology selection, deployment topology, cross-module integration methods |
| Data and domain baseline | `docs/architecture/logical-erd.md`, `domain-boundaries.md`, `data-flows.md` | Core entities and relationships, data ownership, domain invariants, shared transaction/consistency principles |
| Public API baseline | `docs/architecture/api-conventions.md` | Authentication and authorization, error model, versioning, pagination, idempotency, compatibility, and public response conventions |
| Frontend engineering baseline | `docs/architecture/frontend-conventions.md` | Routing, components/design system, state management, request layer, error and accessibility specifications |
| Test and quality baseline | `docs/architecture/test-strategy.md` | Test layering, mandatory quality gates, test environments, and release verification requirements |
| Baseline governance metadata | `docs/architecture/baseline-status.md` | Versions, effective status, approvers, effective dates, in-flight amendments, and waivers for each baseline domain |

OpenSpec `openspec/specs/**` and the design/governance baselines above are complementary: the OpenSpec main specs describe committed, externally observable capability behavior of the system; the project baseline documents describe business, architecture, data, and engineering constraints reused across features. Both must be checked at the start of a feature, and neither can replace the other.

## 3. What Must Be Read Before Feature Development

### 3.1 Fixed Reads (for Every Change)

- `docs/architecture/baseline-status.md`: verify whether it is FROZEN, plus the version, effective date, approvers, and pending amendments.
- `docs/product/acceptance-policy.md`, `docs/product/glossary.md`: verify the shared acceptance and terminology constraints.
- Product requirements, business flows, user stories, business rules, and their stable IDs directly related to this Change.
- `docs/architecture/system-context.md`, `docs/architecture/domain-boundaries.md`: verify the systems, modules, data ownership, and dependency boundaries involved.
- Current specs in `openspec/specs/**` related to this feature's capability / domain; also read the archived specs of dependency Changes, if any.

### 3.2 Impact-Based Reads (Read the Full Text/Relevant Sections Only When Matched)

| Impact area | Baseline files that must be verified |
|---|---|
| Adding/modifying data, entities, queries, transactions | `logical-erd.md`, `domain-boundaries.md`, `data-flows.md` |
| Adding/modifying services, modules, asynchronous flows, third-party dependencies, deployment | `containers-and-deployment.md`, `technology-decisions.md`, relevant ADRs, `data-flows.md` |
| Adding/modifying HTTP APIs, authentication, external integration | `api-conventions.md`, relevant ADRs, security/authentication conventions |
| Modifying pages, routes, components, state, or the visual system | `frontend-conventions.md`, approved design system/component specifications |
| Modifying quality requirements, performance, security, reliability, observability | `test-strategy.md` and the corresponding NFR / ADR / deployment constraints |
| Modifying roles, cross-feature business rules, shared flows/terminology | Corresponding product baseline files and permission/security-related architecture conventions |

AI must not indiscriminately stuff the full text of all documents into context; it must first read the baseline status and catalog, then read the relevant files/sections for this Change's impact area, and leave evidence paths, versions, and reference IDs in the baseline impact list.

## 4. Change Attribution Decision: Stay in the Change or Elevate to the Baseline

| Change type | Authoritative landing point | Whether the project baseline is updated | Typical example |
|---|---|---|---|
| Behavior, rules, AC, and exception scenarios unique to the current feature | The current Change's proposal / delta spec | No | Field filtering rules for order export |
| Pages, buttons, endpoints, and API schemas unique to the current feature | The current Change's page list, Figma audit, OpenAPI | No | Add `GET /orders/{id}` |
| Tables/fields/indexes/migrations and queries unique to the current feature | The current Change's migration, backend design, IO catalog | Usually no | Status field used only by the order export task |
| Classes, methods, internal IO orchestration unique to the current feature | The current Change's detailed design and code | No | One-off cache implementation where a feature calls Redis |
| New shared business rules, global role/permission semantics, cross-feature flows, or shared terminology | Product baseline (synchronize the OpenSpec main specs where necessary) | Yes, after approval | All order-type operations must satisfy unified approval rules |
| A new feature becomes part of the approved product scope and requires new stable US/UC/BR IDs | Product requirements/user story catalog (register only the index, summary, status, and ID); detailed behavior/scenarios/AC remain governed by that Change's OpenSpec spec | Update the product catalog after acceptance approval; do not copy the full feature spec | Add a "Batch export orders" user story ID; detailed export rules remain in the Change spec |
| Changes to system/module boundaries, data ownership, dependency direction, technology stack, deployment topology | Architecture baseline + ADR | Yes, after approval | Split a service, change module data ownership |
| Changes to shared core entities, relationships, domain invariants, or cross-module consistency | Data and domain baseline | Yes, after approval | The customer entity becomes master data shared by multiple contexts |
| Changes to global API error format, authentication, idempotency, pagination/compatibility rules | API public baseline | Yes, after approval | All APIs use a unified error envelope |
| Changes to global frontend components, routing/state management, design token rules | Frontend engineering baseline/design system | Yes, after approval | Site-wide unified form validation and error presentation specification |
| Changes to global test layering, release gates, SLO/NFR thresholds | Test strategy/architecture baseline/ADR | Yes, after approval | All services add a contract-test blocking gate |

Decision questions:

Note: The product requirements baseline may maintain a project-level US/UC/BR catalog and stable IDs; however, the detailed behavior, Given/When/Then scenarios, API schema, and AC of a feature remain in the corresponding OpenSpec Change/archived spec. Adding one product story index does not mean elevating the entire feature design to a public baseline.
1. Do at least two features/modules need to follow or reuse this rule?
2. Does it change approved system boundaries, shared entity semantics, data ownership, public contracts, or quality gates?
3. If the next feature does not read this decision, will it create inconsistency, duplicate implementation, or compatibility risk?

When any answer is "yes", at minimum create a baseline change candidate item and review it; if it is only a local implementation or local behavior of the current feature, leave it in the Change. "Possible reuse in the future" alone is not sufficient grounds for elevating to the baseline.

## 5. Timing and Process of Baseline Changes

### A. Baseline Gaps/Conflicts Found Before Feature Development

1. Fill in `openspec/changes/<change-id>/design/baseline-impact.md` during the feature requirements stage.
2. Mark it as `BASELINE_CHANGE_REQUIRED` and propose the impact domain, target version, rationale, alternatives, and affected Changes.
3. If architecture/data/public contract constraints determine the feature design, the ADR/baseline amendment approval must be completed first, before freezing that Change's detailed design.
4. After approval, update the corresponding baseline documents and the version in `baseline-status.md`; then regenerate/re-check this Change's baseline impact list before continuing feature design.

### B. Changes Required to the Baseline Found During Feature Development

1. Directly editing a frozen baseline is not allowed, and bypassing the baseline to make code pass is not allowed.
2. Pause affected tasks; independent tasks that do not depend on that decision may continue only after the owner confirms it is safe.
3. Record the new finding in the current Change's `baseline-impact.md`, and create/update an ADR or baseline amendment request.
4. After approval, update the baseline version; the current Change must re-read the differences, update design and tasks, and rerun affected verification.
5. If externally observable behavior changes, also update the current Change's OpenSpec delta spec; if public capabilities/prior commitments are affected, also assess main-spec changes and compatibility migration.

### C. Writing Back to the Baseline at Feature Acceptance and Archiving

1. Write back only changes that are approved, implemented, verified, and genuinely valuable for project-level reuse.
2. Feature-specific APIs, pages, physical table structures, IO, and test cases remain in the archived Change and are not copied into the global baseline.
3. For product requirement catalogs, logical ERDs, public conventions, ADRs, or architecture descriptions that need synchronization, update the baseline documents and version records; unapproved implementation facts must not be automatically elevated to specification.
4. Update the baseline status, approver, effective date, amendment summary, and related Change ID; run the baseline consistency audit.
5. After archiving the OpenSpec Change, in-flight Changes perform an impact re-check against the new baseline version and must not silently assume automatic compatibility.

## 6. Binding Baseline Versions to In-Flight Changes

- `docs/architecture/baseline-status.md` is the baseline status index; it must record at least the versions and freeze/approval information for the product, architecture, data/domain, public API, frontend engineering, and test strategy domains.
- Each Change's `design/baseline-impact.md` must record the baseline domain versions adopted at start (baseline snapshot) and reference specific files, sections/IDs.
- When the baseline status changes, compare the versions recorded by the Change with the current versions; re-check only the affected domains, but a `NO_IMPACT` or `REBASE_REQUIRED` conclusion and its basis must be left on record.
- Frozen baselines use incremental version updates: ordinary textual clarification may be a patch version per project rules; public constraint/model changes upgrade at least the minor version; system boundary/major technology strategy changes upgrade the major version. If the team uses another versioning strategy, it must be stated explicitly in `baseline-status.md`.
- `workflow-state.json` records only the index, pending approvals, and blockers; it does not replace baseline documents, ADRs, or approval evidence.

## 7. Mandatory Baseline Impact List for Feature Changes

Every Change must create `design/baseline-impact.md` (according to `templates/change-assets/design/baseline-impact.md`):

- Current baseline versions and the status of each domain;
- Verification results for fixed reads and impact-based reads;
- Constraint ID / file / section / version / applicability / design impact on the current feature;
- Reused existing modules, domain entities, API public conventions, frontend components, and test strategy;
- Conflicts, gaps, and assumptions relative to the baseline;
- Attribution classification: `CHANGE_ONLY`, `BASELINE_CHANGE_REQUIRED`, `BASELINE_UPDATE_AFTER_ACCEPTANCE`, `N/A`;
- ADRs, baseline amendment requests, approvers, and status to be created/updated;
- Rebase conclusions for in-flight Changes;
- Conclusion: `COMPATIBLE`, `BLOCKED_PENDING_BASELINE_CHANGE`, or `APPROVED_BASELINE_AMENDMENT`.

This file is created in stage 05, re-checked during 06–07 design, only appended with findings during stage 08 implementation without modifying the baseline unilaterally, and its write-back verification is completed during stage 10 acceptance.

## 8. Roles and Approval Responsibilities

| Decision scope | Required approval roles |
|---|---|
| Product rules, roles, flows, terminology, acceptance policy | Product owner/business owner |
| System boundaries, module dependencies, technology selection, deployment topology, ADR | Architecture owner/technical owner |
| Core entities, data ownership, shared data invariants | Data owner + architecture owner |
| Public API, frontend public specifications, quality gates | Corresponding technical owner; approved by the architecture owner when cross-team impact is involved |
| Single feature behavior and AC | Product owner; technical implementation reviewed by the corresponding technical owner |

AI may analyze, propose candidate changes, and generate documents, but may not approve on behalf of the owners and may not unilaterally declare the baseline frozen or upgraded.


## 9. Machine-Executable Baseline Governance Engine (Mandatory)

This project no longer uses the textual status in `baseline-status.md` as the sole basis for judgment. The following files constitute the machine-authoritative source:

- `docs/architecture/baseline-manifest.json`: overall/domain versions, status, approvals, effective revision, and the SHA-256 of each baseline file.
- `docs/architecture/constraint-registry.json`: stable Constraint IDs, constraint levels, scope, rule text, source sections, enforcement method, owner, and approval status.
- `openspec/changes/<change-id>/design/baseline-binding.json`: the current Change's binding of every ACTIVE constraint, baseline snapshot, design evidence, implementation verification evidence, exception approvals, and rebase conclusions.
- `scripts/baseline-governance.py`: the sole check entry point for the above data; `workflow.py` invokes it on stage entry/transition.

### 9.1 Freeze Conditions

The end audit of project overall architecture design stage 03 permits transition only when all of the following conditions are satisfied:

1. Manifest `status=FROZEN`, and all six required domains are `FROZEN`.
2. Each domain has a semantic version, owner, approver, approved_at, and effective_revision.
3. Every authoritative baseline file exists and its SHA-256 matches the Manifest; the constraint registry itself also has a SHA-256.
4. Constraint IDs are unique, levels are valid, source files belong to the corresponding domains, and the source sections actually exist.
5. No DRAFT constraints may be mixed into a frozen baseline; ACTIVE constraints must have owner, approved_by, and approved_at.
6. The overall approval must have an approver, approved_at, and an in-repository evidence file.
7. The Evidence for stage 03 must hand off the Manifest and Constraint Registry as outputs.

### 9.2 Constraint Registry Rules

Each constraint contains at least: `id`, `domain`, `revision`, `status`, `level`, `scope`, `title`, `rule`, `rationale`, `source.file`, `source.section`, `enforcement`, `owner`, and approval fields. Levels use `MUST`, `SHOULD`, `MAY`, `PROHIBITED`; statuses use `DRAFT`, `ACTIVE`, `RETIRED`.

- MUST / PROHIBITED are hard constraints; they must not be deviated from except for approved Change-level exceptions. The exceptions object must be empty or have complete status `APPROVED`; rejected/pending exceptions cannot coexist with a `COMPLIANT` decision.
- SHOULD is a strong recommendation; if not followed, a reason and review conclusion must be given.
- MAY indicates that adoption is permitted, not that it is mandatory.
- Only ACTIVE constraints enter Change machine binding; DRAFT rules cannot masquerade as an effective baseline. A frozen registry contains at least one ACTIVE constraint, and all DRAFT rules must be converted to ACTIVE or RETIRED before freezing.
- `AUTOMATED` / `HYBRID` must reference a validator that actually exists in the repository; `MANUAL` / `HYBRID` must require human evidence. When there is no executable validator, automation must not be claimed falsely.
- Modifying/deactivating/adding constraints constitutes a baseline amendment and must not be done merely by editing the Change binding file.

### 9.3 Change Binding and Phased Gates

Run the following when creating Change auxiliary assets:

```bash
python3 scripts/baseline-governance.py init-binding --change-id <change-id>
```

The generated `baseline-binding.json` must cover all ACTIVE constraints in the current registry, and deleting constraint rows is prohibited. Each constraint must be selected as `APPLICABLE` or `NOT_APPLICABLE`; N/A must state the reason. Applicable constraints must be `COMPLIANT` or `EXCEPTION_APPROVED` at the design stage and be linked to real design evidence files.

At the implementation stage, every applicable constraint must have `implementation_verification.status=PASS` and a real evidence file; constraints that genuinely only affect design and not runtime implementation must still explicitly be written as `NOT_APPLICABLE` with a reason. `PENDING`, `NOT_RUN`, and `SKIPPED` cannot be regarded as passing. The acceptance stage must additionally fill in `acceptance_verification` separately, reconfirming constraint compliance with independent acceptance/review evidence, and must not directly copy the PASS from the implementation stage; N/A likewise must state a reason.

Exceptions must record a unique exception_id, deviation reason, scope, approver, approval time, and in-repository approval evidence. A Change-level exception permits only that Change to deviate within the approved scope; it does not modify or lower the project baseline, nor does it automatically authorize other Changes.

Workflow gate mapping:

| Stage | Machine check | Purpose |
|---|---|---|
| 03 Architecture baseline | `audit --require-frozen` | Verify Manifest, constraint catalog, hashes, and approvals after the freeze |
| 04 Proposal planning | `audit --require-frozen` | Ensure the project baseline is still effective |
| 05 Proposal requirements | `check-change --phase requirement` | Constraint coverage complete, applicability determined, baseline binding approved |
| 06 Figma design review | `check-change --phase requirement` | Prevent early requirement bindings from being deleted/modified or baseline drift |
| 07 Detailed design | `check-change --phase design` | Every constraint has a design conclusion and evidence, exceptions approved |
| 08 Implementation | `check-change --phase implementation` | Applicable constraints have implementation verification evidence |
| 09 Independent verification | `check-change --phase implementation` | Independent evidence still covers the approved implementation constraints |
| 10 Acceptance | `check-change --phase acceptance` | All constraints complete final verification |

### 9.4 Baseline Evolution and In-Flight Change Rebase

When the baseline needs modification after freezing, **it must first** run:

```bash
python3 scripts/baseline-governance.py open-amendment \
  --request-id BCR-<id> --domains architecture,data_domain --opened-by <reviewer>
```

This command changes the overall status to `UNDER_AMENDMENT` and marks the specified domains, and all feature-level entry points immediately fail-closed. After modifying documents/constraints, the overall `overall_version` and the semantic version of each affected domain must be upgraded at the same time, then run `refresh-hashes`; then execute `close-amendment --request-id <BCR-ID> --approved-by <owner> --approved-at <date> --effective-revision <git:commit or snapshot:sha256> --evidence <approval evidence file>`. The command checks that affected domain versions were actually upgraded, that hashes are correct, and that evidence exists, then restores FROZEN. After completion, rerun `audit --require-frozen`. During this period, feature development must not continue consuming a baseline that is being modified.

Every affected domain of an in-flight Change must fill in `rebase_reviews`: current version, current fingerprint, conclusion, reviewer, reviewed_at, and in-repository evidence. Each overall version change must also fill in `rebase_reviews.overall`, giving an independent impact conclusion for the overall upgrade. `NO_IMPACT` may retain the original snapshot, but every stage revalidates that the conclusion still corresponds to the current fingerprint/version; where design/implementation need to change, rebase must be completed for the overall and affected domains and marked `REBASE_COMPLETED`, then `refresh-binding` must be run. Refresh resets constraint judgments in changed domains and revokes old binding approvals, requiring re-review.

### 9.5 Constraints and Safety Boundaries

The scripts verify in-repository JSON, file hashes, approval record structure, and evidence existence; they do not provide enterprise identity authentication, electronic signatures, or non-repudiation. `baseline-governance.py audit --require-frozen` and the applicable Change phase gates must be wired into CI, and Git CODEOWNERS, protected branches, and required approvals must be set for baseline files/Manifest/Registry. Otherwise, an Agent/user with permission to directly modify scripts or state JSON or to bypass CI may still evade the gates.
