# Prompt: Project Bootstrap and Toolchain Check

```text
Execute `@project-bootstrap`.

Repository path: <repo-path>
Project summary: <project-summary>
Current Agent/IDE: <agent-and-ide>

First check the existing README, directories, build/CI files, Git status, OpenSpec CLI, and the actual installation status of Superpowers. Probe the static-analysis tools per selected/present language (linters/formatters/type/style checkers such as ESLint/Prettier/tsc, Ruff/mypy, Checkstyle/SpotBugs, gofmt/golangci-lint, shellcheck, sqlfluff) without installing anything, and record tool, installed (YES/NO), version, probe command, and result in the `Static Analysis Toolchain` table of `docs/project/toolchain-report.md`, plus the `Static analysis config present` note for `docs/architecture/quality-gates.json`; missing tools are gaps with owner and blocking condition. Propose a minimal bootstrap plan; do not overwrite existing configuration, and do not install/delete/commit anything. Output the tool status, discovered conventions, gaps, proposed files to create/modify, and checks not executed. When initializing `docs/architecture/baseline-status.md`, you must use `templates/project-baseline/baseline-status.md` and register the version, status, and approval for each domain: product/architecture/data domain/API/frontend/test quality; write DRAFT/PENDING for unknown values, and do not fake FROZEN.
For formal artifacts, follow the templates specified by `process/TEMPLATE-POLICY.md` and `process/OUTPUT-TEMPLATE-MATRIX.csv`; do not delete template fields, and write PENDING for unknown items with the reason.
```

## Variables to Fill Before Running

- Input materials: replace the `<...>` placeholders with real paths, links, or content.
- Change ID: used only in feature-level stages; project-level stages may write `N/A`.
- Loading the Skill: in an OpenCode environment that supports Agent Skills, use `@project-bootstrap`, or explicitly load the Skill of the same name first.

## Execution Tool Protocol (mandatory)

- **Load this project's Skill:** Load `.claude/skills/<skill-id>/SKILL.md` according to the current Agent's real mechanism (e.g. use `@<skill-id>` when OpenCode supports it); do not treat the Skill name as ordinary text. If the repository Skill cannot be loaded, report explicitly and execute according to the Prompt.
- **Superpowers:** First check whether Superpowers is installed and which skill directories are available; if `using-superpowers` exists, read it according to the host mechanism. Do not automatically install or update tools during bootstrap. Check whether the skill is really installed/discoverable first, and read its guidance using the invocation method supported by the host Agent; when unavailable, explain and execute equivalent steps; claiming to have invoked an uninstalled skill is forbidden.
- **OpenSpec:** If `openspec/` exists, run `openspec list --changes`, `openspec list --specs`, and `openspec version` (if the current CLI supports it); when not initialized, only report and do not run init on your own. Commands must actually run and their exit codes/results must be reported; when the CLI does not exist or fails, mark it as blocked/not executed and do not pretend verification passed.
- **State and gates:** `workflow-state.json` is read-only for this stage; advance it only through workflow commands. Before starting, run `python scripts/workflow.py check-entry --step 01-project-bootstrap` (non-zero = stop). Run `python scripts/check-package.py` and `bash scripts/test-scripts.sh` before review. `approve` and `transition` only after the user explicitly approves the pending stage (any unambiguous approval wording counts; silence and check success do not). Pause on pending approvals, missing inputs, or failed verification.
- **Output report:** List the files actually read, the Skills/CLI/scripts actually invoked, generated/modified files, check results, items not executed, and the next step. Do not auto-commit, publish, archive, or overwrite existing files unless the Prompt explicitly authorizes it and the gates have passed.

## Mandatory Deliverable Handoff

Before execution, read the `skill="project-bootstrap"` record in `process/STEP-ARTIFACT-CONTRACTS.md` and `process/STEP-ARTIFACT-CONTRACTS.json`.

- Input verification: the project goals and repository location provided by the user; the repository's existing directories/configuration/AGENTS.md (if present). Report item by item whether each file exists, its version, and approval status; pause if not satisfied.
- Required output: AGENTS.md project-owned sections only (status header and Project Goal; the toolkit-managed block is installed/updated only by `scripts/toolkit-sync.py` and must not be edited inside); workflow-state.json; docs/architecture/baseline-status.md; toolchain check report (docs/project/toolchain-report.md, including the `Static Analysis Toolchain` table and `Static analysis config present` note). Write to the repository according to the templates; do not only show them in chat.
- Inputs for the next step: repository conventions and the toolchain report; workflow-state.json. Clearly state in the report how these files are consumed downstream.
- When the stage completes, present the handoff report according to `templates/workflow/step-handoff-report.md`; distinguish generated, draft, proposed, pending confirmation, and not executed.
- **Stage boundary (mandatory):** Stage completion ≠ permission to enter the next stage. After the artifacts are written and checks pass, run `python scripts/workflow.py request-review --step 01-project-bootstrap --evidence workflow/evidence/01-project-bootstrap.json --summary "<review submission summary>"` (the workflow freezes into pending review), present the report according to the handoff template, and **end the turn immediately**; before the user explicitly approves the pending stage (any unambiguous approval wording counts; silence and check success do not), reading/executing the next stage's Prompt/Skill and creating next-stage artifacts are forbidden. After approval, run `python scripts/workflow.py approve --step 01-project-bootstrap --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval record>`, then run `transition`. Do not fill in approver/approved_at yourself, and do not treat artifact completion or self-check passing as approval. Under risk-based policy this stage is low-risk: `request-review` prints `STATUS=RISK_BASED_FAST_TRACK`, and after the gates you may run `transition` without `approve`; high-risk stages still require approval.
- State: `workflow-state.json` is written only by workflow commands; do not edit it directly or auto-cross approval points.
