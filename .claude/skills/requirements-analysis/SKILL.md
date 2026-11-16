---
name: requirements-analysis
description: Requirements business analysis. Outputs complete business flows (node-level roles and data objects), business data object catalog, RD matrix, business rules, and acceptance policy; user stories and ACs are deferred uniformly to the proposal level, and this stage does not produce use cases.
---

# Requirements Business Analysis

## When to Use
Load this Skill when the workflow enters "requirements business analysis". Handle only one explicit stage at a time; do not execute later stages in advance, and do not modify approved content.

## Input

Reading order: first read `docs/product/BASELINE-BRIEF.md` and the current Change artifacts; read targetedly by matched IDs; read full baselines/architecture/ADR/full specs on demand only when necessary and record the reason (see `docs/INPUT-OUTPUT-POLICY.md`).
Interviews, business materials, legacy system materials, project goals, users and roles, constraints, existing docs/product/*, existing OpenSpec specs (read-only).

## Execution Flow
1. When the host Agent supports it and it is installed, first read/invoke the Superpowers `using-superpowers`, then read/invoke `brainstorming`; you must use the `internet-research` method (WebSearch/WebFetch or the host's equivalent online tools) to complete reference product and market research. Follow the host environment's real Skill invocation mechanism; do not assume that `@`, slash commands, or MCP syntax necessarily apply. If skills are missing, state it explicitly and execute this Skill's clarification steps, and do not claim they were invoked; when there is no network capability, mark BLOCKED and do not substitute memory.
2. Adopt phased requirements discovery: first clarify goals/users/pain points/success criteria, then progressively expand business flows, business rules, data objects, and boundaries; at the same time ask item by item about business exceptions/boundaries (weather/season, device offline, manual takeover, audit/traceability, regulatory reporting, multiple roles, historical data migration, data ownership and retention); ask about key unknowns first, mark them PENDING until confirmed, and write them into `open-questions.md`.
3. **Business flows must be complete and must not omit anything**: cover trigger conditions, preconditions, main flow, alternative flows, exception flows, and postconditions for all business domains (core business domains and supporting domains such as regulation/traceability). Decompose every flow into executable nodes, with stable node numbering `NODE-<flow-number>-<sequence-number>` (e.g., `NODE-004-01`).
4. **Every node must be registered**: executing role, input data objects, output/written data objects, preconditions, processing actions, exceptions/branches, next nodes, associated business rules. Register both purely manual nodes and system nodes; do not replace the node table with summary steps.
5. Establish a business data object catalog: `DO-xxx` stable ID, name, definition, key attributes, business owner, source/consumer nodes. Data objects are business concepts, not database tables.
6. **Output the RD matrix**: register, row by row, the read/write relationships from R (requirement/business rule/flow node) → D (data object), including the owning FLOW/NODE, role, access type (read/write/read-write/validate), and acceptance requirements; each node must have at least one RD record, or explicitly write `N/A` + reason.
7. Unify terminology, roles, permissions, cross-flow states, and acceptance policy; put only globally reused rules into project-level business rules, and leave feature details to the proposal level.
8. **This stage does not output user stories, use cases, or ACs**: US/ACs are generated per Change in stage 05 "Proposal-Level Requirements Analysis"; use case scenarios are written into the proposal-level spec's Scenario, and no separate `use-cases` file is produced. This stage retains only flows, nodes, data objects, the RD matrix, business rules, and acceptance policy.
9. **Maintain project-level standing baselines**: generate `BASELINE-BRIEF.md` (≤1 page entry), `role-permission-matrix.csv`, `change-sizing.md`, `decisions.md`, `assumptions.md`, `lessons.md`, `id-conventions.md`; run `scripts/gen-baseline-index.py --write` to generate `BASELINE-INDEX.md`.
10. Check that flow/node/data object/RD/rule IDs are unique, references are fully closed, and nodes are fully covered; unconfirmed content goes into open-questions, and do not make unauthorized decisions.
11. Do not decide database tables, classes, frameworks, or API details in advance during the requirements stage.

## Output
`docs/product/requirements-analysis.md`, `workflows.md` (including the node table), `data-objects.csv`, `rd-matrix.csv`, `business-rules.md`, `glossary.md`, `acceptance-policy.md`, `open-questions.md`, `reference-research.md`, `BASELINE-BRIEF.md`, `role-permission-matrix.csv`, `change-sizing.md`, `decisions.md`, `assumptions.md`, `lessons.md`, `id-conventions.md`, `BASELINE-INDEX.md` (generated by the script).

## Quality and Safety Boundaries
Every requirement has a source and status; every node of every flow has roles and data objects; RD matrix references are fully closed and cover all nodes; unconfirmed items have an owner and blocking conditions.

## Boundaries with OpenSpec / Superpowers
- If OpenSpec is initialized, run `openspec list --specs` and read the relevant approved specs; this stage does not create a Change.
- This stage applies Superpowers `brainstorming`, whose role is to interactively clarify requirements and compare options; it does not replace business specs. Report "invoked" only when the skill was actually discovered and loaded.
- Figma MCP input must be based on actually accessible links, nodes, and MCP responses.
- Do not automatically commit, publish, archive, or overwrite user files at this stage.

## Recommended Checks
`scripts/check-requirements.py --strict`; `python scripts/check-reference-research.py --strict`

## Actual Tool Invocation Requirements

- **Superpowers:** The stage-scoped mode of `using-superpowers` and `brainstorming`; first clarify goals, users, pain points, scope, and success criteria, and ask item by item about business exceptions/boundaries. You must use the `internet-research` method (WebSearch/WebFetch or the host's equivalent online tools) to complete reference product and market research, and write the results into `docs/product/reference-research.md`; when there is no network capability, mark BLOCKED and do not substitute memory. Write conclusions into `requirements-analysis.md` or `open-questions.md`; do not write a separate design document; stage evidence must write `methods` (brainstorming 3/1/1, internet-research 3/2/1) and run `python scripts/check-method-evidence.py --step 02-requirements-analysis --evidence <evidence.json>`. You must check, read, or invoke skills according to the real mechanism of the current host Agent. Report success only after actually loading/executing; when unavailable, use `mode=equivalent` and write `reason` (unavailability of online research does not count as equivalent and must be BLOCKED).
- **OpenSpec:** Run only `openspec list --specs` and read relevant specs; this stage must not create a Change. Commands must be actually executed and the exit code/result reported. When the CLI is unavailable, mark it "not executed/blocked", and do not fabricate validation results.
- **Project Skill:** Load this Skill according to the actual mechanism of the host Agent; merely mentioning a skill name in a Prompt does not mean the skill was invoked.
- **State Update:** Update `workflow-state.json` only after artifacts are written to the specified paths and the gates pass; when there are pending approvals or verification failures, record the block and do not advance to the next stage.

## Input/Output/Handoff Contract (Mandatory)

Before and after executing this Skill, you must comply with `docs/STEP-ARTIFACT-CONTRACTS.md` and read the contract record for `skill="requirements-analysis"` in `docs/STEP-ARTIFACT-CONTRACTS.json`. Do not infer that the handoff is complete merely from this Skill's brief "Input/Output" paragraphs.

- **Inputs for this stage:** Interviews/business materials/legacy system materials; project goals, users, roles, constraints; existing docs/product/* (if present); existing OpenSpec specs (read-only); reference products provided by the user (name/link/screenshot/account; if none, NONE + reason); internet research tools (WebSearch/WebFetch or host-equivalent capability). Verify existence, version, and approval status item by item; stop and report when missing or unapproved.
- **Outputs for this stage:** docs/product/requirements-analysis.md; docs/product/workflows.md; docs/product/data-objects.csv; docs/product/rd-matrix.csv; docs/product/business-rules.md; docs/product/glossary.md; docs/product/acceptance-policy.md; docs/product/open-questions.md; docs/product/reference-research.md; docs/product/BASELINE-BRIEF.md; docs/product/role-permission-matrix.csv; docs/product/change-sizing.md; docs/product/decisions.md; docs/product/assumptions.md; docs/product/lessons.md; docs/product/id-conventions.md; docs/product/BASELINE-INDEX.md (generated by the script). Generate according to templates and write to disk.
- **Downstream handoff:** Business flows and node-level roles/data objects, business data object catalog, RD matrix, business rules, terminology and acceptance policy, open questions. Explicitly state which files/fields the next stage consumes.
- **End-of-stage presentation:** Use `templates/workflow/step-handoff-report.md` to present input verification, output paths and summaries, traceability relationships, self-check commands/exit codes, unexecuted items, pending-approval/blocked items, and next-stage inputs.
- **State discipline:** Update `workflow-state.json` only after real artifacts are written to disk, gates pass, and required approvals are complete; drafts/artifacts pending review must not be recorded as completed.

## Stage-End Audit (Mandatory)

- Verify the node table flow by flow: every FLOW's main flow, alternative flows, and exception flows have nodes; every node has roles, input/output data objects, preconditions, actions, branches, and next nodes.
- Verify the RD matrix node by node: every NODE has at least one RD record (or N/A + reason); every DO is used by at least one node; references must not dangle.
- Verify that business rules, terminology, and acceptance policy are consistent with flows/nodes; conflicts go into open-questions, and do not choose unilaterally.
- Run `python scripts/check-requirements.py --strict` and `python scripts/check-reference-research.py --strict`; failure prohibits advancing.

## Stage Boundaries and Review Stop (Mandatory)

- Before starting, run `python scripts/workflow.py check-entry --step 02-requirements-analysis [--change-id <id>]`; when the exit code is non-zero, stop immediately and report; do not bypass.
- Artifacts written and checks passing only mean ready for review: run `python scripts/workflow.py request-review --step 02-requirements-analysis --summary "<summary>"`, present the handoff report according to `templates/workflow/step-handoff-report.md`, and then **end the turn immediately**; do not read/execute the next stage's Prompt/Skill or create next-stage artifacts in the same session.
- Only after the user explicitly replies "Review passed 02-requirements-analysis" (the workflow requires explicit user approval) may you run `python scripts/workflow.py approve --step 02-requirements-analysis --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval-record>` and execute `transition`. Do not fill in approver/approved_at yourself, and do not treat self-check success as approval.
- When `pending_approvals` is non-empty, advancing is prohibited; `workflow-state.json` may be managed only through `check-entry`/`request-review`/`approve`/`transition` and similar commands, and direct editing is prohibited.
- Claude Code's PreToolUse hook rejects writes to stage artifacts after the current stage (except shared artifacts) and direct edits to the state file; it also rejects them while pending review. When rejected, you must stop and explain; do not change paths or disable the hook to bypass it.
