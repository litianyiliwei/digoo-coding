---
name: implementation-orchestrator
description: Implementation, TDD, verification, and code review. Implements small tasks using the installed Superpowers workflow and accepts them based on real test results.
---

# Implementation, TDD, Verification, and Code Review

## When to Use
Load this Skill when the workflow enters "implementation, TDD, verification, and code review". Handle only one explicit stage at a time; do not execute later stages in advance, and do not modify approved content.

## Input

Reading order: first read `docs/product/BASELINE-BRIEF.md` and the current Change artifacts; read targetedly by matched IDs; read full baselines/architecture/ADR/full specs on demand only when necessary and record the reason (see `process/INPUT-OUTPUT-POLICY.md`).
Approved OpenSpec artifacts, detailed design, tasks, repository conventions, and available Superpowers.

## Execution Flow
1. First read `openspec instructions apply --change <id>` and the project development notes; verify the actually installed Superpowers skills.
2. Execute Superpowers' `brainstorming`, `using-git-worktrees`, `writing-plans`, `subagent-driven-development`, or `executing-plans` as needed based on complexity.
3. When UI is involved, first read the target framework/transcoding notes, actual token values, PAGE specifications, and state decisions in `figma-audit.md`, plus `figma-code/` (target-framework design code transcoded in 06 according to the overall technology selection) and `figma-layout.csv` (assertion mapping); consume offline by default, and reread Figma page by page in batches only when the version changes or pages are ambiguous. **Implementation uses `figma-code/` directly as the page skeleton**: port the `.vue` (or `.tsx`/`.jsx` for the React stack) design code into the application directory, and only add routing, API calls, state, permissions, and business logic; do not rewrite styles, layout, or copy; when changes are truly needed, record the reason, impact, and approver per `UI-DEVIATION` and update assertions in sync. First establish global CSS variables/target component library theme/font stack; page styles must reference tokens, and hard-coded colors/font sizes must not be scattered; implementation must satisfy the `dom_selector` in `figma-layout.csv` (selectors should preferentially use stable `data-test` / `data-figma-node` attributes). **Do not use screenshots as UI evidence.**
4. For behavior changes, use `test-driven-development`'s RED-GREEN-REFACTOR: write the failing test first and observe the failure, then implement minimally.
5. Implement in small tasks and update OpenSpec task checkboxes; run the relevant tests for each task.
5a. **Static analysis gates (when `docs/architecture/quality-gates.json` exists):** copy/pin the config files from the rule packs in `templates/static-analysis/` into the approved stack roots per the 03 selection; dependency/package installation (for example `npm install` or `pip install`) is allowed only with explicit user authorization recorded in `tasks.md`, never automatically. Run `python scripts/check-quality-gates.py --root . --strict --require-materialized`, then `python scripts/run-quality-gates.py <change-id> --output openspec/changes/<change-id>/design/evidence/static-analysis.json --identity <builder>`, then `python scripts/check-static-analysis.py --change <change-id> --strict`; every non-zero exit is FAIL/BLOCKED. In `## Static analysis` of `code-review.md`, copy the stack/tool/command/config/result/exit-code rows directly from `static-analysis.json` (rows end with the literal `exit 0`), and list every applied waiver with its approver and expiry. `bash scripts/verify-before-completion.sh <change-id>` runs these static gates by default; `--skip-static` is explicitly not full verification and cannot be recorded as PASS evidence.
6. Run `python scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900` for each PAGE, producing `design/evidence/figma-layout-check.json`; run `python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>`. **UI verification is primarily based on machine evidence**: in `## UI fidelity` of `code-review.md`, copy directly from the JSON per PAGE the Figma node, asserted element count/max deviation, layout evidence, conclusion, and approver; only PAGEs with differences or `UI-DERIVED` need supplementary manual explanation and approval, and PAGEs without differences are not visually rechecked page by page. Run `check-code-review.py --strict`. Any missing element, geometry out of tolerance, text/font mismatch, or token inconsistency is FAIL.
7. On failure, use `systematic-debugging`, prioritize finding the root cause, and do not make random changes without evidence.
8. Use `requesting-code-review` periodically; after receiving comments, verify and address them according to `receiving-code-review`.
9. Before finishing, use `verification-before-completion`, run real tests/builds/contract checks, and report commands, exit codes, and unexecuted items.
10. When `design/interface-catalog.csv` exists, implement the interface contracts row by row and run at least one TEST for each interface_id; for native/device/third-party boundaries, state real-device, simulator, double, or manual verification evidence; if unable to execute, write BLOCKED + reason, and do not falsely report success.
11. Stage evidence must write `methods`: `test-driven-development` and `verification-before-completion`, each with a real evidence path; run `python scripts/check-method-evidence.py --step 08-implementation-orchestrator --evidence <evidence.json>`.
10. Do not claim to have used Superpowers skills that are not installed; do not change specs/OpenAPI without authorization. If specs truly need to change, pause and update the Change.

## Output
Code changes, tests, updated tasks, code review report (including `## Static analysis` when `docs/architecture/quality-gates.json` exists), static-analysis evidence (`design/evidence/static-analysis.json` plus per-tool logs under `design/evidence/static-analysis-logs/`) when quality gates are adopted (`docs/architecture/quality-gates.json` exists), and verification evidence.

## Quality and Safety Boundaries
Do not replace tests with code generation; do not report unexecuted checks as passing; unauthorized contract/requirement changes are prohibited. Dependency installation is never automatic: it requires explicit user authorization recorded in `tasks.md`. UI Changes use the 06 target-framework design code as the reproduction baseline: 08 only adds business logic and must not rewrite styles/layout/copy; visual deviations must have `UI-DEVIATION` approval, otherwise blocked.

## Boundaries with OpenSpec / Superpowers
- OpenSpec stores a Change's proposal, behavioral delta specs, design, and tasks; this Skill does not replace OpenSpec's own validation.
- Superpowers is used for R&D methodology and execution discipline; claim that a skill was used only when it is confirmed installed and callable by the Agent.
- Figma MCP input must be based on actually accessible links, nodes, and MCP responses.
- Do not automatically commit, publish, archive, or overwrite user files at this stage.

## Recommended Checks
`scripts/test-all.sh <project-dir>; scripts/verify-before-completion.sh; python scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900; python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>; python scripts/check-code-review.py --change <change-id> --strict`; when `docs/architecture/quality-gates.json` exists: `python scripts/check-quality-gates.py --root . --strict --require-materialized; python scripts/run-quality-gates.py <change-id> --output openspec/changes/<change-id>/design/evidence/static-analysis.json --identity <builder>; python scripts/check-static-analysis.py --change <change-id> --strict`

## Actual Tool Invocation Requirements

- **Superpowers:** Check and load `using-superpowers`, `writing-plans`, and `test-driven-development` per the host mechanism; `systematic-debugging` on failures; `requesting-code-review`/`receiving-code-review` for review; `verification-before-completion` before completion. Stage evidence must write `methods` (`test-driven-development` and `verification-before-completion`, each with a real evidence path) and run `python scripts/check-method-evidence.py --step 08-implementation-orchestrator --evidence <evidence.json>`. You must check, read, or invoke skills according to the real mechanism of the current host Agent. Report success only after actually loading/executing; when unavailable, use `mode=equivalent` and write `reason`.
- **OpenSpec:** First execute `openspec instructions apply --change <id> --json` and `openspec status --change <id>`; after completion, `openspec validate <id> --strict`, without unauthorized spec changes. Commands must be actually executed and the exit code/result reported. When the CLI is unavailable, mark it "not executed/blocked", and do not fabricate validation results.
- **Project Skill:** Load this Skill according to the actual mechanism of the host Agent; merely mentioning a skill name in a Prompt does not mean the skill was invoked.
- **State Update:** `workflow-state.json` is written only by workflow commands; after artifacts and gates pass, run `request-review` and wait for user approval. Never edit state directly; pending approvals still block the next stage.

## Baseline Discipline During Implementation (Mandatory)

- Before development, re-verify `design/baseline-impact.md`, `docs/architecture/baseline-status.md`, and the approved baseline version; code, migrations, and configuration must follow approved constraints.
- If a baseline is found to be inapplicable, conflicting, or missing during implementation, first record evidence in the current Change and pause affected tasks; do not directly edit the frozen baseline or bypass rules in code.
- Create/update the baseline change request and ADR, and update the baseline version after approval by the corresponding owner; then refresh the current Change's baseline snapshot, detailed design, tasks, and verification. Independent, unaffected tasks may continue after owner confirmation.
- Feature-local behavior/endpoints/table migrations/IO/implementation details remain in the Change, and must not be automatically promoted to the global baseline just because development is complete.
- For detailed rules, see `process/BASELINE-FEATURE-INTERACTION.md`.

## Input/Output/Handoff Contract (Mandatory)

Before and after executing this Skill, you must comply with `process/STEP-ARTIFACT-CONTRACTS.md` and read the contract record for `skill="implementation-orchestrator"` in `process/STEP-ARTIFACT-CONTRACTS.json`. Do not infer that the handoff is complete merely from this Skill's brief "Input/Output" paragraphs.

- **Inputs for this stage:** Approved design/baseline-impact.md and current baseline-status.md; approved tasks.md/design.md; design.md (including frontend/backend/test design sections and `### Static Analysis`), design/test-cases.csv, OpenAPI, IO contracts, and traceability.csv; when quality gates are adopted (`docs/architecture/quality-gates.json` exists), `docs/architecture/quality-gates.json` (frozen static-analysis selection), the Change-scoped `design/static-waivers.json` when present, and the rule packs in `templates/static-analysis/`; when UI is involved, `design/figma-audit.md` (target framework/transcoding notes, actual token values, PAGE specifications, state decisions), `design/figma-code/` (target-framework design code), `design/figma-layout.csv` (assertion mapping), and the project token file; `docs/architecture/technology-decisions.md` (target framework consistency); project-level engineering conventions/test strategy; docs/product/open-questions.md (read-only). Verify existence, version, and approval status item by item; stop and report when missing or unapproved.
- **Outputs for this stage:** Actual source code/migrations/configuration (including config files copied/pinned from `templates/static-analysis/` per the approved selection when quality gates are adopted); baseline change requests/ADR drafts when applicable (do not update the frozen baseline without approval); automated test code and run results; openspec/changes/<change-id>/design/evidence/code-review.md (including the `## Static analysis` machine-copied table when `docs/architecture/quality-gates.json` exists, and the `## UI fidelity` numeric table when UI is involved, with values taken directly from `figma-layout-check.json`; only PAGEs with differences/`UI-DERIVED` need manual explanation and approval); `design/evidence/static-analysis.json` and `design/evidence/static-analysis-logs/` when quality gates are adopted; `design/evidence/figma-layout-check.json`; implementation/verification evidence. Generate according to templates and write to disk; if a path contains `<change-id>`, it must be replaced with the current real Change ID.
- **Downstream handoff:** Code diff, test report, review conclusion (including `## Static analysis` results when quality gates are adopted), static-analysis evidence when quality gates are adopted, unresolved issues, `figma-layout-check.json`, and token check results. Explicitly state which files/fields the next stage consumes.
- **End-of-stage presentation:** Use `templates/workflow/step-handoff-report.md` to present input verification, output paths and summaries, traceability relationships, self-check commands/exit codes, unexecuted items, pending-approval/blocked items, and next-stage inputs.
- **State discipline:** `workflow-state.json` is written only by workflow commands. Drafts or artifacts pending review are never recorded as completed; run `request-review` and wait for approval.


## Independent Verification Handoff (New Mandatory Requirement)

Only after the user explicitly approves the pending stage (any unambiguous approval wording counts; silence and check success do not) and `approve`/`transition` have completed may you hand off to the independent Skill `@independent-verifier` (stage `09-independent-verification`), using an independent Agent/context to read-only verify code, specs, ACs, and IO contracts and rerun tests. The Builder must not generate a PASS conclusion itself to replace the Verifier.


## Machine Baseline Gates for the Implementation Stage (Mandatory)

- Before coding, `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design` must pass.
- After implementation is complete, record `implementation_verification.status=PASS`, the verification method, and the real in-repository evidence path for each APPLICABLE constraint; purely design constraints need an explicit NOT_APPLICABLE and reason.
- Before stage 08 transition-out, run `python3 scripts/baseline-governance.py check-change --change-id <id> --phase implementation`. Missing evidence, NOT_RUN, and PENDING all block.

## Stage Boundaries and Review Stop (Mandatory)

- Before starting, run `python scripts/workflow.py check-entry --step 08-implementation-orchestrator [--change-id <id>]`; when the exit code is non-zero, stop immediately and report; do not bypass.
- Artifacts written and checks passing only mean ready for review: run `python scripts/workflow.py request-review --step 08-implementation-orchestrator --summary "<summary>"`, present the handoff report according to `templates/workflow/step-handoff-report.md`, and then **end the turn immediately**; do not read/execute the next stage's Prompt/Skill or create next-stage artifacts in the same session.
- Only after the user explicitly approves the pending stage (any unambiguous approval wording counts; silence and check success do not) may you run `python scripts/workflow.py approve --step 08-implementation-orchestrator --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval-record>` and execute `transition`. Do not fill in approver/approved_at yourself, and do not treat self-check success as approval.
- When `pending_approvals` is non-empty, advancing is prohibited; `workflow-state.json` may be managed only through `check-entry`/`request-review`/`approve`/`transition` and similar commands, and direct editing is prohibited.
- Claude Code's PreToolUse hook rejects writes to stage artifacts after the current stage (except shared artifacts) and direct edits to the state file; it also rejects them while pending review. When rejected, you must stop and explain; do not change paths or disable the hook to bypass it.
