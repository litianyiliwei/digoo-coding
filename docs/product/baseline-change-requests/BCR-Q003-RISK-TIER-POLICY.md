# Q-003 Risk-Tier Policy Baseline Change Request

- Change ID: `N/A` (project baseline request)
- Status: IMPLEMENTED — approved and frozen on 2026-11-17
- Source baseline: overall v0.3.0; product v0.3.0; architecture v0.2.2; test-quality v0.3.0 (FROZEN)
- Related requirements/AC: Q-003; BR-003/006/007; DEC-003; FLOW-001; NODE-001-02/04–07/09
- Generated date/version: 2026-11-17 / v0.1.0-draft

# Project Baseline Change Request

- Request ID: `BCR-Q003-RISK-TIER-POLICY`
- Source Change: `workflow-context-bundles` (blocking dependency); follow-up implementation Change: `risk-tier-check-profiles`
- Impacted baseline domain: Product / Test Quality
- Status: IMPLEMENTED
- Proposer/date: Codex, prepared for the technical/quality owner / 2026-11-17
- Approver: user / project owner (2026-11-17)

## 1. Change Reason and Evidence

Q-003 currently blocks every Stage 08 implementation until a low/standard/high risk matrix and required check sets are approved. The roadmap places `risk-tier-check-profiles` after `workflow-context-bundles` and `artifact-source-of-truth`, while the current Change cannot enter Stage 08 until Q-003 is closed. This creates a dependency cycle.

This request separates two deliverables:

1. Approve the project-wide risk criteria and mandatory check sets in the baseline, closing Q-003.
2. Implement an automated profile selector and evidence recorder later as `risk-tier-check-profiles`, after the context labels and authoritative check catalog are ready.

Evidence: `docs/product/open-questions.md` (Q-003); `docs/architecture/baseline-status.md` (Q-003 Stage 08 blocker); `docs/product/proposal-roadmap.md` (`risk-tier-check-profiles` dependencies); `openspec/changes/workflow-context-bundles/design.md` (Stage 08 remains blocked pending Q-003).

## 2. Current Baseline and Version

- Starting versions: overall v0.2.2; product v0.2.0; test_quality v0.2.0 (FROZEN before this amendment).
- Effective versions after approval and re-freeze: overall v0.3.0; product v0.3.0; test_quality v0.3.0. Architecture remains v0.2.2.
- No baseline file or manifest has been changed by this draft.

## 3. Constraints/Files/Sections to Modify

After approval, update the following as one governed amendment:

- `docs/product/open-questions.md`: move Q-003 from open to closed, citing the approved matrix, version, and evidence.
- `docs/product/requirements-analysis.md`, `docs/product/BASELINE-BRIEF.md`, and `docs/product/change-sizing.md`: synchronize the Stage 02 question status, resident summary, and Change DoD references to the approved policy.
- `docs/product/business-rules.md`: define deterministic classification and mandatory evidence behavior under BR-003/006/007.
- `docs/product/acceptance-policy.md`: state the per-tier verification sets and non-waivable gates.
- `docs/product/decisions.md`: record the user's approved risk-policy decision as DEC-005.
- `docs/architecture/test-strategy.md`: define applicable test/verification commands per tier and unavailable-command behavior.
- `docs/product/proposal-roadmap.md`: distinguish policy definition (this baseline amendment) from automated selector implementation (`risk-tier-check-profiles`); retain its dependency on `workflow-context-bundles` and `artifact-source-of-truth` only for the automation implementation, and on `reliable-gate-runtime` for activation.
- `docs/architecture/baseline-status.md`, `docs/architecture/baseline-manifest.json`, and `docs/architecture/constraint-registry.json`: record approved versions, Q-003 closure, amendment evidence, and refreshed hashes through the prescribed governance commands.

### Proposed deterministic classification matrix

Classify by the highest applicable trigger. An unknown or ambiguous trigger escalates to at least Standard; an Agent may not lower a tier without an explicit owner decision.

| Tier | Entry criteria | Required verification |
|---|---|---|
| Low | Documentation or isolated, reversible local tooling change; no behavior change to shared contracts, workflow state/approval gates, security/permissions/privacy, data model/migration, external/native/device boundary, UI, release/deployment, or frozen baseline. All low-risk conditions must be evidenced. | Package/structure checks; checks and tests directly mapped to changed artifacts/ACs; diff/code review; complete evidence and all workflow/user approval gates. No risk-based full-suite run when the change is demonstrably isolated. |
| Standard | Behavioral change to a local command or single subsystem, or multiple affected artifacts, without any High trigger. | Package/structure checks; all affected module tests and their relevant regression tests; baseline/change consistency checks; code review; independent verification under existing project policy; stage and user approvals. Run the full suite when shared contracts or multiple subsystems are affected. |
| High | Any security/authentication/authorization/privacy/secrets change; data migration or integrity risk; external/native/device/third-party interface; production/deployment/rollback impact; frozen-baseline or cross-stage shared-contract change; workflow state, approval, or hard-gate behavior; or an unresolved/uncertain impact that cannot be bounded. | Full repository regression suite; all applicable security/data/interface/UI/baseline/workflow checks; migration/rollback verification where applicable; independent verification; complete code review and all existing approval gates. Missing required tooling or evidence blocks completion. |

### Non-waivable gates for every tier

- User review and stage approvals; valid workflow state transitions and handoff hashes.
- Baseline approval before changing frozen rules; traceability and required evidence completeness.
- Applicable security/permission checks; policy-required independent verification (including the repository's Stage 09 requirement).
- No failure, unavailable mandatory check, or unapproved exception may be reported as PASS.
- Tests must map to AC/TEST IDs; skipped checks need a rule-based non-applicability reason recorded with the run evidence.

### Classification for the active Change (approved application)

`workflow-context-bundles` is **HIGH** because it changes a shared stage-input contract and prompts consumed across the workflow. It must run the full repository regression suite and all applicable Stage 08 checks under the frozen v0.3.0 policy.

## 4. Alternatives and Trade-offs

1. Keep Q-003 open and leave all implementation blocked. This preserves the current text but does not resolve the dependency cycle or deliver the user's approved low-risk targeted-check goal.
2. Allow `workflow-context-bundles` to proceed under an informal temporary exception. Rejected because the frozen baseline makes Q-003 a hard Stage 08 blocker and an informal exception would bypass that rule.
3. Approve the shared matrix in a baseline amendment, then implement automation as a later Change. Recommended: policy is explicit before implementation, the current Change can be classified consistently, and no Agent invents a local exception.

## 5. Impact Analysis

- Affected Changes: `workflow-context-bundles` (currently blocked; proposed High tier); `artifact-source-of-truth` (verification mapping); `reliable-gate-runtime` (check execution reliability); planned `risk-tier-check-profiles` (automates the approved matrix).
- Impact on archived features/compatibility: none intended; new policy applies prospectively. Existing approved hard gates remain mandatory.
- System/data/security/deployment/quality impact: changes shared product and test-quality policy only; no runtime data migration or external interface.
- Migration and rollback: no code migration. If rejected, leave the frozen baseline and Q-003 unchanged. If approved, apply one versioned baseline amendment; rollback requires a separately approved baseline amendment.

## 6. Decision

- Approve/Reject: APPROVED — user approved the BCR and proposed matrix on 2026-11-17.
- Decision rationale: Define the risk matrix in the baseline before implementation; keep automation as a later Change and remove the policy/implementation dependency cycle. The current `workflow-context-bundles` Change is High and receives full verification.
- Effective version/date: overall v0.3.0; product/test_quality v0.3.0; frozen 2026-11-17.
- Related ADR: N/A — no architecture decision change proposed.

## 7. Implementation and Verification

- Updated baseline files: `docs/product/business-rules.md`, `acceptance-policy.md`, `open-questions.md`, `requirements-analysis.md`, `BASELINE-BRIEF.md`, `change-sizing.md`, `decisions.md`, `proposal-roadmap.md`; `docs/architecture/test-strategy.md`, `baseline-status.md`, `baseline-manifest.json`, and `constraint-registry.json`. `docs/product/BASELINE-INDEX.md` was regenerated from its source records.
- Updated `baseline-status.md`: overall v0.3.0 FROZEN; product and test_quality v0.3.0 FROZEN; Q-003 RESOLVED with user approval evidence.
- Review results for in-flight Changes: `workflow-context-bundles` is HIGH and must run full repository regression plus applicable Stage 08 checks. Its baseline binding and all downstream handoffs must be revalidated after sequential stage reviews; workflow is currently reopened at Stage 01.
- Audit/verification evidence: `workflow/evidence/approval-BCR-Q003-RISK-TIER-POLICY-2026-11-17.md`; `workflow/evidence/BCR-Q003-risk-policy-execution-2026-11-17.md`.
