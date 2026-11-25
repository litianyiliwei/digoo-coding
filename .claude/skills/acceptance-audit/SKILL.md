---
name: acceptance-audit
description: Manual acceptance, archiving, and baseline write-back. Accept against ACs and evidence; archive and write back common decisions only after blocking items are closed.
---

# Manual Acceptance, Archiving, and Baseline Write-Back

## When to Use
Load this Skill when the workflow enters "manual acceptance, archiving, and baseline write-back". Handle only one explicit stage at a time; do not execute later stages in advance, and do not modify approved content.

## Input

Reading order: first read `docs/product/BASELINE-BRIEF.md` and the current Change artifacts; read targetedly by matched IDs; read full baselines/architecture/ADR/full specs on demand only when necessary and record the reason (see `process/INPUT-OUTPUT-POLICY.md`).
Stage 09's independent verification PASS report and JSON evidence (mandatory); implementation branch, ACs, `design/user-stories.md`, `docs/product/acceptance-policy.md`, test/build reports, UI design contract and HTML design docs (optional Figma file), OpenAPI, `design/baseline-impact.md`, current `baseline-status.md`, and approved baseline amendment evidence.

## Execution Flow
1. First verify that `design/evidence/independent-verification-report.md` and `.json` exist with Verdict=PASS, and confirm that the verification revision matches the current revision pending acceptance; reject acceptance when missing/FAIL/BLOCKED.
2. Record the pass/fail/not-applicable result and evidence link for each AC. Accept in the order of `design/user-stories.md`'s `## Acceptance Walkthrough`: the entry AC, the behavior ACs, and the result AC must jointly show that the delivered behavior reaches the result from its entry (PAGE, API operationId, CLI, or event); a walkthrough that cannot be demonstrated is a blocking finding.
2a. **Static analysis reconciliation (when `docs/architecture/quality-gates.json` exists):** rerun `bash scripts/verify-before-completion.sh <change-id> --test-dir <test-dir> --static-output openspec/changes/<change-id>/design/evidence/static-analysis-acceptance.json --static-identity acceptance-auditor` (repeat `--test-dir` for each test root; the script exits 2 when no test dir is given unless `--skip-tests` is passed for an explicitly partial run) and reconcile `## Static analysis` in `acceptance.md` with `design/evidence/static-analysis.json`, `design/evidence/static-analysis-independent.json`, and the acceptance rerun file `design/evidence/static-analysis-acceptance.json` (copy the per stack/tool command, result, and literal `exit 0` rows). The distinct output and identity keep the 08 builder evidence and the 09 independent evidence unmodified. Expired or invalid waivers, a non-PASS verdict, or a drifted gates file block acceptance.
3. Verify pages/events, API contracts, data migration, permissions, logs, and observability; when UI is involved, compare PAGE by PAGE against `figma-audit.md` (target framework/transcoding notes, actual token values/PAGE specifications/states) and the HTML review entry (or the optional Figma file). **Acceptance is primarily based on machine evidence**: PAGEs without differences, not `UI-DERIVED`, and with `figma-layout-check.json` PASS may be signed off in bulk based on machine evidence (still fill each PAGE row and note "machine evidence sign-off"); only for PAGEs with differences, `UI-DERIVED`, or not covered by assertions, open the running system UI and the design review deliverable (HTML review entry or optional Figma file) for side-by-side verification. Sign off PAGE by PAGE in a `## UI acceptance` table row (Result `ACCEPTED` / `DEVIATION_APPROVED` + design source reference (HTML data-node-id or Figma node) + running system entry + differences/approval + acceptance method + reviewer), keep exactly one document-level `- Overall result: ACCEPTED` (or `ACCEPTED WITH APPROVED DEVIATIONS`) line, and ensure `design/evidence/figma-layout-check.json` is PASS; missing evidence must not be archived. **Do not save screenshots; screenshots are not acceptance evidence; the machine geometry evidence `figma-layout-check.json` must be PASS.**
4. Classify findings as defects, requirement changes, or approved deviations; requirement changes open/update a separate Change.
5. Check blocking items, residual risks, go-live/rollback, and manual acceptance personnel.
6. After the acceptance gate passes, first handle approved baseline write-back: update the corresponding baseline documents, domain versions, and status registration, and recheck in-flight Changes.
6a. **Capability and module registry write-back (module model):** write back the accepted Change to `docs/product/capabilities.csv` (`status`, `delivered_slices`, `active_changes`, and `remaining_slices` for a `partial` capability) and to `docs/product/modules.csv` (module `status`/`capabilities` when the module is delivered or its ownership changed). Then run `python scripts/check-capabilities.py --completed <change-id>` and, when the Change completes a module, `python scripts/check-modules.py --completed <module-slug>`; both must exit 0. Registry write-back is not a baseline amendment — cross-feature shared rules still follow the BCR/ADR process.
6b. **Lane close through `workflow.py transition` (v2):** after the user explicitly approves the 10 stage, run `python scripts/workflow.py transition --step 10-acceptance-audit --change-id <change-id> --evidence <acceptance evidence>`. On success the lane becomes `ACCEPTED`, is appended to `completed_changes` (the acceptance evidence downstream dependency gates read), is removed from the capability `active_changes` cell, and the implementation lease is released. Do not hand-edit `completed_changes`, `changes`, or the lease; if the transition fails, fix the blocking condition and re-run it.
7. Then archive according to the current OpenSpec CLI process, merging feature behavior deltas into the main specs; OpenSpec archive and project design baseline write-back are independent judgments. Do not use automatic confirmation parameters to bypass checks for incomplete tasks.

## Output
`design/evidence/acceptance.md` (including `## Static analysis` when `docs/architecture/quality-gates.json` exists), AC acceptance matrix following the walkthrough, updated `docs/product/lessons.md` and the `decisions.md`/`assumptions.md` entries affected by acceptance, capability progress registry write-back (`docs/product/capabilities.csv`), module registry write-back (`docs/product/modules.csv`), residual risks, archive recommendation, baseline write-back items, updated baseline version registration (when applicable), and the in-flight Change recheck list.

## Quality and Safety Boundaries
Every AC has evidence or an explicit block; do not claim completion without acceptance; review differences and verification results before archiving. UI acceptance must not use screenshots; PAGEs without differences may be signed off in bulk based on machine evidence, but difference/`UI-DERIVED` PAGEs must be verified side by side and approvals recorded. When quality gates are adopted, expired or invalid static waivers and a non-PASS static verdict block acceptance.

## Boundaries with OpenSpec / Superpowers
- OpenSpec stores a Change's proposal, behavioral delta specs, design, and tasks; this Skill does not replace OpenSpec's own validation.
- Superpowers is used for R&D methodology and execution discipline; claim that a skill was used only when it is confirmed installed and callable by the Agent.
- HTML design input must be based on real readable files; Figma MCP input (optional) must be based on actually accessible links, nodes, and MCP responses.
- Do not automatically commit, publish, archive, or overwrite user files at this stage.

## Recommended Checks
`scripts/check-acceptance.py <change-id>` (mandatory acceptance gate), `bash scripts/verify-before-completion.sh <change-id> --test-dir <test-dir> --static-output openspec/changes/<change-id>/design/evidence/static-analysis-acceptance.json --static-identity acceptance-auditor` (repeat `--test-dir` per test root; `--skip-tests` only for an explicit partial run; includes the static gates by default when `docs/architecture/quality-gates.json` exists, `--skip-static` is not full verification, and the distinct output keeps 08/09 evidence intact), `python scripts/check-static-analysis.py --change <change-id> --strict` (only when quality gates are adopted, i.e. `docs/architecture/quality-gates.json` exists), `python scripts/check-capabilities.py --completed <change-id>` and `python scripts/check-modules.py --completed <module-slug>` (registry write-back), and `python scripts/baseline-governance.py check-change --change-id <change-id> --phase acceptance`.


## Actual Tool Invocation Requirements

- **Superpowers:** Use `verification-before-completion` to verify real test evidence, and use `requesting-code-review`/`receiving-code-review` when necessary. Load and follow the local `baseline-impact-classification` method Skill to decide which approved, implemented, verified decisions are written back to the project baseline. Stage evidence must write `methods` (real evidence paths and landing sections for verification-before-completion and baseline-impact-classification) and run `python scripts/check-method-evidence.py --step 10-acceptance-audit --evidence <evidence.json>`. When `design/interface-catalog.csv` exists, verify row by row the interface_id's owner, tests, and real-device/simulator/double/manual evidence; if missing, archiving is not allowed. You must check, read, or invoke skills according to the real mechanism of the current host Agent. Report success only after actually loading/executing; when unavailable, use `mode=equivalent` and write `reason`.
- **OpenSpec:** Run `openspec status --change <id>` and `openspec validate <id> --strict`; only after manual approval and all gates passing may you run `openspec archive <id>`, without using `-y` to bypass confirmation. Commands must be actually executed and the exit code/result reported. When the CLI is unavailable, mark it "not executed/blocked", and do not fabricate validation results.
- **Project Skill:** Load this Skill according to the actual mechanism of the host Agent; merely mentioning a skill name in a Prompt does not mean the skill was invoked.
- **State Update:** `workflow-state.json` is written only by workflow commands; after artifacts and gates pass, run `request-review` and wait for user approval. Never edit state directly; pending approvals still block the next stage.

## Baseline Write-Back Rules During Acceptance (Mandatory)

- During acceptance, review item by item the candidate amendments in `design/baseline-impact.md`; write back only content that is approved, implemented, verified, and valuable for cross-feature reuse.
- Write back capability progress (`docs/product/capabilities.csv`) and module ownership (`docs/product/modules.csv`) for every accepted Change; these are product-level mutable registries and are updated without a baseline amendment.
- Feature-specific APIs, pages, physical table fields/migrations, IOs, and test cases remain in the archived Change; do not copy them into the global baseline.
- When write-back is needed, update the corresponding product/architecture/data/common contract/test baselines and the version, approver, effective date, and associated Change/ADR in `docs/architecture/baseline-status.md`; run the baseline audit.
- OpenSpec archive updates the behavioral main specs; it does not mean every Change must modify the project design baseline. The two types of updates are judged and recorded separately.
- After the baseline update, list affected in-flight Changes and require rechecking; silently changing their existing baseline snapshots is prohibited.
- For detailed rules, see `process/BASELINE-FEATURE-INTERACTION.md`.

## Input/Output/Handoff Contract (Mandatory)

Before and after executing this Skill, you must comply with `process/STEP-ARTIFACT-CONTRACTS.md` and read the contract record for `skill="acceptance-audit"` in `process/STEP-ARTIFACT-CONTRACTS.json`. Do not infer that the handoff is complete merely from this Skill's brief "Input/Output" paragraphs.

- **Inputs for this stage:** Implemented code and test evidence; approved ACs/specs/traceability matrix; openspec/changes/<change-id>/design/user-stories.md (proposal-level US/ACs), design/test-cases.csv (TEST coverage), and, when `docs/architecture/quality-gates.json` exists, design/evidence/static-analysis.json and design/evidence/static-analysis-independent.json plus the stage 09 static_checks; when UI is involved, design/figma-audit.md (design source/platform selection, target framework/transcription notes, actual token values/PAGE specifications/states, requirements coverage matrix), design/ui-html/ (default HTML design documents), design/figma-code/ (target-framework design code), design/figma-layout.csv (assertion mapping with platform/viewport), design/evidence/figma-layout-check.json (08 measured results), and the UI fidelity in code-review.md; docs/product/acceptance-policy.md, docs/product/open-questions.md (append-only: new questions may be added; existing questions are closed only by their owner/user); code review records; `design/baseline-impact.md` and current `baseline-status.md`; approved baseline amendment requests/ADRs (if any); running acceptance environment entry (URL/route). Verify existence, version, and approval status item by item; stop and report when missing or unapproved. **Do not use screenshots.**
- **Outputs for this stage:** openspec/changes/<change-id>/design/evidence/acceptance.md (including `## Static analysis` when quality gates are adopted, and `## UI acceptance` with one table row per PAGE for UI Changes: Result (`ACCEPTED` / `DEVIATION_APPROVED`), design source reference (HTML data-node-id or Figma node), running system entry, differences/approval, acceptance method, reviewer, plus the single document-level `- Overall result:` line); acceptance report and approval records; capability registry write-back (`docs/product/capabilities.csv`) and module registry write-back (`docs/product/modules.csv`) with their `--completed` checks; applicable project baseline documents/version registration/in-flight Change recheck; OpenSpec archive results and updated main specs (only after approval). Generate according to templates and write to disk; if a path contains `<change-id>`, it must be replaced with the current real Change ID.
- **Downstream handoff:** Accepted and archived capability specs, acceptance evidence, and dependencies of subsequent Changes. Explicitly state which files/fields the next stage consumes.
- **End-of-stage presentation:** Use `templates/workflow/step-handoff-report.md` to present input verification, output paths and summaries, traceability relationships, self-check commands/exit codes, unexecuted items, pending-approval/blocked items, and next-stage inputs.
- **State discipline:** `workflow-state.json` is written only by workflow commands. Drafts or artifacts pending review are never recorded as completed; run `request-review` and wait for approval.


## Independent Verification Precondition Gate (P0)

- Stage 10 must consume the stage 09 independent verification report and JSON; the Builder's own summary, unit test results, or code review report cannot replace the independent Verifier.
- The verification report must be PASS, and the revision under test must match the current acceptance code; if the code changes after verification, stage 09 must be rerun.


## Machine Baseline Gates for the Acceptance Stage (Mandatory)

- During acceptance, verify item by item the final verification status and evidence of each bound constraint in `baseline-binding.json`, and fill in `acceptance_verification` separately; do not simply copy the Builder's `implementation_verification`. Exceptions are valid only within their approved scope.
- Baseline version or fingerprint changes must have a current rebase review of affected domains; do not silently reuse an old snapshot.
- Before OpenSpec archiving/acceptance is complete, run `python scripts/baseline-governance.py check-change --change-id <id> --phase acceptance`.

## Stage Boundaries and Review Stop (Mandatory)

- Before starting, run `python scripts/workflow.py check-entry --step 10-acceptance-audit [--change-id <id>]`; when the exit code is non-zero, stop immediately and report; do not bypass.
- Artifacts written and checks passing only mean ready for review: run `python scripts/workflow.py request-review --step 10-acceptance-audit --summary "<summary>"`, present the handoff report according to `templates/workflow/step-handoff-report.md`, and then **end the turn immediately**; do not read/execute the next stage's Prompt/Skill or create next-stage artifacts in the same session.
- Only after the user explicitly approves the pending stage (any unambiguous approval wording counts; silence and check success do not) may you run `python scripts/workflow.py approve --step 10-acceptance-audit --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval-record>` and execute `transition`. Do not fill in approver/approved_at yourself, and do not treat self-check success as approval.
- When `pending_approvals` is non-empty, advancing is prohibited; `workflow-state.json` may be managed only through `check-entry`/`request-review`/`approve`/`transition` and similar commands, and direct editing is prohibited.
- Claude Code's PreToolUse hook rejects writes to stage artifacts after the current stage (except shared artifacts) and direct edits to the state file; it also rejects them while pending review. When rejected, you must stop and explain; do not change paths or disable the hook to bypass it.
