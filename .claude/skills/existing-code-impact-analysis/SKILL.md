---
name: existing-code-impact-analysis
description: Existing-code change impact analysis. Confirms whether a Change modifies existing functionality, reads the real code location, and records files/classes/functions/interfaces/tables/tests, compatibility, migration/rollback, risks, and verification.
---

# Existing-Code Change Impact Analysis

This is a local **method Skill**: it is invoked inside a stage and does not own a stage or create stage artifacts on its own. The stage Skill/Prompt remains the authority for output paths, review, and gates.

## When to Use

- **Stage 07 (mandatory determination)**: before detailed design, decide whether this Change modifies existing feature code or is new feature development.
- **Stage 08**: when implementation discovers existing-code impact, callers, or a baseline conflict that was not visible at design time.
- Not for purely greenfield Changes: record `N/A + reason` and stop.

## Inputs

- The user's explicit answer about whether this Change modifies existing functionality; never default it.
- Code location: repository, path, branch, commit/tag, and access method.
- The current `design.md`, `design/baseline-impact.md`, approved specs/AC, and `docs/product/BASELINE-BRIEF.md`.
- The real codebase (files, classes, functions, interfaces, tables, migrations, tests, configuration, feature flags).

## Procedure

1. **Ask, do not assume.** Ask the user whether this Change modifies existing feature code or develops a new feature. Record the answer in `design.md` `### Existing Code Change Impact`.
2. **Greenfield path.** If new feature development, write `N/A + reason` in the same section; do not pretend to have explored code. Record the method entry anyway (the determination itself is the method's output).
3. **Require code access.** For existing-code changes, require the code address (repository/path/branch/commit). Verify it is actually readable. When inaccessible or ambiguous, mark **BLOCKED**; do not infer from names or memory.
4. **Read the real code.** Explore entry points, callers/dependents, public interfaces/contracts, data model and migrations, tests, configuration, feature flags, permissions, background jobs, and scheduled tasks. Record what was read.
5. **Register impact item by item.** For each affected file/class/function/interface/table/test, record: current behavior, modification strategy, compatibility (API/data/behavior), migration or rollback path, risk, and verification method (TEST IDs).
6. **Check the blast radius.** Call sites, API consumers, permission/audit behavior, concurrency/idempotency, performance, offline/weak-network behavior, and rollback safety.
7. **Land the result.** Write the itemized table into `design.md` `### Existing Code Change Impact`; link affected interfaces to `design/interface-catalog.csv` and tests to `design/test-cases.csv`/`traceability.csv`. Do not create a separate impact document.
8. **Baseline conflict.** When the impact conflicts with a frozen baseline, stop and use `baseline-impact-classification` / BCR/ADR; never edit the frozen baseline directly.
9. **Evidence.** Record a `methods` entry for `existing-code-impact-analysis` with a real evidence path and `<artifact>#<heading>` landing section.

## Output Landing by Stage

| Stage | Artifact | Landing section |
|---|---|---|
| 07 | `openspec/changes/<change-id>/design.md` | `### Existing Code Change Impact` |
| 08 | `design/evidence/code-review.md` (newly discovered impact/conflict) or the BCR/ADR that resolves it | The section recording the discovery and resolution |

## Quality and Safety Boundaries

- Never claim code was explored when it was not; inaccessible code means **BLOCKED**.
- Never write code in stage 07; this Skill analyzes and records impact.
- Do not approve baseline exceptions or compatibility breaks on the user's behalf.
- `N/A` is valid only for genuine new-feature development, with a real reason.
- The stage evidence must name the method and its real landing section; a narrative in chat is not evidence.

## Evidence

```json
{
  "skill": "existing-code-impact-analysis",
  "mode": "stage-scoped",
  "artifact_section": "openspec/changes/<change-id>/design.md#Existing Code Change Impact",
  "evidence": "workflow/evidence/07-detailed-design.json"
}
```
