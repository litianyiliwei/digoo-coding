---
name: requirements-analysis
description: Conduct project-level requirements business analysis, competitor research, target-platform inventory, and product baseline authoring.
---

# Stage 02: Requirements Business Analysis

## Role
Transform user goals, interviews, and reference research into a closed, verifiable project product baseline (`FLOW`/`NODE`/`DO`/`RD`/`BR` + target platforms).

## Required Methods & Guidance
- Load `.claude/skills/competitor-research/SKILL.md` (`competitor-research`) and use `brainstorming` + `internet-research` (record real queries, URLs, access dates; never fabricate).
- Consult `process/QUESTION-COVERAGE-CHECKLIST.md` (`02-*`) to prevent discovery blind spots; log unresolved questions in `docs/product/open-questions.md` (append-only).

## Execution Flow
1. Run `python scripts/workflow.py check-entry --step 02-requirements-analysis` and `python scripts/agent-context.py --stage 02`.
2. **Discovery & Target Platforms**: Interview the user on goals, non-goals, roles, constraints, pain points, and target client forms. Fill `## 10. Target Platforms and Client Forms` in `docs/product/requirements-analysis.md` with explicit `YES`/`NO` for all canonical platforms (`web`, `h5`, `mini-program`, `app`, `android`, `ios`, `harmonyos`, `desktop`, `pda`), at least one `YES`, and a reason for every `NO`.
3. **Reference & Competitor Research**: Execute `.claude/skills/competitor-research/SKILL.md` end-to-end and write `docs/product/reference-research.md` (including `## 9. Similar Product Deviation Confirmation` with user confirmer + date for any major deviation).
4. **Core Business Model**: Author closed-reference artifacts using `templates/product/*`:
   - `docs/product/requirements-analysis.md` (overview, scope, NFRs, target platforms)
   - `docs/product/workflows.md` (each `FLOW` has a complete node table: role, input/output `DO`, preconditions, actions, exceptions/branches, next node)
   - `docs/product/data-objects.csv` (`DO` catalog) & `docs/product/rd-matrix.csv` (`RD` matrix covering every node)
   - `docs/product/business-rules.md` (`BR` rules), `docs/product/role-permission-matrix.csv`, `docs/product/glossary.md`, `docs/product/acceptance-policy.md`
   - `docs/product/open-questions.md`, `docs/product/decisions.md`, `docs/product/assumptions.md`, `docs/product/change-sizing.md`, `docs/product/id-conventions.md`, `docs/product/lessons.md`
5. **Standing Entry Point & Index**:
   - Write `docs/product/BASELINE-BRIEF.md` (≤ 60 lines; concise one-page summary for Stages 03–05).
   - Generate `docs/product/BASELINE-INDEX.md` via `python scripts/gen-baseline-index.py --write`.
6. **Stage-End Gates** (no `PENDING`/`TODO`/`TBD` in strict-gated files):
   - `python scripts/check-requirements.py --strict`
   - `python scripts/gen-baseline-index.py --check`
   - `python scripts/check-reference-research.py --strict`
   - `python scripts/check-output-context.py --stage 02`
   - `python scripts/check-method-evidence.py --step 02-requirements-analysis --evidence workflow/evidence/project/02-requirements-analysis.json`

## Input/Output/Handoff Contract
- **Inputs**: Run `python scripts/agent-context.py --stage 02` for the lean read set (user materials, existing matched IDs, open questions).
- **Outputs**: All declared `docs/product/*` artifacts listed in `STEP-ARTIFACT-CONTRACTS.json` step `02`.
- **Downstream Handoff**: Approved product baseline (`FLOW`/`NODE`/`DO`/`RD`/`BR`, target platforms, `reference-research.md`, `BASELINE-BRIEF.md`, `BASELINE-INDEX.md`) for Stage 03.
- **Review & Boundaries**:
  - Generate `workflow/evidence/project/02-requirements-analysis.json` and run:
    `python scripts/workflow.py request-review --step 02-requirements-analysis --evidence workflow/evidence/project/02-requirements-analysis.json --summary "<summary>"`
  - Present `templates/workflow/step-handoff-report.md` and end the turn. Advance (`approve` → `transition`) only after explicit user approval. Follow `AGENTS.md`.
