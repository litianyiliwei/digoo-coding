# Design

- Change ID：workflow-context-bundles
- Status：DRAFT（Stage 07 detailed design）
- Source baseline：product v0.2.0; architecture v0.2.2 (FROZEN)
- Related requirements/AC：AC-001–003; TASK-001–006; PRODUCT-CONTEXT-001; ARCH-BOUNDARY-001; DATA-OWNERSHIP-001; API-CLI-001; QUALITY-EVIDENCE-001; LEGACY-TOOLKIT-001/002
- Generated date/version：2026-11-17 / v0.2.0

## Design Decisions

### Scope and Non-Goals

Implement deterministic context rendering, source selection/provenance, final-text budgets, and an optional TASK-ID execution card in the existing repository tool. Preserve current list and `--full` audit behavior. Keep workflow approvals, frozen baselines, test gates, and external services unchanged. No UI, HTTP API, database, upload, persistent summary, automatic GitHub sync, or agent-host integration is added.

### Key Decisions and Trade-offs

1. **One configuration source with a compatibility layer.** Keep `input_policy.stage_profiles.lean` and `on_demand` as the authoritative ordered source groups in `docs/STEP-ARTIFACT-CONTRACTS.json`. Add a sibling `bundle_policy` in each profile containing `lean_group_ids`, `on_demand_group_ids`, trigger-to-group mappings, ID-prefix-to-group mappings, and budgets. Add a file-backed Stage 02 profile using its existing resident contract files; user-provided interview/reference content remains in the live request and is not copied into a second artifact. Group-ID array lengths must equal the matching source arrays; every trigger/ID reference must resolve to an existing group. This retains current readers such as `stage-io-report.py` while preventing a second copy of file paths. `check-step-contracts.py` validates the cross-references.
2. **Explicit render mode; compatibility by default.** Keep the current list output for callers that omit `--render`; keep `--full` as the audit view. Add `--render --format json|text`, repeatable `--impact-tag`, `--id`, and `--section PATH#HEADING`, plus optional `--task-id`. `text` writes only `bundle_text` to stdout for direct Agent input; `json` adds the manifest for audit and harness use. Update the workflow entry prompts to invoke text mode and consume only its stdout; never inject the surrounding manifest JSON into the model prompt.
3. **Select before reading.** Required groups are always included. Conditional groups are included only when their configured tags match. Tags are the existing UI/API/DATA/THIRD_PARTY/BASELINE/EXISTING_CODE vocabulary and only profile-declared tags are accepted. Stable IDs resolve through configured prefix-to-group mappings and then select matching Markdown blocks/CSV rows. Section selectors resolve only to repo-local paths declared in the current profile. Invalid/unknown inputs fail before stdout is written; path resolution rejects traversal and symlink escape. Selection order follows profile order, independent of argument order.
4. **Provenance describes the exact rendered contribution.** Normalize CRLF to LF, build each source block with a deterministic path/selection header and separator, and count that complete serialized block. Each manifest source records path, group ID, reason, matched tags/ID/section, whole-file SHA-256, selected-content SHA-256, and character contribution. Contributions sum to the normalized `bundle_text` count. Distinct selected group IDs determine group count.
5. **Measure only the text actually injected.** Count Python Unicode code points in normalized `bundle_text`, including the optional task card and deterministic wrappers. Default caps remain 8 groups and 12,000 characters. Do not truncate or silently drop required content. On overrun, emit a JSON `OVER_BUDGET` result with an empty `bundle_text`, actual/allowed counts, and largest contributors, then return nonzero; text format returns no body and a nonzero code. Invalid input errors go to stderr and return nonzero without a partial package.
6. **Budget exceptions are Change-scoped and fail closed.** If present, read only `openspec/changes/<change-id>/design/context-budget-exception.json`. Require schema version, matching Change ID, `status=APPROVED`, reason, approver, approval date, future/current `expires_at`, in-repository evidence path, `max_groups`, and `max_chars`. The exception can raise only the limits it names; it cannot override source/path validation. A malformed, expired, mismatched, or under-authorized record is never treated as approval.
7. **Task cards use structured, approved design data.** Find the exact TASK row in `tasks.md`, its ACs in `design/user-stories.md`, and the corresponding row in the `### Design Task Breakdown and Interface Scope` table. Use allowed paths and verification commands only from that design row. Include detailed design only when workflow state shows Stage 07 completed for the same active Change. Missing design fields use the exact marker defined in the spec and are listed in `missing_fields`; an unknown TASK ID fails. Never infer paths or commands from task titles.

Alternatives considered: a new standalone renderer/config would split the source of truth and create another command to discover; rejected. Replacing `lean`/`on_demand` outright with a new schema would require a wider migration of display/report consumers; deferred in favor of aligned group-ID metadata with validator-enforced consistency. Returning only a file list or estimating source sizes cannot prove what the Agent receives; rejected. Always loading complete files would preserve the present context bloat; rejected.

### Existing Code Change Impact

- Repository/path/branch/commit: `D:\Work\灵犀智学\农业项目\digoo-coding`, `main`, HEAD `91aab8e0f909921082a5096c0d3ac14e735baf18` (current working tree may contain newer uncommitted Stage 07 artifacts).
- Existing function/script: `scripts/agent-context.py`; `load_stage`, `check_path`, and `main` currently print lean/on-demand lists and do not read/render source content or count characters. Change strategy: add argument parsing and pure selection/render helpers; preserve default list mode and `--full`; make all render output atomic after validation.
- Configuration: `docs/STEP-ARTIFACT-CONTRACTS.json` `input_policy.stage_profiles`; add aligned group IDs, trigger/ID mappings, and the two caps. `scripts/check-step-contracts.py` rejects array length mismatch, duplicate group IDs, unknown references, invalid tags, and invalid budgets.
- Consumers/docs: update the command reference in `scripts/README.md` and `scripts/README-zh.md`; update `prompts/00-next-step.md` and stage prompts 02–10 to consume body-only render output and stop on failure; update the usage examples in `docs/INPUT-OUTPUT-POLICY.md` and `docs/INPUT-OUTPUT-POLICY-zh.md`. The existing `stage-io-report.py` continues reading legacy projections. Update `scripts/test-agent-context.py` fixtures for render output, path safety, and prompt invocation consistency.
- Prompt compatibility: `prompts/00-next-step.md` and prompts 02–10 currently request only the file list. They must invoke `--render --format text` and stop on nonzero; no stage may fall back to `--full` after a render failure. Stage 01 has no context-tool invocation and is unchanged.
- Compatibility: existing invocations remain list-only and keep their CLI/output shape; the default group lists are deliberately reclassified where inputs are conditional. `--render` is opt-in at the CLI, then becomes the workflow prompt default. `--full` remains audit-only. No file/database migration. Rollback is reverting the Change files; the old list path remains functional. No production runtime deployment or external dependency is involved.
- Existing tests: `scripts/test-agent-context.py` currently covers only lean-group limits. Stage 08 adds regression cases for rendered content, selectors, provenance, char/group boundaries, exceptions, and TASK cards; tests are designed here but are not run in this stage.

### Design Task Breakdown and Interface Scope

| Task ID | AC | Design work | Allowed modification paths | Verification |
|---|---|---|---|---|
| TASK-001 | AC-001/002 | Add the file-backed Stage 02 profile and aligned group IDs, tag/ID mappings, and validated limits to Stage 02–10 profiles; keep existing file paths in profile arrays. | `docs/STEP-ARTIFACT-CONTRACTS.json`; `scripts/check-step-contracts.py` | TEST-001, TEST-003 |
| TASK-002 | AC-001 | Implement ordered source selection, Markdown/CSV extraction, root-bound path checks, deterministic rendering, and manifest generation. | `scripts/agent-context.py`; `scripts/test-agent-context.py` | TEST-001, TEST-002 |
| TASK-003 | AC-002 | Implement normalized Unicode counting, group counting, over-budget failure output, and Change-scoped exception validation. | `scripts/agent-context.py`; `scripts/test-agent-context.py` | TEST-003, TEST-004 |
| TASK-004 | AC-003 | Extract TASK/AC/design fields and approval state without guessing; include missing fields explicitly. | `scripts/agent-context.py`; `scripts/test-agent-context.py` | TEST-005, TEST-006 |
| TASK-005 | AC-001–003 | Document list, audit, text-render, JSON-render, tags, selectors, and task-card modes; route all file-backed stage prompts through body-only render output. | `scripts/README.md`; `scripts/README-zh.md`; `prompts/00-next-step.md`; `prompts/02-requirements-analysis.md`–`prompts/10-acceptance-audit.md`; `docs/INPUT-OUTPUT-POLICY.md`; `docs/INPUT-OUTPUT-POLICY-zh.md` | TEST-001, TEST-005, TEST-007 |
| TASK-006 | AC-001–003 | Extend isolated temporary-repository CLI fixtures to cover success/failure/boundary behavior and prompt invocation consistency. | `scripts/test-agent-context.py` | TEST-001–007 |

No API operations or cross-boundary interfaces exist. The supported interface is a local CLI over repo-local read-only files and stdout/stderr. Cross-boundary interface records and API→IO mappings are not applicable.

### Design Gaps and Entry Conclusion

- The target process has no embedded Agent-host API. `--format text` provides the exact prompt body; the caller must pass that stdout body onward and retain JSON mode only when it needs the manifest. This keeps manifest overhead outside the declared 12,000-character context budget.
- Exact conditional group and ID-prefix mappings for all stages are configuration work in TASK-001; the validator must reject unbound IDs/tags rather than fallback to full inputs.
- Q-003 risk-tier rules remain open and outside this Change. Stage 08 must remain blocked until its existing prerequisite is closed.
- Design conclusion: compatible with the frozen baseline; no API, data model, or technology selection changes. Allowed to enter implementation only after Stage 07 approval and all normal Stage 08 entry gates, including Q-003, pass.

## Interface Design

### Interface Inventory

| Interface | Request | Success | Failure | Authentication/permissions |
|---|---|---|---|---|
| Existing CLI list mode | `--stage`, optional `--change`, optional `--full` | Existing readable selection list | Existing argument/config failure behavior | Local repo read permission; no write |
| Context render | `--stage`, optional `--change`, `--render`, `--format json|text`, repeated tags/IDs/sections | JSON manifest + body, or body-only text; deterministic exit 0 | Invalid input: stderr + nonzero; over-budget JSON: empty body + metrics + nonzero | Local repo read permission; no write |
| TASK card | Render args plus exact `--task-id` | Card appended to body with source references | Unknown task nonzero; unresolved fields explicitly marked and listed | Same local read-only boundary |

HTTP/API contract: `x-api-scope: none` (see `api/openapi.yaml` marker). CLI IDs are not OpenAPI `operationId`s.

### Interface Boundary Inventory

N/A: files are read from the same checked-out repository and output is stdout/stderr. No HTTP, native/device, third-party, asynchronous, remote storage, or file-import/export integration is introduced.

### Contracts and Error Semantics

JSON success shape: `{status: "OK", bundle_text, manifest: {schema_version, stage, change_id, tags, group_count, character_count, limits, sources[], task_card?}}`. Every source has `path`, `group_id`, `selection_reason`, `matched_tags`, `selected_ids`, `selected_section`, `source_sha256`, `selected_sha256`, and `character_contribution`.

Over-budget JSON shape retains the manifest and sets `status: "OVER_BUDGET"`, `bundle_text: ""`, and `budget: {actual, allowed, largest_sources[]}`; exit code is nonzero. For all other input/config/path/selector errors, do not emit JSON that resembles a complete bundle; write a clear diagnostic to stderr and return nonzero. Text success writes only `bundle_text`; text failure writes no body. Existing list mode is unchanged.

Paths are repo-relative, normalized, and resolved before reading; reject absolute paths, traversal, unreadable files, and symlinks resolving outside the repo. Decode UTF-8 strictly; normalize CRLF to LF before selection/hash/count. No retries, network timeouts, or concurrency state apply to this local read-only command.

### Interface Traceability

| Contract | AC | Test IDs |
|---|---|---|
| Group/tag/ID/section selection and source manifest | AC-001 | TEST-001, TEST-002, TEST-007 |
| Final text budget and approved exception | AC-002 | TEST-003, TEST-004 |
| TASK-ID card and explicit missing data | AC-003 | TEST-005, TEST-006 |

No operationId or cross-boundary interface IDs exist; AC→TEST edges are recorded in `traceability.csv`.

## Frontend Detailed Design

N/A: the approved Change contains only local developer CLI behavior; no page, route, visual component, frontend state, or responsive layout exists.

## Backend Detailed Design

N/A: this repository has no application server or backend service. The local script performs read-only filesystem selection and stdout/stderr rendering; no database, migration, server-side domain model, or remote IO is introduced.

## Test Design

### Test Strategy

Use Python 3.11 standard-library tests in the existing `scripts/test-agent-context.py`, invoking the CLI in isolated temporary repository fixtures. Assert user-observable stdout/stderr, exact JSON shape, stable source order/hashes, no partial body, exit codes, and boundary counts. A static prompt check verifies that every workflow entry prompt invokes body-only render mode. No live Figma, network, database, or third-party dependency is used. Every AC has automated coverage; no manual-only case is needed for deterministic local CLI behavior. Test cases are planned in `design/test-cases.csv`; implementation-stage evidence will hold actual run results.

### Test Environment and Doubles

- Temporary repository fixture with a minimal contract JSON, Markdown/CSV source files, Change artifacts, and optional approval evidence.
- UTF-8 files containing LF/CRLF, non-ASCII code points, duplicate IDs, malformed selectors, missing paths, and an outside-root symlink where the platform supports it.
- Temporary `workflow-state.json` fixtures cover unapproved and Stage 07-approved Change state.
- No external service doubles are required; filesystem fixtures are the only test doubles.

### Manual Verification

N/A for feature behavior: all specified outcomes are deterministic and covered by CLI tests. Stage 10 still performs user acceptance and does not treat automated tests as approval.
