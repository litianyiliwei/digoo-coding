# Project · AI R&D Workflow Toolkit

> Language: English (main) | [简体中文](README-zh.md)

This repository is an AI R&D workflow toolkit built for **OpenSpec + Superpowers + Figma MCP**. It splits product development into 10 gated stages, each backed by an independently loadable Skill, Prompt, templates, and deterministic check scripts. No business code has been implemented yet; the repository is currently in its initialized state.

## Current Repository State

| Item | Value |
|---|---|
| Workflow state | Stage `01-project-bootstrap` completed; next stage is `02-requirements-analysis` (requirements analysis) |
| Active change | None |
| Pending approvals / blockers | None |
| Project baseline | `v0.1.0` DRAFT; none of the six baseline domains is frozen |
| OpenSpec | No active changes and no main specs (`openspec/changes/` and `openspec/specs/` are empty skeletons) |
| Business source code | None |

To continue the process, tell the agent “下一步 / 继续 / 接着做” (next step / continue / keep going). It first loads the `workflow-orchestrator` Skill and then determines the only safe next stage from `workflow-state.json` and the actual artifacts on disk.

## Stage Overview

| Stage | Skill | Prompt | Key Outputs |
|---|---|---|---|
| 01 Project bootstrap & toolchain check | `project-bootstrap` | `prompts/01-project-bootstrap.md` | `AGENTS.md`, `workflow-state.json`, `docs/architecture/baseline-status.md`, `docs/project/toolchain-report.md` |
| 02 Requirements analysis | `requirements-analysis` | `prompts/02-requirements-analysis.md` | `docs/product/` requirements, workflow node tables, data objects, RD matrix, business rules, glossary, acceptance policy |
| 03 Project architecture baseline | `project-architecture-baseline` | `prompts/03-project-architecture-baseline.md` | `docs/architecture/` baseline, ADRs, baseline manifest and constraint registry (frozen) |
| 04 Proposal planning & roadmap | `proposal-planning` | `prompts/04-proposal-planning.md` | `docs/product/proposal-roadmap.md` |
| 05 Feature requirements | `feature-requirements` | `prompts/05-feature-requirements.md` | `openspec/changes/<change-id>/` proposal, specs, design, tasks, user stories, baseline impact and binding |
| 06 Figma design review (Figma-only) | `figma-design-review` | `prompts/06-figma-design-review.md` | `design/figma-audit.md`, `design/figma-code/`, `design/figma-layout.csv` |
| 07 Detailed design | `detailed-design` | `prompts/07-detailed-design.md` | The five sections of `design.md`, `design/test-cases.csv`, OpenAPI, API→IO mapping, `traceability.csv` |
| 08 Implementation & code review | `implementation-orchestrator` | `prompts/08-implementation-orchestrator.md` | Source code, tests, `design/evidence/code-review.md`, `figma-layout-check.json` |
| 09 Independent verification | `independent-verifier` | `prompts/09-independent-verification.md` | `design/evidence/independent-verification-report.md` and `.json` |
| 10 Acceptance audit & archive | `acceptance-audit` | `prompts/10-acceptance-audit.md` | `design/evidence/acceptance.md`, acceptance records, OpenSpec archive, baseline write-back |

The stage DAG has a single authoritative definition in `docs/WORKFLOW-STAGES.json`; each stage's input/output/handoff contract lives in `docs/STEP-ARTIFACT-CONTRACTS.md` and `.json`.

## Directory Structure

| Path | Purpose |
|---|---|
| `.claude/skills/` | 11 project workflow Skills (10 stages plus `workflow-orchestrator`) and 6 OpenSpec helper Skills, 17 in total |
| `prompts/` | Stage Prompts, one per Skill; `prompts/00-next-step.md` is the entry point |
| `scripts/` | Check and utility scripts for structure, traceability, OpenAPI, tests, baseline governance, and the workflow state machine |
| `templates/` | Templates for project baselines, Change auxiliary artifacts, workflow evidence, and handoff reports |
| `docs/` | Process specifications (`PROCESS-MAP.md`, `TEMPLATE-POLICY.md`, `BASELINE-FEATURE-INTERACTION.md`, etc.) and project-level baseline skeletons |
| `openspec/` | OpenSpec configuration and the Change/spec directories (currently empty skeletons) |
| `workflow/` | Stage evidence under `evidence/` and SHA-256 handoff manifests under `handoffs/` |
| `workflow-state.json` | Cross-stage state index; advanced only through `scripts/workflow.py transition`, never edited by hand |
| `AGENTS.md` | Repository-level agent conventions (process entry points, template policy, agent boundaries) |

## Quick Start

If `python3` is unavailable on Windows, use `python` instead; the `.sh` scripts detect both automatically.

```bash
python scripts/next-step.py            # Read-only: print the next stage
python scripts/workflow.py status      # Workflow state summary
python scripts/workflow.py check-entry --step 02-requirements-analysis
python scripts/check-package.py        # Toolkit self-check
bash scripts/check-required-files.sh   # Baseline file presence (non-strict)
```

Before entering a stage, run `check-entry --step <id>` (a non-zero exit code means execution is forbidden). After finishing a stage, produce evidence as instructed and run `workflow.py transition`.

## Core Rules

1. **Artifacts on disk**: every stage writes its outputs to the contract-specified paths, never to chat only; each stage ends with a handoff report based on `templates/workflow/step-handoff-report.md`.
2. **State discipline**: `workflow-state.json` records only stages whose gates have passed and approvals are complete; drafts are never marked complete.
3. **Template governance**: formal outputs follow `docs/TEMPLATE-POLICY.md` and `docs/OUTPUT-TEMPLATE-MATRIX.csv`. Unknown values are written as `PENDING` with an owner and blocking condition; non-applicable items are written as `N/A` with a reason; template fields are never removed.
4. **Baseline first**: before starting a feature Change, the frozen baseline must be read and `design/baseline-impact.md` and `design/baseline-binding.json` produced; frozen baselines are never edited directly during implementation.
5. **UI evidence**: stage 06 is Figma-only. `design/figma-audit.md`, `figma-code/`, and `figma-layout.csv` are the only UI inputs; stages 08/09 run `check-figma-layout.py` and `check-design-tokens.py` for numeric assertions. Screenshots are never used as evidence anywhere in the process.
6. **OpenSpec**: the standard artifacts are `proposal.md`, `specs/<capability>/spec.md`, `design.md`, and `tasks.md`; `tasks.md` must use `- [ ]` / `- [x]`; archiving requires explicit human approval.
7. **Agent boundaries**: no automatic dependency installation, commits, CI changes, archiving, or releases, and no approving unresolved rules on behalf of business, design, or architecture owners.

## Further Reading

- [AGENTS.md](AGENTS.md) — repository conventions and process entry points
- [docs/PROCESS-MAP.md](docs/PROCESS-MAP.md) — overview of stages and artifacts
- [docs/STAGE-IO-OVERVIEW.md](docs/STAGE-IO-OVERVIEW.md) — per-stage input/output overview (generated from the contracts)
- [docs/P0-RUNTIME-GOVERNANCE.md](docs/P0-RUNTIME-GOVERNANCE.md) — state machine, gates, handoff manifests, and independent verification
- [docs/BASELINE-FEATURE-INTERACTION.md](docs/BASELINE-FEATURE-INTERACTION.md) — two-way governance between project baselines and feature Changes
- [docs/TEMPLATE-POLICY.md](docs/TEMPLATE-POLICY.md) — output template governance
- [docs/STEP-ARTIFACT-CONTRACTS.md](docs/STEP-ARTIFACT-CONTRACTS.md) — stage handoff contracts (authoritative list)
- [scripts/README.md](scripts/README.md) — check script reference

> Note: This README is the English main document. [README-zh.md](README-zh.md) is the Simplified Chinese version; both are maintained together, and the Chinese file follows this file when they diverge.
