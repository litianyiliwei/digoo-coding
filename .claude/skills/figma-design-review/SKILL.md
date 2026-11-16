---
name: figma-design-review
description: Figma design and review (Figma-only). Generates real designs through Figma MCP and writes the read results to figma-audit.md as the sole UI input for 07–10.
---

# Figma Design and Review (Figma-only)

## When to Use

Load this Skill when the workflow enters stage 06 "Figma Design and Review". Handle one Change at a time; do not execute detailed design or implementation in advance.

## Core Rules (Mandatory)

- Stage 06 is Figma-only: the sole UI contract is the single file `openspec/changes/<change-id>/design/figma-audit.md` (target framework/transcoding notes, actual token values/each PAGE specification/states/UI review) together with the machine contracts `design/figma-code/` (one **target-framework-aligned** design code file per PAGE: the Vue stack uses `.vue` + that platform's component library (Element Plus for Web, uni-app component library for mobile), the React stack uses `.tsx`/`.jsx`; 08 ports it directly and only adds business logic) and `design/figma-layout.csv` (a compact geometry/text/font assertion table).
- **Framework-aligned transcoding (mandatory)**: Before the first call to `get_design_context`, stage 06 must first read `docs/architecture/technology-decisions.md` and section 1 of `docs/architecture/frontend-conventions.md`, determine and record the target frontend framework/component library; load the official `figma-design-to-code` Skill, and transcode the reference implementation returned by `get_design_context` into target-framework design code. When the target framework is Vue, output `.vue` (using that platform's component library: Element Plus for Web, the uni-app component library for mobile, plus project tokens); when React, output `.tsx`/`.jsx` (project component library + tokens); do not treat the raw React/Tailwind reference implementation as delivery code. Block if the technology selection is undecided or conflicts with the baseline; do not choose a stack yourself.
- Use Figma MCP AI to generate real Figma designs from approved requirements; the user must complete UI review on the real Figma review deliverable.
- After the design is complete, you must actually read the real files/nodes/components/variables through Figma MCP and write the read results to disk; node geometry comes from `get_metadata`, and you must not write only a summary or hand-write coordinates.
- **Do not use screenshots**: reference screenshots, implementation screenshots, and pixel screenshots are not design contracts or gate evidence; the rendering returned by `get_design_context` may be used only for immediate visual comparison, and must not be saved, registered as an asset, or written into any evidence file. Manual acceptance compares the running system with the Figma file, and automated visual regression uses numeric assertions on node geometry and runtime DOM (`scripts/check-figma-layout.py`).
- Block when Figma MCP is unavailable or the real design cannot be read; do not substitute screenshots, hand-written HTML, or fabrication.
- Do not use pen.dev, `prototype.pen`, `PAGE-*.html`, `prototype.md`, `manifest.json`, or `design/design-tokens.json` anymore.
- When there is no UI: in "Design Source and Selection" of `figma-audit.md`, write `- Design source status: N/A` and `- Reason for no UI: <reason>`, then run `--strict` validation; you may also use `--no-ui --reason "<reason>" --strict` for explicit validation. Do not mask omissions with empty files or an N/A without a reason.

## Input

Reading order: first read `docs/product/BASELINE-BRIEF.md` and the current Change artifacts; read targetedly by matched IDs; read full baselines/architecture/ADR/full specs on demand only when necessary and record the reason (see `docs/INPUT-OUTPUT-POLICY.md`).

Approved proposal-level requirements and ACs (proposal/specs/design/user-stories); project business flows, data objects, RD matrix, business rules (workflows/data-objects/rd-matrix/business-rules); `docs/product/open-questions.md` (read-only; do not make unauthorized decisions during generation); `docs/architecture/technology-decisions.md` (overall technology selection, determining the target frontend framework/component library) and sections 1 and 9 of `docs/architecture/frontend-conventions.md` (engineering and visual conventions); `docs/architecture/baseline-status.md`; the current Change's `design/baseline-impact.md` and `design/baseline-binding.json`; actual Figma MCP accessibility (mandatory when UI is involved).

## Execution Flow

1. **Verify inputs**: Check each file for existence, version, and approval status; stop and report when missing or unapproved.
2. **Determine the target framework (precondition for framework alignment)**: Read `docs/architecture/technology-decisions.md` and section 1 of `frontend-conventions.md`, and in `## Design Code` of `figma-audit.md` record `- Target framework: <Vue 3 + TypeScript + Element Plus / React + ...>`, `- Design code extension: <.vue / .tsx / .jsx>`, and the selection rationale (ADR/baseline version). Block when the technology selection is PENDING, mutually conflicting, or unreadable; do not choose yourself.
3. **Determine page scope**: Determine the PAGE list based on the approved proposal/specs/user-stories and project FLOW/NODE/DO/BR; PAGE IDs are frozen at this stage, and 07–10 must not add or rename them.
4. **Select the design source**: Default to Figma MCP AI automatic design; manual Figma design is used only when the user explicitly chooses it. Record the choice, chooser, and date in `## Design Source and Selection` of `figma-audit.md`, and write `- Design source status: APPROVED`.
5. **Generate the real design**: Use Figma MCP (`use_figma` and other actually available tools) to build editable frames page by page per PAGE; after drawing each page, read back the real nodes and confirm the nodes are non-empty.
6. **One-time complete export and framework-aligned transcoding**: First load the official `figma-design-to-code` Skill; `get_variable_defs` reads the actual token values for the whole file; `get_metadata` reads the precise node `x/y/w/h` for each PAGE (used to fill the assertion table); after `get_design_context` generates the reference implementation for each PAGE, immediately transcode it according to the target framework from step 2 and write it to disk as `design/figma-code/PAGE-001.vue … PAGE-00N.vue` (for the React stack, `.tsx`/`.jsx`). Transcoding must preserve real copy, font size/weight, spacing, radius, hierarchy, and `data-node-id`, and replace Tailwind/inline styles with the target UI component library and project tokens (the Vue stack uses that platform's component library (Element Plus for Web, uni-app for mobile) and CSS variables); produce only high-fidelity static pages and do not connect business APIs. When calling `get_design_context`, register `figma-design-to-code` in `skillNames` (prefix with `resource:` when loaded as a resource); returned renderings are for immediate comparison only and are not saved. Download image/SVG assets immediately to `design/figma-assets/` when needed, and do not keep temporary URLs. Call serially, do not poll node by node, and do not have multiple Agents read the same file in parallel; back off on 429/Retry-After, and block if export or transcoding is incomplete.
7. **Establish contracts**: In `figma-audit.md` write actual token values, text styles, PAGE → node/size, block-level specifications for each PAGE, target framework and design code notes, assertion scope, state coverage and decisions, and the asset list; in `figma-code/README.md` write the source `get_design_context`, target framework/extension, component and style/token replacement table, `data-node-id` correspondences, and transcoding deviations; establish the assertion subset in `figma-layout.csv` (each row includes expected `x/y/w/h`, text, font size/weight, tolerance; 06 may leave `route`/`dom_selector` as `PENDING`). When the full `get_design_context` is needed, write it directly to `figma-code/` and do not create separate scattered files.
8. **UI review**: The design owner completes the review on the real Figma review deliverable, and writes `- UI review status: APPROVED`, `- Reviewer: ...`, `- Review evidence: workflow/evidence/06-figma-ui-review.md` in `## UI Review`; the evidence file must actually exist.
9. **Gate**: Run `python scripts/check-figma-audit.py --change <change-id> --strict --require-framework`; the exit code must be 0; if it fails, do not enter 07.
10. **When there is no UI**: In "Design Source and Selection" of `figma-audit.md`, write `- Design source status: N/A` and `- Reason for no UI: <reason>`, and run `python scripts/check-figma-audit.py --change <change-id> --strict`; you may also use `--no-ui --reason "<reason>" --strict` for explicit validation.

## Output

`openspec/changes/<change-id>/design/figma-audit.md` (sole UI contract, single file), containing:
- `## Design Source and Selection`: source, chooser/date, file version, PAGE list.
- `## Design Inputs and Style References`: requirements and ACs, Figma MCP, section 9 of the design conventions.
- `## Design Tokens (Actual Values)`: color hex, spacing/radius/shadow px, CSS variable/Element Plus mapping.
- `## Text Styles (Actual Values)`: font family, weight, size, line height, letter spacing.
- `## PAGEs and Nodes`: PAGE → real node, frame size, state.
- `## PAGE Key Specifications`: block-level position/size/layout/padding/gap/border/radius/font for each PAGE; the full `get_design_context` snapshot may be appended.
- `## Design Code`: target framework and extension, selection rationale (ADR/baseline), source in `figma-code/README.md`, transcoding method (get_design_context reference implementation → target framework components/tokens), component and style replacement table, transcoding deviations, and the correspondence between `data-node-id` and `figma-layout.csv`.
- `## Assertion Scope`: list the key blocks covered by `figma-layout.csv`; elements not included in assertions are covered by the target-framework design code and machine assertions; structural differences are written into `## Differences and Pending Confirmation`.
- `## State Coverage`: default and applicable states for each PAGE; for states with no Figma frame, write the 07 decision/approval.
- `## Asset List`: only real image/SVG assets (file, source node, size); if there are no assets, write `- Assets: none`; do not register reference screenshots.
- `## MCP Read Records`, `## Differences and Pending Confirmation`, `## UI Review`.
- `design/figma-code/README.md`: source `get_design_context`, target framework/extension, transcoding method, component and style/token replacement table, transcoding deviations, `data-node-id` ↔ `figma_node_id` notes.
- `design/figma-code/PAGE-001.vue … PAGE-00N.vue` (for the React stack, `.tsx`/`.jsx`): one target-framework design code file per PAGE, preserving real copy/font size/spacing/hierarchy and `data-node-id`, using the target component library and project tokens; 08 ports it directly as the page skeleton and only adds business logic.
- `design/figma-layout.csv`: compact assertion table (`page_id,route,element_id,figma_node_id,x,y,width,height,dom_selector,assert_geometry,assert_text,tolerance_px,text_content,font_size,font_weight,notes`); 06 may leave `route`/`dom_selector` as `PENDING`, and 07 must fill them completely.
- `design/figma-assets/README.md`: generated only when real image/SVG assets exist (file, source node, sha256, size).

Do not split subdirectories per page/per state, do not generate scattered token/contract JSON, and do not save reference screenshots.

## Quality and Safety Boundaries

- PAGE IDs are stable and unique; the page set matches the Figma review deliverable; every PAGE is fully covered in `PAGEs and Nodes` and `PAGE Key Specifications`.
- Tokens must record actual values; variable names/counts alone are not a specification; every PAGE has at least 3 block-level geometry/layout rows.
- Every PAGE must have target-framework design code (Vue stack `figma-code/PAGE-00N.vue`, React stack `PAGE-00N.tsx`/`.jsx`), and `## Design Code` must state the target framework, extension, and selection rationale; `figma-layout.csv` must cover the key blocks and primary actions of every PAGE, with geometry/text/font values coming from Figma; structural differences are written into `## Differences and Pending Confirmation`.
- States must include default; for states without a Figma frame, the 07 decision, approver, and rationale must be written, and you must not claim they have been reproduced.
- Real image/SVG assets must actually exist in `design/figma-assets/` and be registered by `README.md`; reference screenshots do not enter the asset list.
- MCP read records must correspond to actual successful `get_metadata` and `get_variable_defs` calls; a tool name or "not executed" does not count as a read.
- Do not use screenshots, hand-written HTML, fabricated links, or empty files to replace real Figma designs.
- Pages, elements, and events must not bypass approved product/frontend/permission constraints; on conflict, record the constraint ID and submit an exception/BCR, and do not modify bindings yourself.
- UI review not APPROVED must not enter 07.

## Boundaries with OpenSpec / Superpowers

- OpenSpec stores proposal, delta specs, design, and tasks; this Skill does not replace OpenSpec validation.
- When interaction or multi-platform states need clarification, you may use the stage-scoped mode of Superpowers `brainstorming`, writing conclusions into the state coverage/differences sections of `figma-audit.md`, not a separate design document; claim use only when it is confirmed installed and callable. State coverage includes at least default, loading, empty, error, permission denied/degradation, offline/weak network, push/deep link (when applicable), and Android/iOS/HarmonyOS differences.
- Do not automatically commit, publish, archive, or overwrite user files at this stage.

## Recommended Checks

`python scripts/check-figma-audit.py --change <change-id> --strict --require-framework`; when there is no UI, write `- Design source status: N/A` and `- Reason for no UI: <reason>` in `figma-audit.md`, then run the same command, or use `--no-ui --reason "<reason>" --strict`.

## Actual Tool Invocation Requirements

- **Superpowers:** `brainstorming` (if actually available); when unavailable, explain and perform equivalent clarification steps.
- **OpenSpec:** Run `openspec status --change <id>` and read approved specs; commands must be actually executed and the exit code/result reported.
- **Figma MCP:** Rely on actually accessible capabilities; you must actually generate/read real Figma files, nodes, components, and variables; before the first call to `get_design_context` you must load the official `figma-design-to-code` Skill and transcode the results into target-framework design code; when unavailable, mark "not executed/blocked" and do not fabricate results. This stage does not use pen.dev.
- **State Update:** Update `workflow-state.json` only after artifacts are written to disk and the gates pass.

## Input/Output/Handoff Contract (Mandatory)

Before and after executing this Skill, you must comply with `docs/STEP-ARTIFACT-CONTRACTS.md` and read the contract record for `skill="figma-design-review"` in `docs/STEP-ARTIFACT-CONTRACTS.json`.

- **Inputs for this stage:** Approved proposal/specs/design/user-stories; project business flows/data objects/RD matrix/business rules/role permissions/ID conventions (workflows, data-objects, rd-matrix, business-rules, role-permission-matrix, id-conventions); `docs/product/open-questions.md` (read-only); `docs/architecture/technology-decisions.md` (target frontend framework/component library) and sections 1 and 9 of frontend-conventions; `docs/architecture/baseline-status.md`; `design/baseline-impact.md` and `design/baseline-binding.json`; actual Figma MCP capability (mandatory when UI is involved). Verify existence, version, and approval status item by item; stop and report when missing or unapproved.
- **Outputs for this stage:** `openspec/changes/<change-id>/design/figma-audit.md` (sole UI contract: target framework/transcoding notes, actual token values, text styles, PAGE specifications, state decisions, design code, assertion scope, UI review), `design/figma-code/README.md` and target-framework design code `PAGE-001.vue … PAGE-00N.vue` (React stack `.tsx`/`.jsx`), `design/figma-layout.csv` (compact assertion table: expected geometry/text/font/selectors; `route`/`dom_selector` may be filled by 07); when real images/SVGs exist, append `design/figma-assets/README.md`; do not save reference screenshots (N/A + reason when there is no UI).
- **Downstream handoff:** `figma-audit.md`, `figma-code/`, and `figma-layout.csv` are the sole UI inputs for 07/08/09/10; 07/08 consume them offline by default, and only reread Figma page by page in batches when the Figma file version changes or a page is ambiguous (serially, to avoid rate limits). PAGE IDs and the page set are frozen in 06; `traceability.csv` is initialized by 07 from PAGE → AC and merges API/test mappings.
- **End-of-stage presentation:** Use `templates/workflow/step-handoff-report.md` to present input verification, output paths and summaries, traceability relationships, self-check commands/exit codes, unexecuted items, pending-approval/blocked items, and next-stage inputs.
- **Blocker resolution:** If `blocked_items` exist for this stage in `workflow-state.json`, the `transition` evidence must add `resolved_blockers` (including `step_id`, `resolution`, and existing evidence paths); blocking items from other stages still need to be addressed first.

## Project Baseline Constraints (Read-Only Inheritance)

- Before execution, read `docs/architecture/baseline-manifest.json`, `docs/architecture/constraint-registry.json`, and the current Change's `design/baseline-binding.json`.
- Pages, elements, and events must not bypass approved product/frontend/permission constraints; on conflict, record the constraint ID and submit an exception/BCR, and do not modify bindings yourself.
- Before passing, run `python scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`.

## Stage Boundaries and Review Stop (Mandatory)

- Before starting, run `python scripts/workflow.py check-entry --step 06-figma-design-review [--change-id <id>]`; when the exit code is non-zero, stop immediately and report; do not bypass.
- Artifacts written and checks passing only mean ready for review: run `python scripts/workflow.py request-review --step 06-figma-design-review --summary "<summary>"`, present the handoff report according to `templates/workflow/step-handoff-report.md`, and then **end the turn immediately**; do not read/execute the next stage's Prompt/Skill or create next-stage artifacts in the same session.
- Only after the user explicitly replies "Review passed 06-figma-design-review" (the workflow requires explicit user approval) may you run `python scripts/workflow.py approve --step 06-figma-design-review --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval-record>` and execute `transition`. Do not fill in approver/approved_at yourself, and do not treat self-check success as approval.
- When `pending_approvals` is non-empty, advancing is prohibited; `workflow-state.json` may be managed only through `check-entry`/`request-review`/`approve`/`transition` and similar commands, and direct editing is prohibited.
- Claude Code's PreToolUse hook rejects writes to stage artifacts after the current stage (except shared artifacts) and direct edits to the state file; it also rejects them while pending review. When rejected, you must stop and explain; do not change paths or disable the hook to bypass it.
