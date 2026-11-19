---
name: independent-verifier
description: Verifies, from a read-only, independent perspective, whether the implementation of an OpenSpec Change satisfies approved specs, acceptance criteria, design contracts, and test requirements, and generates traceable verification evidence.
---

# Independent Verification and Acceptance Evidence

## When to Use
Use after the implementation stage is complete and before manual acceptance and OpenSpec archiving. The Verifier does not take on implementation tasks, does not fix code, and does not modify tests on behalf of the Builder; when problems are found, only record evidence and return to the implementation stage.

## Independence and Permissions
- Execute with an independent Agent/new context; the Builder's self-summary must not be used as passing evidence.
Reading order: first read `docs/product/BASELINE-BRIEF.md` and the current Change artifacts; read targetedly by matched IDs; read full baselines/architecture/ADR/full specs on demand only when necessary and record the reason (see `process/INPUT-OUTPUT-POLICY.md`).
- Read-only for source code, configuration, migrations, OpenAPI, specs, and test files; allowed to run test/build commands, and allowed to write this stage's report files.
- Must not modify implementation code, test code, OpenSpec proposal/specs/design/tasks, project baselines, or approval records.
- Record the Builder's and Verifier's Agent/session identifiers, and ensure they are different Agents or independent sessions; record the verified Git revision/commit, or explicitly record the workspace diff fingerprint; if source code changes during verification, this round of evidence is invalid.

## Methods and Tools (Mandatory)

- Use Superpowers `verification-before-completion`: PASS must be supported by real commands, exit codes, and test results; do not use the Builder's report or "I have looked at it" as a substitute for independent execution. Stage evidence must write `methods`, with at least 1 decision and a real evidence path, and run `python scripts/check-method-evidence.py --step 09-independent-verification --evidence <evidence.json>`.
- Use `systematic-debugging` when reproduction of failures/root cause is needed; investigate read-only, and do not fix code or modify tests.
- Do not use `requesting-code-review`/`receiving-code-review` to replace independent verification; the Verifier is the reviewer, not the Builder under review.
- When `design/interface-catalog.csv` exists, verify row by row the interface_id contract, tests, and traceability; missing tests, unexecuted tests, or unapproved differences are judged FAIL/BLOCKED; native/device/third-party boundaries without real-device/simulator/double/manual evidence must not PASS.
- You must independently run `openspec status --change <id>` and `openspec validate <id> --strict`, recording the command, exit code, and result; OpenSpec validation failure means FAIL/BLOCKED.
- Stage evidence checks record `superpowers-verification-methods` (actual skill usage and evidence) and `openspec-validate-independent` (exit codes and logs of status/validate).

## Must Read
- The current Change's proposal, specs, design, and tasks.
- The approved `design/baseline-impact.md` and project baseline versions.
- OpenAPI, API-IO mapping, IO catalog, frontend/backend detailed design, and test design (as applicable).
- The Builder's test/build reports, code review report, and actual code diff; these reports are clues only and cannot replace re-verification.

## Execution
1. Verify the Change ID, approval status, baseline version, and the revision of the code under test.
2. Map every acceptance criterion (AC) to an actual code path, test, and observable evidence; missing mapping must not be judged PASS.
3. Independently execute the project's agreed unit, integration, contract, end-to-end, and static checks; record complete commands, exit codes, and results. Checks that cannot be executed are marked NOT_RUN and must not be treated as passed.
4. Verify API → IO mapping, IO contracts, transaction/idempotency/exception handling, and data migration (when applicable).
5. Verify requirement traceability coverage, OpenSpec task completion, baseline constraint compliance, and compatibility; when UI is involved, independently run `python scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900` and `python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>`, generate `layout_checks` per PAGE from the independent rerun results (asserted element count, max deviation, tolerance, missing elements, verdict, evidence), and verify against the target framework/nodes in `figma-audit.md`, the geometry in `figma-code/`, and the assertions in `figma-layout.csv`. **Manual visual spot-checks target only PAGEs with differences, `UI-DERIVED`, or not covered by assertions**, and record the spot-checked PAGE, reason, and conclusion in `## UI Consistency Verification` of the report; PAGEs without differences and with machine PASS are not preconditioned on page-by-page manual recheck. PASS is not allowed when assertions are missing, elements are missing, geometry/text/font is out of tolerance, or tokens are inconsistent. Verify offline by default, and spot-check the real Figma page by page only when the version changes or there is ambiguity. **Do not use screenshots.** Independently run `openspec status --change <id>` and `openspec validate <id> --strict`, and record the exit codes.
6. Generate `design/evidence/independent-verification-report.md` and `design/evidence/independent-verification.json`.
7. Only `PASS` allows entry into manual acceptance; `FAIL` or `BLOCKED` must return the Change to the implementation/design stage and list reproducible evidence.

## Judgment Rules
- PASS: All applicable ACs have evidence and pass; all required tests are actually executed and pass; there are no unresolved blocking findings; the revision under test is stable; for UI Changes, all machine `layout_checks` PASS, manual spot-check conclusions for difference/`UI-DERIVED` PAGEs are recorded, and there are no unapproved differences.
- FAIL: Findings show implementation does not conform to specs, tests fail, contracts are inconsistent, or ACs are unmet.
- BLOCKED: Missing inputs/environment/permissions/test dependencies, or the revision under test cannot be confirmed; do not substitute conjecture for verification.
- NOT_RUN, SKIPPED, and PENDING are not PASS.

## Output and Gates
The report must list verification scope, revision, AC-by-AC results, test commands and exit codes, API→IO/data/security checks, findings, unexecuted items, and the final verdict. Run `python3 scripts/check-independent-verification.py --report <change>/design/evidence/independent-verification-report.md --evidence <change>/design/evidence/independent-verification.json`, and independently run `openspec status --change <id>` and `openspec validate <id> --strict`; only when the checks pass and verdict=PASS may hand off to stage 10. Stage evidence checks must record `superpowers-verification-methods` and `openspec-validate-independent`.

## Input/Output/Handoff Contract (Mandatory)

Before execution, read the contract for `skill="independent-verifier"` in `process/STEP-ARTIFACT-CONTRACTS.json`. Inputs must come from an approved Change (including the proposal-level US/ACs in `design/user-stories.md`, the TEST coverage in `design/test-cases.csv`, and, when UI is involved, `design/figma-audit.md` (target framework/transcoding notes, actual token values/PAGE specifications/state decisions), `design/figma-code/` (target-framework design code), `design/figma-layout.csv` (assertion mapping), `design/evidence/figma-layout-check.json` (08's measured results), the UI fidelity numeric evidence in `design/evidence/code-review.md`, as well as `docs/product/acceptance-policy.md`, `docs/product/open-questions.md` (read-only)) and the real implementation evidence from stage 08; outputs must be written to disk as a Markdown report and JSON evidence; downstream stage 10 consumes only reports with Verdict=PASS and a check-script exit code of 0. Block when inputs, AC evidence, test run records, or UI assertion evidence are missing. **Do not use screenshots.**


## Independent Baseline Constraint Verification (Mandatory)

- The Verifier must independently read the current Manifest, Constraint Registry, and the Change `baseline-binding.json`, and verify whether each applicable constraint is consistent with actual code/configuration/database migrations/interfaces.
- Do not trust the PASS that the Builder filled in; the Verifier should rerun the corresponding automated checks or record independent manual verification basis, and list the constraint IDs and results in the report.
- Before stage 09 transition-out, run `python3 scripts/baseline-governance.py check-change --change-id <id> --phase implementation`; if the report does not cover the check conclusions for all constraints, judge BLOCKED.

## Stage Boundaries and Review Stop (Mandatory)

- Before starting, run `python scripts/workflow.py check-entry --step 09-independent-verification [--change-id <id>]`; when the exit code is non-zero, stop immediately and report; do not bypass.
- Artifacts written and checks passing only mean ready for review: run `python scripts/workflow.py request-review --step 09-independent-verification --summary "<summary>"`, present the handoff report according to `templates/workflow/step-handoff-report.md`, and then **end the turn immediately**; do not read/execute the next stage's Prompt/Skill or create next-stage artifacts in the same session.
- Only after the user explicitly replies "Review passed 09-independent-verification" (the workflow requires explicit user approval) may you run `python scripts/workflow.py approve --step 09-independent-verification --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval-record>` and execute `transition`. Do not fill in approver/approved_at yourself, and do not treat self-check success as approval.
- When `pending_approvals` is non-empty, advancing is prohibited; `workflow-state.json` may be managed only through `check-entry`/`request-review`/`approve`/`transition` and similar commands, and direct editing is prohibited.
- Claude Code's PreToolUse hook rejects writes to stage artifacts after the current stage (except shared artifacts) and direct edits to the state file; it also rejects them while pending review. When rejected, you must stop and explain; do not change paths or disable the hook to bypass it.
