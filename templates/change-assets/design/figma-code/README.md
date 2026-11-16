# Figma Target-Framework Design Code

- Source: Figma MCP `get_design_context` (the official `figma-design-to-code` Skill was loaded before calling), one file per PAGE (`PAGE-001.vue` … `PAGE-00N.vue`; `.tsx`/`.jsx` for the React stack).
- Target framework: `<Vue 3 + TypeScript + Element Plus / React + ...>`, must be consistent with `docs/architecture/technology-decisions.md`.
- Extension: `<.vue / .tsx / .jsx>`; when the technology selection changes, retranscode according to the new selection and do not mix frameworks.
- Transcoding method: the reference implementation returned by `get_design_context` (usually React + Tailwind) has been replaced with the project component library and tokens according to the target framework; real copy, font size/weight, spacing, radius, hierarchy, and `data-node-id` are preserved; static high-fidelity pages only, no business API integration.
- Replacement register:

| Source (reference implementation) | Target (project stack) | Notes |
|---|---|---|
| `<Tailwind class / original tag>` | `<Element Plus component / CSS variable>` | `<geometry or visual purpose>` |
| `<React component>` | `<Vue component / composable>` | `<behavior and state>` |

- Transcoding deviations: `<none / difference ID + reason + approver>`; structural differences are also registered in `## Differences and Pending Confirmation` of `figma-audit.md`.
- `data-node-id="..."` corresponds one-to-one with `figma_node_id` in `figma-layout.csv`; `figma-layout.csv` is the subset of runtime geometry assertions, and `figma-audit.md` is the token/state/review summary.
- The text, font size, weight, spacing, radius, and hierarchy in the code are the actual Figma values; they must not be rewritten from memory during implementation.
- Temporary Figma asset URLs in the code (`https://www.figma.com/api/mcp/asset/...`) must be downloaded to `figma-assets/` and replaced; they must not be used as runtime resources.
- 08 ports the code in this directory directly as page skeletons, adding only routing, API, state, permissions, and business logic; styles, layout, or copy must not be rewritten. If a visual deviation is truly necessary, it must be approved as `UI-DEVIATION`.
- 06 generates and persists everything in one pass; 07/08 consume offline by default, and re-read page by page (serially, to avoid rate limiting) only when the Figma file version changes or a page is ambiguous.
- **UI verification relies primarily on machine evidence**: PAGES with no differences are subsequently signed off according to the numeric values in `figma-layout-check.json`; only PAGES with differences/`UI-DERIVED` are manually reviewed. Screenshots are not stored.
