---
name: acceptance-audit
description: Conduct human acceptance walkthrough, sign off acceptance evidence, and after explicit approval write back registries/baselines and archive OpenSpec.
---

# Stage 10: Human Acceptance, Archive, and Baseline Write-Back

## Role
Facilitate human acceptance in `## Acceptance Walkthrough` order using Stage 09's `PASS` evidence, obtain explicit user approval, and then atomically complete registry/baseline write-back, OpenSpec archiving, and final lane closure.

## Required Methods
- Load `.claude/skills/baseline-impact-classification/SKILL.md` (`baseline-impact-classification`) and use `verification-before-completion`.

## Execution Flow

### Phase 1: Pre-Approval Verification & Acceptance Evidence (No Global Mutations Yet)
1. **Entry**: Run `python scripts/workflow.py check-entry --step 10-acceptance-audit --change-id <change-id>` and `python scripts/agent-context.py --stage 10 --change <change-id>`.
2. **Verify Stage 09 Integrity**: Confirm `independent-verification.json` has `verdict == "PASS"` and the current repository revision matches Stage 09's verified revision. Do **not** re-run static analysis a third time when the revision is unchanged; cite Stage 09's `static-analysis-independent.json` directly.
3. **Walkthrough & Sign-Off**:
   - Walk through the running system in `## Acceptance Walkthrough` order (`entry` → `behavior` → `result`) against `design/user-stories.md` ACs and `docs/product/change-sizing.md` DoD.
   - Write `openspec/changes/<change-id>/design/evidence/acceptance.md` (≤ 120 lines; no `PENDING`/`TODO`/`TBD` markers allowed by `check-acceptance.py`).
   - For UI Changes: reference `independent-figma-layout-check.json` (fallback `figma-layout-check.json`). Batch-sign off machine-clean pages (`machine evidence sign-off`); perform side-by-side verification only for differing or `UI-DERIVED` pages (`side-by-side verification`). Never save screenshots.
4. **Change-Scoped Baseline Acceptance**:
   - Record `acceptance_verification` in `openspec/changes/<change-id>/design/baseline-binding.json` and classify any newly discovered baseline updates via `baseline-impact-classification`.
   - Do **not** mutate `docs/product/capabilities.csv`, `modules.csv`, frozen baselines, or run `openspec archive` before explicit user approval.
5. **Pre-Approval Gates**:
   - `python scripts/check-acceptance.py <change-id>`
   - `python scripts/baseline-governance.py check-change --change-id <change-id> --phase acceptance`
   - `openspec validate <change-id> --strict`
   - `python scripts/check-output-context.py --stage 10 --change <change-id>`
   - `python scripts/check-method-evidence.py --step 10-acceptance-audit --evidence workflow/evidence/<change-id>/10-acceptance-audit.json`
6. **Request Review & Stop**:
   - Generate `workflow/evidence/<change-id>/10-acceptance-audit.json`, run `request-review`, present `templates/workflow/step-handoff-report.md`, and **end the turn**.

### Phase 2: Post-Approval Write-Back, Archive, and Closure (Only After Explicit User Approval)
7. Run `python scripts/workflow.py approve --step 10-acceptance-audit --change-id <change-id> --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <record>`.
8. **Write-Back Mutable Registries**:
   - Update `docs/product/capabilities.csv` (`status`, `delivered_slices`, `remaining_slices`, `active_changes`) and `docs/product/modules.csv` (status/capabilities); verify with `python scripts/check-capabilities.py --completed <change-id>` and (if a module completed) `python scripts/check-modules.py --completed <module-slug>`.
   - Append reusable findings to `docs/product/lessons.md`, `decisions.md`, and `assumptions.md` (create `lessons.md` if absent; record `N/A + reason` if none).
   - If a baseline amendment was approved, execute `baseline-governance.py open-amendment` / `close-amendment`.
9. **Archive OpenSpec**: Run `openspec archive <change-id>` (never pass `-y` to bypass confirmation).
10. **Close Lane (Run Last)**: Run `python scripts/workflow.py transition --step 10-acceptance-audit --change-id <change-id> --evidence workflow/evidence/<change-id>/10-acceptance-audit.json` to mark the Change `ACCEPTED` and release the implementation lease.

## Input/Output/Handoff Contract
- **Inputs**: Run `python scripts/agent-context.py --stage 10 --change <change-id>` for the lean read set.
- **Outputs**: `design/evidence/acceptance.md`, updated `docs/product/capabilities.csv`, `docs/product/modules.csv`, shared mutable write-back (`lessons.md`/`decisions.md`/`assumptions.md`), OpenSpec archive results, and final approval/transition records.
- **Downstream Handoff**: Archived Change, updated main specs and registries, and released implementation lease for subsequent Changes.
- **Review & Boundaries**:
  - `request-review` command: `python scripts/workflow.py request-review --step 10-acceptance-audit --change-id <change-id> --evidence workflow/evidence/<change-id>/10-acceptance-audit.json --summary "<summary>"`
  - Never archive, mutate global registries, or run `approve`/`transition` before explicit user approval. Follow `AGENTS.md`.
