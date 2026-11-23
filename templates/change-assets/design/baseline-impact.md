# Baseline Applicability and Impact Record

- Change ID: `<change-id>`
- Status: APPROVED
- Established in stage: 05-feature-requirements
- Last review stage:
- Current baseline version:
- Related US / AC / BR / FLOW:

## 1. Baseline Status Snapshot

| Baseline domain | Current version | Status | Approver/effective date | Involved in this Change |
|---|---|---|---|---|
| Product | | FROZEN / DRAFT / STALE | | YES / NO |
| Architecture | | FROZEN / DRAFT / STALE | | YES / NO |
| Data and Domain | | FROZEN / DRAFT / STALE | | YES / NO |
| Public API | | FROZEN / DRAFT / STALE | | YES / NO |
| Frontend Engineering | | FROZEN / DRAFT / STALE | | YES / NO |
| Testing and Quality | | FROZEN / DRAFT / STALE | | YES / NO |

## 2. Fixed-Read Verification

| Baseline file | Version/last updated | Applicable sections/IDs | Read status | Constraint/impact on this feature |
|---|---|---|---|---|
| `docs/architecture/baseline-status.md` | | | READ / MISSING | |
| `docs/product/acceptance-policy.md` | | | READ / MISSING | |
| `docs/product/glossary.md` | | | READ / MISSING | |
| Related product requirements/flows/user stories/business rules | | | READ / N/A / MISSING | |
| `docs/architecture/system-context.md` | | | READ / MISSING | |
| `docs/architecture/domain-boundaries.md` | | | READ / MISSING | |
| Related `openspec/specs/**` | | | READ / N/A / MISSING | |

## 3. Impact-Based Read Verification

| Impact surface | Baseline files that must be read | Related sections/IDs | Version | Constraint summary/design impact |
|---|---|---|---|---|
| Data/entities/transactions | logical-erd / domain-boundaries / data-flows | | | |
| Services/modules/integration/deployment | system-context / containers-and-deployment / technology-decisions / ADR / data-flows | | | |
| HTTP API/authentication/external integration | api-conventions / security decisions | | | |
| Pages/routes/components/state | frontend-conventions / design system | | | |
| NFR/quality/observability | test-strategy / relevant ADR / deployment constraints | | | |
| Shared roles/business rules/flows | relevant product baseline / permission model | | | |

## 4. Reuse and Consistency Mapping

| Current feature design item | Reused baseline capability/component/entity/rule | Source file and version | Handling |
|---|---|---|---|
| | | | REUSE / EXTEND / REPLACE (REPLACE requires approval) |

## 5. Change Ownership Classification

| Finding/change | Classification | Basis for judgment (local/cross-feature/shared constraint) | Authoritative location | Affects other Changes |
|---|---|---|---|---|
| | CHANGE_ONLY / BASELINE_CHANGE_REQUIRED / BASELINE_UPDATE_AFTER_ACCEPTANCE / N/A | | | |

## 6. Baseline Conflicts, Gaps, and Candidate Amendments

| ID | Conflict/gap | Impact domain | Candidate solution/ADR | Affected features/Changes | Owner | Approval status |
|---|---|---|---|---|---|---|
| | | | | | | PENDING / APPROVED / REJECTED |

## 7. In-Flight Change Version Review

| In-flight Change | Referenced baseline version | Current baseline version | Impact analysis | Conclusion |
|---|---|---|---|---|
| | | | | NO_IMPACT / REBASE_REQUIRED / BLOCKED |

## Roadmap Amendment

Fill this section only when this Change is not in the main table of `docs/product/proposal-roadmap.md`. Mirror the approved amendment record from the roadmap's `## Roadmap Amendments` table and record the baseline impact classification.

| Change ID | Primary Capability | Extends | Slice Type | Slice Coverage | Code Target | Reason | Requester | Approver | Date | Baseline Impact |
|---|---|---|---|---|---|---|---|---|---|---|
| N/A + reason (not an off-roadmap Change) | | | | | | | | | | CHANGE_ONLY / BASELINE_CHANGE_REQUIRED |

## 8. Conclusion and Gates

- This Change baseline classification: CHANGE_ONLY
- Overall conclusion: COMPATIBLE
- Allowed to enter detailed design: YES
- Allowed to enter implementation: NO
- Baseline amendments that must be completed first:
- Approver and evidence: PENDING (owner and evidence path required before strict approval)
- Next review occasion: 07 detailed design / 08 implementation findings / 10 acceptance and archiving

> Rule: If a baseline change affects the architecture, data model, public contract, or test gates of the current feature, the baseline must first be approved and updated before detailed design and the implementation plan are frozen. `PENDING` must not be treated as approval.
