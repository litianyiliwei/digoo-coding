# Toolkit Changelog

> Language: English (main) | 简体中文

> Release notes for the workflow toolkit. Projects pin a version through `toolkit-lock.json` and upgrade deliberately with `scripts/toolkit-sync.py`.

## 2.1.0 — 2026-11-19 — Tiered static analysis gates and risk-based approvals

- **Static analysis gates (conditional).** `docs/architecture/quality-gates.json` records the adopted stacks, per-tool `blocking`/`advisory` mode, config paths, blocking severities and waiver policy; `scripts/check-quality-gates.py` validates the selection, `scripts/run-quality-gates.py` runs the blocking tools and captures per-tool logs, and `scripts/check-static-analysis.py` verifies builder and independent-verifier evidence (`design/evidence/static-analysis.json`, `static-analysis-independent.json`, `static-analysis-logs/`) including config/gates hashes, source revision and waiver validity.
- **Dormant until adoption.** No new unconditional required file. `ci-check.sh`, `verify-before-completion.sh` and `workflow.py transition` for 08/09 run the static gates only when `quality-gates.json` exists and otherwise print `SKIP_STATIC_GATES=not-adopted`; an existing project activates them through the next Stage 03 baseline amendment, and no workflow-state migration is required (`state_schema` 1.0).
- **Language kits and constraint.** Static analysis templates for Go, Java, Python, Shell, SQL and TypeScript under `templates/static-analysis/`, plus the `quality-gates.json` baseline template, `static-waivers.example.json`, static-analysis sections in `technology-decisions.md`/`test-strategy.md`, `## Static analysis` sections in code review and acceptance evidence, and the `QUALITY-STATIC-001` constraint.
- **Risk-based approvals.** `process/WORKFLOW-STAGES.json` gains `risk_level`; under the `risk-based` approval policy, low-risk stages (01, 04, 06) may run `request-review` for the audit packet and then transition without a recorded approval (`STATUS=RISK_BASED_FAST_TRACK`), while high-risk stages keep explicit human approval.
- **Question coverage relaxed.** The 02/03/05/07 checklist moves from DRAFT item-by-item enforcement to RECOMMENDED guidance: the contract policy no longer lists per-stage `required_items`, and the `question_coverage` evidence block is optional and only shape-checked when present.
- **Independent verification.** Adds `independent-verification.schema.json` and the corresponding report template; the verifier independently re-runs adopted static gates (`run-quality-gates.py --independent`) with an identity distinct from the builder, and `check-independent-verification.py` validates the evidence.
- **Checks and cleanup.** `ci-check.sh` now bundles the package self-check, script regressions, manifest check and auto-mode layout check (the explicit `check-layout.py --mode toolkit` run stays mandatory); removed the superseded `check-inventory.py`, `check-baseline-governance.py` and `scripts/legacy/` Figma helper; the manifest is regenerated for the full vendored set.

## 2.0.0 — 2026-11-18 — Two-repository separation

- **Repository model.** The toolkit lives in its own repository; each business project lives in a separate repository and vendors this toolkit at fixed paths (`prompts/`, `templates/`, `scripts/`, `process/`, `.claude/skills/<stage>/`, `.claude/hooks/`, `.claude/settings.json`, `.github/workflows/toolkit-ci.yml`).
- **Process documentation.** All toolkit process specifications moved from `docs/` to `process/`; project repositories keep `docs/` for project outputs only.
- **Templates.** Every output template lives under `templates/`; the template matrix no longer registers production paths as templates.
- **Composed files.** `AGENTS.md`, `openspec/config.yaml`, and `.gitignore` use toolkit-managed blocks maintained by `scripts/toolkit-sync.py`; project content stays outside the markers.
- **Upgrade tooling.** `toolkit-sync.py init/verify/plan/apply/repair` installs and upgrades a project repository from a tagged release; `gen-manifest.py` maintains `process/TOOLKIT-MANIFEST.json`; `check-layout.py` enforces ownership in both modes.
- **Migration.** Projects created from this release must run `toolkit-sync.py init`; no workflow-state schema migration is required (`state_schema` 1.0).
