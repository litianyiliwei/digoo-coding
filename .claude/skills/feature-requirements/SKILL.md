---
name: feature-requirements
description: Proposal-level requirements analysis. Generates user stories and ACs per Change and refines them into testable OpenSpec behavioral specs; does not produce separate use case files, scenarios are written into the spec's Scenario.
---

# Proposal-Level Requirements Analysis

## When to Use
Load this Skill when the workflow enters "proposal-level requirements analysis". Handle only one explicit stage at a time; do not execute later stages in advance, and do not modify approved content.

## Input

Reading order: first read `docs/product/BASELINE-BRIEF.md` and the current Change artifacts; read targetedly by matched IDs; read full baselines/architecture/ADR/full specs on demand only when necessary and record the reason (see `docs/INPUT-OUTPUT-POLICY.md`).
Change ID, approved roadmap, project requirements business analysis (FLOW/NODE/DO/RD/BR/acceptance policy), `BASELINE-BRIEF.md`/`change-sizing.md`/`role-permission-matrix.csv`/`decisions.md`/`assumptions.md`/`lessons.md`/`id-conventions.md` (standing baselines), open-questions (read-only), frozen baseline, relevant openspec/specs.

## Execution Flow
1. First run `openspec status --change <id>`, `openspec list --specs` and read the full text of relevant specs; follow the current OpenSpec CLI/Schema guidance.
2. Derive **proposal-level user stories and ACs** from the project business flows, RD matrix, and Change scope (`design/user-stories.md`, US/AC IDs); do not copy the project-level historical story list; keep only entries relevant to this Change and keep stable IDs. specs are the sole source of normative behavior, and scenarios are written in the spec's Scenario; user-stories contain only USs, ACs, and traceability IDs, and do not copy full specs.
3. Every user scenario must state trigger, role, preconditions, main flow, alternative/exception flows, and postconditions, and reference the project FLOW/NODE/DO/BR IDs; the scenario body is written into the Scenario of `specs/<capability>/spec.md`, and no separate `design/use-cases.md` is produced, nor are UC IDs used for traceability.
4. Write verifiable Given/When/Then for every US; every key story has at least one AC covering permissions, null values, boundaries, exceptions, duplicate submission, and concurrency (when applicable). For Changes involving multiple platforms/native/device, scenarios must also cover platform permissions (denial/degradation), offline/weak network, push/deep links, multi-platform differences, failure retry, idempotency/concurrency; write N/A + reason when not applicable.
5. Complete `proposal.md`'s Why, What Changes, Capabilities, and Impact; capability paths use kebab-case and reuse existing paths.
6. Write externally observable behavior into `specs/<capability>/spec.md`, using canonical ADDED/MODIFIED/REMOVED/RENAMED Requirements and Scenario.
7. Put implementation methods in `design.md`, and put tasks only in `tasks.md` with checkboxes.
8. Annotate the corresponding US/AC/BR/FLOW/NODE/DO IDs, permissions, failure paths, and boundary conditions.
9. When beyond baseline scope, first propose ADR/baseline changes; for pure documentation/refactoring Changes with no behavior change, use `skip_specs: true` per OpenSpec conventions, and do not fabricate requirements.
10. After completion, run `python scripts/check-requirements.py --change <change-id> --strict` and `openspec validate <change-id> --strict`, and address all errors/warnings.

## Output
OpenSpec proposal, delta specs, design, tasks, `design/user-stories.md`, `design/baseline-impact.md`, `design/baseline-binding.json`, baseline amendment requests (when applicable), and the pending-approval list.

## Quality and Safety Boundaries
Specs describe WHAT and do not carry implementation details such as class names/frameworks; every Requirement has at least one Scenario; tasks use `- [ ]`; proposal-level US/ACs must reference project FLOW/BR/DO and be verifiable by ACs; do not produce use case files, and scenarios are uniformly written in the spec's Scenario.

## Boundaries with OpenSpec / Superpowers
- OpenSpec stores a Change's proposal, behavioral delta specs, design, and tasks; this Skill does not replace OpenSpec's own validation.
- Superpowers is used for R&D methodology and execution discipline; claim that a skill was used only when it is confirmed installed and callable by the Agent.
- Figma MCP input must be based on actually accessible links, nodes, and MCP responses.
- Do not automatically commit, publish, archive, or overwrite user files at this stage.

## Recommended Checks
`scripts/check-requirements.py --change <change-id> --strict`; `scripts/check-change.sh <change-id>`


## Actual Tool Invocation Requirements

- **Superpowers:** The stage-scoped mode of `brainstorming` checks the completeness of options, requirement boundaries, and multi-platform scenarios; write conclusions into `design/user-stories.md`, the spec's Scenario, or `design.md`, not a separate design document; do not start coding. Stage evidence must write `methods` (at least 3 questions, 1 alternative, 1 decision) and run `python scripts/check-method-evidence.py --step 05-feature-requirements --evidence <evidence.json>`. You must check, read, or invoke skills according to the real mechanism of the current host Agent; when unavailable, use `mode=equivalent` and write `reason`.
- **OpenSpec:** Actually execute `openspec status --change <id>`, `openspec instructions <artifact> --change <id> --json`, `openspec validate <id> --strict`. Commands must be actually executed and the exit code/result reported. When the CLI is unavailable, mark it "not executed/blocked", and do not fabricate validation results.
- **Project Skill:** Load this Skill according to the actual mechanism of the host Agent; merely mentioning a skill name in a Prompt does not mean the skill was invoked.
- **State Update:** Update `workflow-state.json` only after artifacts are written to the specified paths and the gates pass; when there are pending approvals or verification failures, record the block and do not advance to the next stage.

## Project Baseline Reading and Applicability Determination (Mandatory)

- Before starting requirements refinement, first read `docs/architecture/baseline-status.md`, relevant product baselines, `system-context.md`, `domain-boundaries.md`, and the architecture/data/API/frontend/test baselines of affected domains, and read relevant `openspec/specs/**`.
- You must create `openspec/changes/<change-id>/design/baseline-impact.md` according to `templates/change-assets/design/baseline-impact.md`, recording baseline domain versions, actually read files/sections/IDs, constraints, reuse items, conflicts, and ownership classification.
- Explain baseline impact in `proposal.md` / `design.md`. If changes to architecture, data ownership, common contracts, or global quality gates are prerequisites for the feature to exist, mark `BLOCKED_PENDING_BASELINE_CHANGE`; complete baseline amendment approval first, and do not design/code first and add paperwork later.
- A single feature's behavior, API, pages, physical table migrations, and local IO stay in the Change; only cross-feature shared rules/common contracts/core domain models/system-level constraints warrant a baseline amendment.
- For detailed determination rules, see `docs/BASELINE-FEATURE-INTERACTION.md`.

## Input/Output/Handoff Contract (Mandatory)

Before and after executing this Skill, you must comply with `docs/STEP-ARTIFACT-CONTRACTS.md` and read the contract record for `skill="feature-requirements"` in `docs/STEP-ARTIFACT-CONTRACTS.json`. Do not infer that the handoff is complete merely from this Skill's brief "Input/Output" paragraphs.

- **Inputs for this stage:** Approved roadmap/current Change scope; project requirements business analysis (workflows/data-objects/rd-matrix/business-rules/glossary/acceptance-policy) and frozen baseline; docs/product/BASELINE-BRIEF.md, change-sizing.md, role-permission-matrix.csv, decisions.md, assumptions.md, lessons.md, id-conventions.md (standing baselines); docs/product/acceptance-policy.md (project-level acceptance criteria; ACs align with the acceptance policy); associated FLOW/NODE/DO/BR IDs; existing OpenSpec specs; docs/product/open-questions.md (read-only). Verify existence, version, and approval status item by item; stop and report when missing or unapproved.
- **Outputs for this stage:** openspec/changes/<change-id>/proposal.md; openspec/changes/<change-id>/specs/<capability>/spec.md (when applicable); openspec/changes/<change-id>/tasks.md (initial tasks); openspec/changes/<change-id>/design.md (when there are design decisions); openspec/changes/<change-id>/design/user-stories.md (US/AC); openspec/changes/<change-id>/design/baseline-impact.md (mandatory for every Change); openspec/changes/<change-id>/design/baseline-binding.json. Generate according to templates and write to disk; if a path contains `<change-id>`, it must be replaced with the current real Change ID.
- **Downstream handoff:** Approved proposal-level US/ACs (no separate use-case artifact; scenarios live in the spec `Scenario` section), scope boundaries, requirement traceability IDs, baseline snapshot, and constraint bindings. Explicitly state which files/fields the next stage consumes.
- **End-of-stage presentation:** Use `templates/workflow/step-handoff-report.md` to present input verification, output paths and summaries, traceability relationships, self-check commands/exit codes, unexecuted items, pending-approval/blocked items, and next-stage inputs.
- **State discipline:** Update `workflow-state.json` only after real artifacts are written to disk, gates pass, and required approvals are complete; drafts/artifacts pending review must not be recorded as completed.


## Machine Baseline Constraint Binding (Mandatory)

- Before starting requirements refinement, `python3 scripts/baseline-governance.py audit --require-frozen` must pass.
- After the Change auxiliary assets are created, `design/baseline-binding.json` must exist; if `new-change-assets.sh` is used it is generated automatically from the frozen registry, or you may run `python3 scripts/baseline-governance.py init-binding --change-id <id>`.
- Do not delete/merge/rewrite machine-generated constraint IDs; fill in APPLICABLE or NOT_APPLICABLE and a specific reason for each ACTIVE constraint.
- After the stage 05 manual approval binding, run `python3 scripts/baseline-governance.py check-change --change-id <id> --phase requirement`; the handoff may occur only when this gate and the Markdown `baseline-impact.md` both pass.

## Stage Boundaries and Review Stop (Mandatory)

- Before starting, run `python scripts/workflow.py check-entry --step 05-feature-requirements [--change-id <id>]`; when the exit code is non-zero, stop immediately and report; do not bypass.
- Artifacts written and checks passing only mean ready for review: run `python scripts/workflow.py request-review --step 05-feature-requirements --summary "<summary>"`, present the handoff report according to `templates/workflow/step-handoff-report.md`, and then **end the turn immediately**; do not read/execute the next stage's Prompt/Skill or create next-stage artifacts in the same session.
- Only after the user explicitly replies "Review passed 05-feature-requirements" (the workflow requires explicit user approval) may you run `python scripts/workflow.py approve --step 05-feature-requirements --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval-record>` and execute `transition`. Do not fill in approver/approved_at yourself, and do not treat self-check success as approval.
- When `pending_approvals` is non-empty, advancing is prohibited; `workflow-state.json` may be managed only through `check-entry`/`request-review`/`approve`/`transition` and similar commands, and direct editing is prohibited.
- Claude Code's PreToolUse hook rejects writes to stage artifacts after the current stage (except shared artifacts) and direct edits to the state file; it also rejects them while pending review. When rejected, you must stop and explain; do not change paths or disable the hook to bypass it.
