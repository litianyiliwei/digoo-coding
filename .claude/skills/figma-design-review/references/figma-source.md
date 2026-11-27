# Optional Figma Source Reference (Stage 06)

> Load this reference **only** when the user explicitly selects `Figma-to-HTML` conversion or a legacy direct Figma source. Do not load or require Figma MCP for `User-provided HTML` or `AI-authored from requirements`.

## 1. Prerequisites
1. Confirm Figma MCP availability and real read access (`get_metadata`, `get_variable_defs`, `get_design_context`). If the Figma URL/nodes are unreadable or MCP is unavailable, stop and report `BLOCKED`; never fabricate nodes, tokens, or measurements.
2. When transcribing directly from Figma `get_design_context`, load the official `figma-design-to-code` Skill if installed; report honestly if absent.

## 2. Figma-to-HTML Path (Preferred when Figma is provided)
1. Read actual Figma nodes, tokens (`get_variable_defs`), text styles, and layout metadata (`get_metadata` / `get_design_context`) serially per page.
2. Convert each Figma page into a self-contained HTML design page under `openspec/changes/<change-id>/design/ui-html/<platform>/PAGE-00N.html` with `data-node-id` attributes, `tokens.css`, and `index.html`.
3. Record `HTML provenance: Figma-to-HTML` plus actual MCP read records (fileKey, node IDs, timestamp, result) in `design/figma-audit.md`.
4. Render and measure the generated HTML pages to populate `design/figma-layout.csv` (`figma_node_id` stores the HTML `data-node-id`), then transcribe into target-framework code under `design/figma-code/`.

## 3. Legacy Direct Figma Source (Only when user explicitly opts out of HTML)
1. Omit `design/ui-html/` and record `Design source: Figma (legacy direct)` in `design/figma-audit.md`.
2. Populate `design/figma-audit.md` (actual token values, text styles, PAGEs/nodes, MCP read records, requirements coverage, UI review) directly from real Figma MCP responses.
3. Transcribe `get_design_context` output into target-framework design code under `design/figma-code/PAGE-00N.<ext>` using the project's component library and tokens from `docs/architecture/technology-decisions.md`.
4. Populate `design/figma-layout.csv` (`figma_node_id` stores the real Figma node ID `X:Y`) from measured Figma metadata.
5. Never save Figma screenshots or pixel diffs as contracts, assets, or gate evidence.
