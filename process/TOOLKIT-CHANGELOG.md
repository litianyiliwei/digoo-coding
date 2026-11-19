# Toolkit Changelog

> Language: English (main) | 简体中文

> Release notes for the workflow toolkit. Projects pin a version through `toolkit-lock.json` and upgrade deliberately with `scripts/toolkit-sync.py`.

## 2.0.0 — 2026-11-18 — Two-repository separation

- **Repository model.** The toolkit lives in its own repository; each business project lives in a separate repository and vendors this toolkit at fixed paths (`prompts/`, `templates/`, `scripts/`, `process/`, `.claude/skills/<stage>/`, `.claude/hooks/`, `.claude/settings.json`, `.github/workflows/toolkit-ci.yml`).
- **Process documentation.** All toolkit process specifications moved from `docs/` to `process/`; project repositories keep `docs/` for project outputs only.
- **Templates.** Every output template lives under `templates/`; the template matrix no longer registers production paths as templates.
- **Composed files.** `AGENTS.md`, `openspec/config.yaml`, and `.gitignore` use toolkit-managed blocks maintained by `scripts/toolkit-sync.py`; project content stays outside the markers.
- **Upgrade tooling.** `toolkit-sync.py init/verify/plan/apply/repair` installs and upgrades a project repository from a tagged release; `gen-manifest.py` maintains `process/TOOLKIT-MANIFEST.json`; `check-layout.py` enforces ownership in both modes.
- **Migration.** Projects created from this release must run `toolkit-sync.py init`; no workflow-state schema migration is required (`state_schema` 1.0).
