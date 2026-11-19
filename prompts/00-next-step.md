# Prompt: Continue the Development Workflow / Next Step

```text
Execute `@workflow-orchestrator`. My instruction is "next step" (下一步).

First read `workflow-state.json`, `process/PROCESS-MAP.md`, `process/OUTPUT-TEMPLATE-MATRIX.csv`, and verify the current-stage artifacts and approval status; do not trust the state file alone.

Skill invocation requirements: If the current Agent has Superpowers installed/discoverable, first load `using-superpowers` according to that Agent's real mechanism, then load the specific skills applicable to this stage. For requirement business analysis, prefer `brainstorming`; for planning, use `writing-plans`; for implementation, use `test-driven-development`; for troubleshooting, use `systematic-debugging`; for review, use `requesting-code-review`/`receiving-code-review`; before completion, use `verification-before-completion`. Check whether the skills exist first; when missing, report explicitly and execute an equivalent process; do not falsely claim they were invoked.

OpenSpec requirements: If the repository has OpenSpec initialized, run `openspec list --changes` and `openspec list --specs`; if there is an active Change, run `openspec status --change <change-id>`. Before creating/updating artifacts, read `openspec instructions <artifact> --change <change-id> --json`. Only create or modify a Change during the proposal planning / proposal-level requirements analysis stages; do not create a Change early during the requirement business analysis stage. Run `openspec validate <change-id> --strict` when needed; do not automatically archive without human approval.

Context budget: After choosing the stage, first run `python scripts/agent-context.py --stage <id> --change <change-id>`, and read according to the "condensed inputs"; the full `inputs` are only for handoff audit and are not read by default. Output follows the reference-style rules of `process/INPUT-OUTPUT-POLICY.md`; do not copy the input full text.

Stage 02 additional requirements: First confirm with the user whether there are reference products (name/link/screenshot/account); whether or not there are, you must use WebSearch/WebFetch (or a host-equivalent internet tool) to complete internet research, produce `docs/product/reference-research.md`, and run `python scripts/check-reference-research.py --strict`; when there is no internet capability, mark BLOCKED; do not substitute memory.

Choose the single next stage; for feature-level stages you must also read `process/BASELINE-FEATURE-INTERACTION.md` and `docs/architecture/baseline-status.md`, and check the current Change's `design/baseline-impact.md`. Stage 05 must establish that checklist, stages 06–07 review it, stage 08 does not directly modify the frozen baseline, and stage 10 writes back only approved shared decisions. Read `prompts/<next-prompt>` and `.claude/skills/<skill-id>/SKILL.md`, verify prerequisite artifacts, execute according to the templates, and run the stage check scripts. If there are pending approvals, missing inputs, or failed checks, pause and raise specific questions. Before executing the chosen stage, run `python scripts/workflow.py check-entry --step <step-id> [--change-id <id>]`; a non-zero exit code means stop. When the stage work is done, generate `workflow/evidence/<step-id>.json` evidence and run all stage checks, then run `python scripts/workflow.py request-review --step <step-id> --evidence workflow/evidence/<step-id>.json --summary "<review summary>"`, present the handoff report, and end the turn immediately. Do not run `transition` until the user explicitly replies "review passed <step-id>" and you have run `workflow.py approve` with the user's real approver, date, and approval evidence. Directly editing `completed_steps`/`current_step` is forbidden; state can only be written by workflow commands.

Do not cross multiple stages at once, and do not auto-commit, publish, overwrite existing files, or bypass gates. In the final report, state the current stage, the skills/commands actually invoked, artifact paths, check results, and the next step.
```

## Usage Prerequisites
- Use it in an Agent that can read the current project repository and invoke the terminal/Skill.
- If this is ordinary chat without repository access, first upload the state file and related artifacts, or manually copy the corresponding stage Prompt; you cannot pretend to read local files or run the CLI.
- `workflow-state.json` is only a state index; real files, OpenSpec state, and approval records take precedence.

## Mandatory Deliverable Handoff

Before execution, read the `skill="workflow-orchestrator"` record in `process/STEP-ARTIFACT-CONTRACTS.md` and `process/STEP-ARTIFACT-CONTRACTS.json`.

- Input verification: workflow-state.json; process/PROCESS-MAP.md; process/STEP-ARTIFACT-CONTRACTS.json; process/OUTPUT-TEMPLATE-MATRIX.csv; real artifacts and approval records; current OpenSpec CLI state (if initialized). Report item by item whether each file exists, its version, and approval status; pause if not satisfied.
- Required output: next-stage determination report (shown in conversation; not required to be written to disk); `workflow-state.json` is written only by workflow commands (`request-review`/`approve`/`transition`), never by hand. Do not manually write stage artifacts.
- Inputs for the next step: all files in the selected stage's Input Contract. Clearly state in the report how these files are consumed downstream.
- When the stage completes, present the handoff report according to `templates/workflow/step-handoff-report.md`; distinguish generated, draft, proposed, pending confirmation, and not executed.
- Only after the gates pass, the user has replied "review passed <step-id>", and `approve` has been run may you run `workflow.py transition`; do not automatically cross approval points, and do not directly edit the state file.
- **Stop when pending review (mandatory):** When `pending_approvals` is non-empty, you may only report BLOCKED, the pending-review stage, and the submitted artifacts; proposing or executing any next stage is forbidden; you must wait for the user to explicitly reply "review passed <step-id>", then run `approve` before `transition`.


## P0 Runtime Guard (mandatory)

- The stage DAG is read from `process/WORKFLOW-STAGES.json`; do not infer/rewrite dependencies yourself.
- Before execution, run `python3 scripts/workflow.py check-entry --step <step-id> [--change-id <id>]`; a non-zero exit code means execution is forbidden.
- After the stage completes, generate evidence conforming to `workflow/evidence/<step-id>.json`, run all stage checks, call `python scripts/workflow.py request-review --step <step-id> --evidence <path>`, and end the turn. Only after the user replies "review passed <step-id>" run `approve` and then `transition`. Directly editing `completed_steps/current_step` is forbidden.
- transition generates a SHA-256 handoff for the artifacts that the user actually reviewed; the next stage must verify all upstream manifests. When a file hash changes, return to the upstream for re-review; do not silently refresh. Volatile machine-managed artifacts (see `handoff_policy` in the contract) are existence-checked only.
- After stage 08, the independent `independent-verifier` must be run; only PASS allows entry to stage 10. See `process/P0-RUNTIME-GOVERNANCE.md` for details.
