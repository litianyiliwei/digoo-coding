# Change Slicing Rules and Definition of Done

- Change ID: N/A (project-level)
- Status: DRAFT
- Source baseline: docs/product/requirements-analysis.md, proposal-roadmap.md
- Related requirements/AC: N/A
- Generated date/version: PENDING

## 1. What Is a Change

A Change is one independently acceptable business capability that forms a demonstrable vertical slice along "entry → behavior → result"; it is not an architecture layer, a batch of pages, a refactor, or a set of technical tasks.

## 2. Slicing Budget

| Dimension | Suggested limit | When exceeded |
|---|---|---|
| Observable business capability | 1 | Split |
| Key AC | 12 | Split or phase |
| Roles involved | 3 | Check whether it crosses permission domains; split if necessary |
| Cross-domain dependencies | 2 | Build the dependency Change first or narrow the scope |
| New public contracts | 0 | Go through a baseline change/ADR first |

The budget is not a hard number; when exceeded, the reason and approver must be recorded.

## 3. Signals That Require Splitting

- Simultaneously changing the core flows of two or more roles.
- Simultaneously introducing new public rules, public data models, and public APIs.
- Cannot be demonstrated end to end with a single demo script.
- The AC share no common business goal and are merely adjacent at the technical layer.
- Acceptance requires "doing half now and filling in the rest later".

## 4. Definition of Done (DoD)

- [ ] The proposal's Why/What/Non-goals are approved.
- [ ] Delta specs cover all externally observable behavior, with at least one Scenario per Requirement.
- [ ] Every AC has a verification method and evidence path; all blocking AC pass.
- [ ] The baseline impact list and constraint binding are complete; applicable constraints are COMPLIANT or EXCEPTION_APPROVED.
- [ ] Test, build, code review, and independent verification evidence genuinely exists; unexecuted items are listed.
- [ ] Human acceptance passes and the approver is recorded; archiving/baseline write-back is completed per the rules.
- [ ] `lessons.md` has been appended with reusable lessons from this Change (write N/A + reason if none).

## 5. Boundary with the Baseline

- Behavior, pages, APIs, table migrations, IO, and tests unique to the current feature stay in the Change.
- Rules, public contracts, core models, and quality gate changes shared across features must be elevated to baseline changes and approved before design.
- See `process/BASELINE-FEATURE-INTERACTION.md` for detailed determination.

## 6. Usage

- During Step 04 roadmap splitting, read sections 1-3 and annotate the budget for each candidate Change.
- Before Step 05 begins, read section 4 as the admission check for proposal-level requirements.
- During Stage 10 acceptance, verify the DoD item by item.
