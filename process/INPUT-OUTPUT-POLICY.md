# Input/Output Context Policy

> Language: English | [简体中文](INPUT-OUTPUT-POLICY-zh.md)

> Status: APPROVED (2026-11-13, user confirmed "optimize inputs, then optimize outputs based on the lean inputs")
> Scope: Stages 02-10; project level and Change level
> Machine authority: `input_policy` and `output_policy` in `process/STEP-ARTIFACT-CONTRACTS.json`

## 1. Why Convergence

Previously, the `inputs` of stages 05-10 mixed the complete product baseline, complete architecture baseline, ADRs, complete specs, and current Change artifacts together; Stage 02 also lacked a generated lean read set. Although most entries said "read as needed," there was no default reading order, file budget, or trigger condition for every stage. In actual execution, two problems easily occurred:

- Loading all of `docs/product/*` and `docs/architecture/*` into context at once, crowding out the current Change's key contracts;
- Or reading only a few files while claiming "verified against the inputs," missing the sections that actually affect the design.

Now "the complete input set for auditing" and "the default lean reading set" are separated: `inputs` remains the complete contract set (for handoff/traceability), while `input_policy.stage_profiles` defines what each stage reads by default and when to read more.

## 2. Input Layers

| Layer | Content | Reading Rule |
|---|---|---|
| 0 Resident | `docs/product/BASELINE-BRIEF.md` when present (about one page); `baseline-status.md` when relevant | Read the brief first when it exists; Stage 02 may run before it exists and creates it from user-provided goals. Do not repeatedly read the full baseline |
| 1 Current Change | `proposal.md`, `specs/<capability>/spec.md`, `user-stories.md`, `tasks.md`, `design.md`, `baseline-impact.md`, `baseline-binding.json` | Mandatory reading in Change stages |
| 2 Targeted | The `FLOW/NODE/DO/RD/BR/ROLE/CAP/PAGE/API/IO/INTERFACE` rows or sections hit by this Change; architecture sections hit by the design domain | Read the relevant rows/sections by ID, not the whole file |
| 3 On Demand | Complete `docs/product/*`, complete `docs/architecture/*`, `docs/adr/*`, `reference-research.md`, complete specs | Read only when Layers 0-2 cannot answer; the handoff report records the trigger reason |

## 3. Advisory Default Budget

- The default lean set is a guideline of about **8 reading groups** and about **16000 characters** (each group should point to only one file/section where possible; multiple files within a group are targeted by ID) (`max_lean_files` / `max_lean_chars` in the contract). These numbers are advisory, not gates.
- If the guideline is exceeded, narrow the scope or record in Section 1 of the handoff report "why which extra files must be read." Do not skip a file the stage actually needs just to stay under the number.
- Do not use the full baseline package, the full architecture documents, or all ADRs as default context.

## 4. How to Read in Each Stage

Run for the current stage (Stage 02 is project-level discovery and does not require a Change ID):

```bash
python scripts/agent-context.py --stage 07 --change <change-id>
```

The output is divided into:

- `Lean inputs (read by default)`: read in order from the current stage profile; Stage 02 starts with user-provided goals, while Change stages start with the brief and current Change artifacts;
- `On-demand inputs (read after a trigger)`: read only when the corresponding design domain is hit/a decision conflicts;
- `Complete contract inputs (for auditing, not read by default)`: shown only with `--full`, used for handoff auditing rather than default context.

The lean/on-demand list for each stage is authoritative in `input_policy.stage_profiles` of `process/STEP-ARTIFACT-CONTRACTS.json`; `process/STAGE-IO-OVERVIEW.md` displays it in sync.

The orchestrator entry (`prompts/00-next-step.md`) must consume the generated lean package from `scripts/agent-context.py` and the per-step contract record, not hand-read the full 71 KB contract, 30 KB state file and 20 KB template matrix on every turn. Those full files are audit inputs; their targeted row/section is the default.

## 5. Output Optimization

The output principle is **reference-style output**: do not copy the full input text; reference baselines, specifications, and upstream artifacts by ID/path/section; each output writes only the decisions, contracts, or evidence newly added in this stage.

- Summary files (`BASELINE-BRIEF.md`, `requirements-analysis.md`, `baseline-audit-report.md`, `acceptance.md`) write only conclusions/differences/evidence and do not repeat detail tables.
- `design.md` writes only this Change's decisions/contracts/implementation constraints/test mapping; baseline content is referenced by ID, not copied in full.
- Evidence files (`code-review.md`, `independent-verification-report.md`, `acceptance.md`) reference JSON/log/report paths and do not restate all test output.
- Tables retain only decision items, contract items, and evidence items; fixed template fields are not expanded repeatedly.

The advisory line limits for summary files are in the contract's `output_policy.summary_budgets` (for example, `BASELINE-BRIEF.md` around 60 lines, `design.md` around 400 lines, `acceptance.md` around 120 lines). `check-output-context.py` reports over-budget files as warnings by default; `--strict` is an opt-in for projects that want enforcement. When a file is over the guideline, first check whether inputs were copied; if the content is genuinely needed, keep it and record why.

## 6. Relationship with Gates

- `check-step-contracts.py` verifies that every stage 02-10 has `input_policy.stage_profiles`; `max_files` is an advisory guideline and `lean` may exceed it with recorded reasons. `agent-context.py` prints a warning when the guideline is exceeded and continues.
- `check-output-context.py` warns on over-budget summary files by default; `--strict` opts into failing the command.
- The evidence of `workflow.py transition` is still audited against the complete `inputs`; lean reading will not let missing formal inputs pass.
- Section 1 of the handoff report must list the files/sections actually read; on-demand files that were not read must not be claimed as reviewed.
