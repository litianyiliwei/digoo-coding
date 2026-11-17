# 流程与文件优化审计

- Change ID：N/A（流程/工具包审计，不是 Change 产物）
- Status: DRAFT（评估报告，不改变任何阶段状态、基线或契约）
- 来源基线：当前工作区实际文件 + `docs/architecture/baseline-status.md` v0.3.0（只读核对）
- 关联需求/规则：BR-001、BR-002、BR-003、BR-005、BR-006、DEC-001–005
- 生成日期/版本：2026-11-17 / v0.1.0
- 审计方式：4 组只读并行评审（流程文档、脚本、Prompts/Skills、模板与基线），关键结论由主会话逐项复核
- 证据边界：未运行 `request-review`/`approve`/`transition`/`reopen` 等会改写状态的命令；状态哈希失配在隔离副本中复现

> 本报告回答两个问题：**总体流程与 10 个节点是否需要优化？每个流程文件是否需要优化？**
> 结论是：需要优化，但不是推倒重来。流程骨架是对的；主要问题是治理机制把“可变运行时状态、生成物、工具脚本”当成阶段审批产物，导致门禁互相绊倒。

---

## 0. 执行摘要

### 0.1 一句话结论

- **10 阶段 DAG、项目基线/Change 分离、独立验证、Figma-only UI 契约** 这些骨架设计是合理的，应该保留。
- **真正需要动刀的是“状态、审批、交接、文档单一事实源”四件事**，而不是再加阶段或再加规则。
- 当前流程在机制上并未闭合：**Stage 02 一旦按 AGENTS 要求运行 `request-review`，`workflow-state.json` 被重写，01→02 交接哈希立即失配，Stage 02 的 `transition` 会被自己的门禁挡住。** 现有历史只能靠 `handoff-create`/手工重建才走通。
- 另有 **8 处正则错误会让 UI 相关的 06/08/09/10 门禁脚本直接崩溃**，未来任何 UI Change 都无法完成这些阶段。
- 当前活动 Change 的绑定仍是 v0.2.2（基线已到 v0.3.0），`check-change` 与 `check-baseline-impact --strict` 均失败；Stage 02 现在“可以进入”，但继续之前必须先处理这些过期产物。

### 0.2 最高优先级（P0，按阻断程度排序）

| # | 问题 | 影响 | 证据 |
|---|---|---|---|
| P0-1 | 8 处正则把全角 `）` 当分组结束符，`re.search` 运行时抛 `missing ), unterminated subpattern` | UI Change 的 06/08/09/10 门禁脚本不可用；当前 no-UI Change 侥幸绕开 | `scripts/check-acceptance.py:65`、`check-code-review.py:53`、`check-independent-verification.py:93`、`check-figma-audit.py:360,361,436,438,440` |
| P0-2 | Stage 01 交接把 `workflow-state.json`、`AGENTS.md` 等可变/工具产物按 SHA-256 锁定 | `request-review`/`approve`/任何状态写入都会让 01→02 失效，触发 Stage 01 重批级联 | `docs/STEP-ARTIFACT-CONTRACTS.json` step 01；`workflow/handoffs/project/01-...json`；`scripts/workflow.py:70-85,178-216` |
| P0-3 | 审批与证据顺序死结：证据必须先生成（含 `pending`），`transition` 又要求证据里 `approval.status=approved` | 每次都要审批后手改 evidence；或提前伪造批准；两者都违背流程 | `scripts/workflow.py:332,414-420,442`；`docs/P0-RUNTIME-GOVERNANCE.md:77` |
| P0-4 | `reopen` 删除 `approvals_history`，但不清理/标记下游交接与产物；旧 handoff 仍显示 approved | 审计历史丢失；stale handoff 与 stale 设计产物混淆当前状态 | `scripts/workflow.py:547-574`；`workflow/handoffs/workflow-context-bundles/05→08` 仍存在 |
| P0-5 | 状态/绑定/基线版本漂移：state 仍为 0.2.2，manifest 为 0.3.0；active Change binding 为 0.2.2；Q-003 文案仍写“open” | `check-change` 阻断设计阶段；`baseline-impact --strict` 失败；Change 无法继续 | `workflow-state.json` baseline 块；`baseline-binding.json`；`check-baseline-impact.py workflow-context-bundles --strict` 退出 1；`baseline-governance.py check-change --phase design` 退出 3 |

### 0.3 当前仓库状态（审计时）

- `workflow-state.json`：`current_step=02-requirements-analysis`，`completed_steps` 仅 `01-project-bootstrap`。
- `workflow.py check-entry --step 02-requirements-analysis`：当前返回 `ENTRY_READY`（0）。
- 但 `request-review 02` 会写 `pending_approvals` 与 `last_updated`，使 01→02 中的 `workflow-state.json` 哈希失配；这是 P0-2 的具体失败路径。
- 工作区有 85 个已修改/未跟踪条目；`docs/architecture/baseline-manifest.json`、`constraint-registry.json`、活动 Change、全部 `workflow/evidence` 与 `workflow/handoffs` 均未提交。冻结基线绑定的是**工作区**而不是某个 commit。
- 当前基线校验器本身是健康的：`check-requirements --strict`、`check-reference-research --strict`、`check-architecture-baseline --strict`、`baseline-governance audit --require-frozen` 均通过（0，overall v0.3.0，12 条 ACTIVE 约束）。

---

## 1. 总体流程是否需要优化

### 1.1 骨架合理，保留

- 01–04 项目级一次完成：初始化 → 需求 → 架构/基线冻结 → 路线图；05–10 每个 Change 走：提案 → UI → 详细设计 → 实现 → 独立验证 → 验收/归档。阶段边界清晰，职责分离正确。
- 项目基线 vs Change 两条轨分离；`baseline-impact.md` + `baseline-binding.json` 把共享约束带入每个 Change，这是本工具包的强项。
- 09 独立验证与 08 实现分离、Figma-only 06、机器化 UI 几何/Token 证据，这些都是高质量设计，不建议削弱。
- 风险档位（LOW/STANDARD/HIGH）已在 BR-003/BR-006/`change-sizing.md` 中定义；问题只是自动化尚未落地（`risk-tier-check-profiles`）。

### 1.2 五个机制性问题（必须修）

#### 1.2.1 交接绑定对象错误：把“状态/生成物/工具脚本”当成审批产物

当前 `transition` 会把 evidence 中所有 `created/updated/verified` 的输出都哈希进 handoff，且“可变”只由“后续 DAG 阶段是否也声明同一路径”决定。结果是以下文件被锁定：

- `workflow-state.json`（Stage 01 输出，但每次 `request-review`/`approve`/`transition` 都会重写它）。
- `AGENTS.md`（Stage 01 输出；任何流程文档修订都会改它）。
- `docs/architecture/baseline-manifest.json`、`constraint-registry.json`（Stage 03 输出，但基线修订命令会在 DAG 之外重写它们）。
- `docs/product/BASELINE-INDEX.md`（Stage 02 输出，`gen-baseline-index.py --write` 会重生成）。
- `scripts/check-required-files.sh`（Stage 03 evidence 额外列入）、`scripts/check-roadmap.py`（Stage 04 evidence 额外列入）、`scripts/check-design-sections.py`（Stage 07 evidence 额外列入）等工具脚本。

**失败场景**：任何一次流程优化（包括本次要修的正则或状态机）都会改写这些文件 → 上游 handoff 哈希失配 → `check-entry` 拒绝下游 → 只能 `reopen` 并重新人工审批。`reopen_history` 已经记录了 9 次 reopen、4 次 Stage 01 重批；其中多条明确写着“workflow-state.json 改变导致 01→02 交接状态哈希失配”。

**建议**：把交接分为三类：
1. **决策/验收产物**：proposal/spec/design/test-cases/traceability/reports/acceptance —— 严格哈希。
2. **机器管理/生成物**：workflow-state、baseline-manifest、constraint-registry、BASELINE-INDEX、baseline-status —— 只验证存在，不进入哈希。
3. **流程工具脚本**：scripts、prompts、skills、AGENTS —— 不属于阶段业务交付；工具修复走自身 Change/版本，不应让阶段重批。Stage evidence 中非契约声明的额外 output 不应被哈希（或显式标 `evidence_only`）。

#### 1.2.2 审批与证据顺序死结

AGENTS 规定的顺序是：生成 evidence → `request-review` → 停轮 → 用户“review passed” → `approve` → `transition`。但 `parse_evidence` 对 02–10 要求 `evidence.approval.status=approved`；`approve` 只写 state，不写 evidence。于是必须审批后手改 evidence 才能 transition。P0 文档甚至明确要求这样做（`docs/P0-RUNTIME-GOVERNANCE.md:77`），这与“evidence 先生成、不得伪造审批”的规定自相矛盾。

**建议**：
- `transition` 以 `state.approvals_history` 为审批唯一权威，不再要求 evidence 里的 approval 块；evidence 的 `approval` 可保留为“记录”而非“门禁条件”。
- 若必须保留 evidence 字段，`approve` 应自动把批准信息写回 evidence（或生成 `approval` sidecar），避免手改。
- `request-review` 应生成“评审包”：artifact 路径 + 当时的 SHA-256 + 检查命令/退出码摘要；`approve` 校验哈希未变化，任何人改过内容必须重新评审。这同时解决“审批不绑定内容”的问题。

#### 1.2.3 `reopen` 失效不彻底，且删除审计历史

- `reopen` 只从 `completed_steps/pending/blocked/approvals_history` 删除目标及下游；不删除、也不标记 `workflow/handoffs/*` 中的旧交接。当前 `05→06`、`06→07`、`07→08` handoff 仍存在且 `approval=approved`，但 state 里 05–07 已未完成。
- `approve` 写入 `approvals_history` 时按 `step_id` 替换，不区分 `change_id`；下一个 Change 的同一阶段会覆盖上一个 Change 的批准记录。
- `migrate-state` 可以在没有 reopen_history 的情况下重置步骤，且 `load_state` 不校验 `completed_steps` 的依赖闭包；可造成“03 未完成但 04–10 已完成”的状态。

**建议**：reopen 时生成 `workflow/evidence/reopen-<timestamp>.json`，列出被失效的 step、handoff、artifact 哈希与原因，并在这些 handoff 内写 `superseded_by`/`invalidated_at`；保留 `approvals_history` 为 append-only，新增 `superseded_at`/`reopen_reason`；`load_state` 增加依赖闭包校验；`migrate-state` 复用 reopen 语义并写审计记录。

#### 1.2.4 审批/评审内容不受哈希保护

`request-review` 只记录 `targets`（路径列表）与 summary，不记录内容哈希；`approve` 不校验；当前阶段产物在 pending 期间仍可被 Write/Edit（hook 允许当前阶段写入）。这意味着用户批准的内容可能随后被改掉，而审批仍显示 approved。

**建议**：pending 条目存 `{path, sha256}`；`approve` 校验全部匹配；`transition` 再校验一次。hook 在 pending 状态下也应把当前阶段 artifact 视为只读，除非重新 `request-review`。评审包与 handoff report 落盘（例如 `workflow/evidence/<step>-review.md`），避免“聊天里的报告”不可追溯。

#### 1.2.5 基线状态与绑定漂移

- `workflow-state.json` baseline 块：overall 0.2.2 / product 0.2.0 / test_quality 0.2.0；`baseline-manifest.json` 与 `baseline-status.md`：0.3.0 / 0.3.0 / 0.3.0。`sync-baseline-index` 未在 BCR 冻结后运行。
- 活动 Change：proposal/design/tasks/baseline-impact/binding 全部写 v0.2.x；Q-003 仍写“open / Stage 08 blocked”，但 Q-003 已由 BCR 关闭并按 HIGH 执行。
- `baseline-impact.md` 仍 `Status: REVIEW`，`Allowed to enter detailed design: YES (...)` 带括号说明，`check-baseline-impact --strict` 因“精确单词值”规则失败。
- `docs/project/baseline-audit-report.md` 仍为 v0.2.2 候选、Q-003 open、无 active Change。

**建议**：`baseline-governance freeze/close-amendment/refresh-hashes` 结束时自动调用 `workflow.py sync-baseline-index`，并在 `audit --require-frozen` 中增加“state baseline 与 manifest 一致”检查；对 active Change 执行 rebase/refresh-binding（记录 NO_IMPACT 或 REBASE_REQUIRED），并统一把文档版本更新到 0.3.0。

### 1.3 流程比例与节点设计

- **每个 Change 有 6 个人工审批停点（05–10）**；即使无 UI、无 API、风险 LOW，也至少 5–6 次。当前没有“低风险快速路径”，风险档位只影响“检查集”，不影响“阶段数/审批数”。
- **06 对无 UI Change 仍走完整阶段 + 人工审批**：活动 Change 就是 no-UI，却产生了 `figma-audit.md` N/A、一次完整 Stage 06 评审。建议：把 06 做成**条件阶段**——当 05/07 确认 `UI: N/A` 时，机器记录 N/A 并跳过人工审批（仍保留证据），或把 N/A 判定并入 05/07。
- **05 写初始 `design.md`，07 再重写为统一设计**：同一路径被两个阶段写，导致 `mutable_by_design` 与重复评审。建议 05 只写 proposal/spec/tasks/US/AC/impact/binding，`design.md` 由 07 独占；初始设计决策放进 `proposal.md` 或 `design-notes.md`。
- **08 会更新 `tasks.md` 复选框，但 `tasks.md` 未声明为 08 输出**；同类的还有 `traceability.csv`（OUTPUT-FLOW-AUDIT 说 08–10 append，契约说 08–10 read-only，两者矛盾）。建议明确单一写者/可变声明。
- **08 的“实际源代码/测试”没有具体路径与修订指纹进入 handoff**；09 依赖“revision/diff fingerprint”但未成为 08 的声明输出。建议 08 输出 `design/evidence/implementation-diff.json`（commit/diff SHA）并进入 handoff。
- **单活动 Change**：`workflow-state.json` 只有一个 `active_change_id` 与一个线性 `current_step`；路线图里“三个 Change 可并行规划”只能并行规划，不能并行执行。若需要并行，必须重新设计状态模型；若不需要，路线图与文档应明确“串行执行”。
- **无 Change 放弃/暂停路径**：`next-change` 要求前一个 Change 完成 10 并验收；没有 `abandon-change`/`pause-change`，路线图调整时只能 reopen/migrate。

### 1.4 上下文与入口文档

- `prompts/00-next-step.md` 要求先读 `workflow-state.json`（30.9 KB）、`docs/PROCESS-MAP.md`（13.7 KB）、`docs/OUTPUT-TEMPLATE-MATRIX.csv`（20.5 KB），再加上契约记录；这与 8 组/12,000 字符目标直接冲突。
- `docs/STEP-ARTIFACT-CONTRACTS.json` 71.5 KB；`STAGE-IO-OVERVIEW.md` 68.5 KB；`STEP-ARTIFACT-CONTRACTS.md` 41.9 KB。三份都描述同一批 I/O 事实，只有 JSON 是机器权威；MD 是手写副本，overview 是生成视图但生成器里还留有旧文案。
- 当前 `agent-context.py` 仍主要输出“路径清单”，不渲染实际文本、不计算字符数；这正是活动 Change `workflow-context-bundles` 要解决的。建议在该 Change 中一并把 prompt 00 的默认读取集改成“由 agent-context 生成”，而不是手工必读三份大文件。

---

## 2. 逐节点判断（01–10）

| 阶段 | 结论 | 主要问题 | 建议动作 |
|---|---|---|---|
| 01 project-bootstrap | **必须优化** | 把 state/AGENTS/工具报告当交接产物；01 审批三处不一致；入口文档缺少 review 步骤 | 把 state/AGENTS 从 handoff 哈希中移除或标记 volatile；统一 01 审批策略；把 `check-package`/`check-entry` 写进入口 |
| 02 requirements-analysis | **基本合理，需少量优化** | 17 个产物；`BASELINE-INDEX.md` 生成物被哈希；`workflows/glossary/assumptions/lessons/id-conventions` 仍是 READY_FOR_REVIEW/draft 却在 FROZEN 域；上下文 8/8 顶格 | 把生成物列为 volatile；冻结时统一文件状态/版本；把 prompt 02 的必读集交给 agent-context |
| 03 project-architecture-baseline | **必须优化** | manifest/registry/baseline-status 被哈希，但基线修订会在 DAG 外改写；冻结域含 draft 文件；audit report 过期；baseline hash 未归一化 CRLF | 把治理产物列 volatile；freeze/close-amendment 自动更新文件状态/版本与 state；统一 hash 归一化；刷新 audit report |
| 04 proposal-planning | **需要优化** | 只声明 roadmap 输出，但 evidence 额外把 `check-roadmap.py` 哈希；`openspec new change` 归属 04/05 不清；roadmap 校验器只认中文标题 | evidence 只哈希声明产物；明确 Change 创建归属 05 或 04 的“批准后步骤”；roadmap 校验器加英文标题 |
| 05 feature-requirements | **必须优化** | 初始 `design.md` 与 07 双写；`tasks.md` 后续被 08 改但未声明；binding 0.2.2 过期；下游文案仍写 “stage 06 prototype/pages/interaction inventory” | 05 不写 `design.md`；`tasks.md` 声明 08 可变；rebase 并 refresh-binding；删除 legacy 文案 |
| 06 figma-design-review | **需要优化** | no-UI 仍走完整阶段+审批；UI 分支因正则崩溃不可用；`.jsx` 被拒；`figma-assets/README.md` 无模板 | 条件阶段化；修复 8 处正则；允许 `.jsx`、禁止 `.md` 冒充代码；补模板/脚手架 |
| 07 detailed-design | **需要优化** | 工具脚本 `check-design-sections.py` 作为输出被哈希；`design.md` 与 05 双写；仍依赖 legacy `block-inventory.csv` | 工具脚本不进 handoff；design.md 单一写者；移除 legacy 依赖 |
| 08 implementation-orchestrator | **必须优化** | `tasks.md` 未声明为输出；源代码/测试无 handoff 指纹；`test-all.sh`/`verify-before-completion.sh` 未在 prompt 点名；Verifier handoff 放在 review-stop 之前；`stage-evidence.example.json` 可假通过 | 声明 tasks.md 可变；输出 implementation diff；补 gate 命令；调整章节顺序；示例改 `not-run` 或让 transition 校验真实命令 |
| 09 independent-verification | **必须优化** | prompt 同时写“直接 transition”和“request-review”；正则崩溃；AC 覆盖只校验非空；未要求重跑 token 校验；身份靠信任 | 删除直接 transition；修复正则；要求 AC 全集、token 重跑；记录独立会话/上下文证据 |
| 10 acceptance-audit | **需要优化** | 仍写 “Figma/prototype audit”；未点名 `check-acceptance.py`；正则崩溃；`openspec archive -y` 无机器检查；lessons 长期为空 | 删除 legacy 文案；点名 gate；修复正则；增加 archive 无 `-y` 检查；记录流程事故到 lessons |

---

## 3. 文件层面

> 说明：这里覆盖流程工具包文件（Prompts、Skills、流程文档、脚本、模板、基线文档）。`workflow/evidence` 与 `workflow/handoffs` 属于运行证据，不作为“优化对象”，但其中的 stale handoff 需要失效标记。

### 3.1 必须修（会造成门禁不可用、错误通过或流程无法推进）

| 文件 | 问题 | 证据/复现 |
|---|---|---|
| `scripts/check-acceptance.py` | 正则 `Design source status）` 未闭合，UI Change 时崩溃 | `:65`；`re.compile` 报 `missing ), unterminated subpattern` |
| `scripts/check-code-review.py` | 同上，Stage 08 UI 检查崩溃 | `:53` |
| `scripts/check-independent-verification.py` | 同上，Stage 09 UI 检查崩溃 | `:93` |
| `scripts/check-figma-audit.py` | 5 处同类正则；且设计代码后缀允许 `.md`/`.ts`、拒绝 `.jsx` | `:307,360,361,436,438,440` |
| `scripts/workflow.py` | state 自哈希；审批/evidence 顺序；reopen 删历史；`handoff-create --file` 可空 checks/伪造 approved；`contract_doc` 损坏时 fail-open；`migrate-state` 无依赖清理；错误信息 “15” | `:48-50,70-85,178-216,332,386,414-420,442,501-521,547-574,329` |
| `scripts/build-figma-handoff.py` | 无引用、消费已删除的 page/block/interaction inventory、引用不存在的 check-design-spec.py | `:18-22,46-51,227` |
| `docs/WORKFLOW-STAGES.json` | 01 `human_approval_required=false`，与 AGENTS/BR-005/P0/实际历史冲突 | `:11`；AGENTS.md:22-26；P0:71；approvals_history 有 01 |
| `docs/STEP-ARTIFACT-CONTRACTS.json` | 01 输出包含 `workflow-state.json`；未声明 `tasks.md` 由 08 更新；未声明 volatile 文件 | step 01/08；`workflow.py output_paths_for_step('01...')` 只解析到 2 个路径 |
| `docs/STEP-ARTIFACT-CONTRACTS.md` | 42 KB 手写副本，无 MD↔JSON 校验 | `check-step-contracts.py` 不读 MD |
| `prompts/00-next-step.md` | 自相矛盾：:35 正确，:16/:42 直接 transition；无 request-review | `:16,:35,:42` |
| `prompts/04-proposal-planning.md` | 无 check-entry；Change 创建归属不清；未点名 check-roadmap --strict；使用 “review approved” | `:30,:43` |
| `prompts/05-feature-requirements.md` | 无 check-entry；下游仍写 “stage 06 prototype/pages/interaction inventory”；使用 “review approved” | `:40,:43` |
| `prompts/08-implementation-orchestrator.md` | 无 check-entry；未点名 test-all/verify-before-completion；Verifier handoff 在 review-stop 之前 | `:44,:48-50` |
| `prompts/09-independent-verification.md` | `:36` 直接 transition，与 `:40` 的 review 流程矛盾；无 check-entry | `:36,:40` |
| `prompts/10-acceptance-audit.md` | 仍写 “Figma/prototype audit”；未点名 `check-acceptance.py`；无 check-entry | `:10-14` |
| `.claude/skills/workflow-orchestrator/SKILL.md` | `:21/:50` 直接 transition，与 `:54-59` 的 review 规则矛盾 | `:21,:50` |
| `.claude/skills/proposal-planning/SKILL.md` | 把 US/AC 当 04 输入（实际 05 才产生）；`check-roadmap.py` 未带 `--strict` | `:60,:38` |
| `.claude/skills/feature-requirements/SKILL.md` | 下游写 “US/UC/ACs”，但 UC 已明确禁止 | `:65` |
| `.claude/skills/acceptance-audit/SKILL.md` | 仍写 “Figma/prototype audit”；未点名 `check-acceptance.py` | `:14` |
| `README.md` / `README-zh.md` | 当前状态表 4/6 行错误（Stage 01 未完成、无 Change、baseline 0.1.0 DRAFT、OpenSpec 空）；“initialized state”  false；正文又直接 transition | `:5,:11-15,:46,:48` |
| `templates/change-assets/design/baseline-impact.md` | 枚举值（`DRAFT/REVIEW/APPROVED`、`YES/NO`）无法通过 strict 精确值校验；活动 Change 已失败 | `:4,:70-73`；`check-baseline-impact.py:34-43` |
| `templates/product/reference-research.md` | `PRESENT / NONE` 占位符被解析器优先判为 NONE | `:20`；`check-reference-research.py:105-108` |
| `templates/workflow/stage-evidence.example.json` | 示例 checks=passed + 占位 command，`workflow.py` 只信任 status/exit_code/log 存在 | `:33-36`；`workflow.py:299-318` |

### 3.2 需要优化（一致性、可维护性、可移植性）

**Prompts（其余）**
- `prompts/01`、`02`、`03`、`06`、`07`：补 `check-entry`；把 `review approved` 统一为 `review passed`；删掉“Read/update workflow-state.json”改为“read-only，只经 transition 推进”；补点名各自的 contract gate。
- `prompts/workflow-prompts.md`：可保留；建议把全局 review 规则与 check-entry 规则合并进 00。

**Skills（其余）**
- `project-bootstrap`、`requirements-analysis`、`project-architecture-baseline`、`figma-design-review`、`detailed-design`、`implementation-orchestrator`、`independent-verifier`：与 Prompt 有 26–37% 的语义重复；补统一的 “state read-only” 表述；修正编号/阅读顺序等小缺陷。
- `openspec-archive-change`：需要在技能开头加“本仓库只能在 10 阶段验收通过后使用”，否则可绕过 09 PASS/验收。
- `openspec-apply-change`、`openspec-explore`、`openspec-propose`、`openspec-sync-specs`、`openspec-update-change`：本身是通用 OpenSpec 助手，可保留；但建议在项目层加一个统一 guard/说明，禁止在 02–04 直接创建/实现 Change。

**流程文档**
- `AGENTS.md` / `AGENTS-zh.md`：12 KB 常驻；技术栈 PENDING 文案已过期；审批规则与 DAG 冲突；UI 细节可外链；建议缩为路由索引 + 明确 01 策略。
- `docs/PROCESS-MAP.md`：表缺少 00 行；01 检查清单不全；06 no-UI 分支未写；把 gate 详情删掉改链接。
- `docs/TEMPLATE-POLICY.md`：仍列“page/event inventory”“prototype audit”；补状态/owner/date 头。
- `docs/P0-RUNTIME-GOVERNANCE.md`：补 state 自哈希、approve/evidence 顺序、reopen 失效、review 哈希；删 “15” 残留；明确单活动 Change。
- `docs/SUPERPOWERS-MAPPING.md`：`### Impact of Changes to Existing Code` 与 `check-design-sections.py` 要求不符，必须改成 `### Existing Code Change Impact`；删除重复的 methods 最小值。
- `docs/BASELINE-FEATURE-INTERACTION.md`：`baseline-impact` 起始阶段写 03（应为 05）；§9.3 仍用旧 17 阶段编号（08/10/11–12/14–15），必须改成 01–10；补状态头。
- `docs/INPUT-OUTPUT-POLICY.md`：本身 OK；补一句“prompt 00 的默认读取集必须由 agent-context 生成，不得手工必读大文件”。
- `docs/STAGE-IO-OVERVIEW.md` / `-zh`：68/62 KB，生成器 `scripts/stage-io-report.py:98` 仍写 “prototype/page inventory”；建议拆成每阶段一页或 `--stage` 输出，中文由同一源生成。
- `docs/OUTPUT-FLOW-AUDIT.md` / `-zh`：DRAFT 历史日志；59 vs 66 计数；引用不存在的 `design-plan.md`/`api-traceability.csv`；零消费者；建议归档到 `docs/archive/` 并标 SUPERSEDED。
- `docs/project/baseline-audit-report.md`：v0.2.2/Q-003 open/无 active Change；需刷新或归档。
- `docs/project/toolchain-report.md`：READY_FOR_REVIEW；Superpowers 现可用但报告写 “Not discoverable”；含绝对路径；需刷新。
- `docs/adr/README.md`：中文单语、无语言切换；v0.2.2 与整体 0.3.0 关系不清。

**基线/产品文档**
- `docs/product/workflows.md`、`glossary.md`、`assumptions.md`、`lessons.md`、`id-conventions.md`：仍为 READY_FOR_REVIEW / v0.2.0-draft，却在 FROZEN product v0.3.0 域；必须统一状态/版本或明确排除出冻结域。
- `docs/architecture/api-conventions.md`、`containers-and-deployment.md`、`data-flows.md`、`frontend-conventions.md`、`logical-erd.md`：状态 FROZEN 但版本写 `v0.2.0-draft`；应改为对应冻结版本。
- `docs/product/reference-research.md`：Stage 02 已批准但状态仍 READY_FOR_REVIEW；未进入 manifest 哈希。
- `docs/product/BASELINE-INDEX.md`：生成物被 Stage 02 哈希；索引未覆盖 proposal-roadmap/reference-research；应改为 volatile。
- `docs/architecture/baseline-manifest.json`：只哈希 7 个 product 文件；建议覆盖全部正式 product 文件，或明确哪些是“常驻非冻结”。
- `docs/product/proposal-roadmap.md`：表内行仍写 product v0.2.0，而表头写 v0.3.0；更新行版本。
- `workflow-state.json`：baseline 块过期；建议移除（由 manifest 派生），或自动 sync 并参与检查。
- `openspec/changes/workflow-context-bundles/*`：proposal/design/tasks/baseline-impact/binding 全部 v0.2.x；Q-003 文案过期；`baseline-impact` strict 失败；`approval-07` 写 US-001–003 但只有 001/002。需要 rebase/refresh 后再评审。

**脚本（其余）**
- `scripts/next-step.py`：不读 `current_step`，只在依赖未完成时 warning 后仍输出 NEXT_STEP；输出提示缺 request-review。
- `scripts/baseline-governance.py`：hash 未 CRLF 归一化；无 state 同步；`init-binding --force` 绕过 rebase；`previous_fingerprints` 记录时机错误；无写锁。
- `scripts/check-step-contracts.py`：硬编码 02–10；不校验 MD/JSON 一致性；不校验 01 approval flag。
- `scripts/check-roadmap.py`：只认中文标题。
- `scripts/check-required-files.sh`：缺 baseline manifest/registry/BASELINE-BRIEF/BASELINE-INDEX/reference-research 等 9 个 Stage 02 产物。
- `scripts/check-test-cases.py` / `check-inventory.py`：仍依赖已退役的 `block-inventory.csv`；PAGE 集合未拒绝额外 PAGE。
- `scripts/check-api-traceability.py`：`--strict` 无实际效果。
- `scripts/check-output-context.py`：无声明输出时套用全部 budget pattern。
- `scripts/check-figma-layout.py`：同 PAGE 多 route 未拒绝；空 expected text 跳过断言。
- `scripts/check-design-tokens.py`：未映射 token 和非 color/number 类型被静默跳过。
- `scripts/check-independent-verification.py`：AC 集合未与 user-stories 对比；未要求 token 重跑。
- `scripts/agent-context.py`：`RESIDENT` 死表含 `'16'`；仍不渲染内容/不计算字符（活动 Change 范围）。
- `scripts/stage-io-report.py`：生成器旧文案；source hash 未归一化行尾。
- `scripts/new-change-assets.sh`：缺 `interface-catalog.csv`、`figma-assets/README.md`、`independent-verification.schema.json`。
- `scripts/check-change.sh`：重复嵌套 if；未接入 transition。
- `scripts/README.md` / `-zh`：缺 12 个活动脚本（check-step-contracts、next-step、method_evidence、baseline-impact、多个 test-*）；仍保留历史删除脚本；“handoff-create 会重验 gates” 与 `--file` 路径不符。
- `.claude/hooks/stage-boundary-guard.py`：仅拦 Write/Edit/MultiEdit/NotebookEdit；Bash 写可绕过；state 不可读时 fail-open；允许改已批准阶段产物；未保护 handoff JSON。

**模板（其余）**
- `templates/change-assets/design/figma-audit.md`：`.jsx` 与校验器冲突；重复 Design source status；示例带登录页/Noto Sans 具体值。
- `templates/change-assets/design/figma-code/README.md`：写 `.jsx` 但校验器拒绝。
- `templates/change-assets/design/figma-layout.csv`：只有 PAGE-001 行，同模板 PAGE 列表有 001–006；具体登录页文案。
- `templates/change-assets/design/baseline-binding.json`：硬编码 FROZEN/REPLACE_WITH_CHANGE_ID，与生成器字段不一致。
- `templates/workflow/step-handoff-report.md`：未登记到 OUTPUT-TEMPLATE-MATRIX；建议提升为必需模板。
- `templates/product/BASELINE-BRIEF.md`：未登记矩阵。
- `templates/project-baseline/baseline-change-request.md` / `baseline-audit-report.md`：TODO/空值多，应 PENDING + reason。
- `templates/change-assets/evidence/acceptance.md` / `code-review.md`：TODO 占位符，与 TEMPLATE-POLICY 的 PENDING 约定不一致。
- `openspec/config.yaml:8`：仍允许“detailed frontend/backend design 作为辅助文件”，与统一五节 design.md 策略冲突。
- `docs/examples/golden-change.md`：仍把 “Prototype and Page Inventory” 当权威载体；US 表 5 列 vs 当前模板 7 列。
- `.claude/settings.local.json`：已跟踪；包含已删除脚本的 allow 条目和危险 `rm -rf .claude/skills/... *`；建议从 git 移除并重建。
- `.gitignore`/`.gitattributes`：不存在；`__pycache__`/`.lock`/`.tmp`/证据日志/本地设置没有统一策略；行尾 LF/CRLF 会造成 baseline hash 与生成视图 hash 漂移。
- 无 CI：所有门禁只在本机运行，审批身份与执行真实性依赖信任。

### 3.3 基本可用（保留，仅需抽检/小修）

- 以下 Skills 本身可用：`openspec-apply-change`、`openspec-explore`、`openspec-propose`、`openspec-sync-specs`、`openspec-update-change`（建议加项目 guard，但不改主体）。
- 以下脚本当前通过或逻辑基本正确：`check-architecture-baseline.py`、`check-baseline-impact.py`（规则本身合理，模板需改）、`check-interface-catalog.py`、`check-api-io-mapping.py`、`check-requirements.py`、`check-reference-research.py`、`check-traceability.py`、`check-output-template-matrix.py`、`check-output-consumption.py`、`check-design-sections.py`、`check-method-evidence.py`/`method_evidence.py`、`check-package.py`、`gen-baseline-index.py`、`stage-io-report.py`（生成器需改文案）、`validate-openapi.sh`、`verify-before-completion.sh`、`test-all.sh`、多数 `test-*.py`。
- 文档：`docs/INPUT-OUTPUT-POLICY.md`、`docs/OUTPUT-TEMPLATE-MATRIX.csv`、`docs/WORKFLOW-STAGES.json` 的 DAG 结构本身可用。
- 模板：`templates/product/` 多数、`templates/change-assets/design/` 多数、`templates/workflow/stage-evidence.schema.json`、`templates/change-assets/design/independent-verification*` 与验证器一致。

### 3.4 建议归档/删除

| 文件 | 建议 | 原因 |
|---|---|---|
| `docs/OUTPUT-FLOW-AUDIT.md` / `-zh` | 移到 `docs/archive/` 并标 SUPERSEDED | DRAFT、计数过期、引用不存在模板、零消费者 |
| `scripts/build-figma-handoff.py` | 移到 `scripts/legacy/` 或删除 | 无引用、消费已删除产物、引用不存在脚本 |
| `scripts/check-inventory.py` | 明确标 legacy，移出 README 主表 | 仅服务历史 Change |
| `docs/superpowers/plans/2026-11-13-method-and-interface-process.md` | 移到历史/归档区 | 已完成计划、无引用、含与英文主文档冲突的旧约束 |
| `docs/project/baseline-audit-report.md` | 刷新到 v0.3.0 或归档旧版 | 当前仍写 v0.2.2/Q-003 open |
| `docs/project/toolchain-report.md` | 刷新 | 工具状态/版本/绝对路径过期 |
| `docs/adr/README.md` | 英文化并加语言切换，或明确双语 | 英文主仓库中的中文单语文件 |
| `templates/project-baseline/constraint-registry.json` | 英文化 + 扩展示例 | 仅 6 条中文 DRAFT 示例，项目有 12 条 ACTIVE |

---

## 4. 建议修复顺序与路线映射

### P0（先修，否则流程无法可靠推进）

1. **P0-A：8 处正则一行修复**（`check-acceptance.py:65`、`check-code-review.py:53`、`check-independent-verification.py:93`、`check-figma-audit.py:360/361/436/438/440`）。同时补 UI/no-UI 分支测试，防止回归。**不涉及策略，可立即做。**
2. **P0-B：交接绑定重构**（`workflow.py` + contract + evidence）：
   - 明确 `volatile` 清单：`workflow-state.json`、`baseline-manifest.json`、`constraint-registry.json`、`BASELINE-INDEX.md`、`baseline-status.md`、`AGENTS.md`、scripts/prompts/skills。
   - 非契约声明的额外 output 不进入 handoff 哈希（或标 `evidence_only`）。
   - `handoff-create` 必须要求 `--evidence`；`--file` 路径只能用于非人工审批阶段。
   - `load_state` 校验依赖闭包；`migrate-state` 复用 reopen 语义并写审计。
3. **P0-C：审批完整性**（`request-review`/`approve`/`transition`）：
   - pending 条目记录 artifact 哈希；approve 校验；改内容必须重新评审。
   - transition 以 `approvals_history` 为审批权威；停止要求 evidence 内 `approval.status=approved`，或让 approve 写回 evidence。
   - 生成持久化 review packet/handoff report。
4. **P0-D：reopen 失效与审计**：
   - 生成 reopen 失效清单；给旧 handoff 写 `invalidated/superseded`；保留 approvals_history 并加 supersede 标记；不删除历史。
5. **P0-E：基线同步与 active Change rebase**：
   - `baseline-governance freeze/close-amendment` 自动 `sync-baseline-index`；audit 增加 state/manifest 一致性检查。
   - 将 `workflow-context-bundles` 的 proposal/design/tasks/baseline-impact/binding 更新到 v0.3.0、Q-003 CLOSED、HIGH；修复 baseline-impact 精确值；refresh-binding 或记录 NO_IMPACT/REBASE_REQUIRED。

### P1（高价值，建议纳入现有路线图）

6. **文档单一事实源**（对应 `artifact-source-of-truth`）：
   - JSON 为唯一权威；MD 生成或缩为两页规则；STAGE-IO 拆成每阶段一页/`--stage`；加 `--check`。
   - 归档 OUTPUT-FLOW-AUDIT；修复 README 状态表（改为运行 `workflow.py status`）；修复 AGENTS 状态行；修复 BASELINE-FEATURE-INTERACTION 的 17-stage 编号；修复 SUPERPOWERS 标题。
7. **Prompts/Skills 一致性与薄化**：
   - 每个 Prompt 加 `check-entry`；统一 “review passed”；删除 “update workflow-state.json”；点名各自 contract gate。
   - 抽出共享 stage protocol，减少 26–37% 重复；修正 04/05 Change 创建边界、05/10 legacy 文案、08 顺序、09 直接 transition。
   - 增加 `check-prompt-skill-parity.py`（或扩展 check-package），机器校验上述 token。
8. **模板/校验器对齐**：
   - 允许 `.jsx`、禁止 `.md` 冒充代码；修 baseline-impact 模板；修 reference-research 状态；roadmap 英文标题；check-required-files 补 9 个产物；matrix 增加完整性/未登记模板检查；new-change-assets 补三个文件；stage-evidence 示例改 `not-run` 或让 transition 校验真实命令/log。
9. **检查覆盖与测试**：
   - contract 增加 `required_checks`（命令+退出码期望），transition 校验；directory/bare-name output 严格化；AC 全集/PAGE 集合/token 重跑；补 UI/no-UI 测试与聚合 `test-scripts.sh`；把 `test-baseline-impact.py` 提交并登记。
10. **条件阶段与所有权**：
   - 06 条件化（no-UI 自动 N/A + 跳过人工审批）；05 不写 design.md；tasks.md 声明 08 可变；08 输出 implementation diff 指纹。
11. **上下文预算**：
   - prompt 00 的必读集改为 `agent-context.py` 生成；contract JSON 提供 `--step` 提取；STAGE-IO 拆分；在 `workflow-context-bundles` 中验收 8 组/12k 实际计量。
12. **仓库卫生与可移植性**：
   - 添加 `.gitignore`、`.gitattributes`（LF）；移除 tracked settings.local/pyc；baseline hash 与生成视图 hash 归一化；清理 stale allowlist；无 CI 时至少提供 `scripts/test-scripts.sh` 并在 Stage 01 运行。

### P2（结构增强，视需要启动）

13. 状态文件事件日志化（append-only JSONL + 小 state），避免 30 KB 无限增长。
14. 选择性 rebase：按产物哈希判断哪些阶段真的失效，避免全链 reopen。
15. 并行 Change / 放弃 Change / 暂停 Change 的状态模型与命令。
16. 审批身份强化（独立会话 ID、签名/CI、CODEOWNERS）。
17. 中英文成对维护的自动化新鲜度检查。
18. lessons 记录流程事故（当前 `lessons.md` 为空，但已发生 9 次 reopen）。

### 与现有路线的合并建议

| 现有 Change | 建议并入的内容 |
|---|---|
| `reliable-gate-runtime` | P0-A、P0-B、P0-C、P0-D、P1-9、P1-12（状态机/审批/正则/测试/仓库卫生） |
| `artifact-source-of-truth` | P1-6、P1-8、P1-11（文档单一源、模板/生成视图、上下文提取） |
| `workflow-context-bundles` | P1-11（agent-context 渲染/预算），并把 prompt 00 的读取集接入 |
| `risk-tier-check-profiles` | P1-10 的“条件阶段/轻量路径”部分（需政策确认是否允许跳阶段） |
| 新增小 Change（可选） | P1-10 的 06 条件阶段 + tasks.md/design.md 所有权；或并入 reliable/risk-tier |
| 新增小 Change（可选） | 基线选择性 rebase / baseline 同步（也可并入 reliable-gate-runtime） |

**顺序建议**：把 `reliable-gate-runtime` 提到 `workflow-context-bundles` 之前，或至少先做 P0-A/P0-B/P0-C 的最小热修复。当前活动 Change 自己的一次“Stage 02 上下文配置优化”就触发了 Stage 01 重批（reopen_history 2026-11-17T07:39），继续在旧机制上做上下文优化，成本会大于收益。

---

## 5. 本次实际运行过的校验（证据）

| 命令 | 结果 |
|---|---|
| `python scripts/check-requirements.py --strict` | 0，FLOW=1/NODE=9/DO=5/RD=9/BR=7 |
| `python scripts/check-reference-research.py --strict` | 0，3 questions / 3 records / 3 sources / 4 comparisons |
| `python scripts/check-architecture-baseline.py --strict` | 0，existing-system=True，third-party=True，constraints=12 |
| `python scripts/baseline-governance.py audit --require-frozen` | 0，BASELINE_FROZEN_AND_VALID，overall 0.3.0，12 ACTIVE |
| `python scripts/check-output-consumption.py` | 0，66 file outputs / 2 evidence-only / 55 producers |
| `python scripts/check-step-contracts.py` | 0，11 rows / 10 DAG stages |
| `python scripts/check-output-template-matrix.py` | 0，49 outputs |
| `python scripts/check-package.py`（子代理运行） | 0，17 Skills / 12 prompts |
| `python scripts/workflow.py check-entry --step 02-requirements-analysis` | 0，ENTRY_READY（但 request-review 后会因 state 哈希失配而阻断） |
| `python scripts/baseline-governance.py check-change --change-id workflow-context-bundles --phase design` | 3，CHANGE_BASELINE_BLOCKED（整体版本变化、product/test_quality 变化、QUALITY-EVIDENCE-001 绑定版本不一致） |
| `python scripts/check-baseline-impact.py workflow-context-bundles --strict` | 1，strict baseline impact gate failed（approved review state / detailed design gate） |
| `re.compile` 复核 8 处正则 | 全部 `missing ), unterminated subpattern` |
| `workflow.py` 声明输出解析复核 | Stage 01 只解析到 baseline-status 与 toolchain-report；AGENTS/state 未进入声明输出集合 |
| `prompts/*` token 复核 | 10 个阶段 Prompt 均无 `check-entry`；01–05 使用 “review approved”；00/09 存在直接 transition 文案 |

---

## 6. 结论

- **需要优化，且应优先修“机制”而不是继续堆“规则”。** 当前流程不是门禁太少，而是门禁之间互相绊倒：状态文件与工具脚本被当成审批产物，审批与证据顺序互斥，reopen 不彻底，文档多源漂移。
- **10 个阶段节点本身没有需要删除或合并的。** 需要的是：01 的审批策略统一、06 的条件化、05/07 的 design.md 单一写者、08 的 tasks.md/implementation diff 所有权、09/10 的 gate 点名与正则修复。
- **文件层面约 20 个“必须修”文件、约 40 个“需要优化”文件、其余基本可用。** 最高风险是 8 处正则、`workflow.py` 的交接/审批模型、README/AGENTS 的过期状态，以及活动 Change 的 v0.2.x 绑定。
- **建议顺序**：先做 P0-A 正则热修复与 P0-B/C/D 状态机/审批修复（并入或前置 `reliable-gate-runtime`），再完成 `workflow-context-bundles` 的 rebase，之后做文档单一源与模板对齐。
- **当前不要直接继续 Stage 02 并期待正常 transition**；先决定是采用 `reliable-gate-runtime` 修复状态机，还是明确接受 `handoff-create` 的手工重建作为临时路径（后者不建议常态化）。

