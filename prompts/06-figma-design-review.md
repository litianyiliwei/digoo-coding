# Prompt 06: UI Design and Review (HTML-First, Figma Optional)

- Stage ID: `06-figma-design-review` (Change-scoped, conditional)
- Skill: `.claude/skills/figma-design-review/SKILL.md`
- Required method skills: `brainstorming`

## User Input
- Change ID: `<change-id>`
- UI design source: `<User-provided HTML | AI-authored from requirements | Figma-to-HTML | Legacy direct Figma | N/A (no UI)>`
- User-provided HTML path or optional Figma URL: `<path / URL / N/A>`

## Entry Commands (Run First)
1. `python scripts/workflow.py check-entry --step 06-figma-design-review --change-id <change-id>`
2. `python scripts/agent-context.py --stage 06 --change <change-id>`

## Execution Rules
Follow `.claude/skills/figma-design-review/SKILL.md`.
- **No-UI Change**: record `- Design source status: N/A` + `- Reason for no UI: <reason>` in `design/figma-audit.md`, run `check-figma-audit.py --change <change-id> --strict --no-ui --reason "<reason>"`, and use `workflow.py skip-stage`.
- **UI Change (HTML-first default)**: produce `design/ui-html/`, `design/figma-code/`, `design/figma-layout.csv`, and `design/figma-audit.md` covering every declared platform in `design/user-stories.md`. Load `.claude/skills/figma-design-review/references/figma-source.md` only if Figma is explicitly chosen. Never save screenshots.

## Mandatory Deliverable Handoff
- Write all declared outputs to disk and run: `python scripts/check-figma-audit.py --change <change-id> --strict --require-framework` and `python scripts/check-method-evidence.py --step 06-figma-design-review --evidence workflow/evidence/<change-id>/06-figma-design-review.json`.
- Run `python scripts/workflow.py request-review --step 06-figma-design-review --change-id <change-id> --evidence workflow/evidence/<change-id>/06-figma-design-review.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Under `standard` policy, run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves this stage. Under `risk-based` policy (`STATUS=RISK_BASED_FAST_TRACK`), `transition` may run after gates pass. Never edit `workflow-state.json` directly.
