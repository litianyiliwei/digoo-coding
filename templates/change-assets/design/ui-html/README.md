# HTML UI Design Documents (Review Entry)

- Change ID: `<change-id>`
- Design source: `Design-to-HTML`
- HTML provenance: `<User-provided HTML / AI-authored from requirements / Figma-to-HTML (AI conversion)>` (exactly one; for user-provided HTML record the supplier/date; for Figma-to-HTML record the real Figma file/nodes read)
- Target platforms: `<web; app; android>` (must equal `- Target platforms:` in `../user-stories.md`)
- Review entry: `index.html` (opens every PAGE grouped by platform; this is the UI review deliverable)
- Tokens: `tokens.css` (actual CSS custom properties; copy the real values into `../figma-audit.md`)

## Page Index

| PAGE ID | Platform | HTML file | Viewport | Purpose/AC |
|---|---|---|---|---|
| PAGE-001 | web | `web/PAGE-001.html` | 1440×900 | PENDING |
| PAGE-003 | app | `app/PAGE-003.html` | 375×812 | PENDING |

## Authoring Rules

- One self-contained HTML file per PAGE and per platform; no external network dependencies (no CDN, no remote images/fonts).
- Key blocks carry `data-node-id="..."`; `figma-layout.csv` uses the same value in its `figma_node_id` column.
- Design tokens are CSS custom properties (embedded or from `tokens.css`); use the project's actual values, not placeholders.
- Include real copy, font family/weight/size, spacing, radius and responsive rules; static high-fidelity pages only, no business API or real authentication.
- Cover the states listed in `../figma-audit.md` (default plus applicable loading/empty/error/permission/offline) on the review entry; states without a design frame need a 07 decision.
- Do not store reference screenshots or pixel screenshots.

## How Tokens and Geometry Were Derived

Record the actual render/measure step used (for example a headless browser at the PAGE viewport) in `../figma-audit.md` under `## HTML Read Records`. Geometry values in `../figma-layout.csv` must come from that rendered HTML, not from memory.

## Design Code

`../figma-code/` contains one target-framework design code file per PAGE, transcribed from these HTML pages. 08 ports it directly and only adds routing/API/state/permissions/business logic.
