---
name: workflow-orchestrator
description: Determine the single safe next workflow stage from workflow-state.json, disk artifacts, approvals, and OpenSpec state.
---

# Stage 00: Workflow Orchestrator

## Role
Inspect live repository state and select **exactly one** safe next stage (or report the exact blocker). Never advance stages or write downstream artifacts here.

## Execution Flow
1. Run `python scripts/next-step.py` and `python scripts/workflow.py list-changes` first. Do **not** read the full `STEP-ARTIFACT-CONTRACTS.md/.json` files by default.
2. Verify that `workflow-state.json` matches actual files on disk, recorded approvals, and OpenSpec CLI state (`openspec list`, `openspec list --specs` when initialized).
3. Apply multi-lane scheduling rules (v2 state):
   - Project-lane `pending_approvals` or `blocked_items` block **all** Change lanes.
   - A Change lane's own `pending_approvals` or `blocked_items` block only that lane; other runnable Change lanes may still be selected.
   - Never start a Change without `python scripts/workflow.py start-change --change-id <id>` (enforces frozen baseline, roadmap/amendment presence, and transitive `Dependencies` ACCEPTED at Stage 10).
   - Respect `implementation_lease` (07→08 acquires; 10/abandon/reopen releases; concurrent 08 allowed only when `strategy != none` and owned/integration paths are disjoint).
4. Present the next-stage determination report in chat:
   - Selected stage ID, scope (`project` or `change-id`), Skill/Prompt path, and exact entry commands:
     - `python scripts/workflow.py check-entry --step <step-id> [--change-id <id>]`
     - `python scripts/agent-context.py --stage <NN> [--change <id>]`
   - Any active blockers, pending approvals, or unmet dependencies.

## Input/Output/Handoff Contract
- **Inputs**: `workflow-state.json`, `scripts/next-step.py` output, actual disk artifacts/approvals, and OpenSpec CLI state.
- **Outputs**: Next-stage determination report (chat output); `workflow-state.json` is mutated **only** via `scripts/workflow.py` commands when real state changes.
- **Downstream Handoff**: Selected stage's lean input bundle (`scripts/agent-context.py --stage <NN> [--change <id>]`).
- **Stage Boundaries**: Follow `AGENTS.md` (stage completion ≠ approval; never edit `workflow-state.json` directly; never read/execute the next stage before explicit user approval).
