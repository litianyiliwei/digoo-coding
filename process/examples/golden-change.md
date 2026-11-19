# Golden Sample Change (General Reference)

> Language: English | [简体中文](golden-change-zh.md)

- Purpose: gives Agents a model of "what a good Change looks like"; does not replace the OpenSpec templates.
- Status: REFERENCE
- Related: `templates/change-assets/design/baseline-impact.md`, `baseline-binding.json`, `docs/product/change-sizing.md`

> The sample deliberately chooses a capability unrelated to the specific business (report export) and shows only the structure and tracing method. Actual Changes are governed by the OpenSpec schema.

## 1. Change Overview

| Item | Content |
|---|---|
| Change ID | `report-export` |
| Capability | Export reports by filter criteria |
| Scope | Add an export entry, filter parameters, export jobs, and result download |
| Non-goals | No report designer, no scheduled scheduling, no new permission model |
| Related baseline | FLOW-001 (example), BR-005 (permission), DO-001 (report data) |
| Baseline impact | `CHANGE_ONLY`: no public contract/shared model changes |

## 2. proposal.md Skeleton

```markdown
## Why
Users need to obtain report data offline; currently they can only view it online.

## What Changes
- Add an "Export Report" entry and filter parameters
- Create export jobs and return download URLs
- Reuse the existing RBAC and audit rules

## Capabilities
### New Capabilities
- `report-export`: export reports by filter criteria

## Impact
- Affected code: report query, export jobs, frontend entry
- Affected baseline: BR-005 (permission), FLOW-001 (example)
- Non-goals: report designer, scheduled scheduling
```

## 3. delta spec Skeleton

```markdown
## ADDED Requirements

### Requirement: Export reports by filter criteria
The system SHALL allow authorized users to filter reports by time range and status and generate downloadable files.

#### Scenario: Normal export
- **WHEN** the user submits valid filter criteria
- **THEN** the system creates an export job and returns a downloadable result

#### Scenario: Unauthorized export
- **WHEN** the user does not have permission for that data scope
- **THEN** the system rejects the request and returns the unified error model
```

## 4. Proposal-Level US / AC

> Scenarios (formerly UC) are kept in the Scenario sections of the delta spec; `design/user-stories.md` writes only US and AC to avoid duplicating specifications.

`design/user-stories.md`

| US ID | Role | Story/Value | Related | AC |
|---|---|---|---|---|
| US-001 | ROLE-002 | As an authorized user, I want to export filtered reports so that I can analyze them offline | FLOW-001;BR-005 | AC-001 |

```markdown
### AC-001
- Given: the user is logged in and has permission for that data scope
- When: the user submits valid filter criteria
- Then: the system creates an export job and returns a downloadable result
- Errors/boundaries: no permission returns the unified error; no data returns an empty-result explanation
```

## 5. tasks.md Skeleton

```markdown
- [ ] Implement export filter parameters and validation
- [ ] Implement export jobs and result download
- [ ] Add automated tests for the permission and empty-state ACs
- [ ] Update baseline-binding and complete the requirement gate
```

## 6. Prototype and Page Inventory (Stage 06)

The only UI artifact of Stage 06 (Figma-only) is `design/figma-audit.md`: generate and read back a real Figma design through Figma MCP, the user completes UI review on the real Figma file, and the MCP read results and PAGE mapping are persisted as a stable input for subsequent interfaces. pen.dev, prototype.pen, or PAGE HTML are no longer used. When there is no UI, explicitly exclude it with `--no-ui --reason "<reason>" --strict`.

## 7. Detailed Design (Five Sections of design.md)

`design.md` uniformly writes the five sections `## Design Decisions`, `## Interface Design`, `## Frontend Detailed Design`, `## Backend Detailed Design`, and `## Test Design`; test cases are written into `design/test-cases.csv` (TEST ID → AC/PAGE/BLOCK/API/IO). Only when there is an API are `api/openapi.yaml`, `design/api-io-mapping.csv`, and `design/io-catalog.csv` generated; when there is no API, write `x-api-scope: none`. Page/API/test tracing is merged into the single `traceability.csv`.

## 8. Baseline Impact and Binding

`design/baseline-impact.md` must state:

- The current baseline version and the status of each domain;
- Fixed reading items and impact-based reading items;
- Applicable constraint IDs, reuse items, conflicts, and ownership;
- Conclusion: `COMPATIBLE` / `BLOCKED_PENDING_BASELINE_CHANGE` / `APPROVED_BASELINE_AMENDMENT`.

`design/baseline-binding.json` must cover the constraints required by the manifest governance profile (all ACTIVE in `standard`, `critical: true` only in `lite`), filling in `APPLICABLE` / `NOT_APPLICABLE` and the reason for each.

## 9. Acceptance and Write-back

- Every AC has test or manual evidence; blocking items are cleared.
- After manual acceptance passes, archive, and append one reusable lesson to `lessons.md` (if none, N/A + reason).
- Only content with cross-feature reuse value is written back to the baseline; feature-local implementation stays in the archived Change.

## 10. What This Sample Demonstrates

- One Change does only one thing, and non-goals are clearly stated.
- The spec's Scenarios reference project-level FLOW/BR/DO; every US has an AC; ACs include errors/boundaries.
- Specifications write only externally observable behavior; implementation details are left to the five sections of design.md.
- Prototype/page inventory, detailed design, and traceability matrix each have only one authoritative carrier; no duplicate files are created.
- Baseline impact and binding are part of the proposal, not an after-the-fact formality.
