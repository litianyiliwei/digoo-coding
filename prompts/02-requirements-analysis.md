# Prompt: Requirement Business Analysis

```text
Execute `@requirements-analysis`.

Input materials: <materials>
Project goals/users/roles: <goals-and-roles>
Existing product documents: <existing-product-docs>

Output the project-level requirement business analysis: docs/product/requirements-analysis.md, workflows.md, data-objects.csv, rd-matrix.csv, business-rules.md, glossary.md, acceptance-policy.md, open-questions.md, reference-research.md (reference products and internet research).

Reference products and internet research (precondition):
- First ask the user whether there are reference products/competitors/similar systems; ask them to provide names, links, screenshots, trial accounts, or documents, and record the answer.
- Whether or not there are reference products, you must use WebSearch/WebFetch (or a host-equivalent internet tool) to complete internet research with at least 3 research questions, 3 distinct sources (real URLs + access dates), and 2 comparisons; output `docs/product/reference-research.md` and run `python scripts/check-reference-research.py --strict`.
- When there is no internet capability, mark BLOCKED, write it into `open-questions.md`, and do not pass stage 02.

Requirements:
1. Business processes must be complete and omit nothing: cover the main processes, alternative processes, exception processes, and postconditions of all business domains; break each process down into executable nodes, with node IDs in the form NODE-<process-number>-<sequence-number>.
2. Each node must register the executing role, input data objects, output/written data objects, preconditions, processing actions, exceptions/branches, next node, and associated business rules.
3. Build a business data object catalog (DO-xxx) and output the RD matrix (rd-matrix.csv): register row by row requirement/rule → process node → role → data object → access type; each node must have at least one RD record (or N/A + reason).
4. This stage does not output user stories, use cases, or AC: US/AC are deferred to stage 05 proposal-level requirements analysis and generated per Change; use-case scenarios are written into the proposal-level spec's Scenario, and no separate `use-cases` file is produced.
5. When done, run `python scripts/check-requirements.py --strict`; failure means you may not proceed; check process node and RD matrix coverage during the stage-end audit.
6. Together with `brainstorming`, complete the business exception and boundary checklist: at minimum ask about weather/season, device offline, manual takeover, audit/traceability, regulatory reporting, multiple roles, historical data migration, data ownership and retention; write unconfirmed items into `open-questions.md` and do not decide them on your own.
7. Reference products and internet research: you must use the `internet-research` method (WebSearch/WebFetch or a host-equivalent internet tool) to complete research questions, reference products, source records, comparisons, conclusions, and impact mapping, written into `docs/product/reference-research.md`; at least 3 research questions, 3 distinct sources, 2 comparisons, and record access dates and approval. When there is no internet capability, mark BLOCKED and write it into `open-questions.md`; do not substitute memory or pass stage 02.
8. Method evidence: the stage evidence must write `methods`: `brainstorming` at least 3 business clarification questions, 1 alternative, 1 decision; `internet-research` at least 3 research questions, 2 comparisons, 1 decision. Write the landing points into `docs/product/requirements-analysis.md`, `docs/product/open-questions.md`, or `docs/product/reference-research.md`; run `python scripts/check-method-evidence.py --step 02-requirements-analysis --evidence <evidence.json>`.
9. Question coverage (mandatory): before review, fill the 02 section of `process/QUESTION-COVERAGE-CHECKLIST.md` (or copy it into the stage working notes), and write a `question_coverage` array into the stage evidence with one entry per required item. Each entry needs `item_id`, `status` (`answered`/`n/a`/`open`/`deferred`), and: a real `landing` artifact path (optionally `#heading`) for `answered`; `owner`, `blocking`, and `open_question` for `open`; `reason` for `n/a`; `reason`, `approver`, and `target_step` for `deferred`. Open items must also be written into `docs/product/open-questions.md` with an owner and blocking condition. Run `python scripts/check-question-coverage.py --step 02-requirements-analysis --evidence <evidence.json>`; `workflow.py request-review` and `transition` re-check it automatically.
For formal artifacts, follow the templates specified by `process/TEMPLATE-POLICY.md` and `process/OUTPUT-TEMPLATE-MATRIX.csv`; do not delete template fields, and write PENDING for unknown items with the reason.
```

Context: First run `python scripts/agent-context.py --stage <id> --change <change-id>` to obtain condensed inputs; the full `inputs` are only for audit, and by default read the condensed/on-demand list. At stage end, run `python scripts/check-output-context.py --stage <id> --strict` to check the summary output budget.

## Variables to Fill Before Running

- Input materials: replace the `<...>` placeholders with real paths, links, or content.
- Change ID: this stage is project-level, so write `N/A`.
- Loading the Skill: in an environment that supports Agent Skills, use `@requirements-analysis`, or explicitly load the Skill of the same name first.

## Execution Tool Protocol (mandatory)

- **Load this project's Skill:** Load `.claude/skills/<skill-id>/SKILL.md` according to the current Agent's real mechanism; do not treat the Skill name as ordinary text. If the repository Skill cannot be loaded, report explicitly and execute according to the Prompt.
- **Superpowers:** Use the stage-scoped mode of `using-superpowers` and `brainstorming`; first clarify goals, users, pain points, scope, and success criteria, and ask about business exceptions/boundaries item by item (weather/season, device offline, manual takeover, audit/traceability, regulatory reporting, multiple roles, historical data migration). You must use the `internet-research` method (WebSearch/WebFetch or a host-equivalent internet tool) to complete reference product and market research, writing the results into `docs/product/reference-research.md`. Write conclusions into `requirements-analysis.md` or `open-questions.md`; do not write a separate design document. The stage evidence must write `methods` (brainstorming 3/1/1, internet-research 3/2/1) and run `python scripts/check-method-evidence.py --step 02-requirements-analysis --evidence <evidence.json>`. First check whether the skills are really installed/discoverable; when unavailable, use `mode=equivalent` and write `reason` (internet research being unavailable does not count as equivalent and must be BLOCKED).
- **OpenSpec:** Only run `openspec list --specs` and read the relevant specs; this stage must not create a Change. Commands must actually run and their exit codes/results must be reported; when the CLI does not exist or fails, mark it as blocked/not executed.
- **State and gates:** `workflow-state.json` is read-only for this stage; advance it only through workflow commands. Before starting, run `python scripts/workflow.py check-entry --step 02-requirements-analysis` (non-zero = stop). `approve` and `transition` only after the user explicitly replies "review passed 02-requirements-analysis". Pause on pending approvals, missing inputs, or failed verification.
- **Output report:** List the files actually read, the Skills/CLI/scripts actually invoked, generated/modified files, check results, items not executed, and the next step. Do not auto-commit, publish, archive, or overwrite existing files unless the Prompt explicitly authorizes it and the gates have passed.

## Mandatory Deliverable Handoff

Before execution, read the `skill="requirements-analysis"` record in `process/STEP-ARTIFACT-CONTRACTS.md` and `process/STEP-ARTIFACT-CONTRACTS.json`.

- Input verification: interviews/business materials/legacy system materials; project goals, users, roles, constraints; existing docs/product/*; existing OpenSpec specs (read-only). Report item by item whether each file exists, its version, and approval status; pause if not satisfied.
- Required output: docs/product/requirements-analysis.md; docs/product/workflows.md (including the node table); docs/product/data-objects.csv; docs/product/rd-matrix.csv; docs/product/business-rules.md; docs/product/glossary.md; docs/product/acceptance-policy.md; docs/product/open-questions.md; docs/product/BASELINE-BRIEF.md; docs/product/role-permission-matrix.csv; docs/product/change-sizing.md; docs/product/decisions.md; docs/product/assumptions.md; docs/product/lessons.md; docs/product/id-conventions.md; docs/product/BASELINE-INDEX.md (generated by running scripts/gen-baseline-index.py --write). Write to the repository according to the templates; do not only show them in chat.
- Inputs for the next step: business processes and node-level roles/data objects, business data object catalog, RD matrix, business rules, glossary and acceptance policy, open questions; resident baseline brief, role permission matrix, Change slicing rules, decision/assumption register, ID conventions, and baseline index. Clearly state in the report how these files are consumed downstream (stage 03 overall project architecture design).
- When the stage completes, present the handoff report according to `templates/workflow/step-handoff-report.md`; distinguish generated, draft, proposed, pending confirmation, and not executed.
- **Stage boundary (mandatory):** Stage completion ≠ permission to enter the next stage. After the artifacts are written and checks pass, run `python scripts/workflow.py request-review --step 02-requirements-analysis --evidence workflow/evidence/02-requirements-analysis.json --summary "<review submission summary>"` (the workflow freezes into pending review), present the report according to the handoff template, and **end the turn immediately**; before the user explicitly replies "review passed 02-requirements-analysis", reading/executing the next stage's Prompt/Skill and creating next-stage artifacts are forbidden. After approval, run `python scripts/workflow.py approve --step 02-requirements-analysis --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval record>`, then run `transition`. Do not fill in approver/approved_at yourself, and do not treat artifact completion or self-check passing as approval.
- State: `workflow-state.json` is written only by workflow commands; do not edit it directly or auto-cross approval points.

## Stage-End Audit (mandatory)

- Check node completeness process by process: main processes, alternative processes, and exception processes all have NODEs; each node has role, input/output data objects, preconditions, actions, branches, and next node.
- Check RD matrix coverage node by node: each NODE has at least one RD record (or N/A + reason); DO references do not dangle.
- Run `python scripts/check-requirements.py --strict`; the exit code must be 0; write the audit conclusion into the handoff report.
