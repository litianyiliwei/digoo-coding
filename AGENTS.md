# AGENTS.md — Project Repository Conventions

> Language: English | [简体中文](AGENTS-zh.md)

> Status: APPROVED (created 2026-10-30 by the project-bootstrap stage and confirmed by the user on 2026-10-30; converted to English as the main document on 2026-11-13 by user request, with the Chinese translation at `AGENTS-zh.md`; the workflow was reset to Stage 01 on 2026-11-18 and previous project data was moved out of the workspace; the toolkit itself is Python 3.11 + Markdown/JSON/CSV, and project-specific architecture conventions will be re-established in Stage 03)
> Downstream consumers: Agents in all stages (Claude/OpenCode, etc.); from requirements discovery (Stage 02) onward, they must follow this document's process entry and template policy.

## Project Goal

Project. The current repository only contains the AI R&D process toolkit (Skills, Prompts, templates, check scripts) and has no business source code yet.

## Process Entry

- When the user says "next step / continue / carry on", first load the `workflow-orchestrator` Skill (or `prompts/00-next-step.md`) and, based on `workflow-state.json` and the actual artifacts, determine the single safe next stage.
- Before each stage begins, read the contract record for the corresponding Skill in `docs/STEP-ARTIFACT-CONTRACTS.md` and `docs/STEP-ARTIFACT-CONTRACTS.json`.
- At the end of a stage, use `templates/workflow/step-handoff-report.md` to present the handoff report; artifacts must be written to disk at the paths specified by the contract and must not exist only as chat output.

## Stage Boundaries and Review Stop-and-Wait (Mandatory)

- **Stage completion ≠ permission to enter the next stage.** Writing the artifacts and passing checks only means "ready for review"; it does not mean approved. Before explicit user approval, it is forbidden to read or execute the next stage's Prompts/Skills, create the next stage's artifacts, or invoke next-stage tools.
- **Before starting any stage**, you must run `python3 scripts/workflow.py check-entry --step <step-id> [--change-id <id>]`; if the exit code is non-zero, stop immediately and report the blocking reason; do not bypass it.
- **The end-of-stage procedure for every stage (the order is immutable):**
  1. Generate `workflow/evidence/<step-id>.json` and run all check scripts for that stage;
  2. Run `python3 scripts/workflow.py request-review --step <step-id> --evidence workflow/evidence/<step-id>.json --summary "<review submission summary>"`, which writes a review packet pinning the artifact hashes and freezes the process as "pending review" (`current_step` does not advance);
  3. After presenting the handoff report in accordance with `templates/workflow/step-handoff-report.md` (artifact paths, summary, check results/exit codes, items to confirm, next-stage inputs), **end the turn immediately** and do not continue.
- **Only after the user explicitly replies "review passed <step-id>"** may you run `python3 scripts/workflow.py approve --step <step-id> --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval record>` and then run `transition`. Do not fill in approver/approved_at yourself, and do not treat "artifact complete", "checks passed", or the Agent's own judgment as approval.
- **08 (implementation) and 09 (independent verification) must likewise wait for user review**; 09 is completed by an independent Verifier in an independent context, and the Builder must not run the verification in the same session and automatically enter 10.
- **06 is conditional**: a no-UI Change must first run `python scripts/check-figma-audit.py --change <change-id> --strict --no-ui --reason "<reason>"` and then `workflow.py skip-stage --step 06-figma-design-review --evidence workflow/evidence/06-figma-design-review-skip.json`; a UI Change must complete the full Figma review and its evidence must set `approval.required=true`.
- When `pending_approvals` is non-empty, no stage may advance; `workflow-state.json` may only be written by `workflow.py` commands (`request-review`/`approve`/`transition`/`reopen`/`reset-state`/`migrate-state`); `check-entry` is read-only and direct editing is forbidden.
- Under Claude Code, the PreToolUse hook in `.claude/settings.json` rejects writes to stage artifacts later than the current stage, to already-approved stage artifacts that are not volatile, to the current stage's declared artifacts while review is pending, and to `workflow-state.json` directly. When rejected, you must stop and explain; bypassing is forbidden (changing the write path, disabling the hook, or using other tools to evade are all violations). Bash-driven writes are not intercepted by this hook and remain a documented trust limitation.
- Handoffs hash approved decision/acceptance artifacts only. Machine-managed or generated files (`workflow-state.json`, `AGENTS.md`, baseline status/manifest/registry, `BASELINE-INDEX.md`, `toolchain-report.md`) are volatile: handoffs record their existence, not their hash. Evidence outputs not declared in the stage contract are audit-only and must not invalidate a reviewed handoff.

## Template and Artifact Rules

- Formal artifacts follow the templates specified by `docs/TEMPLATE-POLICY.md` and `docs/OUTPUT-TEMPLATE-MATRIX.csv`; template fields must not be deleted; unknown items are written as `PENDING` with the reason and responsible person/blocking condition stated; non-applicable items are written as `N/A` with a reason.
- Before starting Stages 02/03/04/05/07/10, first read `docs/product/BASELINE-BRIEF.md`, `change-sizing.md`, and `id-conventions.md`; load detailed baselines according to the Change impact scope rather than stuffing the whole package into context. When baseline artifacts are missing or `check-requirements.py` has not passed, downstream stages must not be entered.
- Project-level baselines go in `docs/product/`, `docs/architecture/`, and `docs/adr/`; single-feature content goes in `openspec/changes/<change-id>/`.
- Every formal Markdown artifact must state at the beginning: Change ID (if applicable), status, source baseline, related requirement/AC IDs, generation date or version.
- The UI stage (06) of UI-related Changes is Figma-only:
  - Using the approved proposal requirements/ACs, product flow, Section 9 of `docs/architecture/frontend-conventions.md`, and `docs/architecture/technology-decisions.md` (overall technology selection) as inputs, generate a real Figma design via Figma MCP AI; the user must complete the UI review on the real Figma review draft.
  - **Framework-aligned conversion (mandatory)**: 06 must load the official `figma-design-to-code` Skill before calling `get_design_context`, and must first determine the target framework according to the overall technology selection; the returned reference implementation must be converted into target-framework design code: when the technology selection is Vue, output Vue SFC (`.vue`, using that platform's component library (Element Plus for Web, uni-app for mobile) and project tokens); when React, output React (`.tsx`/`.jsx`, using the project component library and tokens). `figma-code/README.md` must record the target framework, file extension, component/style/token substitutions, and deviations; it is forbidden to treat the original React/Tailwind reference implementation directly as deliverable code; 08 only adds business logic on top of this and does not rewrite styles/layout/copy.
  - After the design is complete, you must actually read the real file/nodes/components/variables via Figma MCP and write the token **actual values** (color hex, font size/line height, spacing/corner radius/shadows), text styles, per-PAGE block specifications, state coverage and decisions, design code (including target framework and conversion notes), assertion scope, MCP read records, and UI review APPROVED to the single file `design/figma-audit.md`; at the same time export `design/figma-code/` (target-framework design code) and `design/figma-layout.csv` (runtime assertion mapping). **Screenshots are not contracts, assets, or gate evidence**: the render returned by `get_design_context` may only be used immediately for visual comparison and must not be saved, registered, or committed; real image/SVG assets go in `design/figma-assets/`, with the README registering file/source node/sha256/dimensions, and "none" written when there are no assets. If Figma MCP is unavailable or the real design cannot be read, the stage is blocked; screenshots or fabrication must not be used as substitutes.
  - 06 exports everything in one go; 07/08 consume `figma-audit.md`, `figma-code/`, and `figma-layout.csv` offline by default, and re-read page by page in batches only when the Figma file version changes or a page is ambiguous (serially, to avoid rate limiting). 07 must build the token → CSS variable/Element Plus theme/font mapping in design.md, fill in `route`/`dom_selector` in `figma-layout.csv`, and define `### Responsive and Viewport Rules`; 08 must directly use the target-framework design code as the page skeleton (adding only business logic/routing/API/state), implement the global token layer and fonts, run `check-figma-layout.py` (Figma node geometry vs. 1440×900 runtime DOM; missing elements or out-of-tolerance values mean FAIL) and `check-design-tokens.py`, and generate `design/evidence/figma-layout-check.json`. **UI verification is based primarily on machine evidence**: the per-PAGE values in `code-review.md`'s `## UI fidelity` are copied directly from the JSON, and only PAGEs with deviations/`UI-DERIVED` require manual explanation and an approver; 09 independently re-runs and verifies in `layout_checks` of `independent-verification.json` (missing, out-of-tolerance, or unapproved deviations must not PASS), with manual spot checks limited to deviating/`UI-DERIVED` PAGEs; 10 signs off per PAGE in `acceptance.md`'s `## UI acceptance`, PAGEs with no deviations and a machine PASS may be signed off in bulk based on machine evidence, and only deviating/`UI-DERIVED` PAGEs need side-by-side checking. **Screenshots are not saved throughout the process; screenshots are not UI evidence.** If these UI numerical evidence items are missing, the corresponding stage must not advance or be archived.
  - PAGE IDs and the page set are frozen in 06; PAGEs must not be added or renamed. Modal/drawer/state definitions not defined in Figma must add new Figma artboards, or record the visual specification, approver, and reason as `UI-DERIVED`.
  - pen.dev, `prototype.pen`, `PAGE-*.html`, `prototype.md`, `manifest.json`, `design/design-tokens.json`, or scattered token/contract JSON are no longer used.
- The test case matrix goes in `design/test-cases.csv`; TEST IDs must link back to AC/PAGE/BLOCK/API/IO and be written into the single `traceability.csv`; tests must not exist only as narrative in design.md.

## OpenSpec Conventions

- See `openspec/config.yaml` for configuration (schema: spec-driven); the standard artifacts are `proposal.md`, `specs/<capability>/spec.md`, `design.md`, and `tasks.md`.
- `tasks.md` must use `- [ ]` / `- [x]` checkboxes.
- specs only describe externally observable behavior; class names/frameworks/implementation steps go in design.md.
- Every OpenAPI `operationId` must map to at least one real IO in `design/api-io-mapping.csv`, and IO contracts are written in `design/io-catalog.csv`.
- Manual approval is required before archiving (openspec archive); `-y` must not be used to bypass it.

## Check Scripts

- Package self-check: `python3 scripts/check-package.py`
- Next-stage suggestion (read-only): `python3 scripts/next-step.py`
- Baseline file check: `bash scripts/check-required-files.sh`
- Per-stage validation commands are in `scripts/README.md`; scripts are fail-closed, and passing results cannot be forged.

## Language and Style

- English is the main language for repository documents, Prompts, Skills, and templates; Simplified-Chinese translations of process documents use the same path with `-zh.md`.
- Formal project artifacts and agent replies follow the user's habitual language; code, API fields, and identifiers follow the repository's existing conventions (currently PENDING, to be determined at the first feature implementation).

## Agent Behavior Boundaries

- Do not automatically install dependencies, commit code, modify CI, archive, or release, and do not approve undecided rules on behalf of the business/design/architecture owners.
- Do not overwrite existing files; user approval is required before overwriting/modifying the existing `AGENTS.md`/`AGENTS-zh.md` or configuration.
- Superpowers skill names evolve with versions; during implementation, first confirm the actual installation and availability, and report honestly when missing.
- External tools (pen.dev, Figma MCP) are subject to their actual accessible capabilities; unreadable links/fields must not be treated as reviewed.
