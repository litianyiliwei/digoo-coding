---
name: competitor-research
description: Same-category/competitor product research. Confirms the product landscape with the user, researches real public sources, compares flows/roles/data objects/rules, classifies material deviations, and obtains explicit user confirmation before a major deviation can pass.
---

# Competitor / Similar-Product Research

This is a local **method Skill**: it is invoked inside a workflow stage and does not own a stage or create stage artifacts on its own. The stage Skill/Prompt remains the authority for output paths, review, and gates.

## When to Use

- **Stage 02 (mandatory when reference products exist or market comparison is needed)**: identify same-category products, research them, and write `docs/product/reference-research.md`.
- **Stage 03**: refresh competitor evidence only when technology selection, boundaries, or third-party decisions depend on it.
- **Stage 05**: refresh only the rows relevant to the current Change's scope/scenarios.
- Do not use it for generic market essays, and do not let it replace user interviews or business materials.

## Inputs

- Products the user already knows: same-category, adjacent, or substitute products; name, link, screenshot, trial account, or document.
- Project goals, scope, `FLOW`/`NODE`/`DO`/`RD`/`BR` IDs, NFRs, constraints, and current open questions.
- Internet research tools (`WebSearch`/`WebFetch` or the host's real equivalent). When no network capability exists, mark **BLOCKED**; do not substitute model memory.

## Procedure

1. **Confirm the landscape with the user.** Ask explicitly whether same-category (同类) products, competitors, or similar systems exist. Record names, links, screenshots, trial accounts, or documents. If none, record `NONE` + a real reason; do not silently skip research.
2. **Select products.** When any reference product exists, at least one **same-category** product is mandatory. Adjacent and substitute products are optional but must be labeled by type.
3. **Define comparison dimensions tied to project IDs.** Cover at least: target users/roles, core flow coverage (`FLOW`/`NODE`), data objects (`DO`), business rules and permissions (`BR`/role matrix), exception/offline/regulatory handling, and key UI states. Add pricing/business model only when it changes a project decision.
4. **Research with real sources.** For each product and dimension, record the tool/query, an `http(s)` URL, an access date (`YYYY-MM-DD`), and the key finding. Never invent a URL, date, feature, or screenshot.
5. **Write the evidence into the stage artifact.** In stage 02, write sections 1–7 of `docs/product/reference-research.md`: scope/questions, product list, research records, comparison/lessons, conclusions/assumptions, impact mapping, open questions. Do not create a separate research report.
6. **Compare against the current stage output** in `## 9. Similar Product Deviation Confirmation` (at least 2 rows for a PRESENT product list). Each row records: comparison item, our output/approach, similar-product approach, deviation level (`一致` / `可接受差异` / `重大偏差` or `consistent` / `acceptable` / `major`), impacted `FLOW`/`NODE`/`DO`/`BR`/`NFR`, confirmation status, confirmer, and date.
7. **Stop on a major deviation.** Present the deviation table to the user and ask for an explicit decision. Record `用户已确认` (or `confirmed`) plus the confirmer and date. Never self-approve a major deviation or treat silence as confirmation.
8. **Run the gate.** Run `python scripts/check-reference-research.py --strict`. It must exit 0; it fails on a missing same-category product, a missing/placeholder deviation table, or an unconfirmed major deviation.
9. **Land the conclusions.** Write reusable conclusions into the stage's analysis artifact and unresolved items into `docs/product/open-questions.md` with an owner and blocking condition. Record a `methods` entry for `competitor-research` in the stage evidence (real evidence path + `<artifact>#<heading>` landing section).

## Output Landing by Stage

| Stage | Artifact | Landing section |
|---|---|---|
| 02 | `docs/product/reference-research.md` | Sections 1–9; conclusions also in `requirements-analysis.md` / `open-questions.md` |
| 03 | Stage 02 research file, or the stage's decision artifact when a targeted refresh is required | Decision/assumption section that cites the research rows |
| 05 | Stage 02 research file plus the Change's proposal/spec/open questions | Only the rows relevant to this Change |

## Quality and Safety Boundaries

- Every claim has a real source URL and access date; "research" without sources does not pass.
- No network capability means **BLOCKED**, recorded in `open-questions.md`; do not pass the stage.
- The Skill may recommend, but the user owns the decision on a major deviation.
- Do not create an OpenSpec Change, write business code, or produce a separate design document from this Skill.
- A `NONE` product status still requires `## 9` with `N/A` + a non-placeholder reason.
- Do not claim this Skill was invoked unless it was actually loaded and executed; when unavailable, use `mode=equivalent` with a real `reason`.

## Evidence

The stage evidence `methods` entry should look like:

```json
{
  "skill": "competitor-research",
  "mode": "stage-scoped",
  "artifact_section": "docs/product/reference-research.md#9. Similar Product Deviation Confirmation",
  "evidence": "workflow/evidence/02-requirements-analysis.json",
  "open_questions": ["Q-..."]
}
```

The checker is the machine authority; this Skill is the research method.
