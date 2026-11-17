# Baseline Applicability and Impact Record

- Change ID: `workflow-context-bundles`
- Status: REVIEW
- Established in stage: 05-feature-requirements
- Last review stage: 07-detailed-design (pending Stage 07 approval)
- Current baseline version: overall v0.2.2 (FROZEN); product v0.2.0; architecture/data v0.2.2; API/frontend/test-quality v0.2.0
- Related US / AC / BR / FLOW: US-001–002; AC-001–003; BR-001–004; FLOW-001/NODE-001-02–04

## 1. Baseline Status Snapshot

| Baseline domain | Current version | Status | Approver/effective date | Involved in this Change |
|---|---|---|---|---|
| Product | v0.2.0 | FROZEN | user / 2026-11-17 | YES |
| Architecture | v0.2.2 | FROZEN | user / 2026-11-17 | YES |
| Data and Domain | v0.2.2 | FROZEN | user / 2026-11-17 | YES |
| Public API | v0.2.0 | FROZEN | user / 2026-11-17 | YES |
| Frontend Engineering | v0.2.0 | FROZEN | user / 2026-11-17 | NO |
| Testing and Quality | v0.2.0 | FROZEN | user / 2026-11-17 | YES |

## 2. Fixed-Read Verification

| Baseline file | Version/last updated | Applicable sections/IDs | Read status | Constraint/impact on this feature |
|---|---|---|---|---|
| `docs/architecture/baseline-status.md` | overall v0.2.2 / 2026-11-17 | frozen domains; Q-003 | READ | Do not change risk-tier policy; Q-003 remains out of scope |
| `docs/product/acceptance-policy.md` | product v0.2.0 | AC evidence rules | READ | ACs remain traceable and verifiable |
| `docs/product/glossary.md` | product v0.2.0 | context/input/output terms | READ | Reuse established terms |
| Related product requirements/flows/user stories/business rules | product v0.2.0 | RA-001, FLOW-001/NODE-001-02, BR-001–004 | READ | Preserve stage selection, budget and fail-closed rules |
| `docs/architecture/system-context.md` | architecture v0.2.2 | toolkit boundaries, state governance | READ | Local toolkit CLI; no external runtime/service |
| `docs/architecture/domain-boundaries.md` | architecture v0.2.2 | explicit contracts, single source | READ | Stage inputs and trigger mapping need one authoritative configuration |
| Related `openspec/specs/**` | none registered | N/A | READ (none found) | This Change introduces first capability spec |

## 3. Impact-Based Read Verification

| Impact surface | Baseline files that must be read | Related sections/IDs | Version | Constraint summary/design impact |
|---|---|---|---|---|
| Data/entities/transactions | logical-erd / domain-boundaries / data-flows | DO-002; DATA-OWNERSHIP-001 | v0.2.2 | No persistent business entity; output is transient; one source of truth |
| Services/modules/integration/deployment | system-context / containers-and-deployment / technology-decisions / ADR / data-flows | toolkit CLI; LEGACY-TOOLKIT-001/002 | v0.2.2 | Extend existing local script; do not introduce service or dependency |
| HTTP API/authentication/external integration | api-conventions / security decisions | API-CLI-001 | v0.2.0 | No HTTP/API/auth; CLI failures use nonzero exit codes |
| Pages/routes/components/state | frontend-conventions / design system | FE-NO-UI-001 | v0.2.0 | No UI; frontend convention not applicable |
| NFR/quality/observability | test-strategy / relevant ADR / deployment constraints | NFR-001; QUALITY-EVIDENCE-001 | v0.2.0 | Record real checks and reproducible metrics; no new runtime observability service |
| Shared roles/business rules/flows | relevant product baseline / permission model | FLOW-001, NODE-001-02, BR-001–004, ROLE-002 | v0.2.0 | Retain user approval and input selection semantics; no role/permission expansion |

## 4. Reuse and Consistency Mapping

| Current feature design item | Reused baseline capability/component/entity/rule | Source file and version | Handling |
|---|---|---|---|
| Stage required inputs | Stage artifact contracts and current agent-context selection | `docs/STEP-ARTIFACT-CONTRACTS.json`, architecture v0.2.2 | EXTEND: keep contract as required-input authority |
| Context limits | 8 groups / 12,000 chars | `docs/product/business-rules.md`, product v0.2.0 | REUSE: measure actual rendered text; no default limit change |
| Failure and provenance | nonzero CLI failure; auditable artifact/source IDs | `docs/architecture/api-conventions.md`, v0.2.0 | REUSE |
| Approval/state gates | workflow state commands and human approval | `scripts/workflow.py`, architecture v0.2.2 | REUSE; Change does not alter transitions |
| Agent stage entry | Stage prompts and context tool currently enumerate inputs; render mode makes the prompt body explicit | `prompts/00-next-step.md`, prompts 02–10, Stage 07 review | EXTEND: inject only rendered text; failed rendering stops the stage |

## 5. Change Ownership Classification

| Finding/change | Classification | Basis for judgment (local/cross-feature/shared constraint) | Authoritative location | Affects other Changes |
|---|---|---|---|---|
| Render and report actual context content using existing stage limits | CHANGE_ONLY | Implements existing NODE-001-02 and BR-001; no shared semantic change | `openspec/changes/workflow-context-bundles/` | No; consumers may opt into CLI mode |
| Add opt-in render group IDs and trigger metadata to the existing authoritative stage-input configuration | CHANGE_ONLY | Additive metadata; list-mode CLI/output shape and approved required-input/approval semantics remain unchanged. Conditional-only entries move from default groups to on-demand groups; their source paths remain in one config. | `docs/STEP-ARTIFACT-CONTRACTS.json` `input_policy.stage_profiles`; compatibility is validated against current lean/on-demand groups | Existing callers retain the same command; renderer is opt-in |
| Route stage prompts through body-only render mode | CHANGE_ONLY | Aligns the caller with the new renderer without changing stage sequencing or approval rules | `prompts/00-next-step.md`, prompts 02–10 | All future file-backed stages consume filtered content; no baseline policy change |

## 6. Baseline Conflicts, Gaps, and Candidate Amendments

| ID | Conflict/gap | Impact domain | Candidate solution/ADR | Affected features/Changes | Owner | Approval status |
|---|---|---|---|---|---|---|
| GAP-001 | Resolved in Stage 07: use aligned group IDs and trigger mappings in existing `input_policy.stage_profiles`; retain source paths in the canonical profile arrays | Architecture/API | Additive metadata validated against the existing arrays; no second path registry and no change to the workflow approval contract | All file-backed stage context consumers | Technical owner | PENDING Stage 07 review |
| Q-003 | Risk-tier check profile is open | Testing and Quality | No action in this Change; keep implementation gated by existing project decision | Future implementation changes | Technical/quality owner | OPEN; out of scope |

## 7. In-Flight Change Version Review

| In-flight Change | Referenced baseline version | Current baseline version | Impact analysis | Conclusion |
|---|---|---|---|---|
| `workflow-context-bundles` | v0.2.2 | v0.2.2 | Newly created against current frozen snapshot; fingerprints recorded in baseline-binding.json | NO_IMPACT |

## 8. Conclusion and Gates

- This Change baseline classification: CHANGE_ONLY
- Overall conclusion: COMPATIBLE
- Allowed to enter detailed design: YES (this design is submitted for Stage 07 review)
- Allowed to enter implementation: NO; stage 07/08 gates and Q-003 policy apply
- Baseline amendments that must be completed first: None; Stage 07 resolved the configuration location and keeps approved workflow semantics unchanged
- Approver and evidence: PENDING user review; no approval claimed
- Next review occasion: 13a detailed design / 14 implementation findings / 15 acceptance and archiving

### Stage 07 Baseline Re-review

- Reviewed baseline snapshot: overall v0.2.2 FROZEN; product v0.2.0; architecture/data v0.2.2; API/frontend/test-quality v0.2.0.
- Re-review result: NO_IMPACT. The design reads repo-local inputs, renders to stdout, preserves the approved 8-group/12,000-character limits, and changes no shared product rule, API, data model, frontend stack, third-party integration, or quality gate.
- Applicable constraint conclusions: COMPLIANT; detailed design evidence is recorded in `design.md` and this re-review.
- Non-applicable constraints: FE-NO-UI-001, EXT-GITHUB-001, EXT-FIGMA-001, EXT-WEB-001 remain NOT_APPLICABLE for the reasons in `baseline-binding.json`.
- Review approver/evidence: PENDING Stage 07 technical review; no approval claimed.

> Rule: If a baseline change affects the architecture, data model, public contract, or test gates of the current feature, the baseline must first be approved and updated before detailed design and the implementation plan are frozen. `PENDING` must not be treated as approval.
