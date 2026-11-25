# Target-Framework Design Code

- Source: `design/ui-html/` HTML design documents (one PAGE per platform), rendered and measured in stage 06; the HTML pages are the visual authority regardless of whether they were user-provided, AI-authored, or converted from Figma (Figma-to-HTML).
- Source (optional): Figma MCP `get_design_context` (the official `figma-design-to-code` Skill must be loaded before calling) when the user explicitly selects the Figma source.
- One file per PAGE (`PAGE-001.vue` … `PAGE-00N.vue`; `.tsx`/`.jsx` for the React stack).
- Target framework: `<Vue 3 + TypeScript + Element Plus / React + ...>`, must be consistent with `docs/architecture/technology-decisions.md`.
- Extension: `<.vue / .tsx / .jsx>`; when the technology selection changes, retranscode according to the new selection and do not mix frameworks.
- Transcription method: HTML markup/styles → project component library and tokens; real copy, font size/weight, spacing, radius, hierarchy, `data-node-id`, and platform-specific viewport assumptions are preserved; static high-fidelity pages only, no business API integration. For the Figma source, replace the `get_design_context` reference implementation (usually React + Tailwind) instead.
- Replacement register:

| Source (HTML markup / reference implementation) | Target (project stack) | Notes |
|---|---|---|
| `<HTML tag / Tailwind class>` | `<Element Plus / uni-app component / CSS variable>` | `<geometry or visual purpose>` |
| `<HTML script / stateless interaction>` | `<Vue composable / component event>` | `<behavior and state>` |

- Transcription deviations: `<none / difference ID + reason + approver>`; structural differences are also registered in `## Differences and Pending Confirmation` of `figma-audit.md`.
- `data-node-id="..."` corresponds one-to-one with `figma_node_id` in `figma-layout.csv` (in HTML mode the column stores the HTML `data-node-id`; in Figma mode the real node id); `figma-layout.csv` is the subset of runtime geometry assertions, and `figma-audit.md` is the token/state/review summary.
- The text, font size, weight, spacing, radius, and hierarchy in the code are the actual design values; they must not be rewritten from memory during implementation.
- Temporary asset URLs in the code must be downloaded to `figma-assets/` and replaced; they must not be used as runtime resources.
- 08 ports the code in this directory directly as page skeletons, adding only routing, API, state, permissions, and business logic; styles, layout, or copy must not be rewritten. If a visual deviation is truly necessary, it must be approved as `UI-DEVIATION`.
- 06 generates and persists everything in one pass; 07/08 consume offline by default, and re-read the source page by page only when the HTML/Figma source changes or a page is ambiguous.
- **UI verification relies primarily on machine evidence**: PAGES with no differences are subsequently signed off according to the numeric values in `figma-layout-check.json`; only PAGES with differences/`UI-DERIVED` are manually reviewed. Screenshots are not stored.
