# Toolkit Adoption and Upgrade Guide

> Language: English (main) | [简体中文](TOOLKIT-UPGRADE-zh.md)

> Applies to a **business project repository** that vendors this toolkit. The toolkit repository itself follows `AGENTS.md`.

## 1. Repository Roles

- **Toolkit repository** — this repository: Skills, Prompts, templates, scripts, process specifications and release tags. Maintainers update it freely; projects are unaffected until they upgrade.
- **Project repository** — one per business project: baselines (`docs/`), OpenSpec Changes, design evidence, workflow state, business code, and a vendored copy of the toolkit. The team works here daily.

The project repository never merges the toolkit's git history. `toolkit-lock.json` records exactly which toolkit release is installed.

## 2. Create a Project Repository

1. Create an empty repository (for example on GitHub) and clone it locally.
2. Install the toolkit from a tagged release:

   ```bash
   python <path-to-toolkit>/scripts/toolkit-sync.py init --from <toolkit-git-url-or-local-path> --ref toolkit-v2.0.0 --project .
   ```

   This writes the vendored toolkit files, composes `AGENTS.md` / `AGENTS-zh.md`, `openspec/config.yaml`, `.gitignore`, scaffolds `workflow-state.json` when absent, and writes `toolkit-lock.json`. After installation, declare project-owned paths as described under Project-Owned Paths below.
3. Commit the installation as one commit, then start Stage 01 (`01-project-bootstrap`) as usual.
4. Optionally add the toolkit repository as a read-only remote for future upgrades:

   ```bash
   git remote add toolkit <toolkit-git-url>
   ```

### Project-Owned Paths

After installation, declare any project-specific top-level paths in `project-extensions.json` at the repository root and commit it with the project content:

```json
{
  "root": ["backend", "frontend", "infra", ".vscode"],
  "paths": ["docs/api"]
}
```

- `root` lists additional top-level directories or files owned by the project (service roots, monorepo packages, editor configuration).
- `paths` lists paths under `docs/`; the first child after `docs` becomes allowed (for example `docs/api` allows the `docs/api/` directory).
- The project-mode layout check accepts the vendored toolkit paths, the built-in project-root entries, and these declarations. An undeclared entry fails with a message that includes the exact declaration to add.
- Git-ignored local artifacts do not need to be declared: the check evaluates the repository's tracked content and skips untracked paths that Git ignores (`node_modules/`, `.venv/`, `dist/`). Outside a Git work tree it falls back to scanning the working tree.

## 3. Upgrade a Project

Upgrades run **inside the project repository**, never in the toolkit repository.

```bash
git fetch toolkit --tags
python scripts/toolkit-sync.py plan --ref toolkit-v2.1.0
python scripts/toolkit-sync.py apply --ref toolkit-v2.1.0
```

- `plan` is read-only: it lists added/changed/removed vendored files, local-modification conflicts, and required state migrations.
- `apply` refuses when the working tree is dirty, when `pending_approvals`/`blocked_items` exist, or when another upgrade lock is held. Before writing anything it runs the target release's project layout rules against the current repository; a failure aborts with exit code 2 and leaves the working tree untouched (fix the declarations described under Project-Owned Paths). It then backs up `workflow-state.json` to `workflow/state-backups/`, replaces only manifest-listed paths, refreshes managed blocks, regenerates `process/STAGE-IO-OVERVIEW.md` and the baseline index, runs the layout and CI checks with the installed release, then updates `toolkit-lock.json`.
- Put the result on a branch named `toolkit/upgrade-vX.Y.Z`, open a PR, let CI pass (`toolkit-sync.py verify`, layout, project checks), merge, and let the team pull.

### v2 Workflow State Upgrade (Multi-Change Lanes)

Toolkits that ship the v2 multi-lane state require a one-time state conversion in each project:

```bash
python scripts/workflow.py upgrade-state --reason "adopt multi-lane workflow"
```

- The command is idempotent, backs up the v1 state to `workflow/evidence/state-v2-backup-<timestamp>.json`, moves project stages 01–04 into the `project` lane, and moves the active Change's 05–10 into `changes[<change-id>]`.
- Until it runs, `start-change`, `list-changes` and the v2 lane resolution return `UPGRADE_REQUIRED`; existing v1 commands keep working unchanged.
- After the conversion, start proposals with `start-change --change-id <id>` (the roadmap dependency gate applies), inspect lanes with `list-changes`, and pass `--change-id` for 05–10. `next-change` remains a compatibility alias. Evidence and handoffs written after the conversion use `workflow/evidence/<change-id>/` and `workflow/handoffs/<change-id>/`; old flat evidence stays on disk for audit.

## 4. Static Analysis Gates: Dormant Until Adoption

Static analysis gates are conditional on adoption so an upgrade never breaks an in-flight project.

- No new unconditional required file is added: `scripts/check-required-files.sh --strict` does not require `docs/architecture/quality-gates.json`, and Stage 03's contract output is created only when that stage runs (or is re-run) after the upgrade.
- Every static gate is dormant until `docs/architecture/quality-gates.json` exists: the conditional entry points are `scripts/ci-check.sh`, `scripts/verify-before-completion.sh`, and `scripts/workflow.py transition` for stages 08/09. They run the quality-gate scripts only when the file is present; otherwise CI prints `SKIP_STATIC_GATES=not-adopted` and the stages behave exactly as before.
- An existing project activates the gates through the next Stage 03 baseline amendment (or an explicit Stage 03 rerun): the project selects tools per language, writes and freezes `quality-gates.json`, adds the static analysis sections to `technology-decisions.md`/`test-strategy.md`, and registers the `QUALITY-STATIC-001` constraint. From then on 07/08/09/10 produce and verify the static evidence (`design/evidence/static-analysis.json`, `design/evidence/static-analysis-independent.json`, `design/evidence/static-analysis-logs/`).
- A project that does not adopt static analysis keeps upgrading normally; the toolkit's checks remain green and no stage requires the new artifacts.
- The existing `scripts/test-upgrade-rehearsal.py` exercises init → upgrade → conflict → repair → rollback only; it adds no static-gate fixture and does not exercise the adopted path.

## 5. Module Packages: Default for New Projects

The module model is strategy-driven by `docs/architecture/code-layout.json`; the new-project default is `module-packages`.

- **New projects**: Stage 03 records `code-layout.json` with `strategy: module-packages`, roots, `package_pattern`, `integration_paths`, `frozen_paths`, `module_card` and `dependency_rules`; Stage 04 creates `docs/product/capabilities.csv` and `docs/product/modules.csv` and the module-aware roadmap columns. From then on, the 07 `### Implementation Slice` and 08 footprint checks are hard transition gates.
- **Existing projects** choose per project after upgrade:
  - `none`: leave `code-layout.json` absent (or set `strategy: none`); the slice/footprint gates print `FOOTPRINT_GATE=SKIPPED (strategy none)` and the registry rules are skipped. Nothing new is required.
  - `footprint`: add `code-layout.json` with `strategy: footprint`, roots/package pattern and integration/frozen paths; roadmap rows need `Code Target`; registries and module cards are not required.
  - `module-packages`: additionally add `capabilities.csv`/`modules.csv` (at Stage 04, or by an explicit Stage 04 rerun), the module-aware roadmap columns, and module cards under `<module_path>/MODULE.md`.
- **Adopting the layout and registries**: adopt through the next Stage 03 baseline amendment or an explicit Stage 03 rerun; the layout is frozen with the architecture baseline. `capabilities.csv` and `modules.csv` are mutable product-level registries, not frozen baseline files: Stage 05 updates them and Stage 10 writes them back. They are deliberately not listed in `baseline-manifest.json` and do not need a baseline amendment to change.
- An upgrade never fails because the module files are missing: all module gates are conditional on `code-layout.json` existing and declaring a valid strategy; an invalid layout fails closed rather than silently skipping.

## 6. HTML-first UI Design (Unreleased)

- **No workflow-state migration.** The stage id `06-figma-design-review` and skill name are unchanged; existing `workflow-state.json` files keep working.
- **New Changes:** stage 05 must declare `Target Platforms` in `proposal.md` and `- Target platforms:` in `design/user-stories.md` (canonical `web|h5|mini-program|app|android|ios|harmonyos|desktop|pda`), and stage 06 produces `design/ui-html/` by default with explicit HTML provenance (user-provided HTML, AI-authored from requirements, or Figma-to-HTML conversion). Run `bash scripts/new-change-assets.sh <change-id>` to create the new `ui-html` templates and the updated `figma-audit.md`/`figma-layout.csv`.
- **Existing project artifacts:** add `## 10. Target Platforms and Client Forms` to `docs/product/requirements-analysis.md` and the `Target Platforms` column to the roadmap before the next Stage 04/05 gate. In-flight Changes must add the platform declarations and revised UI contract before their next stage gate; completed Changes are not rewritten.
- **Legacy UI Changes:** `check-figma-audit.py` still accepts a direct Figma source, and without `--require-framework` an older Change can pass its existing contract. New Changes should use the HTML-first contract and run with `--require-framework`.
- **Implementation evidence:** UI acceptance/code-review/verification tables now accept either an HTML `data-node-id` or a Figma node id as the design source reference; `check-figma-layout.py` reads each PAGE's viewport from `figma-layout.csv` and falls back to `--viewport` for older tables.

## 7. Conflicts and Forks

A locally modified vendored file aborts the upgrade and is listed. Choose one:

- `--take-upstream` — accept the toolkit's version (the local edit is discarded).
- `--keep-local` — keep the local content and record the path in `toolkit-lock.json` under `forks`.

Recorded forks should be upstreamed to the toolkit as soon as possible; the next upgrade that includes the upstream change can then drop the fork.

## 8. Rollback

Each upgrade is a single commit. To roll back:

1. `git revert <upgrade-commit>` (or restore the vendored paths from the previous commit).
2. Restore the state backup if a migration ran: `python scripts/workflow.py recover-state --backup workflow/state-backups/<timestamp>.json`.
3. Restore the previous `toolkit-lock.json` from the reverted commit.

## 9. Multi-Person Rules

- Upgrades are dedicated PRs by one designated maintainer; other members only pull the merged commit.
- Vendored paths are read-only for team members; CI's `toolkit-sync.py verify` fails on any hash mismatch.
- One driver per workflow stage; `workflow-state.json` is written only by `scripts/workflow.py`, and concurrent state edits are resolved by re-running workflow commands, never by hand-merging the JSON.
- `.claude/settings.local.json` stays per-machine and gitignored.

## 10. Third-Party Files

`openspec-*` Skills and `opsx` commands are generated by the OpenSpec CLI in the project repository. `toolkit-sync.py` never writes or deletes them; the lock records their presence and the CLI version at install time. Regenerate them with the OpenSpec CLI when the CLI is upgraded.

## 11. CI Expectations

The vendored `.github/workflows/toolkit-ci.yml` runs `bash scripts/ci-check.sh`, which in project mode executes toolkit package checks, the manifest check, the layout check, `toolkit-sync.py verify --require-lock`, and the project checks. The layout check evaluates Git-tracked repository content and skips untracked paths that Git ignores, so dependency and build directories present locally (or installed before the check in CI) do not fail it. A failing `verify` means a vendored file was edited by hand; run `toolkit-sync.py repair` or re-apply the release.
