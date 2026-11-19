# Prompt: Proposal Breakdown, Dependency Ordering, and Roadmap

```text
Execute `@proposal-planning`.

Approved baseline: <baseline>
Requirement business analysis/RD matrix: <requirements-and-rd>
Slicing rules and lessons: <change-sizing-and-lessons>
Open questions: <open-questions>
Stage 03 audit report: <baseline-audit-report>
Priorities/constraints: <priorities>

Divide OpenSpec Changes by independently acceptable business capability. For each item give the change-id, value, scope/non-goals, associated FLOW/NODE/DO/BR, expected acceptance direction, dependencies, risks, data migration, compatibility, and ordering rationale; mark each item's size budget according to `docs/product/change-sizing.md`; if over budget, you must split it or record the reason and acceptance owner; proposal-level UC/US/AC are refined in stage 05. First read open-questions, decisions/assumptions, lessons, and the stage 03 audit report, and carry open questions, baseline gaps, and known anti-patterns into the candidate Changes' risks/dependencies; do not close them on your own. When splitting, you must check platform/native/device/third-party prerequisite dependencies: cross-platform approach, native plugins and JS Bridge, devices/gateways, third-party approvals such as maps/weather/payment/real-name verification/traceability, data migration and offline sync; these dependencies must not be hidden in notes. Output a Mermaid dependency graph; prefer vertical slices, and do not split horizontally by frontend/backend technical layers.
For formal artifacts, follow the templates specified by `process/TEMPLATE-POLICY.md` and `process/OUTPUT-TEMPLATE-MATRIX.csv`; do not delete template fields, and write PENDING for unknown items with the reason.
Baseline interaction requirements: mark for each candidate Change the applicable product/architecture/data/shared API/frontend/test baseline versions, constraints to reuse, and potential baseline amendments. Feature-local changes stay in the Change; cross-feature shared constraint changes are listed as baseline change candidates and must not be presumed approved.
```

Context: First run `python scripts/agent-context.py --stage <id> --change <change-id>` to obtain condensed inputs; the full `inputs` are only for audit, and by default read the condensed/on-demand list. At stage end, run `python scripts/check-output-context.py --stage <id>` to check the advisory summary-output budget; over-budget is a warning, not a gate.

## Variables to Fill Before Running

- Input materials: replace the `<...>` placeholders with real paths, links, or content.
- Change ID: used only in feature-level stages; project-level stages may write `N/A`.
- Loading the Skill: in an OpenCode environment that supports Agent Skills, use `@proposal-planning`, or explicitly load the Skill of the same name first.

## Execution Tool Protocol (mandatory)

- **Load this project's Skill:** Load `.claude/skills/<skill-id>/SKILL.md` according to the current Agent's real mechanism (e.g. use `@<skill-id>` when OpenCode supports it); do not treat the Skill name as ordinary text. If the repository Skill cannot be loaded, report explicitly and execute according to the Prompt.
- **Superpowers:** Use the stage-scoped mode of `brainstorming` to clarify proposal boundaries, alternative splits, and platform/native dependencies; write conclusions into `proposal-roadmap.md`; do not write a separate design document. The stage evidence must write `methods` (brainstorming with a real evidence path and landing section) and run `python scripts/check-method-evidence.py --step 04-proposal-planning --evidence <evidence.json>`. First check whether the skills are really installed/discoverable; when unavailable, use `mode=equivalent` and write `reason`.
- **OpenSpec:** First run `openspec list --specs` and `openspec list --changes`; only after the proposal is approved may you run `openspec new change <change-id>` one by one. Commands must actually run and their exit codes/results must be reported; when the CLI does not exist or fails, mark it as blocked/not executed and do not pretend verification passed.
- **State and gates:** `workflow-state.json` is read-only for this stage; advance it only through workflow commands. Before starting, run `python scripts/workflow.py check-entry --step 04-proposal-planning` (non-zero = stop). Run `python scripts/check-roadmap.py --strict` before review. `approve` and `transition` only after the user explicitly approves the pending stage (any unambiguous approval wording counts; silence and check success do not). Pause on pending approvals, missing inputs, or failed verification.
- **Output report:** List the files actually read, the Skills/CLI/scripts actually invoked, generated/modified files, check results, items not executed, and the next step. Do not auto-commit, publish, archive, or overwrite existing files unless the Prompt explicitly authorizes it and the gates have passed.

## Mandatory Deliverable Handoff

Before execution, read the `skill="proposal-planning"` record in `process/STEP-ARTIFACT-CONTRACTS.md` and `process/STEP-ARTIFACT-CONTRACTS.json`.

- Input verification: frozen project baseline; product requirements/nodes/RD/role permission matrix; `BASELINE-BRIEF.md`, `change-sizing.md`, `decisions.md`, `assumptions.md`, `lessons.md`; known technical debt and dependencies. Report item by item whether each file exists, its version, and approval status; pause if not satisfied.
- Required output: docs/product/proposal-roadmap.md; scope/dependency/value description for each candidate Change. Write to the repository according to the templates; do not only show them in chat.
- Inputs for the next step: approved Change list, priorities, dependency order. Clearly state in the report how these files are consumed downstream.
- When the stage completes, present the handoff report according to `templates/workflow/step-handoff-report.md`; distinguish generated, draft, proposed, pending confirmation, and not executed.
- Baseline interaction: Must verify baseline reading/change ownership per `process/BASELINE-FEATURE-INTERACTION.md`; stage 05 creates/updates `design/baseline-impact.md`, and later stages review it; the frozen baseline must not be modified without approval.
- **Stage boundary (mandatory):** Stage completion ≠ permission to enter the next stage. After the artifacts are written and checks pass, run `python scripts/workflow.py request-review --step 04-proposal-planning --evidence workflow/evidence/04-proposal-planning.json --summary "<review submission summary>"` (the workflow freezes into pending review), present the report according to the handoff template, and **end the turn immediately**; before the user explicitly approves the pending stage (any unambiguous approval wording counts; silence and check success do not), reading/executing the next stage's Prompt/Skill and creating next-stage artifacts are forbidden. After approval, run `python scripts/workflow.py approve --step 04-proposal-planning --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval record>`, then run `transition`. Do not fill in approver/approved_at yourself, and do not treat artifact completion or self-check passing as approval. Under risk-based policy this stage is low-risk: `request-review` prints `STATUS=RISK_BASED_FAST_TRACK`, and after the gates you may run `transition` without `approve`; high-risk stages still require approval.
- State: `workflow-state.json` is written only by workflow commands; do not edit it directly or auto-cross approval points.


## Machine Baseline Constraints (mandatory)

Before proposal breakdown, run `python3 scripts/baseline-governance.py audit --require-frozen`. Read the Constraint Registry and mark for each candidate Change the potentially applicable Constraint IDs, affected domains, and baseline change candidates; do not modify the frozen baseline, and do not treat DRAFT rules as approved constraints.
