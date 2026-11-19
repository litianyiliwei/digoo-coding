# Superpowers Skill Mapping

> Language: English | [简体中文](SUPERPOWERS-MAPPING-zh.md)

This project's Skills are responsible for business stages; Superpowers is responsible for coding methods and collaboration processes. They are not one set of skills that need to replace each other.

| This Project's Stage | Corresponding Superpowers Skill (if present in the installed version) | Usage |
|---|---|---|
| Conversation startup/skill discovery | `using-superpowers` | If installed and discoverable by the Agent, read its rules first, then select task-relevant skills; execute according to the host Agent's actual invocation method |
| Requirements business analysis/solution discussion | `brainstorming` | First clarify goals, users, pain points, scope, success criteria, and open questions with the user; do not generate a complete solution in one pass without clarification; requirement specifications ultimately land in the project baseline/OpenSpec |
| Reference product/internet research | `internet-research` | Use WebSearch/WebFetch or the host's equivalent networked tools to record research questions, sources, comparisons, conclusions, and impact mapping; when there is no network capability, mark BLOCKED and do not substitute memory |
| Plan implementation | `using-git-worktrees`, `writing-plans` | After the solution is approved, prepare an isolated workspace and split it into small tasks |
| Coding implementation | `test-driven-development` | RED → GREEN → REFACTOR, verification first |
| Task execution | `subagent-driven-development` or `executing-plans` | Execute in the mode supported by the current environment and set checkpoints |
| Failure handling | `systematic-debugging` | Reproduce, locate the root cause, verify the fix; do not make random changes |
| Code review | `requesting-code-review`, `receiving-code-review` | Check against the specification/plan and verify review feedback |
| Pre-completion verification | `verification-before-completion` | Prove with real commands and results that the feature is fixed/implemented |
| 07 Detailed Design | `brainstorming`, `writing-plans` | Use `brainstorming` to compare trade-offs among data models, interface shapes, state transitions, and test strategies; use `writing-plans` to split the approved spec/AC into design tasks and a test plan; method evidence must be recorded |
| 09 Independent Verification | `verification-before-completion`, `systematic-debugging` (read-only) | Use `verification-before-completion` to require real commands/exit codes/test results; use `systematic-debugging` to reproduce failures and locate root causes without fixing code; the code review skill must not replace independent verification |
| Branch completion | `finishing-a-development-branch` | After all verifications pass, discuss merge/PR/cleanup; do not publish automatically |

Skill names and trigger rules may vary with the Superpowers version and Agent adaptation. Check the current installation before implementation; if a skill is missing, report it explicitly and execute an equivalent explicit process; do not claim to have invoked a skill that does not exist.

## OpenSpec Participation Matrix

OpenSpec in this project is both a "specification and validation system" and an available "exploration/revision method." However, its `propose` generates proposal/specs/design/tasks in one pass, which conflicts with this project's staged gates for 05/06/07, so allowed and forbidden uses must be distinguished.

| Stage | Must Execute (real commands) | Allowed (with boundaries) | Forbidden |
|---|---|---|---|
| 02 Requirements Business Analysis | `openspec list --specs` and read related specs | `openspec-explore` read-only thinking (must not create a Change or write code) | `openspec new change`, `openspec-propose` |
| 03 Overall Architecture | `openspec list --specs`, `openspec list --changes` | `openspec-explore` read-only comparison of architecture/boundaries | `openspec new change`, `openspec-propose` |
| 04 Proposal Breakdown | `openspec list --specs`, `openspec list --changes` | `openspec-explore` read-only; after approval, run `openspec new change` one at a time | `openspec new change` before approval, `openspec-propose` |
| 05 Proposal Requirements | `openspec status --change`, `openspec list --specs`, `openspec instructions <artifact> --change --json`, `openspec validate --strict` | `openspec-explore` (within the current Change scope); `openspec-update-change` (requirement revision, requires re-review) | `openspec-propose`; skipping 05 and directly creating Change artifacts |
| 06 Figma | `openspec status --change`, read approved specs | `openspec-explore` read-only clarification of interactions | `openspec-propose`, `openspec-update-change` (requirement changes must go back to 05) |
| 07 Detailed Design | `openspec status --change`, `openspec instructions design --json`, `openspec validate --strict` | `openspec-explore` (when design is ambiguous); `openspec-update-change` (only for design decision consistency, requires re-review) | `openspec-propose`; using design to overwrite approved behavior in reverse |
| 08 Implementation | `openspec instructions apply --json`, `openspec status --change`, `openspec validate --strict` | Read tasks/specs/design; must not modify specs | `openspec-propose`, `openspec-update-change` (spec conflicts must pause and go back to 05/07) |
| 09 Independent Verification | `openspec status --change`, `openspec validate --strict` | Read-only specs/design/tasks | `openspec-propose`, `openspec-update-change`, `openspec-sync-specs` |
| 10 Acceptance and Archiving | `openspec validate --strict`; `openspec archive` after user approval | `openspec-sync-specs` (if the main specs need to be synced first) | `openspec archive -y`, unapproved archiving, `openspec-propose` |

## In-Stage Method Patterns (stage-scoped brainstorming)

The full Superpowers `brainstorming` process requires writing a standalone design document and getting separate approval; this project's stage gates require artifacts to land in existing carriers such as `design.md` / `technology-decisions.md` and to be approved by stage review. Directly stacking the two would produce out-of-band documents and a second approval process. Therefore, this project uses the **stage-scoped** mode by default:

1. Load `using-superpowers` and `brainstorming`, and actually use their method of "clarify first, then compare alternatives, then record trade-offs."
2. Write clarification questions, alternatives, decisions, and open items into the stage's existing artifacts (the interview record in `technology-decisions.md`, `### Key Decisions and Trade-offs` in `design.md`, `open-questions.md`, etc.), without writing a separate `docs/superpowers/specs/` design document.
3. The stage's `request-review` + explicit user approval is the approval of that method's artifacts; no second approval set is added.
4. Only when the user explicitly requests a "standalone Superpowers design document" should the full `brainstorming` process be executed; in that case, the handoff report must state the out-of-band document path, and the stage artifacts must remain authoritative.
5. When a skill is genuinely unavailable, use `mode=equivalent`, record `reason` and equivalent steps; do not treat "available" as "used."

## Per-Stage Communication Checklist (Mandatory)

### 03 Overall Project Architecture

- System origin: new system, secondary development based on an existing system, or hybrid; do not default.
- If secondary development: require the code address (repository/local path/branch/commit), actually explore the code structure, technology stack, module boundaries, API/data models, build/test/release commands, existing conventions, and technical debt; write them into "Existing System Secondary-Development Constraints" in `technology-decisions.md`, and convert them into `LEGACY-*` constraints in `constraint-registry.json`; BLOCKED when the code is inaccessible.
- Third-party interfaces: list the provider, purpose, protocol, authentication, SLA/quota, sandbox/test account, approval, data sharing/privacy, errors/timeouts, owner; write them into the "Third-Party Interface Dependency List," the EXTERNAL data flows in `data-flows.md`, and "Third-Party Interface and Integration Conventions" in `api-conventions.md`; if none, write NONE + reason.

### 07 Detailed Design

- Change type: modifying existing feature code or new feature development; do not default.
- If modifying existing feature code: require the code address (repository/path/branch/commit), actually explore files/classes/functions/data structures/tests/migrations; write them into `### Existing Code Change Impact` in `design.md` (files/classes/functions/interfaces/tables/tests, modification strategy, compatibility, migration/rollback, risks, verification method); BLOCKED when the code is inaccessible.
- Third-party interfaces: cross-check with the 03 list; create a `THIRD_PARTY_API` row in `interface-catalog.csv` for each third-party interface, recording provider/protocol/authentication/input-output/errors/timeout retry idempotency/SLA/quota/sandbox/data sharing privacy/test_ids/owner; tests cover sandbox, simulator, or manual verification via `interface_ids`/`fakes_env` in `test-cases.csv`.

## Method Evidence

The stage evidence for 02-10 must include a `methods` block recording skill/mode/questions/alternatives/decisions/open_questions/artifact_section/evidence. The policy is in `method_policy` of `process/STEP-ARTIFACT-CONTRACTS.json`; separate validation command:

```bash
python scripts/check-method-evidence.py --step <step-id> --evidence <evidence.json>
```

`workflow.py transition` automatically invokes the same validation; Section 4 of the handoff report must show key questions, alternatives, decisions, open items, and artifact locations. Without `methods`, without the required method skills, without a real evidence path, or without the required artifact landing section, the stage must not advance. Question/alternative/decision counts are not enforced.



## Must Execute, Not Merely Mention

- Each stage's Prompt must first load the corresponding project Skill and check whether the applicable Superpowers skill is actually available.
- Detailed design must actually use `brainstorming` and `writing-plans` and record method evidence; independent verification must use `verification-before-completion`, run OpenSpec `status`/`validate` independently, and must not use the code review skill to replace independent verification.
- The requirements business analysis stage explicitly uses `brainstorming` and `internet-research`; it usually occurs before a formal OpenSpec Change, so read existing specs first and do not create a Change prematurely. Research results are written into `docs/product/reference-research.md`.
- OpenSpec-related stages must run the real CLI: use `openspec list/status/instructions/validate` to read status and rules; archive only after user approval and passing gates.
- If the Agent has no repository/terminal/Skill access, it must request files from the user or state that it cannot execute; it must not simulate tool results.
