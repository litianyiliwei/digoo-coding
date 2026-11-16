# Stage Output Flow Audit

> Language: English | [简体中文](OUTPUT-FLOW-AUDIT-zh.md)

> 2026-11-13 update: Added Stage 02 `reference-research.md` and Stage 07 `design/interface-catalog.csv`; file-type output counts follow the actual output of `scripts/check-output-consumption.py`.
> 2026-11-11 second update: Stage 06 has been changed to Figma-only. `pen.dev`, `prototype.pen`, `PAGE-*.html`, `prototype.md`, `manifest.json`, and `design-tokens.json` are all removed from the process; Stage 06's only UI artifact is `figma-audit.md` (Figma MCP generation/read snapshot + PAGE inventory and mapping + UI review APPROVED). Historical artifacts are archived in each Change's `design/legacy/`. The current contracts are authoritative in `docs/STEP-ARTIFACT-CONTRACTS.json` and `docs/STAGE-IO-OVERVIEW.md`.
> 2026-11-11 cleanup: The old top-level `scripts/legacy`, `prompts/legacy`, `.claude/skills/legacy`, `templates/change-assets/legacy`, `workflow/evidence/legacy`, `workflow/handoffs/legacy`, old prototype snapshots, and temporary build scripts have been moved to `_trash/2026-11-11/`; old paths in the historical paragraphs of this document are retained as records of that time.

> Numbering note: This document records the analysis process before renumbering (old numbers 05/09/10/10b/11/12/13a-e/14b/15). New numbering mapping: 05→03, 09→04, 10→05, 10b→06, 11→07, 12→08, 13a→09, 13b→10, 13c→11, 13d→12, 13e→13, 14b→15, 15→16; `docs/WORKFLOW-STAGES.json` is authoritative.
> 2026-11-09 vibe refactoring note: Stages have been further consolidated into 01-10 (06 = prototype/page inventory, 07 = detailed design/interface/test, 08 = implementation, 09 = independent verification, 10 = acceptance), and the old artifact split (use-cases/design-plan/frontend-design/backend-design/test-design/api-traceability) has been merged into new carriers. **Section 3 has been updated to the current 01-10 topology; Section 3.1 and Sections 4-9 retain the historical analysis of the old 17 stages.** The current authority remains `docs/STAGE-IO-OVERVIEW.md` and `docs/STEP-ARTIFACT-CONTRACTS.json`.

- Change ID: N/A (process audit)
- Status: DRAFT (analysis report, does not change stage contracts)
- Source baseline: `docs/STEP-ARTIFACT-CONTRACTS.json`, `docs/WORKFLOW-STAGES.json`, `docs/OUTPUT-TEMPLATE-MATRIX.csv`
- Related requirements/AC: N/A (process document)
- Generation date: 2026-11-06; latest review: 2026-11-10
- Version: v0.3 (current 01-10 flow table)

## 1. Determination Criteria

| Status | Meaning |
|---|---|
| Consumed | The downstream stage's `inputs` explicitly lists the file/content, or a gate script reads it directly |
| Indirectly consumed | Referenced downstream only with aggregate wording such as "project-level baseline/frontend and backend detailed design," without listing specific files |
| Archived only | Exists only as stage evidence, approval record, or handoff hash, with no downstream reader |
| Not persisted | The contract lists "content" as an output but specifies no file path, so downstream cannot consume it reliably |

## 2. Overall Conclusions

The current 01-10 main chain is closed: 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10. Every stage's file-type inputs can be traced to an upstream stage or to explicit "in-package static/external material"; all 59 file-type outputs have registered consumers (1 of which is pure evidence), and reverse validation found no "read but unregistered" references (0). The state machine has been validated in the real process: after Stage 03 was frozen, it successfully advanced to 04, and `check-entry 04` returned `ENTRY_READY`.

Boundaries and design choices confirmed in this review round:

1. **Input sources**: The process documents of 00 are in-package static authority, the business materials of 02 are external inputs, and `openspec/specs/**` of 05/07 are archived-state inputs; it is expected that they have no DAG producer, and upstream artifacts must not be fabricated.
2. **Output usage**: All fixed-path outputs have downstream consumers; "content-type outputs" such as code/test results and acceptance reports have no fixed path and are verified by stage gate scripts (`test-all.sh`, `verify-before-completion.sh`, `check-independent-verification.py`) rather than by contract matching.
3. **Declarative shared artifacts**: `baseline-status.md` (01/03), `design.md` (05/07), `traceability.csv` (initialized in 07, only appended by 08/09/10), and `lessons/decisions/assumptions` (02/10) are legitimately updated by multiple stages; the handoff manifest automatically marks them `mutable_by_design`, and downstream verifies only their existence, avoiding normal updates being misjudged as drift.
4. **Operating boundary**: A single active Change; `next-change` supports entering the next Change serially and does not support concurrent scheduling. Rework rolls back along the dependency closure via `reopen`.

## 3. Current 01-10 Per-Stage Flow Table

| Stage | Input Sources (traceable producers) | Output Consumers (registered) | Determination |
|---|---|---|---|
| 00 Next-Step Orchestration | `workflow-state.json` (runtime); in-package static authority: `PROCESS-MAP.md`, `STEP-ARTIFACT-CONTRACTS.json`, `WORKFLOW-STAGES.json`, `BASELINE-FEATURE-INTERACTION.md`, `OUTPUT-TEMPLATE-MATRIX.csv`; real artifacts/approvals/OpenSpec CLI (external) | Next-stage determination report (displayed in conversation); `workflow-state.json` → SYSTEM/runtime | Entry stage; static authority having no DAG producer is expected; pending/blocked must not be crossed. |
| 01 Project Initialization | User project goals and repository location, repository status (external); existing `AGENTS.md` (self-read/self-write) | `AGENTS.md` → ALL; `workflow-state.json` → SYSTEM; `baseline-status.md` → 03-10; `toolchain-report.md` → 03 | External inputs; all outputs registered; `baseline-status.md` and Stage 03 are declarative shared artifacts, and the handoff marks them `mutable_by_design`. |
| 02 Requirements Business Analysis | Interviews/business materials/legacy system materials/project goals (external); existing `docs/product/*` (if present); `openspec/specs/**` (read-only archive) | requirements-analysis/workflows/data-objects/rd-matrix/business-rules → 03/04/05 (workflows also 06/07); glossary → 03/04/05; acceptance-policy → 03/04/07/10; open-questions → 03/04/05/06; BASELINE-BRIEF/role-permission/change-sizing → 03/04/05/10; decisions/assumptions/id-conventions → 03/04/05/10; lessons → 04/05/10; BASELINE-INDEX → 03 | External/read-only inputs; all outputs registered; `BASELINE-INDEX.md` has had its contract and consumption records added. |
| 03 Overall Project Architecture | 01 (toolchain-report, initial baseline-status); 02 (complete requirements + resident baseline); open-questions (read-only); technology selection interviews/non-functional requirements (external) | Architecture/contracts/tests 9 documents → 07/08; frontend-conventions → 06/07/08; containers-and-deployment → 07; baseline-status → 04-10; baseline-manifest/constraint-registry → 04/05 + runtime baseline gate; baseline-audit-report → 04 | Inputs closed; outputs closed; all 22 constraint sources are locatable; frozen and actually advanced to 04 (`ENTRY_READY`). |
| 04 Proposal Breakdown, Dependency Ordering, and Roadmap | 03 (manifest/registry/status/audit-report); 02 (complete requirements + resident baseline); open-questions; technical debt (external) | `proposal-roadmap.md` → 05 | Single output, single consumer; reasonable. The next Change is reopened by `next-change` at 05 and read again. |
| 05 Proposal-Level Requirements | 04 roadmap; 02 requirements/resident baseline; 03 baseline; `openspec/specs/**` (read-only archive); open-questions | proposal → 06/07/09; spec → 06/07/08/09/10; tasks → 07/08/09; design → 06/07/08/09/10; user-stories → 06/07/08/09/10; baseline-impact/binding → 06-10 | Inputs closed; outputs closed; AC is the sole anchor for testing and verification. |
| 06 Figma Design and Review | 05 proposal/spec/design/user-stories; 02 workflows/data-objects/rd-matrix/business-rules; 03 frontend-conventions Section 9; baseline-status/impact/binding; Figma MCP (when UI is involved) | `figma-audit.md` (Figma MCP generation/read snapshot + PAGE inventory and mapping + UI review) → 07/08/09/10 | Inputs closed; the only UI artifact is figma-audit.md; no longer produces pen/HTML/prototype.md/manifest/06 traceability/design-tokens. |
| 07 Detailed Design | 05/06 (proposal/spec/tasks/design/US, figma-audit); 02 (FLOW/DO/RD/BR/acceptance-policy/BASELINE-BRIEF); 03 architecture/contracts/tests/ADR; baseline-impact/binding; Figma MCP (read in real time when available, otherwise use the figma-audit persisted snapshot) | design.md → 08/09/10; test-cases → 08/09/10; openapi/api-io-mapping/io-catalog (when there is an API) → 08/09; traceability → 08/09/10 (this stage initializes PAGE→AC and merges API/tests) | Inputs closed; outputs closed; conditional artifacts must use `n/a` + `waiver_reason`. |
| 08 Implementation and Verification | 05 tasks/spec/US; 06 figma-audit/PAGE inventory; 07 design/test-cases/API/IO/traceability; 03 architecture/contracts/tests; baseline; Figma | Code/migrations/configuration, tests and results (content-type, no fixed path); code-review → 09/10; implementation evidence; conditional BCR/ADR | Inputs closed; fixed-path output registration closed; content-type outputs are verified by `test-all.sh` / `verify-before-completion.sh`. |
| 09 Independent Verification | 08 code/revision/code-review/test evidence; 05 proposal/spec/design/tasks/US; 06 figma-audit; 07 API/IO/test-cases/traceability; 03/05 baseline; Figma | independent-verification-report.md/json → 10 | Inputs closed; consumed only by 10; requires an execution context different from the Builder's. |
| 10 Acceptance and Archiving | 09 report/json; 08 code/tests/code-review; 05 spec/US/traceability/design; 06 figma-audit; 07 test-cases; deployment evidence; 05 baseline-impact/binding; 03 baseline-status; 02 acceptance-policy/BASELINE-BRIEF/change-sizing/lessons/decisions/assumptions/id-conventions | acceptance.md (pure evidence); lessons/decisions/assumptions → subsequent 03/04/05/10; acceptance report/approval record; when baseline revision is needed, submit a revision request and follow the amendment process | Inputs closed; the read-after-write of 10 has been added; acceptance is marked `evidence_only`; archived specs become inputs of subsequent Changes. |

> Review evidence (2026-11-11): `check-output-consumption.py` passes, 59 file outputs / 1 pure evidence / 0 unregistered reverse references; `check-step-contracts.py` has 11 contracts corresponding to 10 DAG stages; `stage-io-report.py --check` is up to date. Regenerated on 2026-11-11 after the Stage 06 rules converged.
> Counting note: After Stage 06 converged there were actually 57; this round, after adding Stage 07's update output declarations for `baseline-impact.md` and `baseline-binding.json`, there are 59. Script output is authoritative going forward.

### 3.1 Old 17-Stage Per-Stage Table (historical; do not use for the current process)

| Stage | Explicitly Consumed Outputs | Indirectly Consumed/Archive-Only Outputs | Outputs Without Consumers or Not Persisted | Recommendation |
|---|---|---|---|---|
| 00 Orchestration | `workflow-state.json` is read by 00/01/runtime | The next-stage determination report is only for the user | Optional write to `docs/workflow/next-step-report.md`, no fixed consumer | Keeping this report as conversation output is sufficient; do not force it to be persisted as a formal stage artifact |
| 01 Initialization | `workflow-state.json`, `baseline-status.md` are read by later stages and gates | `AGENTS.md` is implicitly read by all Agents; `toolchain-report.md` appears only in this stage's `next_inputs` | `toolchain-report.md` has no downstream input | Add toolchain/environment constraints to the 05 architecture inputs, or explicitly mark it as "initialization evidence only" |
| 02 Requirements Business Analysis | requirements-analysis, workflows, data-objects, rd-matrix, business-rules are explicitly read by 05/09/10/11 | glossary is read only by 05; acceptance-policy is only vaguely referenced by 05/09 | open-questions is read only by 06 | Add open-questions to 05/09/10 inputs; add acceptance-policy to 13e/15; add glossary to 10/13a |
| 05 Overall Architecture | baseline-status, manifest, registry are read by gates and 09/10/13/14/15; api/frontend/test conventions are explicitly read by 13b/13c/13e respectively | system-context, domain-boundaries, containers, data-flows, logical-erd, technology-decisions, ADR are summarized only as "project-level baseline" by 13a/13d | `baseline-audit-report.md` has no downstream input | Add the audit report to 09 inputs; list specific architecture files in 13a/10/11/12 inputs, forbidding writing only "baseline" |
| 09 Roadmap | `proposal-roadmap.md` and the candidate scope/baseline applicability summary are read by 10 | None | Items 2 and 3 of the outputs are actually fields of the roadmap, not independent artifacts | Merge into one roadmap file; 10's inputs explicitly reference the "candidate Change row" |
| 10 Proposal Requirements | proposal, specs, baseline-impact, baseline-binding are read by 06/11/12/09-13/14/15/15 | `tasks.md` is explicitly read only by 14; `design.md` only by 14/15; `user-stories.md`/`use-cases.md` only by 06/11 | 10/11/12 do not list `design.md` as input; 13/15/16 do not list US/AC as input | Add `design.md` to 10/11/12/13e inputs; add US/AC to 13/15/16 inputs; add tasks to 13a |
| 06 Prototype | prototype-build and prototype-audit are explicitly read by 11; pen.dev pages serve as the basis for page derivation | None | None | Keep; clarify in 11 that "prototype pages are drafts, and page-inventory is the authoritative list after approval" |
| 11 Inventory | page/block/interaction inventory is read by 12/10/11/12/13e | None | None | Keep; clarify that page-inventory is the only authoritative page list, and figma-audit only performs mapping verification |
| 12 Figma Audit | `figma-audit.md` is read by 13a/13c | 13b lists "Figma interaction" only as optional | None | Keep; make 13b explicitly read figma-audit's interaction/state differences |
| 13a Design Control | `design.md` is read by 14/15 | "task breakdown/gap list" appears only in the `next_inputs` text | The task breakdown/gap list has no file path; 13b-e do not read `design.md` | Write the task breakdown/gaps into a fixed section of `design.md`, or add `design/design-plan.md`; list `design.md` in 13b-e inputs |
| 13b OpenAPI | `openapi.yaml` is read by 13c/13d/13e/14/15 | None | The "operationId to page event/AC tracing relationship" has no file, and 13e cannot merge it reliably | Add `design/api-traceability.csv`, or explicitly write it into `traceability.csv` and declare that it is created by 13b and extended by 13e |
| 13c Frontend Design | `frontend-design.md` is read by 13e/14 | The test/component state mapping is a "Test plan" section within the document and is not specified separately | No independent file, easily missed | Make it a fixed section of `frontend-design.md`, and have 13e reference the section name |
| 13d Backend Design | `backend-design.md`, `api-io-mapping.csv`, `io-catalog.csv` are read by 13e/14/15 | None | None | Keep |
| 13e Test Design | `test-design.md`, `traceability.csv` are read by 14/15/15 | None | None | Keep; clarify that traceability is the only traceability aggregation file |
| 14 Implementation | Code/migrations/configuration, test code and results, code-review, implementation evidence are read by 15/16 | Conditional BCR/ADR enters only the baseline revision process | None | Keep |
| 15 Independent Verification | report + JSON are explicitly read by 15 | None | None | Keep |
| 15 Acceptance and Archiving | acceptance, archive results, roadmap/baseline write-back are used by subsequent Changes and baseline revisions | None | None | Keep |

## 4. Key Issues

### P0: Flow Gaps Affecting Downstream Correctness

| ID | Issue | Impact | Recommendation |
|---|---|---|---|
| F-01 | 13a's "task breakdown/design gap list" has no file | 13b-e cannot confirm the design scope and gaps, and frontend/backend may each supplement design separately | Write it into a fixed section of `design.md`, or add `design/design-plan.md`; 13b-e read it explicitly |
| F-02 | 13b's operationId tracing relationship has no file | 13e can only re-derive it from OpenAPI and the interaction inventory, easily missing mappings | Add `design/api-traceability.csv`; 13e merges it into `traceability.csv` |
| F-03 | `design.md` is not listed as input by 10/11/12/13e | 13a's unified design decisions may be ignored by subsequent design | Explicitly add `design.md` to the four stages' inputs |
| F-04 | US/UC/AC are not explicitly listed as inputs by 13/15/16 | Tests and acceptance may rely only on specs, missing proposal-level ACs | Add `design/user-stories.md`, `design/use-cases.md` to 13/15/16 inputs |
| F-05 | `open-questions.md` is read only by 06 | Open issues may bypass architecture, roadmap, and proposal requirements | Add open-questions to 05/09/10 inputs |
| F-06 | `acceptance-policy.md` is not explicitly read by 13e/15 | Test design and acceptance criteria may be inconsistent with the project acceptance policy | Add acceptance-policy to 13e/15 inputs |
| F-07 | `baseline-audit-report.md` has no consumer | Gaps/pending items found in the 05 audit do not affect the roadmap | Add baseline-audit-report to 09 inputs |

### P1: Drift Prevention and Verifiability

| ID | Issue | Recommendation |
|---|---|---|
| F-08 | Downstream inputs use the aggregate "project-level baseline" and cannot prove that specific files were read | 09-12 inputs list specific paths such as system-context, data-flows, logical-erd, technology-decisions, ADR, api/frontend/test conventions |
| F-09 | Page facts exist in three places: the prototype-build page list, page-inventory, and the figma-audit mapping | Clarify the authority order: 06 draft → 11 approved list → 12 only verifies, does not redefine; differences in 12 go back to 11 for revision |
| F-10 | Tracing facts are scattered: 11's Prompt requires updating `traceability.csv`, but 11's contract outputs do not list that file; 13b's tracing relationship exists only in "content"; only 13e declares producing `traceability.csv`, so the same file has multiple writers but undefined ownership | Define a single `traceability.csv`: initialized by 11, only appended by 13b/13e; the contract explicitly states in 11/13b/13e that this file is a cumulative artifact |
| F-11 | UC/US and specs repeatedly describe the same behavior | Clarify that specs are the sole source of normative behavior; UC/US retain only scenarios, ACs, and tracing IDs, and do not copy full specifications |
| F-12 | The contract has no machine-readable `consumed_by` | Add a `consumed_by` list to every output, and add `check-output-consumption.py` to check for dead outputs |

### P2: Streamlining and Noise Reduction

| ID | Issue | Recommendation |
|---|---|---|
| F-13 | 01 `toolchain-report.md` has no downstream consumer | Add it to 05 as an environment/tool constraint input, or mark it `evidence_only` and exclude it from "must be consumed" |
| F-14 | 00 `next-step-report.md` is an optional file | Keep it as conversation output and do not force persistence; avoid producing files that no one reads |
| F-15 | 09 outputs split roadmap fields into three "outputs" | Merge into a single `proposal-roadmap.md` artifact, with field-level requirements written in the template |
| F-16 | 13c's "test cases/component state mapping" has no specified carrier | Make it a fixed section of `frontend-design.md`, referenced by 13e by section name |

## 5. Recommended Mechanism Changes

1. **Add consumer fields to the contract**

   ```json
   {
     "outputs": [
       {
         "path": "docs/architecture/data-flows.md",
         "consumed_by": ["09-feature-design", "12-backend-detail-design"],
         "evidence_only": false
       }
     ]
   }
   ```

   For content-type outputs, `path` may point to a file section, such as `openspec/changes/<change-id>/design.md#design-plan`.

2. **Add a dead-output check**
   - Every `outputs` must have at least one `consumed_by`, or an explicit `evidence_only: true`.
   - `consumed_by` must point to a subsequent stage that actually exists in the DAG.
   - Downstream `inputs` must be able to find the upstream output in reverse (at least a path match).
   - Wire it into `check-package.py` and add `scripts/check-output-consumption.py`.

3. **Unify tracing and page authority**
   - `traceability.csv`: initialized by 11, appended by 13b with API→EVT/AC, appended by 13e with TEST→AC/API/IO.
   - `page-inventory.csv`: the only page list after 11's approval; the page list in 06 is only a draft; 12 only verifies and does not create separate page IDs.

4. **Change "content outputs" into "file + section outputs"**
   - 13a: `design.md#design-plan` (task breakdown/gaps).
   - 13b: `design/api-traceability.csv`.
   - 13c: `frontend-design.md#test-plan`.
   - This lets downstream verify by path/section instead of relying on chat content.

## 6. Conclusion

The current flow is not "a large number of worthless outputs"; rather, **key outputs lack clear consumers, content outputs lack persistence locations, and downstream inputs are too coarse**. Fixing F-01 to F-07 first, then doing `consumed_by` and dead-output checks, can significantly reduce the risk of "the stage is done but downstream did not use/read it." The archive-type outputs in P2 can be retained as evidence and need not be deleted.

## 7. P0 Fix Record (2026-11-06)

| ID | Fix |
|---|---|
| F-01 | Add `design/design-plan.md` (template `templates/change-assets/design/design-plan.md`); 13a outputs it and writes the task breakdown/gaps/admission conclusion; 10-13 inputs read it explicitly |
| F-02 | Add `design/api-traceability.csv` (template `templates/change-assets/design/api-traceability.csv`); 13b outputs it, and 13e merges it into the single `traceability.csv` |
| F-03 | The contracts, Skills, and Prompts of 10/11/12/13e all add `design.md` and `design/design-plan.md` inputs |
| F-04 | Add proposal-level `design/user-stories.md` and `design/use-cases.md` (US/UC/AC) to 13/15/16 inputs |
| F-05 | Add `docs/product/open-questions.md` (read-only) to 05/09/10 inputs |
| F-06 | Add `docs/product/acceptance-policy.md` to 13e/15 inputs |
| F-07 | Add `docs/project/baseline-audit-report.md` to 09 inputs |

The contract tables, stage overview, template matrix, and Prompts/Skills have been synchronized; `check-package.py`, `check-step-contracts.py`, `check-output-template-matrix.py`, and `stage-io-report.py --check` have all been re-verified.

## 8. P1 Fix Record (2026-11-06)

| ID | Fix |
|---|---|
| F-08 | 09-12 inputs changed to list system-context, domain-boundaries, containers, data-flows, logical-erd, technology-decisions, api/frontend/test conventions, and ADR file by file; the Change artifact inputs of 13a-15 also changed to explicit paths, no longer writing only "baseline/detailed design" |
| F-09 | Clarify page authority order: the 06 prototype-build page list is a draft → 11 page-inventory is the only authority after approval → 12 figma-audit only verifies mapping, and differences go back to 11 for revision |
| F-10 | `traceability.csv` is initialized by 11, 13b writes `api-traceability.csv`, and 13e merges them; the contracts, Prompts/Skills, and template matrix of the three have been unified |
| F-11 | Clarify that specs are the sole source of normative behavior; UC/US retain only scenarios, ACs, and tracing IDs, and do not copy full specifications (Stage 05 Prompt/Skill and the two templates have been annotated) |
| F-12 | The contract adds an `output_consumption` mapping (58 file outputs), adds `scripts/check-output-consumption.py` and wires it into `check-package.py`; every file output must have a downstream consumer or an explicit `evidence_only` |

`stage-io-report.py`'s per-stage details now show the consuming stage of each file; the overview has been regenerated.

## 9. P2 Fix Record (2026-11-06)

| ID | Fix |
|---|---|
| F-13 | 01 `toolchain-report.md` has been added as an input to 05 for toolchain/test commands/environment constraints, and is no longer an unconsumed archive |
| F-14 | 00's next-stage determination report is changed to "displayed in conversation, not forced to persist," and no longer produces an unread `next-step-report.md` |
| F-15 | 09's three outputs are merged into one `docs/product/proposal-roadmap.md` (scope/dependencies/value/baseline applicability domain/potential revisions are all fields of this file) |
| F-16 | 13c's "test cases/component state mapping" is fixed as a section of `frontend-design.md` and is no longer a pathless content output |

The consumption mapping is now 59 file outputs (including the 2 baseline artifacts re-declared by 07); there are no evidence-only outputs (all file outputs have explicit consumers or belong to runtime/future stages).

## 10. 2026-11-10 Current 01-10 Topology Fix Record

> This section records the second round of flow review and fixes under the current topology; Sections 1-9 retain the historical analysis of the old 17 stages.

| ID | Issue | Fix |
|---|---|---|
| R-01 | The current stage's `pending_approvals` blocks its own `transition` and has no release entry | `workflow.py transition` allows submitting approved approvals in evidence and atomically clearing that stage's pending approvals; unapproved ones are still rejected |
| R-02 | Multiple Changes have no iteration entry | Add `workflow.py next-change`: archive 05-10 into `completed_changes`, switch `active_change_id`, and reopen from 05 |
| R-03 | 09 failure / 10 rejection has no rollback path | Add `workflow.py reopen`: roll back along the dependency closure, clear related approvals/blocks, and record `reopen_history` |
| R-04 | `transition` does not verify whether the outputs declared by the contract are complete | Check evidence against `STEP-ARTIFACT-CONTRACTS.json`; conditional non-applicable items must have `status=n/a` + `waiver_reason` |
| R-05 | Legitimate downstream updates to shared artifacts such as 01/03 and 05/07 break upstream handoff hashes | The handoff manifest automatically writes `mutable_by_design`, and such artifacts are only verified for existence |
| R-06 | The 02 contract missed registering `BASELINE-INDEX.md` | Added to 02 outputs and consumption records |
| R-07 | 10 updates `decisions.md`/`assumptions.md`/`id-conventions.md` but did not declare reading them | Added to 10 inputs and consumption records |
| R-08 | 06's `prototype.md`/`design-spec.json`/`figma-handoff.*` are actually read by 08/09/10 but were not registered | Added 5 `consumed_by` entries; `check-output-consumption.py` gains reverse validation |
| R-09 | Old-topology handoffs remain in the project directory | Moved into `workflow/handoffs/legacy/` |
| R-10 | workflow-orchestrator still requires manually changing `completed_steps`/`current_step` | Changed to require `transition` |
| R-11 | After a stage completes there is no "pending review" state, and the Agent can proceed directly to the next stage | Add `workflow.py request-review` (freezes `current_step`, writes `pending_approvals`) and `approve` (writes `approvals_history`); `transition` mandatorily requires approval records for 02-10; 08/09 are also set to manual approval; the PreToolUse hook rejects cross-stage writes during pending review |
| R-11 | Figma design inputs have no unified definition | Unify, across Stage 06/07 Prompts/Skills, the Figma audit and handoff templates, contracts, and per-stage tables, as: `figma-audit.md` + `figma-code/` (design code (get_design_context persisted)) + `figma-layout.csv` (runtime assertion mapping) + real image/SVG assets + project design specification; no reference screenshots, and `check-figma-audit.py --strict` enforces node completeness and assertion subsets |

Parallel Stage 03 work has also corrected the constraint source section: the `file`/`section` of all current 22 constraints are locatable, and `audit --require-frozen` no longer reports missing sources.

Verification: `check-package.py`, `check-step-contracts.py`, `check-output-consumption.py`, `stage-io-report.py --check`, and `test-workflow-runtime.py` (15 items) all pass; `baseline-governance.py audit` is `BASELINE_VALID`. Later on 2026-11-10, Stage 03 completed manual approval, all 22 constraints were set to ACTIVE and frozen, `audit --require-frozen` returned `BASELINE_FROZEN_AND_VALID`; `transition` advanced to 04 under the new 14-item output completeness rules, and `check-entry 04` is `ENTRY_READY`. The per-stage table in Section 3 of this document has been updated to the current 01-10 topology, and the old table is retained in 3.1.

## 11. 2026-11-11 Stage 06 Convergence and Flow Fixes

> Per the user's explicit rule: the prototype output is only `prototype.pen`, and the post-prototype-review output is only HTML; subsequent interface inputs come from Figma MCP, and when necessary the MCP read results are persisted as files.

| ID | Issue | Fix |
|---|---|---|
| R-12 | 06a produces `prototype.md`, `manifest.json`, and the initial `traceability.csv`, which contradicts "prototype only has pen, post-review only has HTML" | The 06 contract, Prompt, Skill, template matrix, and `check-stage06a.py` converge to `prototype.pen` + `PAGE-*.html`; `build-figma-source.py` drops the manifest and directly verifies the freshness and marker completeness of HTML and pen |
| R-13 | `design-tokens.json` is mandatorily read by 06b/07 but no stage produces it | Removed from the process: visual specifications now come from Section 9 of `frontend-conventions.md` + the Figma MCP `get_variable_defs` read results; current Change files are archived in `design/legacy/2026-11-11-pre-figma-mcp-redesign/` |
| R-14 | `prototype.pen` is depended on by manifest/build scripts but is not a contract output | Explicitly made a 06 output, consumed_by=GATE; the HTML after review is the only downstream UI structure and content baseline |
| R-15 | 07/09 Prompts read `BASELINE-BRIEF.md` / `acceptance-policy.md` but the contract does not register them | Added to 07/09 inputs and `output_consumption` |
| R-16 | 10's baseline_interaction claims it can directly update `baseline-status.md`; the rules still say Stage 10 creates the baseline impact list | Changed to write only `lessons/decisions/assumptions`, with baseline changes going through `open-amendment/close-amendment`; the baseline impact list belongs to Stage 05 |
| R-17 | The frozen baseline `frontend-conventions.md` was directly modified during Stage 06, `BASELINE_INVALID` | Went through the baseline revision process and was re-frozen, with a NO_IMPACT rebase review recorded for the in-flight Change; see `docs/architecture/baseline-status.md` for details |
| R-18 | Section 3 of `OUTPUT-FLOW-AUDIT.md` still describes the old 06 artifacts | Synchronized to the current `prototype.pen` + `PAGE-*.html` + `figma-audit.md` model |

Verification is based on the actual output of this round's `check-package.py`, `check-step-contracts.py`, `check-output-consumption.py`, `stage-io-report.py --check`, and `baseline-governance.py audit`.

## 12. 2026-11-11 Stage 06 Changed to Figma-only

> Per the user's explicit instruction "change to Figma-only": Stage 06 no longer goes through pen.dev prototypes and HTML handoffs; Figma becomes the only design tool and the only UI authority.

| ID | Issue | Fix |
|---|---|---|
| R-19 | 06a's `prototype.pen` and `PAGE-*.html` form "two designs, two toolchains," and HTML is only an intermediate consumed by Figma generation | Stage 06 converges to `06-figma-design-review`: the only artifact is `design/figma-audit.md` (Figma MCP generation/read snapshot + PAGE inventory and mapping + UI review APPROVED); `check-stage06a.py` and `build-figma-source.py` gates are deleted (archived in `scripts/legacy/`); 07-10 consume only figma-audit and real-time Figma |
| R-20 | `figma-audit.md` previously verified only PAGEs whose HTML existed and could not independently define the page set | `check-figma-audit.py` is changed to parse PAGE IDs from `## Page Coverage` and require each PAGE to close in the node mapping; `check-test-cases.py` also reads PAGE from figma-audit |
| R-21 | `frontend-conventions.md` §11/§13 and `acceptance-policy.md` still reference 06a HTML | Revise the frontend/product baselines through `BCR-2026-11-11-FIGMA-ONLY` and re-freeze; old version v1.0.1 → v1.0.2 |

## 13. 2026-11-12 UI Consistency Flow Convergence

Per user instruction (merge Figma persisted files, rework the process to "export once, consume offline downstream"; version control and MCP interruptions are guaranteed by the user, and rate limiting needs process avoidance):

- 06's only UI contract converges to `design/figma-audit.md` (token actual values, text styles, per-PAGE block specifications, design code, assertion scope, state coverage and decisions, asset inventory, MCP read records, UI review APPROVED) and `design/figma-code/` (design code (get_design_context persisted)), `design/figma-layout.csv` (runtime assertion mapping); no longer split per-page/per-state subdirectories or generate scattered token/contract JSON; **no screenshots, no saved reference images**.
- 06 exports completely in one pass (`get_variable_defs` once for the whole process, `get_metadata` once per PAGE, `get_design_context` as needed); 07/08 consume offline by default, re-reading page by page in batches only when the Figma file version changes or a page is ambiguous (serially, avoiding rate limiting).
- 07 must create the token → CSS variable/Element Plus theme/font mapping, fill in the route/dom_selector of `figma-layout.csv`, and define responsive rules; 08 must implement the global token layer and fonts, run `check-figma-layout.py` (Figma node geometry vs 1440×900 runtime DOM) and `check-design-tokens.py`, and write the per-PAGE numeric table and `figma-layout-check.json` in `## UI fidelity` of `code-review.md`; 09 independently verifies in `layout_checks`; 10 directly compares the running system and the Figma file and manually signs off PAGE by PAGE in `## UI acceptance`; **no screenshots are used throughout the process**.
- Machine gates: `check-figma-audit.py --strict` (06, node/assertion mapping completeness), `check-design-sections.py` (07, route/dom_selector and responsive rules), `check-figma-layout.py` + `check-design-tokens.py` + `check-code-review.py --strict` (08), `check-independent-verification.py` (09 `layout_checks`), `check-acceptance.py` (10 UI acceptance run entry/sign-off); missing any UI numeric evidence blocks advancement/archiving; screenshots are not gate evidence.
- Contracts and templates have been synchronized: `docs/STEP-ARTIFACT-CONTRACTS.json/.md`, `docs/STAGE-IO-OVERVIEW.md`, `docs/OUTPUT-TEMPLATE-MATRIX.csv`, `templates/change-assets/design/figma-audit.md`, `templates/change-assets/evidence/code-review.md`, `templates/change-assets/evidence/acceptance.md`, `templates/change-assets/design/independent-verification-report.md` and their schemas.
