# Prompt Index for Each Workflow Stage

Prompt files are in `prompts/` and correspond one-to-one to `.claude/skills/<skill-id>/SKILL.md`; replace the angle-bracket placeholders with the current project's real values before execution. The workflow entry point is `prompts/00-next-step.md`. Prompts from the old split-stage version have been moved to `_trash/2026-11-11/prompts/legacy/` and are no longer part of the vibe workflow.

| Stage | Prompt | Skill |
|---|---|---|
| 00 Next-Step Orchestration | `prompts/00-next-step.md` | `workflow-orchestrator` |
| 01 Project Bootstrap and Toolchain Check | `prompts/01-project-bootstrap.md` | `project-bootstrap` |
| 02 Requirements Business Analysis | `prompts/02-requirements-analysis.md` | `requirements-analysis` |
| 03 Project Overall Architecture Design | `prompts/03-project-architecture-baseline.md` | `project-architecture-baseline` |
| 04 Proposal Breakdown, Dependency Ordering, and Roadmap | `prompts/04-proposal-planning.md` | `proposal-planning` |
| 05 Proposal-Level Requirements Analysis | `prompts/05-feature-requirements.md` | `feature-requirements` |
| 06 Figma Design and Review (Figma-only) | `prompts/06-figma-design-review.md` | `figma-design-review` |
| 07 Detailed Design, Interfaces, and Test Design | `prompts/07-detailed-design.md` | `detailed-design` |
| 08 Implementation, TDD, Verification, and Code Review | `prompts/08-implementation-orchestrator.md` | `implementation-orchestrator` |
| 09 Independent Verification and Acceptance Evidence | `prompts/09-independent-verification.md` | `independent-verifier` |
| 10 Manual Acceptance, Archiving, and Baseline Write-Back | `prompts/10-acceptance-audit.md` | `acceptance-audit` |

Inputs, outputs, approval points, and gates are governed by `process/STEP-ARTIFACT-CONTRACTS.json`; for the stage overview see `process/STAGE-IO-OVERVIEW.md`.

## Stage Boundary and Review Stop (Global)

All stage Prompts share the same hard rule: writing artifacts only means they are ready for review. You must run `python scripts/workflow.py request-review --step <step-id> --evidence workflow/evidence/<step-id>.json`, show the report per the handoff template, and end the turn immediately; only after the user explicitly replies "review passed <step-id>" may you `approve` and then `transition`. When `pending_approvals` is non-empty, execution of any next stage is forbidden; `workflow-state.json` may only be written by `scripts/workflow.py` commands.
