---
name: project-bootstrap
description: Project initialization and toolchain check. Initializes repository context and tool status; does not overwrite user files.
---

# Project Initialization and Toolchain Check

## When to Use
Load this Skill when the workflow enters "project initialization and toolchain check". Handle only one explicit stage at a time; do not execute later stages in advance, and do not modify approved content.

## Input
Repository path, project summary, current tools, and IDE/Agent environment.

## Execution Flow
1. Read the README, directory structure, build configuration, CI, Git status, and existing OpenSpec configuration.
2. Run non-destructive tool probes; read `openspec --version`, `openspec init --help`, or related help output; do not guess parameters from memory.
3. Check whether the current Agent can discover `.claude/skills/<name>/SKILL.md`, and confirm that Superpowers is installed and its actual skill names.
4. Propose a minimal supplementary plan for missing files; any overwrite, installation, deletion, commit, and CI change requires explicit user authorization.

## Output
Tool status table, summary of existing directories/rules, conflict and gap list, minimal initialization plan; when initializing `docs/architecture/baseline-status.md`, use `templates/project-baseline/baseline-status.md` as the template, and do not write only an unversioned TODO status.

## Quality and Safety Boundaries
Do not overwrite existing files; do not write "not found" as "installed"; explicitly mark every check that was not executed.

## Boundaries with OpenSpec / Superpowers
- OpenSpec stores a Change's proposal, behavioral delta specs, design, and tasks; this Skill does not replace OpenSpec's own validation.
- Superpowers is used for R&D methodology and execution discipline; claim that a skill was used only when it is confirmed installed and callable by the Agent.
- Figma MCP input must be based on actually accessible links, nodes, and MCP responses.
- Do not automatically commit, publish, archive, or overwrite user files at this stage.

## Recommended Checks
`scripts/check-package.py`


## Actual Tool Invocation Requirements

- **Superpowers:** `using-superpowers` (if present) and check the Superpowers skills available to the current Agent; do not automatically install or overwrite tools. You must check, read, or invoke skills according to the real mechanism of the current host Agent. Report success only after actually loading/executing; when unavailable, state it explicitly and perform equivalent steps.
- **OpenSpec:** If `openspec/` exists, actually run `openspec version`, `openspec list --changes`, `openspec list --specs`; when uninitialized, only report and do not run init without user approval. Commands must be actually executed and the exit code/result reported. When the CLI is unavailable, mark it "not executed/blocked", and do not fabricate validation results.
- **Project Skill:** Load this Skill according to the actual mechanism of the host Agent; merely mentioning a skill name in a Prompt does not mean the skill was invoked.
- **State Update:** `workflow-state.json` is written only by workflow commands; after artifacts and gates pass, run `request-review` and wait for user approval. Never edit state directly; pending approvals still block the next stage.

## Input/Output/Handoff Contract (Mandatory)

Before and after executing this Skill, you must comply with `process/STEP-ARTIFACT-CONTRACTS.md` and read the contract record for `skill="project-bootstrap"` in `process/STEP-ARTIFACT-CONTRACTS.json`. Do not infer that the handoff is complete merely from this Skill's brief "Input/Output" paragraphs.

- **Inputs for this stage:** Project goals and repository location provided by the user; existing repository directories/configuration/AGENTS.md (if present). Verify existence, version, and approval status item by item; stop and report when missing or unapproved.
- **Outputs for this stage:** AGENTS.md project-owned sections only (status header and Project Goal; the toolkit-managed block is installed/updated only by `scripts/toolkit-sync.py` and must not be edited inside); workflow-state.json; docs/architecture/baseline-status.md (establish domain version registration based on `templates/project-baseline/baseline-status.md`); toolchain check report (docs/project/toolchain-report.md). Generate according to templates and write to disk; if a path contains `<change-id>`, it must be replaced with the current real Change ID.
- **Downstream handoff:** Repository conventions and toolchain report; workflow-state.json. Explicitly state which files/fields the next stage consumes.
- **End-of-stage presentation:** Use `templates/workflow/step-handoff-report.md` to present input verification, output paths and summaries, traceability relationships, self-check commands/exit codes, unexecuted items, pending-approval/blocked items, and next-stage inputs.
- **State discipline:** `workflow-state.json` is written only by workflow commands. Drafts or artifacts pending review are never recorded as completed; run `request-review` and wait for approval.

## Stage Boundaries and Review Stop (Mandatory)

- Before starting, run `python scripts/workflow.py check-entry --step 01-project-bootstrap [--change-id <id>]`; when the exit code is non-zero, stop immediately and report; do not bypass.
- Artifacts written and checks passing only mean ready for review: run `python scripts/workflow.py request-review --step 01-project-bootstrap --summary "<summary>"`, present the handoff report according to `templates/workflow/step-handoff-report.md`, and then **end the turn immediately**; do not read/execute the next stage's Prompt/Skill or create next-stage artifacts in the same session.
- Only after the user explicitly replies "Review passed 01-project-bootstrap" (the workflow requires explicit user approval) may you run `python scripts/workflow.py approve --step 01-project-bootstrap --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval-record>` and execute `transition`. Do not fill in approver/approved_at yourself, and do not treat self-check success as approval.
- When `pending_approvals` is non-empty, advancing is prohibited; `workflow-state.json` may be managed only through `check-entry`/`request-review`/`approve`/`transition` and similar commands, and direct editing is prohibited.
- Claude Code's PreToolUse hook rejects writes to stage artifacts after the current stage (except shared artifacts) and direct edits to the state file; it also rejects them while pending review. When rejected, you must stop and explain; do not change paths or disable the hook to bypass it.
