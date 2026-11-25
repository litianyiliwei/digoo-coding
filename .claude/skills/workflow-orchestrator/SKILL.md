---
name: workflow-orchestrator
description: When the user says "next step/continue/carry on" (下一步/继续/接着做), decide the single safe next stage based on workflow-state.json, real artifacts, approval status, and OpenSpec status in the repository.
---

# Workflow Orchestrator

## Trigger Conditions
Use when the user says "next step", "continue", "carry on", "continue the R&D workflow" (下一步/继续/接着做), or asks to resume the previous workflow.

Reading order: first read `docs/product/BASELINE-BRIEF.md` and the current Change artifacts; read targetedly by matched IDs; read full baselines/architecture/ADR/full specs on demand only when necessary and record the reason (see `process/INPUT-OUTPUT-POLICY.md`).

## Must Follow
1. First read `workflow-state.json` (`project` lane + `changes` lanes in v2; run `python scripts/workflow.py list-changes` for a compact view), `process/PROCESS-MAP.md`, `process/OUTPUT-TEMPLATE-MATRIX.csv`, then check the real files corresponding to each active lane's current stage. The state file is only a clue and must not replace file validation.
2. Check which Skills the current Agent can discover. If Superpowers' `using-superpowers` exists, first load it in the way supported by the host Agent; then load the relevant Superpowers Skills according to the task. Do not invent invocation syntax or claim to have executed a skill that is not installed.
3. If OpenSpec is initialized, execute `openspec list --changes` and `openspec list --specs`; for active Changes execute `openspec status --change <id>`. Before creating or editing OpenSpec artifacts, use `openspec instructions <artifact> --change <id> --json` according to the actual CLI version to obtain guidance.
4. If a lane has pending approvals, blocking items, missing required artifacts from the previous step, validation failures, or key questions awaiting user confirmation, stop that lane and explicitly raise the items that need user decisions. A project-lane pending/blocked item stops every Change lane; another Change lane's pending item does not block this lane.
5. Respect the state `approval_policy`: `standard` requires approval for every human-reviewed stage; `risk-based` fast-tracks low-risk stages 01/04/06 after the gates while high-risk stages still require explicit approval. Never infer approval from the policy.
6. Advance only one lane's one stage; do not execute multiple stages or multiple lanes at once, and do not skip approval gates. When more than one lane is runnable and the user did not name one, list each lane's next stage and ask the user to choose; do not choose on their behalf. Start a new Change only through `workflow.py start-change --change-id <id>` (its dependency gate is mandatory); do not enter 05 by editing state.
7. Execute according to the next stage's Prompt and Skill. Prompt paths are in `prompts/`, and Skill paths are in `.claude/skills/<skill-id>/SKILL.md`.
8. Tool calls must be actually executed: OpenSpec CLI uses terminal commands; Superpowers reads/invokes skills according to the current Agent's skill loading mechanism; HTML design authoring/rendering and (optional) Figma MCP may use only actually available capabilities or provided exports.
9. After completion, run the stage's check scripts, generate evidence, and run `python scripts/workflow.py request-review --step <step-id> --evidence <evidence.json> --summary "<summary>"`. Present the handoff report and end the turn. Only after the user explicitly approves the pending stage (any unambiguous approval wording counts; silence and check success do not) may you run `workflow.py approve` and then `workflow.py transition`. Direct editing of `completed_steps`/`current_step` is prohibited. Do not fabricate test results.
10. If the current stage requires customer/product/architecture/design manual approval, record it in `pending_approvals` and wait for explicit user approval before continuing.
11. Output: current status, check evidence, tools/skills executed, next step, blocking items. If it is only analysis not yet written to files, do not mark it completed.

## Division of Labor Between OpenSpec and Superpowers
- OpenSpec: manages feature Change proposal/specs/design/tasks, status, structural validation, and archiving.
- Superpowers: methods that constrain discovery/design/planning/TDD/debugging/review/pre-completion verification.
- This toolkit's business-stage Skills: define each stage's inputs, outputs, templates, and gates for this project.
The three are complementary; mentioning a name cannot replace actual loading or command execution.

## Baseline Interaction Hints (Mandatory)

- When selecting feature-level stages, in addition to checking ordinary inputs, you must read `process/BASELINE-FEATURE-INTERACTION.md` and the current `docs/architecture/baseline-status.md`. Stage 05 creates baseline-impact; stages 06–07 recheck; stage 08 does not directly modify the frozen baseline; stage 10 writes back according to approval results.

## Input/Output/Handoff Contract (Mandatory)

Before and after executing this Skill, you must comply with `process/STEP-ARTIFACT-CONTRACTS.md` and read the contract record for `skill="workflow-orchestrator"` in `process/STEP-ARTIFACT-CONTRACTS.json`. Do not infer that the handoff is complete merely from this Skill's brief "Input/Output" paragraphs.

- **Inputs for this stage:** workflow-state.json; process/PROCESS-MAP.md; process/STEP-ARTIFACT-CONTRACTS.json; process/OUTPUT-TEMPLATE-MATRIX.csv; real artifacts and approval records; current OpenSpec CLI status (if initialized). Verify existence, version, and approval status item by item; stop and report when missing or unapproved.
- **Outputs for this stage:** next-stage determination report (displayed in conversation; not required to be written to disk); workflow-state.json (updated by transition only when the real state changes).
- **Downstream handoff:** all files in the selected stage's Input Contract. Explicitly state which files/fields the next stage consumes.
- **End-of-stage presentation:** Use `templates/workflow/step-handoff-report.md` to present input verification, output paths and summaries, traceability relationships, self-check commands/exit codes, unexecuted items, pending-approval/blocked items, and next-stage inputs.
- **State discipline:** `workflow-state.json` is written only by workflow commands. Drafts or artifacts pending review are never recorded as completed; run `request-review` and wait for approval.


## P0 Runtime Guard (Mandatory)

- The stage DAG reads `process/WORKFLOW-STAGES.json`; do not infer/rewrite dependencies yourself.
- Before execution, run `python scripts/workflow.py check-entry --step <step-id> [--change-id <id>]`; a non-zero exit code means execution is prohibited. At 05/08 the same gate also rechecks the lane's roadmap dependencies; a dependency reopened after delivery blocks the lane.
- After the stage completes, run the stage checks, generate evidence conforming to `workflow/evidence/<change-id>/<step-id>.json` (project stages: `workflow/evidence/project/<step-id>.json`; v1 projects keep the flat path), run `python scripts/workflow.py request-review --step <step-id> [--change-id <id>] --evidence <path>`, present the handoff report, and end the turn. Only after the user explicitly approves the pending stage (any unambiguous approval wording counts; silence and check success do not) run `approve` and then `transition`. Direct editing of `completed_steps/current_step` is prohibited.
- transition generates a SHA-256 handoff; the next stage must verify all upstream manifests. When file hashes change, return to the upstream for re-review and do not silently refresh. In v2, handoffs, approvals and review packets are namespaced per Change lane.
- After stage 08, the independent `independent-verifier` must be run, and only PASS may enter stage 10. For details, see `process/P0-RUNTIME-GOVERNANCE.md`.

## Stage Boundaries and Review Stop (Mandatory)

- When a lane has `pending_approvals`, only report that lane as BLOCKED with the stage and artifacts under review; do not suggest or execute that lane's next stage. Other lanes may still be reported as runnable, but choose only one lane per turn and ask the user when the choice is theirs.
- When the user only says "next step", first verify real artifacts and `approvals_history`; if the previous stage has no user approval record, do not `transition`, and only report that it is pending review.
- Before any stage starts, `check-entry` must be run; after the stage completes, `request-review` must be run and the turn must end immediately; do not advance two stages consecutively in the same session.
- Only after the user explicitly approves the pending stage (any unambiguous approval wording counts; silence and check success do not) may you `approve` and then `transition`; do not fill in approver/approved_at yourself.
