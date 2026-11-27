# Stage Handoff Report

- Stage ID:
- Skill:
- Change ID (fill N/A for project-level):
- Execution time:
- Status: DRAFT / BLOCKED / READY_FOR_REVIEW / APPROVED

## 1. Inputs Actually Read

| File/resource | Exists | Version/last updated | Approval status | Relevance to this stage |
|---|---|---|---|---|
| | | | | |

## 2. Outputs of This Stage

| Output file | Created/modified/not generated | Core content summary | Downstream use |
|---|---|---|---|
| | | | |

## 3. Traceability and Coverage

- Upstream requirements/stories/ACs:
- Artifact IDs of this stage:
- Downstream consumption relationships:
- UI consistency (when UI is involved): assertion coverage of `figma-code/` / `figma-layout.csv`, max deviation and difference conclusions of `figma-layout-check.json` (paths and conclusions; no screenshots)
- Uncovered/not-applicable items and reasons:

## 4. Method Evidence

> For detailed issues/alternatives/decisions, see the `methods` block in the stage evidence; at least list the key items here. 02–10 must pass `python scripts/check-method-evidence.py --step <step-id> --evidence <evidence.json>`.

| Skill/mode | Clarifying questions (key items) | Alternatives | Decision | Open questions | Artifact location | Evidence path |
|---|---|---|---|---|---|---|
| | | | | | | |

## 5. Self-Check and Tool Execution Evidence

| Command/tool | Actually executed | Exit code/result | Evidence/log location |
|---|---|---|---|
| | | | |

### Advisory Warnings (Non-Blocking)

> Aggregated from `WARN:` / `WARN (advisory):` lines in gate logs and advisory method checks (also recorded in the review packet's `warnings` field). Non-blocking; reviewer judges sufficiency. Write `None` if no warnings were emitted.

- 

## 6. Pending Confirmation, Risks, and Blockers

- Pending approval:
- Blockers:
- Assumptions/conflicts:
- Not-executed items (with reasons):


## 7. Baseline Applicability and Change Handoff

- Current baseline version/status:
- Baseline domains/files/sections read in this stage:
- Baseline classification of this Change: CHANGE_ONLY / BASELINE_CHANGE_REQUIRED / BASELINE_UPDATE_AFTER_ACCEPTANCE / N/A
- Current conclusion: COMPATIBLE / BLOCKED_PENDING_BASELINE_CHANGE / APPROVED_BASELINE_AMENDMENT
- Review conclusion: NO_IMPACT / REBASE_REQUIRED / N/A
- BCR / ADR paths and approval status:
- Baseline files and versions to update (write N/A if none):
- Affected in-flight Changes:

## 8. Next-Stage Handoff

- Next stage:
- Required reading for the next stage:
- UI evidence (when UI is involved): numeric UI fidelity / `layout_checks` / `UI acceptance` of `design/figma-audit.md`, `design/figma-code/`, `design/figma-layout.csv`, `design/evidence/figma-layout-check.json`, `code-review.md` (no screenshots)
- Input completeness: PASS / FAIL
- Allowed to proceed: YES / NO
- Questions requiring user confirmation:

> Only when real artifacts exist, gates pass, and the required approvals are complete may this stage be recorded in `workflow-state.json.completed_steps`.
