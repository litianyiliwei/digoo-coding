# Stage, Skill, Prompt, and Script Cross-Reference

> Language: English | [简体中文](PROCESS-MAP-zh.md)

| Stage | Skill ID | Prompt File | Automated Checks |
|---|---|---|---|
| 01 Project Initialization and Toolchain Check | `project-bootstrap` | `prompts/01-project-bootstrap.md` | `scripts/check-package.py` |
| 02 Requirements Business Analysis | `requirements-analysis` | `prompts/02-requirements-analysis.md` | `scripts/check-requirements.py --strict` (process nodes, data objects, RD matrix structure) + `python scripts/check-reference-research.py --strict` (reference products and internet research: ≥3 questions, ≥3 sources, ≥2 comparisons) |
| 03 Overall Project Architecture Design | `project-architecture-baseline` | `prompts/03-project-architecture-baseline.md` | `scripts/check-required-files.sh --strict` + `python scripts/check-architecture-baseline.py --strict` (Existing System Secondary-Development Constraints / Third-Party Interface Dependency List / LEGACY-*/EXT-*) + technology selection interview record + stage-end audit `baseline-governance.py freeze` / `audit --require-frozen` |
| 04 Proposal Breakdown, Dependency Ordering, and Roadmap | `proposal-planning` | `prompts/04-proposal-planning.md` | `baseline-governance.py audit --require-frozen` + `scripts/check-roadmap.py --strict` |
| 05 Proposal-Level Requirements Analysis | `feature-requirements` | `prompts/05-feature-requirements.md` | `scripts/check-requirements.py --change <change-id> --strict` (UC optional) + `baseline-governance.py check-change --phase requirement` + `scripts/check-baseline-impact.py <change-id>` |
| 06 Figma Design and Review (Figma-only) | `figma-design-review` | `prompts/06-figma-design-review.md` | `scripts/check-figma-audit.py --change <change-id> --strict --require-framework` (target framework/conversion notes + single-file token actual values + per-PAGE block specifications + figma-code/ target-framework design code + figma-layout.csv assertion mapping + assertion scope rationale + state decisions + UI review APPROVED) |
| 07 Detailed Design, Interfaces, and Test Design | `detailed-design` | `prompts/07-detailed-design.md` | When UI is involved, read the token actual values, per-PAGE specifications, state decisions, and `figma-assets/` from `figma-audit.md`; offline consumption by default, re-reading page by page only on version change/ambiguity while avoiding rate limiting; `openspec instructions design --change <change-id> --json` + `scripts/check-change.sh <change-id>` + `scripts/check-design-assets.sh <change-id> --strict --lint-api` + `scripts/check-design-sections.py --change <change-id>` + `scripts/check-test-cases.py --change <change-id> --strict` + `scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict` + when there is an API, `scripts/check-api-traceability.py --change <change-id>` + `openspec validate <change-id> --strict` + `baseline-governance.py check-change --phase design` + when there are cross-boundary interfaces, `scripts/check-interface-catalog.py --change <change-id> --strict` |
| 08 Implementation, TDD, Verification, and Code Review | `implementation-orchestrator` | `prompts/08-implementation-orchestrator.md` | `baseline-governance.py check-change --phase implementation` + `scripts/test-all.sh` + `verify-before-completion.sh` + `scripts/check-figma-layout.py` + `scripts/check-design-tokens.py` + `scripts/check-code-review.py --change <change-id> --strict` (UI Changes directly port the target-framework design code; `## UI fidelity` values are taken from figma-layout-check.json, and only deviating/UI-DERIVED PAGEs require manual explanation) |
| 09 Independent Verification and Acceptance Evidence | `independent-verifier` | `prompts/09-independent-verification.md` | `openspec status --change <change-id>` + `openspec validate <change-id> --strict` + `scripts/check-independent-verification.py --report <report> --evidence <json>` (UI Changes verify, in layout_checks, the per-PAGE asserted element count/max deviation/tolerance/missing elements/verdict and independent re-run record); Stage 10 is entered only after PASS |
| 10 Manual Acceptance, Archiving, and Baseline Write-back | `acceptance-audit` | `prompts/10-acceptance-audit.md` | `baseline-governance.py check-change --phase acceptance` + `scripts/check-acceptance.py <change-id>` + `verify-before-completion.sh` |

> `00` (`workflow-orchestrator` + `prompts/00-next-step.md`) is the non-DAG orchestration entry: it verifies state, approvals and real artifacts, chooses exactly one safe next stage, and never advances state itself.
> `06` is conditional: UI Changes run the full Figma review; no-UI Changes run `check-figma-audit --strict --no-ui` and then `workflow.py skip-stage`, producing a skip handoff instead of a human review.

## Method and Evidence Gates

- Stage evidence for 02–10 must include a `methods` block; `python scripts/check-method-evidence.py --step <step-id> --evidence <evidence.json>` can validate it separately, and `workflow.py transition` automatically calls the same logic.
- Stage evidence for 02/03/05/07 must also include a `question_coverage` block; `python scripts/check-question-coverage.py --step <step-id> --evidence <evidence.json>` validates every required item from `process/QUESTION-COVERAGE-CHECKLIST.md`, and `workflow.py request-review` / `transition` call it automatically.
- The `brainstorming` for 02/03/04/05/07 must record at least questions/alternatives/decisions; 03/07 require at least 4 questions and 2 alternatives. Without such records, the stage must not advance.
- 03 must discuss "new system / secondary development based on an existing system / hybrid, code location, third-party interfaces": for secondary development, actually read the code and write it into the `Existing System Secondary-Development Constraints` section of `technology-decisions.md` and the `LEGACY-*` entries of `constraint-registry.json`; third-party interfaces are written into `Third-Party Interface Dependency List`, EXTERNAL data flows, and API conventions.
- 07 must discuss "modification of existing feature code / new feature development, code location, third-party interfaces": when modifying existing features, actually read the code and write it into `### Existing Code Change Impact` in `design.md`; third-party interfaces are written into `THIRD_PARTY_API` rows of `interface-catalog.csv` and test/fakes evidence.
- When 07 has HTTP API, native bridge, device, third-party, asynchronous, or file boundaries, it must generate `design/interface-catalog.csv` and run `check-interface-catalog.py --change <change-id> --strict`; a Change with only HTTP API must also register `HTTP_API` rows in the catalog.
- For the per-stage allowed/forbidden scope of OpenSpec/Superpowers, see the "OpenSpec Participation Matrix" and "In-Stage Method Patterns" in `process/SUPERPOWERS-MAPPING.md`.

## Context Budget

- The contract's `inputs` is the complete audit/traceability set; default reading follows `input_policy.stage_profiles.lean` (≤8 read groups per stage, about ≤16000 characters).
- Reading order: `BASELINE-BRIEF` → current Change artifacts → targeted row/section reads by matched ID → full baselines/architecture/ADRs/full specs only when necessary and on demand, with the reason recorded.
- Run `python scripts/agent-context.py --stage <id> --change <change-id>` to get the lean package; `--full` is only for handoff audits.
- Output uses reference-style output and does not copy full input text; see `output_policy.summary_budgets` for summary line limits. Full rules are in `process/INPUT-OUTPUT-POLICY.md`.

## Check Strategy Notes

> Note: neither the project level nor the proposal level produces `use-cases` files. The project level expresses business flows with FLOW/NODE; proposal-level use case scenarios are written uniformly in the Scenario sections of delta specs, and US/AC remain in `design/user-stories.md`.

Requirement clarification, customer communication, Figma visuals, and architectural soundness cannot be reliably determined by generic shell scripts; these stages have explicit deliverables and manual review checklists rather than a fabricated automated "pass".

For formal artifact template levels and paths, refer to `process/TEMPLATE-POLICY.md` and `process/OUTPUT-TEMPLATE-MATRIX.csv`; after changing the template directory, run `python3 scripts/check-output-template-matrix.py`. Detailed design is consolidated into the five sections of `design.md`, and the API→IO mapping is mandatory only when APIs exist.

## Interaction Between Project Baseline and Feature Changes

- Stage 04: for each candidate Change, preliminarily read the frozen baseline, identify applicable domains, constraint reuse, and potential amendments; reflect this in the roadmap.
- Stage 05: mandatorily create `openspec/changes/<change-id>/design/baseline-impact.md`, recording the baseline version, files/sections/IDs, applicable constraints, reused items, conflicts, and classification.
- Stages 06–07: re-verify the baseline version by design domain; any baseline change must result in `NO_IMPACT` or `REBASE_REQUIRED`.
- Stage 08: follow the approved baseline; when implementation finds a conflict, pause the affected tasks and submit a BCR/ADR; frozen baselines must not be edited directly.
- Stage 10: write back only decisions that are approved, implemented, verified, and reusable across features; feature-specific details remain in the archived Change.
- Full rules: `process/BASELINE-FEATURE-INTERACTION.md`; Change record template: `templates/change-assets/design/baseline-impact.md`.

## Conversational Continuation Flow

- In an Agent with repository access and tool execution capability, use `prompts/00-next-step.md` or say "next step".
- After a stage's artifacts and checks are ready, run `workflow.py request-review --evidence ...`, present the handoff report, and end the turn. Only after the user explicitly replies "review passed <step-id>" run `approve` and then `transition`.
- `workflow-state.json` is only used for locating; the AI must check the real files, approval records, and OpenSpec CLI status.
- Project baseline stages differ from feature Change stages: the requirements business analysis stage only reads existing OpenSpec specs; a Change is created only after the proposal is approved.
- When there is a pending approval, a blocker, missing prerequisite artifacts, or a CLI validation failure, the process must not advance automatically.

## Mandatory Input/Output Handoff

The formal inputs, formal outputs, downstream consumption relationships, approval points, and quality gates of each stage are governed by `process/STEP-ARTIFACT-CONTRACTS.md` and the machine-readable `process/STEP-ARTIFACT-CONTRACTS.json`. Every Skill/Prompt embeds the corresponding contract reference. At the end of each stage, `templates/workflow/step-handoff-report.md` must be presented; unapproved artifacts must not serve as the formal inputs of the next stage.

When UI is involved, the sole UI contract of Stage 06 is the single file `design/figma-audit.md` (target framework/conversion notes, token actual values, text styles, per-PAGE block specifications, state decisions, design code, assertion scope, UI review APPROVED) together with `design/figma-code/` (the target-framework design code that 06 converts according to the overall technology selection: Vue stack `.vue` + Element Plus, React stack `.tsx`/`.jsx`) and `design/figma-layout.csv` (runtime assertion mapping); 07/08 consume them offline by default, re-reading page by page in batches only when the Figma file version changes or a page is ambiguous (serially, avoiding rate limiting). 07 uses the design code as the baseline to fill in `### PAGE→BLOCK→Component Mapping` (registering only business adaptations and `UI-DEVIATION`), fills in `route`/`dom_selector`, and defines responsive rules; 08 directly ports the design code and adds only business logic, runs `check-figma-layout.py` and `check-design-tokens.py`, and the values in `code-review.md`'s `## UI fidelity` are taken directly from `figma-layout-check.json`; 09 independently re-runs and verifies in `layout_checks`, with manual spot checks limited to deviating/`UI-DERIVED`/unasserted PAGEs (missing/out-of-tolerance/unapproved deviations must not PASS); 10 signs off non-deviating PAGEs in bulk based on machine evidence, and signs off deviating/`UI-DERIVED` PAGEs in `## UI acceptance` after side-by-side checking. **Screenshots are not saved throughout the process.** The Figma review draft is the final authority for visuals/components/variables, and PAGE IDs are frozen by 06. pen.dev, prototype.pen, PAGE-*.html, prototype.md, manifest.json, design-tokens.json, page-inventory/block-inventory/interaction-map/design-spec/figma-handoff are no longer used.

## P0 Runtime Governance

- The stage DAG is governed by `process/WORKFLOW-STAGES.json`; state transitions may only go through `scripts/workflow.py transition`.
- Each successful transition generates a SHA-256 handoff manifest; the downstream entry automatically verifies that upstream handoff files have not drifted; artifacts declared as outputs by later stages are marked `mutable_by_design` and only their existence is verified.
- After Stage 08 implementation, Stage 09 independent read-only verification must be completed, and Stage 10 may be entered only after PASS.
- For rework, use `workflow.py reopen --step <id> --reason <reason>`; after the current Change is accepted, use `workflow.py next-change --change-id <id>` to start the next Change.
- For detailed commands, Evidence JSON, and limitations, see `process/P0-RUNTIME-GOVERNANCE.md`.

## Baseline Governance Engine Gates

- Project baseline freezing: `baseline-governance.py freeze` / `audit --require-frozen`; the script verifies domain statuses, approval evidence, constraint sources, and SHA-256.
- Project baseline amendment: `open-amendment` first switches the overall status to UNDER_AMENDMENT; all Change stages are blocked during amendment; `close-amendment` re-freezes only after the affected domains' versions are upgraded, hashes refreshed, and approval evidence is complete.
- Change binding: Stage 05 automatically creates `baseline-binding.json`, establishing a record for every ACTIVE Constraint ID one by one; Stages 06–07 are gated by design evidence, Stages 08/09 by implementation evidence, and Stage 10 by acceptance.
- See Section 9 of `process/BASELINE-FEATURE-INTERACTION.md` for full usage rules; automated checks are not equivalent to approval identity authentication, and protected branches/CI/CODEOWNERS are still required.
