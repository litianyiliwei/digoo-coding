# P0 Runtime Governance: State Machine, Stage Guards, SHA-256 Handoffs, and Independent Verification

> Language: English | [简体中文](P0-RUNTIME-GOVERNANCE-zh.md)

This toolkit upgrades process specification from Prompt conventions to executable gates. `docs/WORKFLOW-STAGES.json` is the single authoritative definition of the stage DAG; Skills/Prompts own the working method, while scripts own state transitions and verifiable constraints.

## 1. State Machine and Guards

View status:

```bash
python3 scripts/workflow.py status
```

Check whether a stage can be entered (this verifies dependencies, the current stage, approvals/blockers, and all upstream handoff hashes):

```bash
python3 scripts/workflow.py check-entry --step 01-project-bootstrap
python3 scripts/workflow.py check-entry --step 05-feature-requirements --change-id <change-id>
```

After a stage is complete, first prepare the evidence JSON, then run the only permitted state transition entry point:

```bash
python3 scripts/workflow.py transition --step 01-project-bootstrap --evidence workflow/evidence/01-project-bootstrap.json
```

The state machine advances only when all of the following conditions hold simultaneously:
- the current stage matches `workflow-state.json.current_step`;
- all DAG predecessor stages are complete;
- no pending approvals / blockers;
- all required outputs actually exist and are located inside the project root;
- at least one gate check, where every automated check must supply a real command, `exit_code=0`, and an in-repository log file; manual checks must supply a reviewer and an evidence file;
- human-reviewed stages (01–10) have a non-superseded `approvals_history` record written by `approve`; the evidence `approval` block is descriptive;
- the upstream handoff package exists and non-volatile artifact hashes are unchanged (volatile machine-managed files are existence-checked only).

### UI Consistency Gate

Changes involving UI must additionally satisfy the following conditions before advancement is permitted:
- 06: `design/figma-audit.md` is the sole UI contract (target framework/transcoding notes, actual token values, text styles, per-PAGE block specs, design code, assertion scope, state coverage and decisions, MCP read records, UI review APPROVED); at the same time produce `design/figma-code/` (the `.vue`/`.tsx` target-framework design code transcoded according to the overall technology selection in 06) and `design/figma-layout.csv` (assertion mapping); `check-figma-audit.py --strict --require-framework` exits with code 0; no screenshots are used.
- 08: port the target-framework design code directly and add only business logic; `design/evidence/code-review.md` contains `## UI fidelity`, with the Figma node, asserted element count/max deviation, layout evidence `design/evidence/figma-layout-check.json#PAGE-xxx`, differences, conclusion, and approver for each PAGE; the numbers are taken directly from the JSON, and only difference/`UI-DERIVED` PAGEs require manual explanation; `check-figma-layout.py` and `check-design-tokens.py` exit with code 0; `check-code-review.py --strict` exits with code 0.
- 09: `independent-verification.json` contains `layout_checks`, covering asserted element count/max deviation/tolerance/missing elements/verdict/evidence per PAGE and independently rerunning `check-figma-layout.py`; `check-independent-verification.py` exits with code 0; when `differences` exist without `deviation_approved`, PASS is not allowed.
- 10: `acceptance.md` contains `## UI acceptance`, signed off per PAGE by the design owner; PAGEs with no differences are batch-signed off based on machine evidence, while difference/`UI-DERIVED` PAGEs are checked side by side; `check-acceptance.py` exits with code 0.
- 07/08 consume the 06 export package offline by default; re-read in page batches (serially, to avoid rate limiting) only when the Figma file version changes or a page is ambiguous. When any of the above UI evidence is missing, transition or archiving is not permitted.

### Interface Boundary Gate

- When 07 involves HTTP API, App↔Native (uni-app/Flutter/React Native/native bridge), device, third-party, asynchronous, or file boundaries, it must generate `design/interface-catalog.csv` and reference it in `### Interface Boundary Inventory` of `design.md`; when there are no cross-boundary interfaces, write `N/A + reason` and mark that output `n/a` + `waiver_reason` in the evidence.
- `python scripts/check-interface-catalog.py --change <change-id> --strict` validates required fields, bidirectional consistency between HTTP_API and OpenAPI operationIds, and that every interface has at least one TEST and traceability row; add `--require-native` when the overall technology selection is uni-app/Flutter/React Native/native App.
- 08/09/10 consume this catalog row by row: 08 executes tests/real-device runs/stubs for each interface_id and records evidence; 09 independently cross-checks contracts, tests, and traceability, and judges FAIL/BLOCKED when anything is missing or not executed; 10 may archive only after signing off each row's owner and evidence.

State files are written using a temporary file plus atomic replacement and an exclusive lock; each successful transition appends to `transition_history`, retaining evidence paths, outputs, gate results, and approval summaries. Do not directly edit `completed_steps` or `current_step`; to repair state you must first establish the evidence and go through the controlled recovery process. When a topology refactor invalidates old stage IDs, use `python3 scripts/workflow.py migrate-state --reason <reason> --reset-step <stage-to-rerun>`: invalidated stages are retained in `legacy_completed_steps` and `topology_migrations`, and the current stage is recomputed according to the new DAG.

### Stage Review Stop (Mandatory)

Stage completion does not equal permission to enter the next stage. After each stage's artifacts and checks are complete, the process must first be frozen as pending review:

```bash
python3 scripts/workflow.py request-review --step 02-requirements-analysis --evidence workflow/evidence/02-requirements-analysis.json --summary "Requirements business analysis submitted for review"
```

- `request-review` writes `pending_approvals` and does **not** advance `current_step`; afterwards both `next-step.py` and `check-entry --step <next-stage>` will block.
- The Agent must present the handoff report according to `templates/workflow/step-handoff-report.md` and **end the turn immediately**; it must not, in the same session, read or execute the next stage's Prompt/Skill or create next-stage artifacts.
- Only after the user explicitly replies "Review passed <step-id>" may the approval be recorded:

```bash
python3 scripts/workflow.py approve --step 02-requirements-analysis --approver "<user>" --approved-at 2026-11-13 --evidence workflow/evidence/02-approval.md
```

- `approve` validates that the approval evidence file actually exists, writes the approval record into `approvals_history`, and clears that stage's `pending_approvals`; only then can `transition` be executed.
- `transition` requires a corresponding `approvals_history` record for all human-reviewed stages (01–10); merely writing the approval in the evidence or using `handoff-create` cannot bypass this.
- `reopen` clears the approval records of the reverted stages; after rerunning, review must be performed again.
- Under Claude Code, the PreToolUse hook in `.claude/settings.json` rejects writes to artifacts of stages after the current stage (shared artifacts excepted) and direct edits to `workflow-state.json`; it rejects them equally while review is pending. Other Agents should stop on their own based on `pending_approvals` and `current_step`.

### Clearing Approvals and Deadlock Boundaries

- `pending_approvals` for the current stage do not block that stage's own `transition`. After approval is complete, run `approve`: it verifies that every reviewed artifact hash in the review packet is unchanged, and appends a record to `approvals_history`. `transition` uses `approvals_history` as the approval authority, re-verifies the same hashes, and atomically clears that stage's pending approval item. The evidence `approval` block is descriptive and no longer has to say `approved`.
- `blocked_items` for the current stage can be resolved through the evidence's `resolved_blockers`: for each item write `step_id`, `resolution`, and an existing in-repository evidence path; after a successful transition the state machine atomically clears that stage's blocker items. Blocker items of other stages still must be handled first.
- Pending approval items of other stages or other Changes still prevent entry into subsequent stages.
- If a human-reviewed stage (01–10) has no non-superseded `approvals_history` record, `transition` refuses and the state does not advance; there is no "advance first, approve later" path. A stage that called `request-review` also needs a recorded approval even if its DAG flag is false.
- When a human-reviewed stage (01–10) has no `approvals_history` record, `transition` refuses outright; `request-review` and explicit user approval must come first.
- `check-entry` still reports the current stage's pending approval items; it is used to prevent re-executing that stage before approval, not to prevent submitting approved evidence.

### Rework Reopen

```bash
python3 scripts/workflow.py reopen --step 07-detailed-design --reason "Test design gap"
```

- Removes the target stage and all its downstream stages according to the DAG dependency closure, clears those stages' `pending_approvals` / `blocked_items`, and sets `current_step` back to the target stage.
- Does not delete approval history: matching `approvals_history` records are marked `superseded_at`/`supersede_reason`, and the removed approvals are copied into `reopen_history`.
- Invalidates only outgoing handoffs (`from_step` in the removed set): they get `invalidated_at`/`invalidated_reason`; the incoming handoff from the still-completed predecessor stays valid so the reopened stage can re-enter.
- Appends `reopen_history`, recording the reason, removed stages, superseded approvals, invalidated handoffs, and time.
- After rerunning a stage, evidence and the handoff package must be regenerated; an old handoff manifest at the same path is overwritten by the new `transition`.

### Conditional Stage Skip

```bash
python3 scripts/workflow.py skip-stage --step 06-figma-design-review --change-id <id> --evidence workflow/evidence/06-figma-design-review-skip.json
```

- Only stages with `"conditional": true` may be skipped (currently 06 for no-UI Changes).
- The skip evidence must set `skip: true`, a reason, and include a real passing `check-figma-audit.py --strict --no-ui` check with an in-repository log.
- The command records the skipped stage in `completed_steps` + `skipped_steps`, advances the current step, and writes a skip handoff (`skipped: true`, no artifacts) that downstream entry accepts.
- UI Changes must not use skip-stage; their 06 evidence sets `approval.required=true` and requires the recorded user UI review.

### Reset to Uninitialized

```bash
python3 scripts/workflow.py reset-state --reason "user requested a clean restart" --note "..."
```

- Archives the full previous state under `workflow/evidence/state-reset-<timestamp>.json`.
- Sets `completed_steps=[]`, `current_step=01-project-bootstrap`, clears `active_change_id`, pending/blocked items, approvals, transitions and baseline index, and records `reset_history` with a pointer to the archive.
- Marks every existing handoff `invalidated`; stale evidence files remain on disk for audit.
- This is an administrative reset, not a stage transition. Use it only on explicit user instruction.

### Multi-Change Iteration

```bash
python3 scripts/workflow.py next-change --change-id change-b
```

- Available only when the current Change's 05–10 are all complete, there are no pending/blocker items, and `transition_history` contains the acceptance record for that Change's 10.
- Archives 05–10 into `completed_changes`, retains project-level 01–04, switches `active_change_id`, and sets `current_step` back to 05.
- The first Change still enters 05 normally from 04; concurrent scheduling of multiple Changes is not supported.
- `abandon-change --change-id <id> --reason <text>` closes an active Change **without** acceptance: it supersedes approvals, invalidates outgoing handoffs, removes 05–10 from `completed_steps`, clears `active_change_id` and records `abandoned_changes`. The Change directory is left for audit; it is not archived.
- Every state-changing command appends an audit line to `workflow/state-events.jsonl` (`review_requested`, `approved`, `transition`, `reopen`, `skip`, `abandon_change`, `next_change`, `reset`, `migrate`, `baseline_index_synced`). The JSONL log is secondary audit data; `workflow-state.json` remains the operational state.

### Declarative Output Completeness

- `transition` reads the file-type outputs declared for that stage in `STEP-ARTIFACT-CONTRACTS.json` and requires the evidence to list one record for each output.
- Outputs whose condition does not apply must be written as `status: "n/a"` with `waiver_reason`, and may not be silently omitted; omissions fail before the state advances.
- Content-type outputs (such as "actual source code/migrations/configuration") have no fixed path and are still verified by that stage's gate scripts.

### Method Evidence Gate

- Evidence for 02–10 must contain `methods`; the policy follows `method_policy` in `docs/STEP-ARTIFACT-CONTRACTS.json`, and when it is absent the built-in default policy of `scripts/method_evidence.py` applies.
- Each method record contains skill/mode/questions/alternatives/decisions/open_questions/artifact_section/evidence. `brainstorming` records at least 4 questions and 2 alternatives in 03/07, and at least 3 questions and 1 alternative in 02/05; `writing-plans`, `test-driven-development`, and `verification-before-completion` record at least 1 decision and a real evidence path.
- In 03, the `brainstorming` questions/decisions must cover "new system/existing system/code address/third-party interfaces"; in the case of secondary development of an existing system, the code address must actually be read and "Existing System Secondary-Development Constraints" written in `technology-decisions.md`, converted into `LEGACY-*` in `constraint-registry.json`; third-party interfaces are written into the "Third-Party Interface Dependency List", EXTERNAL data flows, and API conventions.
- Run `python scripts/check-architecture-baseline.py --strict` before the end of 03; the baseline must not be frozen when "Existing System Secondary-Development Constraints", "Third-Party Interface Dependency List", code access records, third-party data flows, or `LEGACY-*`/`EXT-*` constraints are missing.
- In 07, the `brainstorming` questions/decisions must cover "existing functionality/new functionality/code address/third-party interfaces"; when modifying existing functionality, `### Existing Code Change Impact` in `design.md` must register files/classes/functions/interfaces/tables/tests, modification strategy, compatibility, migration/rollback, and risks; third-party interfaces must enter `interface-catalog.csv` as `THIRD_PARTY_API` rows with test/fakes evidence.
- `mode=equivalent` may be used only when the skill is truly unavailable, must record a `reason`, and must record the absence in `docs/project/toolchain-report.md`; "available" must not be treated as "used".
- 02's `internet-research` must record at least 3 research questions, 2 comparisons/alternatives, and 1 decision, with results written into `docs/product/reference-research.md`; `python scripts/check-reference-research.py --strict` additionally validates at least 3 real source URLs, access dates, `Reference product status`, and impact mapping. When there is no network access, mark BLOCKED and do not bypass it with `equivalent`.
- Standalone validation: `python scripts/check-method-evidence.py --step <step-id> --evidence <path>`; `workflow.py transition` invokes the same logic automatically.
- Section 4 of the handoff report must present key questions, alternatives, decisions, open items, artifact locations, and evidence paths.

### Input/Output Context Budget

- The contract `inputs` is the full audit/traceability set; default reads follow `input_policy.stage_profiles.lean` (≤8 read groups per stage, about ≤16000 characters). `agent-context.py` prints the lean/on-demand list by default; only `--full` prints the complete audit inputs.
- Reading order: `BASELINE-BRIEF` → current Change artifacts → targeted reads by matched FLOW/NODE/DO/RD/BR/ROLE/CAP/PAGE/API/IO/INTERFACE → full baseline/architecture/ADR/complete specs only when necessary, on demand, with the reason recorded.
- Outputs use reference-style output and do not copy input text in full; line limits for summary/evidence files are defined in `output_policy.summary_budgets`. At the end of a stage you may run `python scripts/check-output-context.py --stage <id> [--change <change-id>]`; if over budget, first check whether upstream content was copied, and if necessary split the Change or link upstream files.
- Full rules are in `docs/INPUT-OUTPUT-POLICY.md`.

### Evidence JSON Example

Start from `templates/workflow/stage-evidence.example.json`; the structure is described by `templates/workflow/stage-evidence.schema.json`. For each stage, replace the file paths, commands, exit codes, and approval information in the example with the real evidence for this run.

```json
{
  "step_id": "01-project-bootstrap",
  "change_id": null,
  "baseline_version": "",
  "outputs": [
    {"path": "AGENTS.md", "status": "created", "required": true},
    {"path": "docs/architecture/baseline-status.md", "status": "created", "required": true}
  ],
  "checks": [
    {"name": "toolchain-check", "kind": "automated", "status": "passed", "command": "python3 scripts/check-package.py", "exit_code": 0, "log": "workflow/evidence/logs/toolchain-check.log"}
  ],
  "approval": {"required": true, "status": "pending"}
}
```

When moving from project level to feature level, the evidence for stage 05 must contain a real `change_id`; the state machine uses it to bind subsequent feature handoff packages.

## 2. SHA-256 Handoff Packages

On a successful `transition`, a handoff manifest that cannot silently drift is generated for each direct downstream stage:

```text
workflow/handoffs/
├── project/04-proposal-planning--05-feature-requirements.json
└── <change-id>/07-detailed-design--08-implementation-orchestrator.json
```

Each manifest records the source/target stage, Change ID, baseline version, approval/gate summary, and the SHA-256 and size of each output file. SHA-256 computation first normalizes CRLF to LF, so Windows/Linux checkout differences are not misreported as drift; content changes are still blocked. Downstream `check-entry` automatically verifies all preceding handoff packages. A file being modified, deleted, or resolved outside its path blocks entry.

Manual check:

```bash
python3 scripts/workflow.py handoff-verify --manifest workflow/handoffs/<change-id>/07-detailed-design--08-implementation-orchestrator.json
```

`handoff-create` is only for manually confirmed recovery/rebuild; it must not be used to bypass a failed gate or approval. If the state has already been committed but the process was interrupted before generating the manifest, regenerate with the original stage's approved evidence: `python3 scripts/workflow.py handoff-create --from-step <from> --to-step <to> --change-id <id> --evidence <original-stage-evidence.json>`. For project-level stages, omit `--change-id`. `--evidence` is mandatory; the free-form `--file` path is no longer accepted, and the 09 independent-verification recovery must preserve the verifier evidence and PASS proof.

### Declarative Mutable Artifacts

- If an artifact is also declared as an output by a later stage (for example, `baseline-impact.md` by 05/07 or `figma-layout.csv` by 06/07), the handoff manifest records `mutable_by_design: true`. `design.md` is owned by 07 only (05 records initial decisions in `proposal.md`). `baseline-status.md` is owned by 01 and updated by 03, but is volatile, so its hash is never pinned. `traceability.csv` is initialized and merged by 07, is read-only in 08–10, and is no longer declared as a later output.
- `handoff_policy.volatile_artifacts` in the contract additionally marks machine-managed or generated files (`workflow-state.json`, `AGENTS.md`, baseline status/manifest/registry, `BASELINE-INDEX.md`, `toolchain-report.md`). Handoffs record their existence but never their hash, so routine state, index and baseline refreshes do not invalidate an upstream approval.
- Downstream verification only requires such artifacts to still exist and does not compare against the original hash; artifacts not declared by a later stage are still strictly compared by SHA-256.
- This marker is generated automatically by `transition` and `handoff-create` according to `STEP-ARTIFACT-CONTRACTS.json` and may not be declared manually.

## 3. Independent Verifier

After the stage 08 Builder completes, stage `09-independent-verification` must be executed before entering stage 10 manual acceptance. The Verifier uses a different Agent/independent session identity from the Builder, inspects code and design in a read-only manner, and is allowed only to write reports; the structured evidence must record `verifier_identity` and `builder_identity`, and the two must differ; the Verifier must not fix implementation or tests.

Outputs:
- `openspec/changes/<change-id>/design/evidence/independent-verification-report.md`
- `openspec/changes/<change-id>/design/evidence/independent-verification.json`

Check:

```bash
python3 scripts/check-independent-verification.py \
  --report openspec/changes/<change-id>/design/evidence/independent-verification-report.md \
  --evidence openspec/changes/<change-id>/design/evidence/independent-verification.json
```

It passes only when Verdict=PASS, every AC has evidence, all tests were actually executed with exit code 0, the revision is stable, read-only constraints are satisfied, and there are no BLOCKER/CRITICAL findings. NOT_RUN / SKIPPED / PENDING do not equal PASS.

## 4. Boundaries and Limitations

- This version centers on a single active Change in a single `workflow-state.json`; `next-change` supports entering the next Change in sequence, but a concurrent state scheduler for multiple Changes has not yet been implemented.
- The scripts can verify files, hashes, command exit codes, and structured evidence, but cannot prove that human review opinions themselves are genuine; approver identity is guaranteed by the team's existing permission system.
- Verifier independence requires the Agent runtime to provide independent sessions/different Agents; if the same Agent plays both Builder and Verifier, it must explicitly be marked as non-independent and must not claim that independent verification passed.
- `workflow.py transition` is the controlled entry point for a local repository, not a security sandbox; an Agent with repository write permission may still bypass the scripts and edit files directly. Teams should further restrict this through Agent tool permissions/CI branch protection.

## 5. Project Baseline Governance Engine

The state machine also invokes `scripts/baseline-governance.py` to ensure that, beyond "the stage can be entered", in-stage artifacts also inherit the currently effective project baseline. The machine-authoritative files are `docs/architecture/baseline-manifest.json` and `constraint-registry.json`; each Change binds every ACTIVE Constraint ID in `design/baseline-binding.json`.

For first freeze ordering, BCR amendments, version upgrades, Change constraint applicability/exceptions, independent design/implementation/acceptance evidence, and in-flight Change rebase, see Section 9 of `docs/BASELINE-FEATURE-INTERACTION.md`. Core commands:

```bash
python3 scripts/baseline-governance.py audit
python3 scripts/baseline-governance.py audit --require-frozen
python3 scripts/baseline-governance.py init-binding --change-id <change-id>
python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement
python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase design
python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase implementation
python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase acceptance
```

The toolkit's default Manifest and example constraints are all DRAFT; a passing `audit` only means the structure is valid, not that the project baseline has been frozen. Real projects must complete owner approval before freezing; example rules or example approval information must not be treated directly as the project's official specification.
