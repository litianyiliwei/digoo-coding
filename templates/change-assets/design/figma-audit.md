# UI Design Contract and UI Review (Single File, HTML-first)

- Change ID: `<change-id>`
- Design source: `Design-to-HTML`
- HTML provenance: `AI-authored from requirements`
- HTML provenance options: `User-provided HTML` (stakeholder directly supplied the HTML) or `Figma-to-HTML (AI conversion)` (AI read an approved Figma file and converted it)
- Figma input (only for Figma-to-HTML): `<real Figma link / fileKey / node ids>` or `N/A`
- Target platforms: `<web; app; android>` (must equal `- Target platforms:` in `design/user-stories.md` and `## Target Platforms` in `proposal.md`)
- Review entry: `design/ui-html/index.html` (the HTML review deliverable, including Figma-to-HTML pages; a real Figma link is recorded as the upstream input for Figma-to-HTML, or for the legacy direct Figma source)
- Machine contract: `figma-code/` (one **target-framework-aligned** design code file per PAGE: for the Vue stack, `.vue` + that platform's component library (Web uses Element Plus, mobile uses the uni-app component library); for the React stack, `.tsx`/`.jsx`) and `figma-layout.csv` (a concise geometry/text/font assertion table)
- Asset directory: `figma-assets/` (image/SVG assets and `README.md` only; **reference screenshots are not stored**)

> This file is the only UI contract for 06 and the only interface input for 07/08/09/10. The file names `figma-audit.md`, `figma-code/`, `figma-layout.csv` are historical; both design sources share the same contract shape.
> **HTML-first**: stage 06 produces self-contained, high-fidelity HTML design documents under `design/ui-html/` (one file per PAGE, grouped by platform, with a browsable `index.html`). The HTML review entry is the review deliverable; tokens, PAGE specifications, design code and the assertion table are derived from the rendered HTML. HTML provenance is explicit: user-provided HTML, AI-authored from requirements, or Figma-to-HTML conversion; Figma is the upstream input for the Figma-to-HTML path.
> The machine criteria are the numeric assertions of expected geometry/text/font in `figma-layout.csv` against the runtime DOM (`scripts/check-figma-layout.py`), plus token actual-value comparison by `scripts/check-design-tokens.py`; **screenshots are not gate evidence**. Implementation follows the target-framework design code in `figma-code/`.
> 06 exports the design once and transcodes according to the overall technology selection; 07/08 consume offline by default, and re-read the source only when it changes or a page is ambiguous.
> When there is no UI: write `- Design source status: N/A` and `- Reason for no UI: <reason>` in "Design Source and Selection"; there is no need to fill in the token/node sections.

## Design Source and Selection

- Design source status: PENDING (replace with APPROVED only after the design review; use N/A + a reason for a no-UI Change)
- Design source: `Design-to-HTML`
- HTML provenance: `AI-authored from requirements`
- Source selected/supplied by, date: `<name or role / YYYY-MM-DD>`
- Target platforms: `<web; app; android>` (semicolon-separated canonical values)

| Item | Content |
|---|---|
| Design source | Design-to-HTML |
| HTML provenance | `<selected: User-provided HTML / AI-authored from requirements / Figma-to-HTML (AI conversion)>` |
| Selector/date | `<name or role / YYYY-MM-DD>` |
| PAGE list | `<PAGE-001…PAGE-00N>`, frozen in this stage; 07–10 must not add or rename |
| Platform coverage | `<web: PAGE-001…; app: PAGE-0NN…; android: PAGE-0NN…>`; at least one PAGE per declared platform |
| Source version | `<HTML snapshot commit/time; for Figma-to-HTML, the Figma version/lastModified>` |
| Notes | This file records token actual values, per-page specifications, platform coverage and assets; undefined pages/states must be explicitly recorded as differences |

## Design Inputs and Style References

| Input | Source/path | Status |
|---|---|---|
| Requirements and AC | `openspec/changes/<change-id>/proposal.md`, `design/user-stories.md` | READ |
| HTML design docs | `design/ui-html/index.html`, `design/ui-html/<platform>/PAGE-00N.html` | READ |
| Figma MCP (optional) | Real Figma link/fileKey and `get_metadata`/`get_variable_defs` records when provenance is Figma-to-HTML or the legacy direct Figma source | READ / N/A |
| Design conventions | `docs/architecture/frontend-conventions.md` (Visual Conventions section) and `docs/architecture/technology-decisions.md` | READ |

## Design Tokens (Actual Values)

> Read from the HTML design documents' CSS custom properties (or actual Figma variables when provenance is Figma-to-HTML/legacy direct Figma); variable names cannot replace actual values. Colors must have hex; spacing/radius/font size must have units.

| Variable | Type | Actual value | CSS variable / component-library mapping |
|---|---|---|---|
| `color/bg` | COLOR | `#f4f7f1` | `--color-bg` |
| `color/surface` | COLOR | `#ffffff` | `--color-surface` |
| `color/brand` | COLOR | `#2f6b3f` | `--color-brand` |
| `color/text` | COLOR | `#1f2a24` | `--color-text` |
| `color/text-secondary` | COLOR | `#5f6f64` | `--color-text-secondary` |
| `color/border` | COLOR | `#dce5d7` | `--color-border` |
| `space/page` | NUMBER | `22px` | `--space-page` |
| `radius/card` | NUMBER | `10px` | `--radius-card` |
| `radius/control` | NUMBER | `8px` | `--radius-control` |
| `shadow/card` | EFFECT | `<actual value>` | `--shadow-card` |

## Text Styles (Actual Values)

| Style | Font family | Weight | Font size | Line height | Letter spacing |
|---|---|---|---|---|---|
| `Type/12 Regular` | Noto Sans SC | 400 | 12px | 100% | 0 |
| `Type/14 Regular` | Noto Sans SC | 400 | 14px | 100% | 0 |
| `Type/14 Medium` | Noto Sans SC | 500 | 14px | 100% | 0 |
| `Type/18 Regular` | Noto Sans SC | 400 | 18px | 100% | 0 |
| `Type/24 Bold` | Noto Sans SC | 700 | 24px | 100% | 0 |
| `Type/44 Bold` | Noto Sans SC | 700 | 44px | 100% | 0 |

## PAGEs and Nodes

> One row per PAGE, frozen in 06. `Design source ref` is the HTML file path for the HTML source (including Figma-to-HTML), or the real Figma node id for the legacy direct Figma source. `Viewport/frame size` uses the platform's real review size (Web 1440×900; App/H5 375×812; tablet/PDA 768×1024). PAGE IDs are unique across platforms.

| PAGE ID | Platform | Design source ref | Viewport/frame size | State |
|---|---|---|---|---|
| PAGE-001 Login (Web) | web | `ui-html/web/PAGE-001.html` | 1440×900 | default |
| PAGE-002 User Management (Web) | web | `ui-html/web/PAGE-002.html` | 1440×900 | default |
| PAGE-003 Login (App) | app | `ui-html/app/PAGE-003.html` | 375×812 | default |
| PAGE-004 Home (Android) | android | `ui-html/android/PAGE-004.html` | 412×915 | default |

## PAGE Key Specifications

> Each page must have block-level actual values (position/size/layout/padding/gap/border/radius/font/fill), not just "top bar, sidebar, list".
> Element-level text/spacing/font size/hierarchy reference `figma-code/`; `figma-layout.csv` is the runtime assertion subset; this table is a block summary, not the only geometry source.

### PAGE-001 Login (Web)

| Block | data-node-id / Figma node | Position/size | Layout/spacing | Fill/border/radius | Font/text |
|---|---|---|---|---|---|
| Brand area | `login-brand` | x=0,y=0,w=600,h=900 | vertical gap 22, padding 22 | fill `color/brand` | `Type/44 Bold`, `Type/18 Regular` |
| Form area | `login-form-area` | x=600,y=0,w=840,h=900 | centered, padding 64 | fill `color/bg` | — |
| Form card | `login-form-card` | x=210,y=265,w=420,h=370 | vertical gap 18, padding 18 | `color/surface`, 1px `color/border`, radius 10 | `Type/24 Bold` |
| Login button | `login-submit` | x=19,y=280,w=66,h=39 | padding 18/10 | `color/brand`, radius 8 | `Type/14 Medium` |

### PAGE-003 Login (App)

| Block | data-node-id / Figma node | Position/size | Layout/spacing | Fill/border/radius | Font/text |
|---|---|---|---|---|---|
| Status bar | `app-status-bar` | x=0,y=0,w=375,h=44 | padding 12/0 | fill `color/surface` | — |
| Brand header | `app-brand` | x=0,y=44,w=375,h=180 | vertical gap 12, padding 24 | fill `color/brand` | `Type/24 Bold` |
| Form card | `app-form-card` | x=16,y=240,w=343,h=360 | vertical gap 16, padding 16 | `color/surface`, radius 12 | `Type/18 Regular` |
| Login button | `app-login-submit` | x=16,y=520,w=343,h=48 | centered, radius 8 | `color/brand` | `Type/14 Medium` |

<!-- Add the remaining PAGEs in the same table format; use figma-code/ as the authority for text/structure in the design code; the assertion scope is described in ## Assertion Scope. -->

## HTML Design Docs

- Review entry: `design/ui-html/index.html` (links every PAGE grouped by platform; this is the design owner's review deliverable)
- Provenance: `AI-authored from requirements` / `User-provided HTML` / `Figma-to-HTML (AI conversion)`; for user-provided HTML, record who supplied it and when; for Figma-to-HTML, record the real Figma file/nodes read
- README: `design/ui-html/README.md` (platform/page index, provenance, token source, rendering/measurement method, design-code transcription notes)
- Tokens: CSS custom properties are embedded per PAGE and/or defined in `design/ui-html/tokens.css`
- Page files: `design/ui-html/<platform>/PAGE-00N.html`; each file is self-contained (no external network dependency), uses real copy, and tags key blocks with `data-node-id`
- Review notes: `<platform navigation, responsive rules, states shown on the review entry>`

## HTML Read Records

> Records of the actual rendering/measurement used to fill tokens, PAGE specifications and `figma-layout.csv`, plus the Figma read/conversion step when provenance is Figma-to-HTML. Do not claim a render that was not executed. The rows below are examples: replace every row with the real command, target, result, and time (the `--strict` check rejects placeholder markers). When a legacy Change uses the direct Figma source, delete this section and fill `## MCP Read Records` instead.

| Step/command | Target | Actual result | Time | Status |
|---|---|---|---|---|
| Figma read + HTML conversion (Figma-to-HTML only) | `<fileKey / node ids>` | real nodes read and converted to HTML pages | `<time>` | Success / N/A |
| Headless render + DOM measure | `ui-html/web/PAGE-001.html` @ 1440×900 | geometry/text/font extracted for `<N>` assertion rows | `<time>` | Success |
| Headless render + DOM measure | `ui-html/app/PAGE-003.html` @ 375×812 | geometry/text/font extracted for `<N>` assertion rows | `<time>` | Success |

## Design Code

- Target framework: `<Vue 3 + TypeScript + Element Plus / React + ...>` (must be consistent with `docs/architecture/technology-decisions.md`)
- Design code extension: `<.vue / .tsx / .jsx>`
- Selection basis: `<ADR-002 / technology-decisions version and approval date>`
- Transcription method: default is **HTML → target-framework design code** (`design/ui-html/` pages → `figma-code/PAGE-00N.vue`). Replace HTML-specific markup with the target component library and project tokens while preserving real copy, font size/weight, spacing, radius, hierarchy and `data-node-id`; produce static high-fidelity pages only, with no business API integration. For Figma-to-HTML, record loading the official `figma-design-to-code` Skill, reading the real Figma source, and converting it to HTML before transcription.
- `figma-code/README.md`: explains the source, target framework/extension, component and style/token replacements, transcription deviations, and the correspondence between `data-node-id` and `figma-layout.csv`.
- `figma-code/PAGE-001.vue … PAGE-00N.vue` (`.tsx`/`.jsx` for the React stack): one target-framework design code file per PAGE. 08 ports these directly as page skeletons, adding only routing/API/state/permissions/business logic, and must not rewrite styles, layout, or copy.
- `figma-layout.csv`: concise assertion table, columns include `page_id,platform,viewport,route,element_id,figma_node_id,x,y,width,height,dom_selector,assert_geometry,assert_text,tolerance_px,text_content,font_size,font_weight,notes`; coordinates are relative to the top-left corner of the PAGE frame/viewport. In HTML mode `figma_node_id` stores the HTML `data-node-id` value. 06 establishes the assertion subset (`route`/`dom_selector` may temporarily be `PENDING`), 07 must fill them in.
- Gates: `python scripts/check-figma-audit.py --change <change-id> --strict --require-framework` validates the source, target platform coverage, the existence of design code for each PAGE, and the completeness of assertion-table geometry/text/selectors; 08/09 run `python scripts/check-figma-layout.py --change <change-id> --base-url <url>` (per-page viewports come from the CSV), comparing expected `x/y/w/h`, text, and fonts element by element; `python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>` precisely compares token actual values.
- **UI verification relies primarily on machine evidence**: PAGES with no differences use the numeric values in `figma-layout-check.json` directly in 08/09/10; only PAGES with differences/`UI-DERIVED` require manual review and approval. Reference screenshots or pixel screenshots are not stored.

## Assertion Scope

> `figma-layout.csv` is the only subset of runtime assertions; elements not included in assertions are covered by the design code and manual acceptance. If there is a structural difference (present in the design source but absent in implementation, or different layout), it must be registered in `## Differences and Pending Confirmation` and wait for approval from the design owner.
> Each PAGE must have at least 1 assertion row; it is recommended to cover key blocks such as the top bar/sidebar/main area/title/primary action/table card. Non-web platforms use their own viewport values instead of 1440×900.

| PAGE | Assertion coverage | Not asserted/notes |
|---|---|---|
| PAGE-001 | Brand area, brand title, form card, form title, account input, button, bottom note | Subtitle/labels, etc. are covered by the design code and manual acceptance |
| PAGE-003 | Status bar, brand header, form card, login button | Platform-specific keyboard/safe-area handling is covered by 07 design and manual acceptance |
| PAGE-00N | `<...>` | `<...>` |

## State Coverage

> Each PAGE must list the applicable states; states that "have no design frame" must document the 07 design decision, approver, and reference basis, and must not claim they have been reproduced.
> Non-default states do not require screenshots; 08 covers visible elements and state differences via the assertion mapping, 09 verifies independently, and 10 batch-signs off PAGES with no differences based on machine evidence and performs side-by-side verification for PAGES with differences/`UI-DERIVED`.
> Platform states include at least default, loading, empty, error, permission denied/degradation, offline/weak network, push/deep link (when applicable), and Android/iOS/HarmonyOS differences.

| PAGE ID | State | Design has frame | Notes/decision |
|---|---|---|---|
| PAGE-001 | default | Yes | — |
| PAGE-001 | loading | No | 07 design decision: `<button loading style/basis>`; approver `<...>` |
| PAGE-003 | offline | No | 07 design decision: `<offline placeholder and retry>`; approver `<...>` |

## Requirements Coverage

> Every AC and US declared in `design/user-stories.md` must map to at least one PAGE for every declared platform, or an explicit `N/A + reason` for that platform. Every PAGE must map back to at least one requirement. `PARTIAL` is allowed only with an approver note and does not satisfy the completion check. This table is the machine-checked completeness/consistency matrix for the HTML-assisted review; the design owner confirms it in `## UI Review`.

| Requirement | Type | Platform | PAGE / Block | States | Coverage | Evidence / notes |
|---|---|---|---|---|---|---|
| AC-001 | AC | web | PAGE-001/PAGE-001-E01 | default; error | FULL | `ui-html/web/PAGE-001.html#login-form` |
| AC-001 | AC | app | PAGE-003/PAGE-003-E02 | default; permission-denied | FULL | `ui-html/app/PAGE-003.html` |
| US-001 | US | web; app | PAGE-001; PAGE-003 | default | FULL | derived from AC-001 |
| AC-004 | AC | desktop | N/A | N/A | N/A | desktop is not a target platform for this Change |

## Asset List

> Only register real image/SVG assets (logo, icons, illustrations, etc.), downloaded to `figma-assets/`; temporary source URLs must not be kept.
> **Reference screenshots must not be registered** (`PAGE-*.default.png`, etc.); visual comparison uses `figma-code/` / `figma-layout.csv`.
> When there are assets, also write `figma-assets/README.md` (file name, source node/page, sha256, size); when there are no assets, write `- Assets: none`.

| Asset | Source node/page | File | Size | Purpose |
|---|---|---|---|---|
| `<logo>` | `<PAGE-001 / node>` | `figma-assets/asset-logo.svg` | `<w×h>` | `<...>` |

<!-- Optional legacy Figma-source section (keep only for a legacy direct Figma source; delete for Design-to-HTML).
## MCP Read Records

| Tool/command | Target file/node | Actual return | Time | Status |
|---|---|---|---|---|
| `get_variable_defs` | `<fileKey>` | number of token actual values | `<time>` | Success |
| `get_metadata` | 6 PAGEs | page structure and x/y/w/h in the design code | `<time>` | Success |
| `get_design_context` | `3:2`…`11:2` (as needed) | per-page specifications/styles/assets | `<time>` | Success |
-->

## Differences and Pending Confirmation

| Difference ID | Requirement/AC requirement | Actual design status | Impact | Choice/reason | Approver/status |
|---|---|---|---|---|---|
| UI-DIFF-001 | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |

## UI Review

- UI review status: DRAFT (changed to APPROVED after the design owner reviews the HTML review entry; a legacy direct Figma source uses its real Figma review draft)
- Reviewer: `<name or role>`
- Review date: `<YYYY-MM-DD>`
- Coverage review status: DRAFT (changed to APPROVED after the owner confirms every AC/US maps to PAGE(s) per declared platform and every PAGE maps back to a requirement)
- Coverage reviewed by: `<name or role / YYYY-MM-DD>`
- Review evidence: `workflow/evidence/06-figma-ui-review.md`
- Review scope: requirement coverage completeness/consistency (`## Requirements Coverage`), PAGE coverage per declared platform, key blocks, state variants, permission/navigation behavior, token actual values, target framework/page structure and copy of `figma-code/`, assertion scope of `figma-layout.csv`

> Fields that cannot be read must be registered as "not checked"; results must not be fabricated; when the selected design source is unavailable or cannot be read, block stage 06 rather than substitute screenshots or invented text.
> Manual UI review is completed on the HTML review entry (or the real Figma file for the legacy direct Figma source); automated visual regression uses numeric assertions of design geometry against the runtime DOM, not screenshots.
