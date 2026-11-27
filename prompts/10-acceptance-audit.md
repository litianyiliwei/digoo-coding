# Prompt 10: Human Acceptance, Archive, and Baseline Write-Back

- Stage ID: `10-acceptance-audit` (Change-scoped)
- Skill: `.claude/skills/acceptance-audit/SKILL.md`
- Required method skills: `verification-before-completion`, `baseline-impact-classification` (`.claude/skills/baseline-impact-classification/SKILL.md`)

## User Input
- Change ID: `<change-id>`
- Running acceptance environment URL / entry point: `<url / route>`

## Entry Commands (Run First)
1. `python scripts/workflow.py check-entry --step 10-acceptance-audit --change-id <change-id>`
2. `python scripts/agent-context.py --stage 10 --change <change-id>`

## Execution Rules
Follow `.claude/skills/acceptance-audit/SKILL.md` and `.claude/skills/baseline-impact-classification/SKILL.md`.
- **Pre-approval**: verify Stage 09 `PASS` & unchanged revision, walk through `## Acceptance Walkthrough` in `design/user-stories.md`, write `design/evidence/acceptance.md` (machine-evidence sign-off for clean UI pages; side-by-side for differing/`UI-DERIVED` pages) and `acceptance_verification` in `design/baseline-binding.json`. Do not mutate global registries or run `openspec archive` before approval.
- **Post-approval**: after explicit user approval, write back `capabilities.csv`, `modules.csv`, `lessons.md`/`decisions.md`/`assumptions.md`, run `openspec archive <change-id>` (never `-y`), and finish with `workflow.py transition`.

## Mandatory Deliverable Handoff
- Run pre-approval gates (`check-acceptance.py`, `baseline-governance.py check-change --phase acceptance`, `openspec validate <change-id> --strict`, `check-method-evidence.py`), then run `python scripts/workflow.py request-review --step 10-acceptance-audit --change-id <change-id> --evidence workflow/evidence/<change-id>/10-acceptance-audit.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Run `python scripts/workflow.py approve`, post-approval write-back/archive, and `transition` only after the user explicitly approves this stage. Never edit `workflow-state.json` directly.
