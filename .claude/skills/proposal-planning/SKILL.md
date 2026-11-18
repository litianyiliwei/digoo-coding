---
name: proposal-planning
description: Proposal decomposition, dependency ordering, and roadmap. Divides OpenSpec Changes by independently acceptable business capabilities and orders them.
---

# Proposal Decomposition, Dependency Ordering, and Roadmap

## When to Use
Load this Skill when the workflow enters "proposal decomposition, dependency ordering, and roadmap". Handle only one explicit stage at a time; do not execute later stages in advance, and do not modify approved content.

## Input

Reading order: first read `docs/product/BASELINE-BRIEF.md` and the current Change artifacts; read targetedly by matched IDs; read full baselines/architecture/ADR/full specs on demand only when necessary and record the reason (see `docs/INPUT-OUTPUT-POLICY.md`).
Reviewed and frozen project overall architecture baseline, business flows/nodes/RD matrix, business rules, acceptance policy, open-questions, `BASELINE-BRIEF.md`/`change-sizing.md`/`decisions.md`/`assumptions.md`/`lessons.md`/`id-conventions.md` (standing baselines), stage 03 baseline audit report, risks, dependencies, and product priorities.

## Execution Flow
1. Split Changes by business capabilities that users can perceive and that can be independently accepted, not horizontally by frontend/backend/database.
2. For each item, state value, goals, non-goals, associated FLOW/NODE/DO/BR, expected acceptance direction, dependencies, data migration, risks, and release strategy; dependencies must explicitly check platform/native/device/third-party preconditions (cross-platform approach, native plugins and JS Bridge, devices/gateways, third-party approvals such as maps/weather/payment/real-name verification/traceability, offline sync), and must not be hidden in notes. Proposal-level UC/US/AC are refined in stage 05 and must not be fabricated at this stage.
3. Read open-questions and the stage 03 baseline audit report, bring open issues, audit gaps, and pending-approval items into the risks/dependencies/blocking conditions of candidate Changes, and do not unilaterally close them.
4. Prefer vertical slices that span UI/API/domain/persistence/test as early as possible.
5. Identify the independent rationale and prerequisite dependencies of infrastructure-type Changes.
6. When ordering, explain business value, risks, unlock relationships, and parallelism.
7. Check whether each item's size can be clearly designed, implemented, and accepted; continue splitting Changes that are too large.

## Output
Proposal roadmap, dependency Mermaid diagram, Change list, and ordering rationale.

## Quality and Safety Boundaries
Each Change has independent acceptance conditions; no cyclic dependencies; do not hide unknown dependencies in notes.

## Boundaries with OpenSpec / Superpowers
- OpenSpec stores a Change's proposal, behavioral delta specs, design, and tasks; this Skill does not replace OpenSpec's own validation.
- Superpowers is used for R&D methodology and execution discipline; claim that a skill was used only when it is confirmed installed and callable by the Agent.
- Figma MCP input must be based on actually accessible links, nodes, and MCP responses.
- Do not automatically commit, publish, archive, or overwrite user files at this stage.

## Recommended Checks
`scripts/check-roadmap.py --strict`


## Actual Tool Invocation Requirements

- **Superpowers:** The stage-scoped mode of `brainstorming`, first compare decomposition options, platform/native dependencies, and risks, write conclusions into `proposal-roadmap.md`, and create Changes only after approval. Stage evidence must write `methods` (at least 2 questions, 2 alternatives, 1 decision) and run `python scripts/check-method-evidence.py --step 04-proposal-planning --evidence <evidence.json>`. You must check, read, or invoke skills according to the real mechanism of the current host Agent; when unavailable, use `mode=equivalent` and write `reason`.
- **OpenSpec:** First run `openspec list --specs` and `openspec list --changes`; only after the proposal is approved may you run `openspec new change <id>`. Commands must be actually executed and the exit code/result reported. When the CLI is unavailable, mark it "not executed/blocked", and do not fabricate validation results.
- **Project Skill:** Load this Skill according to the actual mechanism of the host Agent; merely mentioning a skill name in a Prompt does not mean the skill was invoked.
- **State Update:** `workflow-state.json` is written only by workflow commands; after artifacts and gates pass, run `request-review` and wait for user approval. Never edit state directly; pending approvals still block the next stage.

## Interaction Between Project Baselines and Feature Decomposition (Mandatory)

- When splitting each Change, read `docs/architecture/baseline-status.md` and the frozen product/architecture/data/common contract/test baselines; check relevant sections according to the impact surface of the candidate feature.
- In `docs/product/proposal-roadmap.md`, add for each candidate Change the columns "applicable baseline domains, baseline constraints to reuse, potential baseline conflicts/amendments, approval preconditions".
- Initially classify changes as `CHANGE_ONLY`, `BASELINE_CHANGE_REQUIRED`, `BASELINE_UPDATE_AFTER_ACCEPTANCE`, or `N/A`. Do not automatically escalate to a baseline change just because a feature uses a new component/new field/new API.
- If the baseline status is not FROZEN, or there are pending amendments or conflicts, explicitly list them as risks/blocks; do not treat DRAFT/PENDING rules as approved constraints.
- For detailed rules, see `docs/BASELINE-FEATURE-INTERACTION.md`.

## Input/Output/Handoff Contract (Mandatory)

Before and after executing this Skill, you must comply with `docs/STEP-ARTIFACT-CONTRACTS.md` and read the contract record for `skill="proposal-planning"` in `docs/STEP-ARTIFACT-CONTRACTS.json`. Do not infer that the handoff is complete merely from this Skill's brief "Input/Output" paragraphs.

- **Inputs for this stage:** Frozen project baseline; project requirements analysis, workflows, data objects, RD matrix, business rules, and acceptance policy (US/ACs are produced in Stage 05, not consumed here); docs/product/BASELINE-BRIEF.md, role-permission-matrix.csv, change-sizing.md, decisions.md, assumptions.md, lessons.md, id-conventions.md (baseline standing layer and lessons write-back); known technical debt and dependencies. Verify existence, version, and approval status item by item; stop and report when missing or unapproved.
- **Outputs for this stage:** docs/product/proposal-roadmap.md; scope/dependency/value description for each candidate Change. Generate according to templates and write to disk; if a path contains `<change-id>`, it must be replaced with the current real Change ID.
- **Downstream handoff:** Approved Change list, priorities, dependency order. Explicitly state which files/fields the next stage consumes.
- **End-of-stage presentation:** Use `templates/workflow/step-handoff-report.md` to present input verification, output paths and summaries, traceability relationships, self-check commands/exit codes, unexecuted items, pending-approval/blocked items, and next-stage inputs.
- **State discipline:** `workflow-state.json` is written only by workflow commands. Drafts or artifacts pending review are never recorded as completed; run `request-review` and wait for approval.


## Machine Baseline Constraints (Mandatory)

- Before roadmap decomposition, run `python3 scripts/baseline-governance.py audit --require-frozen` and read the Manifest and Constraint Registry.
- Record for each candidate Change the Constraint IDs that may apply, potential exceptions, and baseline amendment candidates; do not treat DRAFT constraints as current rules, and do not skip ACTIVE constraints.
- Do not modify the frozen baseline; baseline amendments may only go through BCR/ADR and `open-amendment`.

## Stage Boundaries and Review Stop (Mandatory)

- Before starting, run `python scripts/workflow.py check-entry --step 04-proposal-planning [--change-id <id>]`; when the exit code is non-zero, stop immediately and report; do not bypass.
- Artifacts written and checks passing only mean ready for review: run `python scripts/workflow.py request-review --step 04-proposal-planning --summary "<summary>"`, present the handoff report according to `templates/workflow/step-handoff-report.md`, and then **end the turn immediately**; do not read/execute the next stage's Prompt/Skill or create next-stage artifacts in the same session.
- Only after the user explicitly replies "Review passed 04-proposal-planning" (the workflow requires explicit user approval) may you run `python scripts/workflow.py approve --step 04-proposal-planning --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval-record>` and execute `transition`. Do not fill in approver/approved_at yourself, and do not treat self-check success as approval.
- When `pending_approvals` is non-empty, advancing is prohibited; `workflow-state.json` may be managed only through `check-entry`/`request-review`/`approve`/`transition` and similar commands, and direct editing is prohibited.
- Claude Code's PreToolUse hook rejects writes to stage artifacts after the current stage (except shared artifacts) and direct edits to the state file; it also rejects them while pending review. When rejected, you must stop and explain; do not change paths or disable the hook to bypass it.
