# OpenSpec + Superpowers AI Development Workflow Toolkit

This toolkit breaks down 15 development workflow stages into independently loadable Skills, reproducible Prompts, baseline templates, and deterministic check scripts. It is designed for `pen.dev` + `Figma MCP` + `OpenSpec` + `Superpowers` + Claude/compatible agent workflows.

## Contents

- `.claude/skills/<skill-id>/SKILL.md`: 20 project workflow skills.
- `prompts/`: Prompts corresponding one-to-one with each stage skill; `prompts/00-next-step.md` serves as the "next step" entry point.
- `workflow-state.json`: Cross-stage state index; real artifacts and approval status must be verified before proceeding.
- `.claude/skills/workflow-orchestrator/SKILL.md`: Responsible for "next step" judgment, prerequisite checks, and gates.
- `scripts/next-step.py`: Reads the state file and prints suggested next stages (does not automatically modify state).
- `docs/product/`, `docs/architecture/`, `docs/design/`, `docs/adr/`: Project-level baseline and design checklist templates.
- `openspec/config.yaml`: Sample project context and artifact rules. **Compare with existing files before merging; do not blindly overwrite existing OpenSpec configurations.**
- `scripts/`: Structure, tracking, OpenAPI, test, and pre-completion check scripts, along with non-overwriting initialization helpers for change artifacts.
- `docs/SUPERPOWERS-MAPPING.md`: Mapping between project stages and official Superpowers skills.
- `docs/REVIEW-REPORT.md`: Self-inspection report and known limitations of this package.
- `docs/TEMPLATE-POLICY.md` & `docs/OUTPUT-TEMPLATE-MATRIX.csv`: Define which outputs require templates, template locations, and validation gates.
- `scripts/check-output-template-matrix.py`: Checks whether template files registered in the template matrix actually exist.

## Installation & Integration into Existing Projects

1. Extract the ZIP file to a temporary directory first to inspect differences; do not directly overwrite files with the same name in your project.
2. Merge `.claude/skills/`, `prompts/`, and `scripts/` into your project root. Keep existing skills with the same name after manual comparison.
3. Read `docs/TEMPLATE-POLICY.md` and `docs/OUTPUT-TEMPLATE-MATRIX.csv` to determine stage templates and quality gates. Merge `docs/` templates into existing documentation; do not use templates to overwrite real project content.
4. Merge `openspec/config.yaml` (`context` / `rules`) into your existing configuration; ensure schemas and rules fit your actual business needs.
5. If OpenSpec is not yet initialized, run `openspec init` in your project root (check `openspec init --help` for parameters). Do not use the template package to overwrite existing `openspec/specs/` or `openspec/changes/`.
6. Run:

   ```bash
   python3 scripts/check-package.py
   python3 scripts/next-step.py
   bash scripts/check-required-files.sh
   ```

7. Adjust test commands according to your actual repository directory structure, then run on a specific change:

   ```bash
   openspec new change <change-id>
   bash scripts/new-change-assets.sh <change-id>
   # After writing proposal/specs/design/tasks using prompts/ and corresponding skills, run:
   bash scripts/check-change.sh <change-id>
   bash scripts/check-design-assets.sh <change-id> --strict --lint-api
   bash scripts/validate-openapi.sh openspec/changes/<change-id>/api/openapi.yaml
   bash scripts/test-all.sh <frontend-dir> <backend-dir>
   ```

## Key Design Conventions

- Project-level baselines are stored in `docs/`; feature-level changes are described using OpenSpec Changes.
- OpenSpec `specs/**/spec.md` describes observable behavior, avoiding class names, frameworks, or step-by-step implementation details.
- In the current `spec-driven` workflow, standard artifacts are `proposal.md`, `specs/<capability>/spec.md`, `design.md`, and `tasks.md`. Other detailed design files serve as auxiliary materials in the change directory; file existence does not imply automatic OpenSpec validation of their content.
- `tasks.md` must use `- [ ]` / `- [x]`, otherwise OpenSpec cannot accurately track task progress.
- OpenSpec archiving updates the main specification and moves the entire change into the archive; verify that deltas are correct and tasks/acceptance criteria are completed before archiving.
- When saying "next step", execute `@workflow-orchestrator` or copy `prompts/00-next-step.md` first. This capability requires agent access to repository files, terminal, and skills. New chat sessions must reload states and real artifacts rather than relying solely on conversation memory.
- Superpowers skill names evolve over versions. Check installed versions during implementation; this package references official skill names like `brainstorming`, `writing-plans`, `test-driven-development`, `systematic-debugging`, `requesting-code-review`, `receiving-code-review`, `verification-before-completion`, etc. Report any missing skills truthfully.
- All external tools (`pen.dev`, Figma MCP) must be evaluated based on actual accessible capabilities; unreadable links/fields cannot be treated as reviewed.
- Not every AI output requires a template; formal, trackable outputs consumed downstream must follow the templates defined in `docs/OUTPUT-TEMPLATE-MATRIX.csv`.
- Every OpenAPI `operationId` must be explicitly mapped to one or more `io_id` entries in `design/api-io-mapping.csv`, and each IO ID must have a complete contract in `design/io-catalog.csv`. Databases, files, HTTP/Feign, Redis, MQ, object storage, and search are all considered concrete I/O. Pure computation/health check endpoints without I/O are only permitted as explicit exceptions with reasons and approvals; do not fabricate I/O just to fill out the table.

## Recommended Workflow

Requirements → Prototype Difference & Confirmation → Product Baseline → Overall Architecture / Domain / Public Contracts → Baseline Audit → Change Sorting → OpenSpec Specification → Page/Event Checklist → Figma Audit → API / Frontend / Backend / Test Design → Superpowers TDD → Automated Verification → Manual Acceptance → Archiving & Baseline Writeback.

## What Will NOT Be Done Automatically

By default, this package does not automatically install dependencies, commit code, modify CI, archive, publish, or approve pending rules on behalf of business/design/architecture leads.