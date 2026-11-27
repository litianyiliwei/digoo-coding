---
name: proposal-planning
description: Slice project requirements into ordered, independently deliverable feature Changes, dependency DAG, and capability/module registries.
---

# Stage 04: Proposal Planning and Roadmap

## Role
Break the frozen project baseline into vertical, independently acceptable feature Changes, establish their dependency DAG, and initialize the capability and module ownership registries.

## Required Methods
- Use `brainstorming` to evaluate slicing boundaries, dependency ordering, and incremental delivery value.

## Execution Flow
1. Run `python scripts/workflow.py check-entry --step 04-proposal-planning` and `python scripts/agent-context.py --stage 04`.
2. **Initialize Registries** (aligned with `docs/architecture/code-layout.json`):
   - `docs/product/modules.csv`: register `module_slug`, `module_name`, `domain_id`, `frontend_paths`, `backend_paths`, `shared_paths`, `capabilities`, `status`, `notes` (one module = one bounded business subdomain).
   - `docs/product/capabilities.csv`: register `capability_slug`, `capability_name`, `domain_id`, `owner_module`, `related_modules`, `status`, `delivered_slices`, `remaining_slices`, `active_changes`, `notes`.
3. **Author `docs/product/proposal-roadmap.md`** (using `templates/product/proposal-roadmap.md`):
   - Fill every required column: `Change ID`, `Primary Capability`, `Owner Module`, `Related Modules`, `Slice Type` (`initial|extend`), `Slice Coverage` (`partial|full`), `Code Target`, `Demo Path`, `Slice Budget`, `Dependencies` (`none`/`N/A` or semicolon-separated prerequisite Change IDs), `Target Platforms` (semicolon subset of canonical platforms), `Value`, `Baseline Domains`, `Potential Amendment`.
   - In `## Ordering Rationale`, explain every dependency edge using `- <change> ← <dependency>: <reason>` (DAG must be acyclic).
   - Respect `docs/product/change-sizing.md` budgets; flag any potential baseline amendments explicitly.
4. **Stage-End Gates**:
   - `python scripts/check-capabilities.py`
   - `python scripts/check-modules.py`
   - `python scripts/check-roadmap.py --strict`
   - `python scripts/check-method-evidence.py --step 04-proposal-planning --evidence workflow/evidence/project/04-proposal-planning.json`

## Input/Output/Handoff Contract
- **Inputs**: Run `python scripts/agent-context.py --stage 04` for the lean read set (`BASELINE-BRIEF.md`, `change-sizing.md`, frozen baseline manifest/registry/status, `code-layout.json`, `baseline-audit-report.md`, matched IDs).
- **Outputs**: `docs/product/proposal-roadmap.md`, `docs/product/capabilities.csv`, `docs/product/modules.csv`.
- **Downstream Handoff**: Approved proposal roadmap, dependency DAG, target platforms, and capability/module registries for Stage 05.
- **Review & Boundaries**:
  - Generate `workflow/evidence/project/04-proposal-planning.json` and run:
    `python scripts/workflow.py request-review --step 04-proposal-planning --evidence workflow/evidence/project/04-proposal-planning.json --summary "<summary>"`
  - Present `templates/workflow/step-handoff-report.md` and end the turn.
  - Under `standard` policy, run `approve` and `transition` only after explicit user approval. Under `risk-based` policy (`STATUS=RISK_BASED_FAST_TRACK`), `transition` may run after gates pass. Follow `AGENTS.md`.
