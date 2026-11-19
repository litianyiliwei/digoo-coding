# Project Baseline Status and Version Register

- Project name:
- Overall baseline version: `v0.1.0`
- Overall status: DRAFT / FROZEN / UNDER_AMENDMENT
- Most recent effective date:
- Product owner:
- Architecture owner:
- Technical owner:
- Baseline repository version/Commit:

## 1. Versions by Baseline Domain

| Baseline domain | Authoritative files | Version | Status | Approver | Effective date | Most recent related Change / ADR |
|---|---|---|---|---|---|---|
| Product | `docs/product/*` | v0.1.0 | DRAFT / FROZEN | | | |
| Architecture | `docs/architecture/system-context.md`, `domain-boundaries.md`, `containers-and-deployment.md`, `data-flows.md`, `technology-decisions.md`, `docs/adr/*` | v0.1.0 | DRAFT / FROZEN | | | |
| Data and Domain | `docs/architecture/logical-erd.md`, `domain-boundaries.md`, `data-flows.md` | v0.1.0 | DRAFT / FROZEN | | | |
| Public API | `docs/architecture/api-conventions.md` | v0.1.0 | DRAFT / FROZEN | | | |
| Frontend Engineering | `docs/architecture/frontend-conventions.md` | v0.1.0 | DRAFT / FROZEN | | | |
| Test and Quality | `docs/architecture/test-strategy.md`, `docs/architecture/quality-gates.json` (when adopted) | v0.1.0 | DRAFT / FROZEN | | | |

## 2. Effective Rules

- Domains with status `FROZEN` are the norms feature development must follow; feature Changes must record the actual domain versions they reference.
- `DRAFT` domains may serve as references but must not masquerade as approved constraints; feature designs that affect such a domain must flag the risk and obtain the owner's approval.
- `UNDER_AMENDMENT` indicates an in-progress baseline revision; the old version remains authoritative until the approval takes effect, and the revision rules must not be used as mandatory requirements in advance.
- Every formal change must record the revision version, change reason, approver, effective date, related ADR/Change, and affected in-flight Changes.

## 3. Versioning Policy

Semantic versioning is used by default:
- PATCH: clarifications, typos, and reference fixes that do not change normative semantics.
- MINOR: newly added backward-compatible shared rules, entities/public conventions, or quality requirements.
- MAJOR: changes to system boundaries, data ownership, public contracts, or constraints that may make existing features incompatible.

Projects may adopt another policy, but it must be stated explicitly here and applied consistently.

## 4. Currently Pending Baseline Revisions

| Revision ID | Impacted domain | Originating Change | Change summary | Status | Owner/Approver | Effective version |
|---|---|---|---|---|---|---|
| | | | | PENDING / APPROVED / REJECTED / IMPLEMENTED | | |

## 5. Freeze Approval Records

| Baseline version | Approval scope | Approver | Date | Evidence/Meeting minutes |
|---|---|---|---|---|
| | | | | |
