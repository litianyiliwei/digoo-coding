# Prompt: Manual Acceptance, Archiving, and Baseline Write-Back

```text
Execute `@acceptance-audit`, Change: <change-id>.

Independent verification report and JSON: <independent-verification-report-and-json>
AC/specs: <spec-paths>
Proposal-level US/AC: <user-stories-and-ac>
Acceptance policy and DoD: <acceptance-policy-and-sizing>
Lessons list: <lessons>
Test/build reports: <evidence-paths>
Figma audit and design evidence: <design-evidence>

First confirm that the stage 09 independent verification Verdict=PASS and that the verified revision matches the current code; if not satisfied, stop acceptance. Then accept AC item by item, recording results, evidence, and owners; when UI is involved, compare PAGE by PAGE against the real Figma review file and `figma-audit.md` (target framework/transcoding notes, token actual values/PAGE specifications/states). **Acceptance relies primarily on machine evidence**: PAGES with no differences, not `UI-DERIVED`, and with `figma-layout-check.json` PASS may be signed off in bulk based on machine evidence (fill in the per-PAGE rows as usual, noting "machine evidence sign-off"); only PAGES with differences, `UI-DERIVED`, or not included in assertions require opening the running system interface and Figma side by side for verification. In `## UI acceptance` of `design/evidence/acceptance.md`, sign off per PAGE (`- Overall result: <ACCEPTED / DEVIATION_APPROVED>` + Figma node + running system entry + differences/approval + acceptance method (machine evidence sign-off / side-by-side verification) + reviewer), and confirm that `design/evidence/figma-layout-check.json` is PASS; **do not save screenshots; screenshots are not acceptance evidence**; missing running entry or sign-off blocks archiving. Check interfaces, data migrations, permissions, and observability against the AC. Check item by item against the DoD in `docs/product/change-sizing.md`; after acceptance, append this round's reusable lessons to `docs/product/lessons.md` (if none, N/A + reason), and update the status of entries in `decisions.md`/`assumptions.md` affected by the acceptance result. Classify findings as defects, requirement changes, or approved deviations. List blocking items, residual risks, and rollback/release matters. After acceptance passes, first determine whether there is an approved project baseline amendment: when the baseline needs modification, submit a baseline amendment request, and after approval execute it via `baseline-governance.py open-amendment/close-amendment`; do not directly write the frozen baseline; then separately execute OpenSpec archive to merge behavioral specs. These are not the same action; feature-specific details remain in the Change. Do not use `-y` to bypass unfinished tasks or confirmations.
Formal artifacts must follow the templates specified in `docs/TEMPLATE-POLICY.md` and `docs/OUTPUT-TEMPLATE-MATRIX.csv`; do not delete template fields, write PENDING for unknown items and explain why.
Baseline interaction requirements: write back to the project baseline only decisions that are approved, implemented, verified, and valuable for cross-feature reuse. Feature-specific APIs, pages, table migrations, IOs, and tests remain in the archived Change. Update the baseline version and approval records, and list in-flight Changes that need re-checking. OpenSpec main spec archiving and project design baseline write-back are two independent judgments.
```

Context: first run `python scripts/agent-context.py --stage <id> --change <change-id>` to get the condensed input; the full `inputs` are for audit only, and by default read from the condensed/on-demand list. At stage end, run `python scripts/check-output-context.py --stage <id> --strict` to check the summary output budget.

## Variables to Fill Before Running

- Input materials: replace the `<...>` placeholders with real paths, links, or content.
- Change ID: used only in feature-level stages; project-level stages may write `N/A`.
- Load Skill: in an OpenCode environment that supports Agent Skills, use `@acceptance-audit`, or explicitly load the same-named Skill first.

## Execution Tool Protocol (Must Be Followed)

- **Loading project Skills:** load `.claude/skills/<skill-id>/SKILL.md` according to the current Agent's actual mechanism (for example, use `@<skill-id>` when OpenCode supports it); do not treat the Skill name as plain text only. If the repository Skill cannot be loaded, report clearly and execute per this Prompt.
- **Superpowers:** for the acceptance/archiving stage use `verification-before-completion`; if a code review is needed, use `requesting-code-review`/`receiving-code-review`. Stage evidence must write `methods` (at least 1 decision and a real evidence path), and run `python scripts/check-method-evidence.py --step 10-acceptance-audit --evidence <evidence.json>`. When `design/interface-catalog.csv` exists, check each interface_id's owner, tests, and real-device/simulator/double/manual evidence row by row; if missing, it must not be archived. First check whether the skills are actually installed/discoverable, and read their guidance using the invocation method supported by the host Agent; if unavailable, use `mode=equivalent` and write `reason`; claiming to have invoked an uninstalled skill is forbidden.
- **OpenSpec:** before acceptance run `openspec status --change <id>` and `openspec validate <id> --strict`; only after all gates pass and explicit approval has been obtained may you execute `openspec archive <id>`, and you must not add `-y` to bypass confirmation. Commands must actually be executed and their exit codes/results reported; if the CLI does not exist or fails, mark it as blocked/not executed; do not pretend verification passed.
- **State and gates:** `workflow-state.json` is read-only for this stage; advance it only through workflow commands. Before starting, run `python scripts/workflow.py check-entry --step 10-acceptance-audit --change-id <change-id>` (non-zero = stop). `approve` and `transition` only after the user explicitly replies "review passed 10-acceptance-audit". Pause on pending approvals, missing inputs, or failed verification.
- **Output report:** list the files actually read, Skills/CLI/scripts actually invoked, files generated/modified, check results, items not executed, and next steps. Do not automatically commit, publish, archive, or overwrite existing files unless the Prompt explicitly authorizes it and the gates have passed.

## Mandatory Deliverable Handoff

Before execution, read the `skill="acceptance-audit"` record in `docs/STEP-ARTIFACT-CONTRACTS.md` and `docs/STEP-ARTIFACT-CONTRACTS.json`.

- Input verification: implemented code and test evidence; approved AC/specs/traceability matrix; design/user-stories.md, design/test-cases.csv; docs/product/acceptance-policy.md, change-sizing.md, lessons.md, BASELINE-BRIEF.md, open-questions.md (read-only); code review records; when UI is involved, `design/figma-audit.md` (target framework/transcoding notes, token actual values/PAGE specifications/states), `design/figma-code/` (target framework design code), `design/figma-layout.csv` (assertion mapping), `design/evidence/figma-layout-check.json` (actual PASS), and the `## UI fidelity` in `design/evidence/code-review.md`; the running acceptance environment entry (URL/route). Report item by item whether each file exists, its version, and approval status; pause if not satisfied.
- Must output: openspec/changes/<change-id>/design/evidence/acceptance.md (when UI is involved, containing `## UI acceptance` per-PAGE sign-off: Figma node, running system entry, differences/approval, acceptance method (machine evidence sign-off / side-by-side verification), `- Overall result: ...`, reviewer); the acceptance report and approval records; the OpenSpec archive result and updated main specs (only after approval); project roadmap/baseline status write-back (when applicable); the updated docs/product/lessons.md (and necessary status changes in decisions.md/assumptions.md). Write into the repository per the templates; do not show them only in chat.
- Next-step input: the accepted and archived capability specs, acceptance evidence, and dependencies of subsequent Changes. In the report, clearly state how these files are consumed downstream.
- At stage completion, show the handoff report per `templates/workflow/step-handoff-report.md`; distinguish generated, draft, suggestion, pending confirmation, and not executed.
- Baseline interaction: you must verify baseline reads/change ownership per `docs/BASELINE-FEATURE-INTERACTION.md`; stage 05 creates/updates `design/baseline-impact.md`, and later stages re-check it; the frozen baseline must not be modified without approval.
- **Stage boundary (mandatory):** stage completion ≠ permission to enter the next stage. After the artifacts are written and checks pass, run `python scripts/workflow.py request-review --step 10-acceptance-audit --summary "<review summary>"` (the flow is frozen as pending review), show the report per the handoff template, and then **end the turn immediately**; before the user explicitly replies "review passed 10-acceptance-audit", you are forbidden to read/execute the next stage's Prompt/Skill and forbidden to create next-stage artifacts. After approval, run `python scripts/workflow.py approve --step 10-acceptance-audit --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval record>`, then run `transition`. Do not fill in approver/approved_at yourself, and do not treat artifact completion or self-check passing as approval.
- Update `workflow-state.json` only after the gates pass and approval is complete; do not automatically cross approval points.


## Independent Verification Precondition Gate (P0)

Stage 10 must read stage 09's `independent-verification-report.md` and `.json`. If it is not PASS, the code changed after verification, or the report is missing, it must return to stage 09 for re-verification and must not continue archiving.


## Machine Baseline Acceptance Gate (Must Be Executed)

Before acceptance/archiving, check item by item the implementation verification evidence bound to the baseline, approved exceptions, and the current rebase conclusion; fill in `acceptance_verification` separately for each ACTIVE constraint (PASS/NOT_APPLICABLE, method, real acceptance evidence); do not directly copy the implementation-stage PASS. Execute `python3 scripts/baseline-governance.py check-change --change-id <id> --phase acceptance`. Uncovered ACTIVE constraints, PENDING exceptions, missing acceptance evidence, or an incomplete rebase all block archiving.
