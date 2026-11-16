# ID Naming and Allocation Conventions

- Change ID: N/A (project-level)
- Status: DRAFT
- Source baseline: docs/TEMPLATE-POLICY.md, stage templates
- Related requirements/AC: All stable IDs
- Generated date/version: PENDING

## 1. Two ID Layers

| Layer | Prefix | Example | Allocator | Scope |
|---|---|---|---|---|
| Project-level | FLOW/NODE/DO/RD/BR/TERM/Q/DEC/ASM/CAP/LESSON/ROLE | FLOW-001, NODE-001-01, DO-001 | Step 02/03 baseline owner | Whole project |
| Change-level | US/AC/TEST/PAGE/BLOCK/ELEM/EVT/IO/TASK | US-001, AC-001 | Current Change | Unique within that Change |

## 2. Parallel Allocation Rules

- Project-level IDs are allocated only during baseline stages; feature Changes must not create or reuse project-level IDs.
- Change-level IDs are unique within that Change; cross-Change references must carry the Change prefix, for example `report-export:US-001`.
- Change-level IDs must not be registered in `docs/product/` baseline documents; when elevation is needed, go through a baseline change first and allocate a project-level ID.
- Reusing retired IDs is prohibited; on retirement, mark `RETIRED` in the source document and keep the original row.

## 3. Reference Closure

- Every reference must point to an ID that actually exists; unknown IDs are judged as errors by `check-requirements.py`.
- Renaming/reordering does not change IDs; wording revisions keep the original ID and record the version.
- Search existing documents before adding a new ID to avoid semantic duplication.
