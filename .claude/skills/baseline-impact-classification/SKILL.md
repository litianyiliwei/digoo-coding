---
name: baseline-impact-classification
description: Classifies each Change item against the frozen project baseline as CHANGE_ONLY, BASELINE_CHANGE_REQUIRED, BASELINE_UPDATE_AFTER_ACCEPTANCE, or N/A; records versions, constraints, conflicts, recheck conclusions, and write-back decisions.
---

# Baseline Impact Classification

This is a local **method Skill**: it is invoked inside a stage and does not own a stage or create stage artifacts on its own. The stage Skill/Prompt remains the authority for output paths, review, and gates.

## When to Use

- **Stage 05 (required)**: create the Change's initial `design/baseline-impact.md` and constraint binding.
- **Stage 07**: recheck the design against the current baseline and record `NO_IMPACT` or `REBASE_REQUIRED`.
- **Stage 10 (required)**: decide which approved, implemented, verified decisions are written back to the project baseline.
- **Stage 03/04** may use it for the initial baseline freeze or roadmap-level applicability.

## Inputs

- `docs/product/BASELINE-BRIEF.md`, `docs/architecture/baseline-status.md`, `docs/architecture/baseline-manifest.json`, and `docs/architecture/constraint-registry.json`.
- `process/BASELINE-FEATURE-INTERACTION.md` and `templates/change-assets/design/baseline-impact.md`.
- The current Change's proposal/spec/AC, `design.md`, interface/API/data decisions, and acceptance evidence.

## Classification

| Classification | Meaning | Action |
|---|---|---|
| `CHANGE_ONLY` | Feature-local behavior, endpoint, page, physical migration, IO, or test | Keep it in the Change; no baseline amendment |
| `BASELINE_CHANGE_REQUIRED` | Changes a cross-feature shared rule, boundary, core domain model, public API/frontend convention, or global quality gate | Propose a BCR/ADR; open an amendment; block affected work until approved |
| `BASELINE_UPDATE_AFTER_ACCEPTANCE` | An approved decision that should be written back only after implementation/verification/acceptance | Record it now; write back at acceptance |
| `N/A` | No baseline impact | Write `N/A + reason`; do not leave it blank |

## Procedure

1. **Read the baseline first.** Start with `BASELINE-BRIEF.md`, then `baseline-status.md`, `baseline-manifest.json`, and the applicable domain files/constraints.
2. **Identify affected domains.** Use the manifest domains (for example product, architecture, data/domain, API, frontend, test/quality); record the version, file, section/ID read, and why it applies.
3. **Classify every item.** Apply the table above; when uncertain, classify conservatively as `BASELINE_CHANGE_REQUIRED` and record the open question rather than assuming no impact.
4. **Record the evidence.** Fill `design/baseline-impact.md`: baseline version, files/sections/IDs read, constraints, reused items, conflicts, ownership classification, approval status, and recheck conclusion.
5. **Bind constraints.** At stage 05 run `python scripts/baseline-governance.py init-binding --change-id <id>`; at stage 07 write design evidence for each bound constraint; at stage 10 fill `acceptance_verification` for each ACTIVE constraint.
6. **Handle a required baseline change.** Do not edit the frozen baseline. Submit a BCR/ADR, run `baseline-governance.py open-amendment`, and block affected work. Close only after the owner approves, the domain version and hashes are refreshed, and evidence is complete.
7. **Handle write-back.** For `BASELINE_UPDATE_AFTER_ACCEPTANCE`, do not write back early. At acceptance, write back only decisions that are approved, implemented, verified, and reusable across features; feature-specific details stay in the archived Change.
8. **Handle version drift.** If any baseline version changed, record `NO_IMPACT` or `REBASE_REQUIRED`; after an approved rebase refresh the binding and re-review affected designs.
9. **Run the gates.** `python3 scripts/check-baseline-impact.py <change-id>`, `python3 scripts/baseline-governance.py check-change --change-id <id> --phase requirement|design|acceptance`, and at stage 03 `audit --require-frozen`.
10. **Evidence.** Record a `methods` entry for `baseline-impact-classification` with a real evidence path and `<artifact>#<heading>` landing section.

## Output Landing by Stage

| Stage | Artifact | Landing section |
|---|---|---|
| 05 | `openspec/changes/<change-id>/design/baseline-impact.md` + `design/baseline-binding.json` | `## 5. Change Ownership Classification` |
| 07 | `design/baseline-impact.md` (design recheck) + `baseline-binding.json` design evidence | `## 8. Conclusion and Gates` (`NO_IMPACT` / `REBASE_REQUIRED`) |
| 10 | `design/baseline-impact.md` (write-back decision) + `design/evidence/acceptance.md` | `## 8. Conclusion and Gates` and acceptance verification |

## Quality and Safety Boundaries

- Never edit `docs/architecture/baseline-manifest.json`, `constraint-registry.json`, or frozen domain files directly during a Change.
- Never approve a baseline amendment or exception on the owner's behalf.
- Do not silently bypass a conflict; record it and block affected work.
- `N/A` must carry a reason and cannot be inferred from silence.
- A feature-local change must not be promoted to a baseline amendment just to avoid design work.

## Evidence

At stage 05:

```json
{
  "skill": "baseline-impact-classification",
  "mode": "stage-scoped",
  "artifact_section": "openspec/changes/<change-id>/design/baseline-impact.md#5. Change Ownership Classification",
  "evidence": "workflow/evidence/05-feature-requirements.json"
}
```

At stage 10:

```json
{
  "skill": "baseline-impact-classification",
  "mode": "stage-scoped",
  "artifact_section": "openspec/changes/<change-id>/design/baseline-impact.md#8. Conclusion and Gates",
  "evidence": "workflow/evidence/10-acceptance-audit.json"
}
```
