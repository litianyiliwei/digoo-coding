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

   This writes the vendored toolkit files, composes `AGENTS.md` / `AGENTS-zh.md`, `openspec/config.yaml`, `.gitignore`, scaffolds `workflow-state.json` when absent, and writes `toolkit-lock.json`.
3. Commit the installation as one commit, then start Stage 01 (`01-project-bootstrap`) as usual.
4. Optionally add the toolkit repository as a read-only remote for future upgrades:

   ```bash
   git remote add toolkit <toolkit-git-url>
   ```

## 3. Upgrade a Project

Upgrades run **inside the project repository**, never in the toolkit repository.

```bash
git fetch toolkit --tags
python scripts/toolkit-sync.py plan --ref toolkit-v2.1.0
python scripts/toolkit-sync.py apply --ref toolkit-v2.1.0
```

- `plan` is read-only: it lists added/changed/removed vendored files, local-modification conflicts, and required state migrations.
- `apply` refuses when the working tree is dirty, when `pending_approvals`/`blocked_items` exist, or when another upgrade lock is held. It backs up `workflow-state.json` to `workflow/state-backups/`, replaces only manifest-listed paths, refreshes managed blocks, regenerates `process/STAGE-IO-OVERVIEW.md` and the baseline index, runs the layout and CI checks, then updates `toolkit-lock.json`.
- Put the result on a branch named `toolkit/upgrade-vX.Y.Z`, open a PR, let CI pass (`toolkit-sync.py verify`, layout, project checks), merge, and let the team pull.

## 4. Static Analysis Gates: Dormant Until Adoption

Static analysis gates are conditional on adoption so an upgrade never breaks an in-flight project.

- No new unconditional required file is added: `scripts/check-required-files.sh --strict` does not require `docs/architecture/quality-gates.json`, and Stage 03's contract output is created only when that stage runs (or is re-run) after the upgrade.
- Every static gate is dormant until `docs/architecture/quality-gates.json` exists: the conditional entry points are `scripts/ci-check.sh`, `scripts/verify-before-completion.sh`, and `scripts/workflow.py transition` for stages 08/09. They run the quality-gate scripts only when the file is present; otherwise CI prints `SKIP_STATIC_GATES=not-adopted` and the stages behave exactly as before.
- An existing project activates the gates through the next Stage 03 baseline amendment (or an explicit Stage 03 rerun): the project selects tools per language, writes and freezes `quality-gates.json`, adds the static analysis sections to `technology-decisions.md`/`test-strategy.md`, and registers the `QUALITY-STATIC-001` constraint. From then on 07/08/09/10 produce and verify the static evidence (`design/evidence/static-analysis.json`, `design/evidence/static-analysis-independent.json`, `design/evidence/static-analysis-logs/`).
- A project that does not adopt static analysis keeps upgrading normally; the toolkit's checks remain green and no stage requires the new artifacts.
- The existing `scripts/test-upgrade-rehearsal.py` exercises init → upgrade → conflict → repair → rollback only; it adds no static-gate fixture and does not exercise the adopted path.

## 5. Conflicts and Forks

A locally modified vendored file aborts the upgrade and is listed. Choose one:

- `--take-upstream` — accept the toolkit's version (the local edit is discarded).
- `--keep-local` — keep the local content and record the path in `toolkit-lock.json` under `forks`.

Recorded forks should be upstreamed to the toolkit as soon as possible; the next upgrade that includes the upstream change can then drop the fork.

## 6. Rollback

Each upgrade is a single commit. To roll back:

1. `git revert <upgrade-commit>` (or restore the vendored paths from the previous commit).
2. Restore the state backup if a migration ran: `python scripts/workflow.py recover-state --backup workflow/state-backups/<timestamp>.json`.
3. Restore the previous `toolkit-lock.json` from the reverted commit.

## 7. Multi-Person Rules

- Upgrades are dedicated PRs by one designated maintainer; other members only pull the merged commit.
- Vendored paths are read-only for team members; CI's `toolkit-sync.py verify` fails on any hash mismatch.
- One driver per workflow stage; `workflow-state.json` is written only by `scripts/workflow.py`, and concurrent state edits are resolved by re-running workflow commands, never by hand-merging the JSON.
- `.claude/settings.local.json` stays per-machine and gitignored.

## 8. Third-Party Files

`openspec-*` Skills and `opsx` commands are generated by the OpenSpec CLI in the project repository. `toolkit-sync.py` never writes or deletes them; the lock records their presence and the CLI version at install time. Regenerate them with the OpenSpec CLI when the CLI is upgraded.

## 9. CI Expectations

The vendored `.github/workflows/toolkit-ci.yml` runs `bash scripts/ci-check.sh`, which in project mode executes toolkit package checks, the manifest check, the layout check, `toolkit-sync.py verify --require-lock`, and the project checks. A failing `verify` means a vendored file was edited by hand; run `toolkit-sync.py repair` or re-apply the release.
