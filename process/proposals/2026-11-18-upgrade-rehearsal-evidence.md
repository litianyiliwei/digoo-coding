# Upgrade Rehearsal Evidence — 2026-11-18

> Status: EVIDENCE
> Scope: `scripts/test-upgrade-rehearsal.py` (automated end-to-end rehearsal in a temporary directory)
> Toolkit version under rehearsal: 2.0.0 → 2.1.0 → rollback 2.0.0

## Command

```bash
python scripts/test-upgrade-rehearsal.py
```

## Scenario and assertions

1. **init** — a fixture toolkit release (v2.0.0) is installed into an empty project via `toolkit-sync.init`; the project receives vendored files, composed `AGENTS.md`/`AGENTS-zh.md`/`openspec/config.yaml`/`.gitignore`, a default `workflow-state.json`, and `toolkit-lock.json`. No project output directories are created.
2. **plan** — a v2.1.0 source changes `prompts/01.md`, adds `prompts/02.md`, removes `scripts/a.py`; `plan` reports exactly these as changed/added/removed.
3. **apply** — `apply` returns 0; files are updated/added/removed; the project-owned `docs/product/baseline.md` is byte-identical afterwards; `toolkit-lock.json` reports version 2.1.0; the stub `stage-io-report.py` regenerates `process/STAGE-IO-OVERVIEW.md`; stub layout/CI checks pass.
4. **conflict** — a local edit to `prompts/02.md` (a vendored file) makes the next `apply` abort with exit 2 and leaves the local content untouched.
5. **repair** — after corrupting `workflow-state.json`, `repair` recomposes managed blocks, regenerates derived files and restores `workflow-state.json` from `workflow/state-backups/`; `current_step` is `01-project-bootstrap` again.
6. **rollback** — re-applying v2.0.0 with `--take-upstream` downgrades the lock and restores v1 file contents.

## Result

`REHEARSAL_PASSED` (exit 0). Transcript lines observed:

```
STEP init: v2.0.0 installed
STEP plan: added/changed/removed reported
STEP apply: upgraded, outputs untouched, derived file regenerated
STEP conflict: locally modified vendored file aborted the upgrade
STEP repair: managed blocks recomposed, workflow state restored from backup
STEP rollback: downgraded to 2.0.0 with --take-upstream
REHEARSAL_PASSED
```

## Notes

- The rehearsal runs entirely in a temporary directory; it does not touch this repository.
- After the fresh-review fix pass, the rehearsal's CI step is a faithful non-stub subset: it runs the project-mode `gen-manifest` skip and the real vendored `toolkit-sync.py verify --require-lock` inside `apply` (the layout check remains a stub, and the fixture vendors the real `toolkit-sync.py`). This exercises the two integration failures found in review (Critical 1 and Critical 2).
- Derived-file regeneration runs through a stub `stage-io-report.py`, so failures in the apply pipeline's subprocess invocation, working directory, or failure detection still fail the rehearsal.
