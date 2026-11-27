# Prompt 03: Project Overall Architecture Design

- Stage ID: `03-project-architecture-baseline` (project-level)
- Skill: `.claude/skills/project-architecture-baseline/SKILL.md`
- Required method skills: `brainstorming`
- Question coverage guide: `process/QUESTION-COVERAGE-CHECKLIST.md`

## User Input
- Technology stack preferences & constraints: `<must be confirmed via interview; never assume>`
- Existing system repo/branch/commit (if extending): `<path/URL or N/A + reason>`
- Third-party interfaces (or `NONE + reason`): `<list or NONE + reason>`
- Static analysis adoption preference: `<adopt / not adopt>`
- Code layout strategy: `<module-packages | footprint | none>`

## Entry Commands (Run First)
1. `python scripts/workflow.py check-entry --step 03-project-architecture-baseline`
2. `python scripts/agent-context.py --stage 03`

## Execution Rules
Follow `.claude/skills/project-architecture-baseline/SKILL.md` to conduct the architecture & platform boundary interview, author the project architecture baseline, `code-layout.json`, optional `quality-gates.json`, `baseline-manifest.json`, `constraint-registry.json`, `baseline-status.md`, and `baseline-audit-report.md`. Use `process/QUESTION-COVERAGE-CHECKLIST.md` (`03-*`) as discovery guidance.

## Mandatory Deliverable Handoff
- Write all declared outputs to disk and run: `bash scripts/check-required-files.sh --strict`, `python scripts/check-architecture-baseline.py --strict`, `python scripts/check-quality-gates.py --root . --strict`, `python scripts/check-method-evidence.py --step 03-project-architecture-baseline --evidence workflow/evidence/project/03-project-architecture-baseline.json`, and `python scripts/baseline-governance.py audit --require-frozen`.
- Run `python scripts/workflow.py request-review --step 03-project-architecture-baseline --evidence workflow/evidence/project/03-project-architecture-baseline.json --summary "<summary>"`, present `templates/workflow/step-handoff-report.md`, and end the turn.
- Run `python scripts/workflow.py approve` and `transition` only after the user explicitly approves this stage. Never edit `workflow-state.json` directly.
