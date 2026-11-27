---
name: figma-design-review
description: Author and review HTML-first (Figma optional) UI design documents, target-framework design code, layout assertions, and the UI design contract.
---

# Stage 06: UI Design and Review (HTML-First, Figma Optional)

## Role
Establish the frozen per-platform PAGE set, self-contained HTML design documents (`design/ui-html/`), target-framework static design code (`design/figma-code/`), runtime layout assertions (`design/figma-layout.csv`), and single UI contract (`design/figma-audit.md`).

## Required Methods
- Use `brainstorming` for UI structure, state coverage, and platform adaptation decisions.
- Load `.claude/skills/figma-design-review/references/figma-source.md` **only** when `Figma-to-HTML` or legacy direct Figma is explicitly selected by the user.

## Execution Flow

### Path A: No-UI Change (Conditional Skip)
- Run `python scripts/workflow.py skip-stage --step 06-figma-design-review --change-id <change-id> --reason "<reason>"` (auto-generates minimal N/A `design/figma-audit.md`, runs `check-figma-audit.py --strict --no-ui`, and writes skip evidence when none exists) and end the turn. (Alternatively, supply a pre-built `--evidence` file after running `check-figma-audit.py --no-ui`.)

### Path B: UI Change (HTML-First Default)
1. **Entry**: Run `python scripts/workflow.py check-entry --step 06-figma-design-review --change-id <change-id>` and `python scripts/agent-context.py --stage 06 --change <change-id>`. Read `- Target platforms:` from `design/user-stories.md` and `## Visual Conventions` from `docs/architecture/frontend-conventions.md`.
2. **HTML Design Docs (`design/ui-html/`)**:
   - Record one explicit HTML provenance: `User-provided HTML`, `AI-authored from requirements`, or `Figma-to-HTML`.
   - Produce `README.md`, `index.html` (review entry), `tokens.css`, and one self-contained `<platform>/PAGE-00N.html` per PAGE per declared platform (with stable `data-node-id` attributes, real copy, zero external network dependencies). Every declared platform needs ≥ 1 PAGE; PAGE IDs freeze in Stage 06.
3. **Render & Measure (`design/figma-layout.csv`)**:
   - Render each HTML page at its platform viewport and extract actual geometry/text/font values (`figma_node_id` stores HTML `data-node-id`).
   - Prefer setting `dom_selector` directly to `[data-node-id="<id>"]`; `route` may be finalized in Stage 07 (`PENDING` only in `route` if not yet routed).
4. **Target-Framework Transcription (`design/figma-code/`)**:
   - Determine target framework from `docs/architecture/technology-decisions.md` (e.g., Vue `.vue` + Element Plus / uni-app, or React `.tsx`).
   - Transcribe each PAGE into `design/figma-code/PAGE-00N.<ext>` preserving layout, tokens, copy, and `data-node-id` (static skeleton only; Stage 08 adds business logic without rewriting styles/layout/copy). Document framework, extension, substitutions, and deviations in `design/figma-code/README.md`.
5. **Single UI Contract (`design/figma-audit.md`)**:
   - Populate actual token values, text styles, PAGE list, design code notes, `## Assertion Scope` (referencing `figma-layout.csv`), state coverage (routine states such as loading/empty/error/toast/skeleton may be filled with project tokens and recorded as `UI-DERIVED (routine)` without an approver; non-routine derived modals/states still require a new PAGE or `UI-DERIVED` with approver), `## Requirements Coverage` (every AC/US per declared platform `FULL` or `N/A + reason`, every PAGE back-mapped), asset list (`design/figma-assets/` for real image/SVG only; **never save screenshots**), render/measure records, and UI review approval.
   - `docs/product/open-questions.md` is append-only for unresolved page questions.
6. **Stage-End Gates**:
   - `python scripts/check-figma-audit.py --change <change-id> --strict --require-framework`
   - `python scripts/check-method-evidence.py --step 06-figma-design-review --evidence workflow/evidence/<change-id>/06-figma-design-review.json`

## Input/Output/Handoff Contract
- **Inputs**: Run `python scripts/agent-context.py --stage 06 --change <change-id>` for the lean read set.
- **Outputs**: `design/figma-audit.md`, `design/ui-html/` (omitted only for legacy direct Figma), `design/figma-code/`, `design/figma-layout.csv`, and `design/figma-assets/README.md` (only when real image/SVG assets exist).
- **Downstream Handoff**: Frozen per-platform PAGEs, tokens, target-framework design code, and layout assertion table for Stage 07 (consumed offline by default).
- **Review & Boundaries**:
  - Generate `workflow/evidence/<change-id>/06-figma-design-review.json` (set `approval.required=true` for UI Changes) and run:
    `python scripts/workflow.py request-review --step 06-figma-design-review --change-id <change-id> --evidence workflow/evidence/<change-id>/06-figma-design-review.json --summary "<summary>"`
  - Present `templates/workflow/step-handoff-report.md` and end the turn.
  - Under `standard` policy, run `approve` and `transition` only after explicit user approval. Under `risk-based` policy (`STATUS=RISK_BASED_FAST_TRACK`), `transition` may run after gates pass. Follow `AGENTS.md`.
