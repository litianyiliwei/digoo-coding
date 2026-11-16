# Figma Design Contract and UI Review (Single File)

- Change ID: `<change-id>`
- Figma file/page: `<real Figma link>`
- fileKey: `<fileKey>`
- File version/snapshot time: `<version number, lastModified, or export version / time>`
- Design source status: DRAFT
- UI review status: DRAFT
- Machine contract: `figma-code/` (one **target-framework-aligned** design code file per PAGE: for the Vue stack, `.vue` + that platform's component library (Web uses Element Plus, mobile uses the uni-app component library); for the React stack, `.tsx`/`.jsx`) and `figma-layout.csv` (a concise geometry/text/font assertion table)
- Asset directory: `figma-assets/` (image/SVG assets and `README.md` only; **reference screenshots are not stored**)

> This file is the only UI contract for 06 and the only interface input for 07/08/09/10.
> The real Figma review draft is the final authority for visuals/structure/components/variables; this file must record **actual values** and **per-page specifications**, not just variable names.
> The machine criteria are the numeric assertions of expected geometry/text/font in `figma-layout.csv` against the runtime DOM (`scripts/check-figma-layout.py`), plus token actual-value comparison by `scripts/check-design-tokens.py`; **screenshots are not gate evidence**. Implementation follows the target-framework design code in `figma-code/`.
> 06 exports node geometry, tokens, and real assets in one pass and transcodes according to the overall technology selection; 07/08 consume offline by default, and re-read Figma only when the file version changes or a page is ambiguous.
> When there is no UI: write `- Design source status: N/A` and `- Reason for no UI: <reason>` in "Design Source and Selection"; there is no need to fill in the Figma/token/node sections.

## Design Source and Selection

- Design source status: APPROVED
- Design source selection: Figma MCP AI automatic design (manual Figma design only when the user explicitly chooses it)

| Item | Content |
|---|---|
| Design source selection | Figma MCP AI automatic design / Manual Figma design |
| Selector/date | `<name or role / YYYY-MM-DD>` |
| PAGE list | `<PAGE-001…PAGE-00N>`, frozen in this stage; 07–10 must not add or rename |
| File version | `<Figma version/commit or lastModified>` |
| Notes | This file records token actual values, per-page specifications, and assets; undefined pages/states must be explicitly recorded as differences |

## Design Inputs and Style References

| Input | Source/path | Status |
|---|---|---|
| Requirements and AC | `openspec/changes/<change-id>/proposal.md`, `design/user-stories.md` | READ |
| Figma MCP | Real Figma link/fileKey and `get_metadata`/`get_variable_defs` records | READ |
| Design conventions | `docs/architecture/frontend-conventions.md` Section 9 and `docs/architecture/technology-decisions.md` | READ |

## Design Tokens (Actual Values)

> Read from actual Figma variables/styles; variable names cannot replace actual values. Colors must have hex; spacing/radius/font size must have units.

| Variable | Type | Actual value | CSS variable / Element Plus mapping |
|---|---|---|---|
| `color/bg` | COLOR | `#f4f7f1` | `--color-bg` |
| `color/surface` | COLOR | `#ffffff` | `--color-surface` |
| `color/brand` | COLOR | `#2f6b3f` | `--color-brand` |
| `color/text` | COLOR | `#1f2a24` | `--color-text` |
| `color/text-secondary` | COLOR | `#5f6f64` | `--color-text-secondary` |
| `color/border` | COLOR | `#dce5d7` | `--color-border` |
| `color/brand-text-light` | COLOR | `#e8f1e3` | `--color-brand-text-light` |
| `color/brand-text-muted` | COLOR | `#d8e8d4` | `--color-brand-text-muted` |
| `space/page` | NUMBER | `22px` | `--space-page` |
| `radius/card` | NUMBER | `10px` | `--radius-card` |
| `radius/control` | NUMBER | `8px` | `--radius-control` |
| `shadow/card` | EFFECT | `<actual value>` | `--shadow-card` |

## Text Styles (Actual Values)

| Style | Font family | Weight | Font size | Line height | Letter spacing |
|---|---|---|---|---|---|
| `Type/12 Regular` | Noto Sans SC | 400 | 12px | 100% | 0 |
| `Type/13 Regular` | Noto Sans SC | 400 | 13px | 100% | 0 |
| `Type/14 Regular` | Noto Sans SC | 400 | 14px | 100% | 0 |
| `Type/14 Medium` | Noto Sans SC | 500 | 14px | 100% | 0 |
| `Type/18 Regular` | Noto Sans SC | 400 | 18px | 100% | 0 |
| `Type/24 Bold` | Noto Sans SC | 700 | 24px | 100% | 0 |
| `Type/44 Bold` | Noto Sans SC | 700 | 44px | 100% | 0 |

## PAGEs and Nodes

| PAGE ID | Figma node | Frame size | State |
|---|---|---|---|
| PAGE-001 Login | `3:2` | 1440×900 | default |
| PAGE-002 User Management | `5:2` | 1440×900 | default |
| PAGE-003 Roles and Permissions | `7:2` | 1440×900 | default |
| PAGE-004 Audit Log | `8:2` | 1440×900 | default |
| PAGE-005 Notification Center | `9:2` | 1440×900 | default |
| PAGE-006 System Configuration | `11:2` | 1440×900 | default |

## PAGE Key Specifications

> Each page must have block-level actual values (position/size/layout/padding/gap/border/radius/font/fill), not just "top bar, sidebar, list".
> Element-level text/spacing/font size/hierarchy reference `figma-code/`; `figma-layout.csv` is the runtime assertion subset; this table is a block summary, not the only geometry source.
> The full `get_design_context` snapshot may be appended after this page's specifications; do not create separate scattered files.

### PAGE-001 Login

| Block | Figma node | Position/size | Layout/spacing | Fill/border/radius | Font/text |
|---|---|---|---|---|---|
| Brand area | `3:3` | x=0,y=0,w=600,h=900 | vertical gap 22, padding 22 | fill `color/brand` | `Type/44 Bold`, `Type/18 Regular`, `Type/14 Regular` |
| Form area | `3:7` | x=600,y=0,w=840,h=900 | centered, padding 64 | fill `color/bg` | — |
| Form card | `3:8` | x=210,y=265,w=420,h=370 | vertical gap 18, padding 18 | `color/surface`, 1px `color/border`, radius 10 | `Type/24 Bold`, `Type/13 Regular` |
| Account input | `3:12` | x=19,y=132,w=382,h=40 | horizontally centered, left/right padding 12 | `color/surface`, 1px `color/border`, radius 8 | `Type/13 Regular` |
| Password input | `<node>` | `<x,y,w,h>` | `<layout>` | `<fill/border/radius>` | `<font>` |
| Login button | `3:17` | x=19,y=280,w=66,h=39 | padding 18/10 | `color/brand`, radius 8 | `Type/14 Medium` |
| Bottom note | `<node>` | `<x,y,w,h>` | `<layout>` | `<fill>` | `<font/text>` |

<!-- Add the remaining PAGEs in the same table format; use figma-code/ as the authority for text/structure in the design code; the assertion scope is described in ## Assertion Scope. -->

## Design Code

- Target framework: `<Vue 3 + TypeScript + Element Plus / React + ...>` (must be consistent with `docs/architecture/technology-decisions.md`)
- Design code extension: `<.vue / .tsx / .jsx>`
- Selection basis: `<ADR-002 / technology-decisions version and approval date>`
- Transcoding method: record of loading the official `figma-design-to-code` Skill; replacement table from the `get_design_context` reference implementation to target-framework components/styles/tokens; static high-fidelity pages only, no business API integration.
- `figma-code/README.md`: explains the source, target framework/extension, component and style/token replacements, transcoding deviations, and the correspondence between `data-node-id` and `figma-layout.csv`.
- `figma-code/PAGE-001.vue … PAGE-00N.vue` (`.tsx`/`.jsx` for the React stack): one target-framework design code file per PAGE, containing real copy, font size/weight, spacing, radius, hierarchy, and `data-node-id`. 08 ports these directly as page skeletons, adding only routing/API/state/permissions/business logic, and must not rewrite styles, layout, or copy.
- `figma-layout.csv`: concise assertion table, columns include `page_id,route,element_id,figma_node_id,x,y,width,height,dom_selector,assert_geometry,assert_text,tolerance_px,text_content,font_size,font_weight,notes`; coordinates are relative to the top-left corner of the PAGE frame. 06 establishes the assertion subset (`route`/`dom_selector` may temporarily be `PENDING`), 07 must fill them in.
- Gates: `python scripts/check-figma-audit.py --change <change-id> --strict --require-framework` validates the target framework, the existence of design code for each PAGE, and the completeness of assertion-table geometry/text/selectors; 08/09 run `python scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900`, comparing expected `x/y/w/h`, text, and fonts element by element; `python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>` precisely compares token actual values.
- **UI verification relies primarily on machine evidence**: PAGES with no differences use the numeric values in `figma-layout-check.json` directly in 08/09/10; only PAGES with differences/`UI-DERIVED` require manual review and approval. Reference screenshots or pixel screenshots are not stored.

## Assertion Scope

> `figma-layout.csv` is the only subset of runtime assertions; elements not included in assertions are covered by the design code and manual acceptance. If there is a structural difference (present in Figma but absent in implementation, or different layout), it must be registered in `## Differences and Pending Confirmation` and wait for approval from the design owner.
> Each PAGE must have at least 1 assertion row; it is recommended to cover key blocks such as the top bar/sidebar/main area/title/primary action/table card.

| PAGE | Assertion coverage | Not asserted/notes |
|---|---|---|
| PAGE-001 | Brand area, brand title, form card, form title, account input, button, bottom note | Subtitle/labels, etc. are covered by the design code and manual acceptance |
| PAGE-00N | `<...>` | `<...>` |

## State Coverage

> Each PAGE must list the applicable states; states that "have no Figma frame" must document the 07 design decision, approver, and reference basis, and must not claim they have been reproduced.
> Non-default states do not require screenshots; 08 covers visible elements and state differences via the assertion mapping, 09 verifies independently, and 10 batch-signs off PAGES with no differences based on machine evidence and performs side-by-side verification for PAGES with differences/`UI-DERIVED`.

| PAGE ID | State | Figma has frame | Notes/decision |
|---|---|---|---|
| PAGE-001 | default | Yes | — |
| PAGE-001 | loading | No | 07 design decision: `<button loading style/basis>`; approver `<...>` |
| PAGE-001 | error | No | 07 design decision: `<error message style/basis>`; approver `<...>` |
| PAGE-002 | default/empty/no-permission | Yes/No/No | Explain each individually |
| … | … | … | … |

## Asset List

> Only register real image/SVG assets (logo, icons, illustrations, etc.), downloaded to `figma-assets/`; Figma temporary URLs must not be kept.
> **Reference screenshots must not be registered** (`PAGE-*.default.png`, etc.); visual comparison uses `figma-code/` / `figma-layout.csv`.
> When there are assets, also write `figma-assets/README.md` (file name, source node, sha256, size); when there are no assets, delete the table above and write `- Assets: none`.

| Asset | Source node | File | Size | Purpose |
|---|---|---|---|---|
| `<logo>` | `<node>` | `figma-assets/asset-logo.svg` | `<w×h>` | `<...>` |

## MCP Read Records

| Tool/command | Target file/node | Actual return | Time | Status |
|---|---|---|---|---|
| `get_variable_defs` | `<fileKey>` | number of token actual values | `<time>` | Success |
| `get_metadata` | 6 PAGEs | page structure and x/y/w/h in the design code | `<time>` | Success |
| `get_design_context` | `3:2`…`11:2` (as needed) | per-page specifications/styles/assets | `<time>` | Success |

## Differences and Pending Confirmation

| Difference ID | Requirement/AC requirement | Actual Figma status | Impact | Choice/reason | Approver/status |
|---|---|---|---|---|---|
| UI-DIFF-001 | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |

## UI Review

- UI review status: DRAFT (changed to APPROVED after the design owner reviews on the real Figma review draft)
- Reviewer: `<name or role>`
- Review date: `<YYYY-MM-DD>`
- Review evidence: `workflow/evidence/06-figma-ui-review.md`
- Review scope: PAGE coverage, key blocks, state variants, permission/navigation behavior, token actual values, target framework/page structure and copy of `figma-code/`, assertion scope of `figma-layout.csv`

> Fields that cannot be read must be registered as "not checked"; MCP results must not be fabricated; when Figma MCP is unavailable, block stage 06 rather than substitute screenshots or invented text.
> Manual UI review is completed on the real Figma file; automated visual regression uses numeric assertions of node geometry against the runtime DOM, not screenshots.
