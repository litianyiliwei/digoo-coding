# Target-Framework Design Code

- Target framework & extension: `<Vue 3 + Element Plus (.vue) / React (.tsx)>` (matches `docs/architecture/technology-decisions.md`)
- Transcribed from: `../ui-html/` (or Figma `get_design_context` when legacy Figma is chosen); authoritative tokens, coverage, and review live in `../figma-audit.md`.

## Replacement Register

| Source (HTML / reference) | Target (project stack) | Notes |
|---|---|---|
| `<HTML tag / class>` | `<component / CSS var>` | `<visual/layout purpose>` |

- Transcription deviations: `<none | UI-DEVIATION-001 (also logged in ../figma-audit.md)>`

> Rules: one file per PAGE (`PAGE-00N.<ext>`) preserving `data-node-id`, tokens, layout, and copy; Stage 08 adds business logic without rewriting styles/layout/copy.
