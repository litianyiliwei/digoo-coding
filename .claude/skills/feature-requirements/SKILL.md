---
name: feature-requirements
description: Author Change-scoped proposal, delta specs, user stories/ACs, initial tasks, baseline impact/binding, and capability/module updates.
---

# Stage 05: Proposal-Level Requirements Analysis

## Role
Define externally observable behavior, user stories, acceptance criteria, and baseline impact for a single Change. Do **not** create `design.md` here (Stage 07 is its single writer).

## Required Methods & Guidance
- Load `.claude/skills/baseline-impact-classification/SKILL.md` (`baseline-impact-classification`) and use `brainstorming`.
- Consult `process/QUESTION-COVERAGE-CHECKLIST.md` (`05-*`) for Change-level edge cases.

## Execution Flow
1. **Entry**:
   - Ensure the Change lane was started via `python scripts/workflow.py start-change --change-id <change-id>` (verifies frozen baseline, roadmap/amendment presence, and transitive dependencies ACCEPTED at Stage 10).
   - Run `python scripts/workflow.py check-entry --step 05-feature-requirements --change-id <change-id>` and `python scripts/agent-context.py --stage 05 --change <change-id>`.
   - Scaffold Change assets via `bash scripts/new-change-assets.sh <change-id>` if not already present.
2. **Proposal & Target Platforms**:
   - Write `openspec/changes/<change-id>/proposal.md` with `### New Capabilities` / `### Modified Capabilities` aligned to `proposal-roadmap.md` and `## Target Platforms` matching the roadmap row verbatim.
   - If the Change is outside the roadmap main table, add an approved `## Roadmap Amendments` row in `docs/product/proposal-roadmap.md` (`Reason`, `Requester`, `Approver`, `Date`, `Baseline Impact`, `Depends On`, `Target Platforms`, `Owner Module`, `Related Modules`).
3. **Delta Specs & User Stories / ACs**:
   - Write `openspec/changes/<change-id>/specs/<capability>/spec.md` describing observable behavior (`ADDED`/`MODIFIED`/`REMOVED`/`RENAMED` Requirements + `#### Scenario:`), with no implementation details (evaluate `skip_specs: true` only for pure doc/tooling/refactoring Changes).
   - Write `openspec/changes/<change-id>/design/user-stories.md`:
     - Declare `- Target platforms:` identical to `proposal.md` and roadmap.
     - Every `### AC-xxx` includes `- Scenario: <exact spec Scenario title>` and `- Slice position: entry|behavior|result`.
     - Cover every declared platform (or write `N/A + reason`), plus `## Acceptance Walkthrough` (one AC at each slice position) and `## Slice Budget` (exception requires `- Budget exception: <approver> — <reason>`).
   - Write initial `- [ ]` checkboxes in `openspec/changes/<change-id>/tasks.md`.
4. **Baseline Impact & Registries**:
   - Follow `.claude/skills/baseline-impact-classification/SKILL.md` to fill `design/baseline-impact.md` and generate `design/baseline-binding.json` (`baseline-governance.py init-binding`).
   - Update `docs/product/capabilities.csv` and `docs/product/modules.csv` when introducing/updating capabilities or modules (owner module must list the capability).
5. **Stage-End Gates**:
   - `python scripts/check-requirements.py --change <change-id> --strict`
   - `openspec validate <change-id> --strict`
   - `python scripts/check-capabilities.py` & `python scripts/check-modules.py`
   - `python scripts/check-roadmap.py --strict` (when a roadmap amendment was added)
   - `python scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`
   - `python scripts/check-method-evidence.py --step 05-feature-requirements --evidence workflow/evidence/<change-id>/05-feature-requirements.json`

## Input/Output/Handoff Contract
- **Inputs**: Run `python scripts/agent-context.py --stage 05 --change <change-id>` for the lean read set.
- **Outputs**: `proposal.md`, `specs/<capability>/spec.md` (when applicable), `tasks.md`, `design/user-stories.md`, `design/baseline-impact.md`, `design/baseline-binding.json`, updated `docs/product/capabilities.csv`, `docs/product/modules.csv`, and optional `proposal-roadmap.md` amendment.
- **Downstream Handoff**: Approved proposal, delta specs, US/ACs with target platforms, and baseline binding for Stage 06.
- **Review & Boundaries**:
  - Generate `workflow/evidence/<change-id>/05-feature-requirements.json` and run:
    `python scripts/workflow.py request-review --step 05-feature-requirements --change-id <change-id> --evidence workflow/evidence/<change-id>/05-feature-requirements.json --summary "<summary>"`
  - Present `templates/workflow/step-handoff-report.md` and end the turn. Advance (`approve` → `transition`) only after explicit user approval. Follow `AGENTS.md`.
