# Proposal Roadmap

> Change ID: PENDING (project-level: N/A)
> Status: PENDING
> Source baseline: PENDING
> Related requirement/AC IDs: PENDING
> Version/date: PENDING

> Every candidate Change is independently acceptable and ordered by dependency and value. Requirement and AC detail is written at the proposal level (Stage 05), not here.

## Candidate Changes

| Change ID | Primary Capability | Owner Module | Related Modules | Slice Type | Slice Coverage | Code Target | Demo Path | Slice Budget | Dependencies | Target Platforms | Value | Baseline Domains | Potential Amendment |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

> `Primary Capability` is exactly one capability slug registered in `docs/product/capabilities.csv`. `Owner Module` is exactly the module slug registered in `docs/product/modules.csv` that owns that capability. `Related Modules` lists the other modules modified by the Change (semicolon-separated; `N/A + reason` when none). `Slice Type` is `initial | extend`; `Slice Coverage` is `partial | full`. `Code Target` must match registered module paths. `Demo Path` records how the delivered behavior is demonstrated at acceptance. `Slice Budget` records the AC count and any approved exception. `Dependencies` is `none` / `N/A` when the Change has no prerequisite, otherwise a semicolon-separated list of Change IDs that must be **accepted and delivered** before this Change may start; unknown IDs, self-dependencies, duplicate edges and cycles fail `check-roadmap.py --strict`. Every dependency edge also needs a line in `## Ordering Rationale` in the form `- <change> ← <dependency>: <reason>`. `Target Platforms` is a semicolon-separated subset of `web|h5|mini-program|app|android|ios|harmonyos|desktop|pda`; Stage 05 must declare the same set in `proposal.md` and `design/user-stories.md`, and Stage 06 must produce at least one HTML PAGE per declared platform. Do not hide platforms in notes.

## Roadmap Amendments

A Change raised outside this main table in Stage 05 must be recorded here with an approved amendment row, including its owner and related modules, before requirements analysis can pass. `Baseline Impact` is `CHANGE_ONLY` when the Change fits an existing baseline domain without touching frozen decisions, or `BASELINE_CHANGE_REQUIRED` when public contracts, shared data models, domains, containers, third-party dependencies, or frozen decisions are touched.

| Change ID | Primary Capability | Owner Module | Related Modules | Slice Type | Slice Coverage | Code Target | Reason | Requester | Approver | Date | Baseline Impact | Depends On | Target Platforms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | CHANGE_ONLY / BASELINE_CHANGE_REQUIRED | PENDING | PENDING |

> `Depends On` follows the same rule as the main table's `Dependencies` column. An amendment row without all approval fields does not participate in the dependency graph. `Target Platforms` follows the same rule as the main table.

## Ordering Rationale

PENDING

## Out of Scope

- PENDING
