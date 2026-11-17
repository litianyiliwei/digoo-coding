# Input/Output Context Policy

> Language: English | [简体中文](INPUT-OUTPUT-POLICY-zh.md)

> Status: APPROVED (2026-11-13, user confirmed "optimize inputs, then optimize outputs based on the lean inputs")
> Scope: Stages 02-10; project level and Change level
> Machine authority: `input_policy` and `output_policy` in `docs/STEP-ARTIFACT-CONTRACTS.json`

## 1. Why Convergence

Previously, the `inputs` of stages 05-10 mixed the complete product baseline, complete architecture baseline, ADRs, complete specs, and current Change artifacts together; Stage 02 also lacked a generated lean read set. Although most entries said "read as needed," there was no default reading order, file budget, or trigger condition for every stage. In actual execution, two problems easily occurred:

- Loading all of `docs/product/*` and `docs/architecture/*` into context at once, crowding out the current Change's key contracts;
- Or reading only a few files while claiming "verified against the inputs," missing the sections that actually affect the design.

Now "the complete input set for auditing" and "the default lean reading set" are separated: `inputs` remains the complete contract set (for handoff/traceability), while `input_policy.stage_profiles` defines what each stage reads by default and when to read more.

## 2. Input Layers

| Layer | Content | Reading Rule |
|---|---|---|
| 0 Resident | `docs/product/BASELINE-BRIEF.md` when present (≤1 page); `baseline-status.md` when relevant | Read the brief first when it exists; Stage 02 may run before it exists and creates it from user-provided goals. Do not repeatedly read the full baseline |
| 1 Current Change | `proposal.md`, `specs/<capability>/spec.md`, `user-stories.md`, `tasks.md`, `design.md`, `baseline-impact.md`, `baseline-binding.json` | Mandatory reading in Change stages |
| 2 Targeted | The `FLOW/NODE/DO/RD/BR/ROLE/CAP/PAGE/API/IO/INTERFACE` rows or sections hit by this Change; architecture sections hit by the design domain | Read the relevant rows/sections by ID, not the whole file |
| 3 On Demand | Complete `docs/product/*`, complete `docs/architecture/*`, `docs/adr/*`, `reference-research.md`, complete specs | Read only when Layers 0-2 cannot answer; the handoff report records the trigger reason |

## 3. Default Budget

- The default lean set is **≤8 reading groups** and about **≤16000 characters** (each group should point to only one file/section where possible; multiple files within a group are targeted by ID) (`max_lean_files` / `max_lean_chars` in the contract).
- When the budget is exceeded: first split the Change, narrow the scope, or record in Section 1 of the handoff report "why which extra files must be read."
- It is not allowed to use the full baseline package, the full architecture documents, or all ADRs as default context.

## 4. How to Read in Each Stage

Run for the current stage (Stage 02 is project-level discovery and does not require a Change ID):

```bash
python scripts/agent-context.py --stage 07 --change <change-id>
```

The output is divided into:

- `Lean inputs (read by default)`: read in order from the current stage profile; Stage 02 starts with user-provided goals, while Change stages start with the brief and current Change artifacts;
- `On-demand inputs (read after a trigger)`: read only when the corresponding design domain is hit/a decision conflicts;
- `Complete contract inputs (for auditing, not read by default)`: shown only with `--full`, used for handoff auditing rather than default context.

The lean/on-demand list for each stage is authoritative in `input_policy.stage_profiles` of `docs/STEP-ARTIFACT-CONTRACTS.json`; `docs/STAGE-IO-OVERVIEW.md` displays it in sync.

## 5. Output Optimization

The output principle is **reference-style output**: do not copy the full input text; reference baselines, specifications, and upstream artifacts by ID/path/section; each output writes only the decisions, contracts, or evidence newly added in this stage.

- Summary files (`BASELINE-BRIEF.md`, `requirements-analysis.md`, `baseline-audit-report.md`, `acceptance.md`) write only conclusions/differences/evidence and do not repeat detail tables.
- `design.md` writes only this Change's decisions/contracts/implementation constraints/test mapping; baseline content is referenced by ID, not copied in full.
- Evidence files (`code-review.md`, `independent-verification-report.md`, `acceptance.md`) reference JSON/log/report paths and do not restate all test output.
- Tables retain only decision items, contract items, and evidence items; fixed template fields are not expanded repeatedly.

The recommended line limits for summary files are in the contract's `output_policy.summary_budgets` (for example, `BASELINE-BRIEF.md` ≤60 lines, `design.md` ≤400 lines, `acceptance.md` ≤120 lines). When the limit is exceeded, first check whether inputs were copied; if necessary, split the Change or link to upstream files.

## 6. Relationship with Gates

- `check-step-contracts.py` verifies that every stage 02-10 has `input_policy.stage_profiles`, and that the number of `lean` entries does not exceed `max_files`.
- The evidence of `workflow.py transition` is still audited against the complete `inputs`; lean reading will not let missing formal inputs pass.
- Section 1 of the handoff report must list the files/sections actually read; on-demand files that were not read must not be claimed as reviewed.
