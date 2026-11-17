# 参考产品与互联网调研

- Change ID: N/A (project-level)
- Status: READY_FOR_REVIEW
- Source baseline: user request to optimize AI coding workflow; official public documentation
- Related requirements/AC: FLOW-001 / NODE-001-02–06 / DO-002–005 / BR-001–007 / NFR-001
- Research date: 2026-11-17 (official sources rechecked)
- Research executor: Codex desktop; WebSearch and official documentation pages

> The user confirmed no preferred reference product. The following official public documentation was selected for comparison; it does not imply adopting any product wholesale.

## 1. Research Scope and Questions

| Q ID | Research question | Why it matters | Corresponding business domain/FLOW |
|---|---|---|---|
| RQ-001 | How should persistent instructions and task context stay useful without loading unrelated knowledge every time? | Directly affects context cost and instruction adherence | FLOW-001 / NODE-001-02 |
| RQ-002 | How can a multi-step AI coding workflow preserve review gates and resume safely? | Directly affects approval integrity and interruption recovery | FLOW-001 / NODE-001-03–06 |
| RQ-003 | Which artifact boundaries prevent duplicate specifications and oversized handoffs? | Directly affects maintenance cost and coding context size | FLOW-001 / NODE-001-02–04 |

## 2. Reference Product List

- Reference product status: PRESENT
- Reason no user-provided reference product: the user confirmed none is preferred; official public documentation was selected for comparison.

| Product/Solution | Type (same category/adjacent/substitute) | Access method (official site/docs/trial/screenshot/user-provided) | Link | Research date | Notes |
|---|---|---|---|---|---|
| OpenSpec spec-driven schema | Adjacent: spec/change artifact workflow | Official documentation | https://openspec.dev/docs/schemas/spec-driven | 2026-11-17 | Separates proposal, capability behavior specs, design, and tasks; allows specs to be skipped for changes with no behavior delta |
| GitHub Spec Kit workflows | Adjacent: agentic software delivery workflow | Official documentation | https://github.github.com/spec-kit/workflows/overview.html | 2026-11-17 | Defines resumable multi-step workflows with distinct review gates; persisted state supports resume, while interrupted side effects may repeat |
| Claude Code best practices | Adjacent: coding-agent context and enforcement guidance | Official documentation | https://code.claude.com/docs/en/best-practices | 2026-11-17 | Distinguishes model-followed guidance from deterministic enforcement; covers concise scoped instructions, skills, runnable checks, and hard-rule enforcement |

## 3. Research Records

| No. | Research question | Tools/methods used | Query terms or source | URL | Access date | Key findings |
|---|---|---|---|---|---|---|
| 1 | RQ-001 | Web search and direct open of official docs | `Claude Code best practices context keep CLAUDE.md short scope rules skills` | https://code.claude.com/docs/en/best-practices | 2026-11-17 | Guidance distinguishes model-followed instructions from deterministic enforcement; context is reduced through concise, scoped instructions, while hard rules use executable checks or enforcement mechanisms. |
| 2 | RQ-002 | Web search and direct open of official docs | `GitHub Spec Kit workflows review gates resume workflow official docs` | https://github.github.com/spec-kit/workflows/overview.html | 2026-11-17 | YAML workflows compose agent, shell, and control-flow steps; review gates pause or resume runs, and approval of one gate does not approve another. Persisted state supports resuming; interrupted side effects may repeat. |
| 3 | RQ-003 | Web search and direct open of official docs | `OpenSpec spec-driven schema proposal specs design tasks official docs` | https://openspec.dev/docs/schemas/spec-driven | 2026-11-17 | The built-in schema separates proposal, capability behavior specs, design, and tasks; task planning follows proposal/spec/design prerequisites. |

## 4. Comparison and Lessons

| Comparison item | Reference product approach | Candidate approach for this project | Adoption decision | Rationale | Related FLOW/DO/BR |
|---|---|---|---|---|---|
| Context loading | Claude Code guidance keeps persistent instructions short and scopes detailed rules to relevant paths/skills | Use a stage/task read set with impact tags, ID-targeted references, and measured budget | 部分采纳 | Existing project needs stronger audit contracts, but its audit set should not be the default prompt bundle | FLOW-001 / DO-002 / BR-001 |
| Review and resume | Spec Kit stores run state and pauses at explicit review gates; OpenSpec provides artifact prerequisites and validation | Keep workflow state, handoff hashes, and user approvals; reduce repeated narrative while retaining the gate | 部分采纳 | Resumability is useful; this project’s user-approved stage boundary remains mandatory | FLOW-001 / DO-005 / BR-005 |
| Artifact boundaries | OpenSpec distinguishes observable behavior specs from design and task implementation | Maintain one authority per fact; summarize with IDs/paths and generate indexes/reports from authoritative data | 采纳 | Reduces duplicated text and context drift while preserving traceability | FLOW-001 / DO-003 / BR-002/004 |
| Verification | Claude Code guidance emphasizes executable checks; Spec Kit workflows place review gates after defined artifacts | Separate fast structural checks from targeted tests and risk-triggered full verification | 部分采纳 | Keeps feedback quick without removing required security, approval, baseline, or independent-verification checks | FLOW-001 / DO-004 / BR-003/006/007 |

## 5. Conclusions and Assumptions

- Reusable conclusions: Layer context; scope detailed instructions; keep one authoritative artifact per fact; make checks executable and review gates resumable.
- Conclusions not adopted and reasons: Do not replace this repository’s approval/state controls with another tool’s default workflow; the reference docs are design evidence, not policy approval.
- New/updated assumptions (ASM-xxx): ASM-001, that this effort optimizes the process toolkit rather than a separate business application.
- New/updated decisions (DEC-xxx): DEC-001 separates package structure checks from regression test execution; already approved in Stage 01. Other proposed process changes await project-owner review.

## 6. Impact Mapping

| Research conclusion | Impacted object (FLOW/NODE/DO/BR/NFR) | Impact type (new/modified/no impact) | Handling status |
|---|---|---|---|
| Context is loaded by task relevance, not by complete audit inventory | FLOW-001/NODE-001-02/DO-002/BR-001/NFR-001 | modified | Requirement recorded; detailed contract update remains for an approved process-change stage |
| Artifact prerequisites and human gates can coexist with resumable runs | FLOW-001/NODE-001-03–06/DO-005/BR-005 | no impact | Preserve the currently approved gate; optimize repeated handoff prose later |
| Specs, design, tasks, and verification serve different purposes | FLOW-001/NODE-001-03–05/DO-003–004/BR-002/004/006 | modified | Require one authority per fact and avoid reprinting upstream details |

> When there is no impact, write `N/A + reason`; do not leave it blank.

## 7. Open Questions

No research questions remain open. The former Q-003 policy question was resolved through the approved `BCR-Q003-RISK-TIER-POLICY`; the automation selector remains planned work, not an unresolved policy decision.

| Q ID | Question | Owner | Deadline/Blocking condition |
|---|---|---|---|
| N/A | No open research question | N/A | Q-003 resolved 2026-11-17; see `docs/product/open-questions.md` and the approved BCR |

## 8. Sources and Approval

- Research date: 2026-11-17
- Research executor: Codex desktop; official docs accessed using WebSearch/WebFetch-equivalent browser search/open
- Source credibility/limitations: Official product documentation; reflects each product’s own intended workflow, not independent performance measurements or a guarantee of suitability here.
- Product/business owner: User
- Approval status: DRAFT
