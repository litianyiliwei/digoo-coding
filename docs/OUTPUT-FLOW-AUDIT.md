# 阶段输出流转审计

> 2026-11-13 更新：新增阶段 02 `reference-research.md` 与阶段 07 `design/interface-catalog.csv`；文件型输出计数以 `scripts/check-output-consumption.py` 实际输出为准。
> 2026-11-11 二次更新：阶段 06 已改为 Figma-only。`pen.dev`、`prototype.pen`、`PAGE-*.html`、`prototype.md`、`manifest.json`、`design-tokens.json` 全部移出流程；06 的唯一 UI 产物是 `figma-audit.md`（Figma MCP 生成/读取快照 + PAGE 清单与映射 + UI 评审 APPROVED）。历史产物归档到各 Change 的 `design/legacy/`。当前契约以 `docs/STEP-ARTIFACT-CONTRACTS.json` 与 `docs/STAGE-IO-OVERVIEW.md` 为准。
> 2026-11-11 清理：旧顶层 `scripts/legacy`、`prompts/legacy`、`.claude/skills/legacy`、`templates/change-assets/legacy`、`workflow/evidence/legacy`、`workflow/handoffs/legacy`、旧原型快照与临时构建脚本已移至 `_trash/2026-11-11/`；本文历史段落中的旧路径保留为当时记录。

> 编号说明：本文记录重编号前的分析过程（旧编号 05/09/10/10b/11/12/13a–e/14b/15）。新编号映射：05→03、09→04、10→05、10b→06、11→07、12→08、13a→09、13b→10、13c→11、13d→12、13e→13、14b→15、15→16；以 `docs/WORKFLOW-STAGES.json` 为准。
> 2026-11-09 vibe 重构说明：阶段已进一步合并为 01–10（06=原型/页面清单，07=详细设计/接口/测试，08=实现，09=独立验证，10=验收），旧产物拆分（use-cases/design-plan/frontend-design/backend-design/test-design/api-traceability）已并入新载体。**第 3 节已更新为当前 01–10 拓扑；第 3.1 节及第 4–9 节保留旧 17 阶段历史分析。** 当前权威仍以 `docs/STAGE-IO-OVERVIEW.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 为准。

- Change ID：N/A（流程审计）
- 状态：DRAFT（分析报告，不改变阶段契约）
- 来源基线：`docs/STEP-ARTIFACT-CONTRACTS.json`、`docs/WORKFLOW-STAGES.json`、`docs/OUTPUT-TEMPLATE-MATRIX.csv`
- 关联需求/AC：N/A（流程文档）
- 生成日期：2026-11-06；最近复核：2026-11-10
- 版本：v0.3（当前 01–10 流转表）

## 1. 判定口径

| 状态 | 含义 |
|---|---|
| 已消费 | 下游阶段的 `inputs` 明确列出该文件/内容，或门禁脚本直接读取 |
| 间接消费 | 只被下游用“项目级基线/前后端详细设计”等聚合措辞引用，未列具体文件 |
| 仅留档 | 只作为阶段证据、审批记录或交接哈希存在，没有下游读取 |
| 未落盘 | 契约把“内容”列为输出，但没有指定文件路径，下游无法稳定消费 |

## 2. 总体结论

当前 01–10 主链路已闭合：01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10。每个阶段的文件型输入均可追溯到上游阶段或明确的“包内静态/外部材料”；59 个文件型输出全部有登记消费者（其中 1 个为纯证据），反向校验未发现“已读取但未登记”的引用（0 条）。状态机已在真实流程中验证：阶段 03 冻结后成功推进到 04，`check-entry 04` 返回 `ENTRY_READY`。

本轮复核确认的边界与设计选择：

1. **输入来源**：00 的流程文档属于包内静态权威，02 的业务材料属于外部输入，05/07 的 `openspec/specs/**` 属于归档态输入；它们没有 DAG 生产者是预期的，不应伪造上游产物。
2. **输出使用**：所有固定路径输出都有下游消费者；代码/测试结果、验收报告等“内容型输出”没有固定路径，由阶段门禁脚本（`test-all.sh`、`verify-before-completion.sh`、`check-independent-verification.py`）核验，而不是靠契约匹配。
3. **声明式共同产物**：`baseline-status.md`（01/03）、`design.md`（05/07）、`traceability.csv`（07 初始化，08/09/10 只追加）、`lessons/decisions/assumptions`（02/10）由多个阶段合法更新；handoff manifest 自动标记 `mutable_by_design`，下游只核验存在性，避免正常更新被误判为漂移。
4. **运行边界**：单个活动 Change；`next-change` 支持串行进入下一个 Change，不支持并发调度。返工通过 `reopen` 按依赖闭包回退。

## 3. 当前 01–10 逐阶段流转表

| 阶段 | 输入来源（可追溯生产者） | 输出消费者（已登记） | 判定 |
|---|---|---|---|
| 00 下一步编排 | `workflow-state.json`（运行时）；包内静态权威：`PROCESS-MAP.md`、`STEP-ARTIFACT-CONTRACTS.json`、`WORKFLOW-STAGES.json`、`BASELINE-FEATURE-INTERACTION.md`、`OUTPUT-TEMPLATE-MATRIX.csv`；真实产物/审批/OpenSpec CLI（外部） | 下一阶段判定报告（对话展示）；`workflow-state.json` → SYSTEM/运行时 | 入口阶段；静态权威无 DAG 生产者属预期；不得越过 pending/blocked。 |
| 01 项目初始化 | 用户项目目标与仓库位置、仓库现状（外部）；既有 `AGENTS.md`（自读自写） | `AGENTS.md` → ALL；`workflow-state.json` → SYSTEM；`baseline-status.md` → 03–10；`toolchain-report.md` → 03 | 外部输入；输出全部登记；`baseline-status.md` 与 03 为声明式共同产物，handoff 标记 `mutable_by_design`。 |
| 02 需求业务梳理 | 访谈/业务材料/旧系统资料/项目目标（外部）；既有 `docs/product/*`（若存在）；`openspec/specs/**`（只读归档） | requirements-analysis/workflows/data-objects/rd-matrix/business-rules → 03/04/05（workflows 亦 06/07）；glossary → 03/04/05；acceptance-policy → 03/04/07/10；open-questions → 03/04/05/06；BASELINE-BRIEF/role-permission/change-sizing → 03/04/05/10；decisions/assumptions/id-conventions → 03/04/05/10；lessons → 04/05/10；BASELINE-INDEX → 03 | 外部/只读输入；输出全部登记；`BASELINE-INDEX.md` 已补契约与消费记录。 |
| 03 项目总体架构 | 01（toolchain-report、初始 baseline-status）；02（需求全量 + 常驻基线）；open-questions（只读）；技术选型访谈/非功能需求（外部） | 架构/契约/测试 9 份 → 07/08；frontend-conventions → 06/07/08；containers-and-deployment → 07；baseline-status → 04–10；baseline-manifest/constraint-registry → 04/05 + 运行时基线门禁；baseline-audit-report → 04 | 输入闭合；输出闭合；22 条约束来源全部可定位；已冻结并实际推进到 04（`ENTRY_READY`）。 |
| 04 提案路线图 | 03（manifest/registry/status/audit-report）；02（需求全量 + 常驻基线）；open-questions；技术债（外部） | `proposal-roadmap.md` → 05 | 单输出、单消费者；合理。下一个 Change 由 `next-change` 重开 05 后再次读取。 |
| 05 提案级需求 | 04 roadmap；02 需求/常驻基线；03 基线；`openspec/specs/**`（只读归档）；open-questions | proposal → 06/07/09；spec → 06/07/08/09/10；tasks → 07/08/09；design → 06/07/08/09/10；user-stories → 06/07/08/09/10；baseline-impact/binding → 06–10 | 输入闭合；输出闭合；AC 是测试与验证的唯一锚点。 |
| 06 Figma 设计与评审 | 05 proposal/spec/design/user-stories；02 workflows/data-objects/rd-matrix/business-rules；03 frontend-conventions 第 9 节；baseline-status/impact/binding；Figma MCP（涉及 UI 时） | `figma-audit.md`（Figma MCP 生成/读取快照 + PAGE 清单与映射 + UI 评审）→ 07/08/09/10 | 输入闭合；唯一 UI 产物为 figma-audit.md；不再产出 pen/HTML/prototype.md/manifest/06 traceability/design-tokens。 |
| 07 详细设计 | 05/06（proposal/spec/tasks/design/US、figma-audit）；02（FLOW/DO/RD/BR/acceptance-policy/BASELINE-BRIEF）；03 架构/契约/测试/ADR；baseline-impact/binding；Figma MCP（可用时实时读取，否则用 figma-audit 落盘快照） | design.md → 08/09/10；test-cases → 08/09/10；openapi/api-io-mapping/io-catalog（有 API）→ 08/09；traceability → 08/09/10（本阶段初始化 PAGE→AC 并合并 API/测试） | 输入闭合；输出闭合；条件产物必须 `n/a` + `waiver_reason`。 |
| 08 实现验证 | 05 tasks/spec/US；06 figma-audit/PAGE 清单；07 design/test-cases/API/IO/traceability；03 架构/契约/测试；baseline；Figma | 代码/迁移/配置、测试与结果（内容型，无固定路径）；code-review → 09/10；实现证据；条件 BCR/ADR | 输入闭合；固定路径输出登记闭合；内容型输出由 `test-all.sh` / `verify-before-completion.sh` 核验。 |
| 09 独立验证 | 08 代码/revision/code-review/测试证据；05 proposal/spec/design/tasks/US；06 figma-audit；07 API/IO/test-cases/traceability；03/05 基线；Figma | independent-verification-report.md/json → 10 | 输入闭合；仅 10 消费；要求与 Builder 不同执行上下文。 |
| 10 验收归档 | 09 report/json；08 代码/测试/code-review；05 spec/US/traceability/design；06 figma-audit；07 test-cases；部署证据；05 baseline-impact/binding；03 baseline-status；02 acceptance-policy/BASELINE-BRIEF/change-sizing/lessons/decisions/assumptions/id-conventions | acceptance.md（纯证据）；lessons/decisions/assumptions → 后续 03/04/05/10；验收报告/批准记录；需要基线修订时提交修订请求并走 amendment 流程 | 输入闭合；10 的读后写已补；acceptance 标记 `evidence_only`；归档规格成为后续 Change 输入。 |

> 复核证据（2026-11-11）：`check-output-consumption.py` 通过，59 个文件输出 / 1 个纯证据 / 0 条未登记反向引用；`check-step-contracts.py` 11 条契约对应 10 个 DAG 阶段；`stage-io-report.py --check` 为最新。2026-11-11 阶段 06 规则收敛后重新生成。
> 计数说明：阶段 06 收敛后实际为 57 个；本轮补齐 07 对 `baseline-impact.md` 与 `baseline-binding.json` 的更新输出声明后为 59 个。后续以脚本输出为准。

### 3.1 旧 17 阶段逐阶段表（历史，勿用于当前流程）

| 阶段 | 已明确消费的输出 | 间接消费/仅留档的输出 | 无消费者或未落盘 | 建议 |
|---|---|---|---|---|
| 00 编排 | `workflow-state.json` 被 00/01/运行时读取 | 下一阶段判定报告只面向用户 | 可选写入 `docs/workflow/next-step-report.md`，无固定消费者 | 该报告保持对话输出即可；不要作为正式阶段产物强制落盘 |
| 01 初始化 | `workflow-state.json`、`baseline-status.md` 被后续阶段和门禁读取 | `AGENTS.md` 被所有 Agent 隐式读取；`toolchain-report.md` 只在本阶段 `next_inputs` 出现 | `toolchain-report.md` 没有下游输入 | 把工具链/环境约束加入 05 架构输入，或明确标记为“仅初始化证据” |
| 02 需求业务梳理 | requirements-analysis、workflows、data-objects、rd-matrix、business-rules 被 05/09/10/11 明确读取 | glossary 仅 05 读取；acceptance-policy 只被 05/09 笼统引用 | open-questions 只在 06 被读取 | 将 open-questions 加入 05/09/10 输入；acceptance-policy 加入 13e/15；glossary 加入 10/13a |
| 05 总体架构 | baseline-status、manifest、registry 被门禁和 09/10/13/14/15 读取；api/frontend/test conventions 分别被 13b/13c/13e 明确读取 | system-context、domain-boundaries、containers、data-flows、logical-erd、technology-decisions、ADR 只被 13a/13d 用“项目级基线”概括 | `baseline-audit-report.md` 没有下游输入 | 09 输入增加审计报告；13a/10/11/12 输入列出具体架构文件，禁止只写“基线” |
| 09 路线图 | `proposal-roadmap.md` 及候选范围/基线适用摘要被 10 读取 | 无 | 输出第 2、3 项其实是 roadmap 的字段，不是独立产物 | 合并为一个 roadmap 文件；10 的输入明确引用“候选 Change 行” |
| 10 提案需求 | proposal、specs、baseline-impact、baseline-binding 被 06/11/12/09–13/14/15/15 读取 | `tasks.md` 只被 14 明确读取；`design.md` 只被 14/15 读取；`user-stories.md`/`use-cases.md` 只被 06/11 读取 | 10/11/12 没把 `design.md` 列为输入；13/15/16 没把 US/AC 列为输入 | 把 `design.md` 加入 10/11/12/13e 输入；把 US/AC 加入 13/15/16 输入；tasks 加入 13a |
| 06 原型 | prototype-build、prototype-audit 被 11 明确读取；pen.dev 页面作为页面推导依据 | 无 | 无 | 保持；在 11 中明确“prototype 页面是草案，page-inventory 是批准后的权威清单” |
| 11 清单 | page/block/interaction 清单被 12/10/11/12/13e 读取 | 无 | 无 | 保持；明确 page-inventory 为唯一权威页面清单，figma-audit 只做映射核对 |
| 12 Figma 审计 | `figma-audit.md` 被 13a/13c 读取 | 13b 只把“Figma 交互”列为可选 | 无 | 保持；13b 明确读取 figma-audit 的交互/状态差异 |
| 13a 设计总控 | `design.md` 被 14/15 读取 | “任务分解/缺口清单”只体现在 `next_inputs` 文字 | 任务分解/缺口清单没有文件路径；13b–e 没读 `design.md` | 任务分解/缺口写入 `design.md` 的固定章节，或新增 `design/design-plan.md`；13b–e 输入列 `design.md` |
| 13b OpenAPI | `openapi.yaml` 被 13c/13d/13e/14/15 读取 | 无 | “operationId 到页面事件/AC 的追踪关系”没有文件，13e 无法稳定合并 | 新增 `design/api-traceability.csv`，或明确写入 `traceability.csv` 并声明由 13b 创建、13e 扩展 |
| 13c 前端设计 | `frontend-design.md` 被 13e/14 读取 | 测试/组件状态映射作为文档内的“Test plan”章节，未单独指定 | 无独立文件，容易被遗漏 | 明确为 `frontend-design.md` 的固定章节，并由 13e 引用章节名 |
| 13d 后端设计 | `backend-design.md`、`api-io-mapping.csv`、`io-catalog.csv` 被 13e/14/15 读取 | 无 | 无 | 保持 |
| 13e 测试设计 | `test-design.md`、`traceability.csv` 被 14/15/15 读取 | 无 | 无 | 保持；明确 traceability 为唯一追踪聚合文件 |
| 14 实现 | 代码/迁移/配置、测试代码与结果、code-review、实现证据被 15/16 读取 | 条件性 BCR/ADR 只进入基线修订流程 | 无 | 保持 |
| 15 独立验证 | report + JSON 被 15 明确读取 | 无 | 无 | 保持 |
| 15 验收归档 | acceptance、archive 结果、路线图/基线回写被后续 Change 和基线修订使用 | 无 | 无 | 保持 |

## 4. 重点问题

### P0：影响下游正确性的流转缺口

| 编号 | 问题 | 影响 | 建议 |
|---|---|---|---|
| F-01 | 13a 的“任务分解/设计缺口清单”没有文件 | 13b–e 无法确认设计范围和缺口，容易出现前端/后端各自补设计 | 写入 `design.md` 固定章节，或新增 `design/design-plan.md`；13b–e 明确读取 |
| F-02 | 13b 的 operationId 追踪关系没有文件 | 13e 只能从 OpenAPI 和交互清单重新推导，容易漏映射 | 新增 `design/api-traceability.csv`，13e 合并进 `traceability.csv` |
| F-03 | `design.md` 没被 10/11/12/13e 列为输入 | 13a 的统一设计决策可能被后续设计忽略 | 四个阶段输入明确加入 `design.md` |
| F-04 | US/UC/AC 没被 13/15/16 明确列为输入 | 测试和验收可能只依赖 specs，遗漏提案级 AC | 13/15/16 输入加入 `design/user-stories.md`、`design/use-cases.md` |
| F-05 | `open-questions.md` 只被 06 读取 | 未决问题可能绕过架构、路线图和提案需求 | 05/09/10 输入加入 open-questions |
| F-06 | `acceptance-policy.md` 没被 13e/15 明确读取 | 测试设计和验收口径可能与项目验收政策不一致 | 13e/15 输入加入 acceptance-policy |
| F-07 | `baseline-audit-report.md` 没有消费者 | 05 审计发现的缺口/待批项不影响路线图 | 09 输入加入 baseline-audit-report |

### P1：防漂移与可验证性

| 编号 | 问题 | 建议 |
|---|---|---|
| F-08 | 下游输入用“项目级基线”聚合，无法证明具体文件被读取 | 09–12 输入列出 system-context、data-flows、logical-erd、technology-decisions、ADR、api/frontend/test conventions 等具体路径 |
| F-09 | 页面事实有三处：prototype-build 页面清单、page-inventory、figma-audit 映射 | 明确权威顺序：06 草案 → 11 批准清单 → 12 只核对不重定义；12 的差异回到 11 修订 |
| F-10 | 追踪事实分散：11 的 Prompt 要求更新 `traceability.csv`，但 11 契约 outputs 未列出该文件；13b 的追踪关系只在“内容”里；13e 才声明产出 `traceability.csv`，同一文件存在多写者但所有权未定义 | 定义唯一 `traceability.csv`：11 初始化，13b/13e 只追加；契约在 11/13b/13e 中明确该文件为累计产物 |
| F-11 | UC/US 与 specs 重复描述同一行为 | 明确 specs 是规范行为唯一来源；UC/US 只保留场景、AC 和追踪 ID，不复制完整规格 |
| F-12 | 契约没有机器可读 `consumed_by` | 每个输出增加 `consumed_by` 列表，并新增 `check-output-consumption.py` 检查死输出 |

### P2：精简与降噪

| 编号 | 问题 | 建议 |
|---|---|---|
| F-13 | 01 `toolchain-report.md` 无下游消费者 | 加入 05 作为环境/工具约束输入，或标记 `evidence_only`，不纳入“必须被消费” |
| F-14 | 00 `next-step-report.md` 为可选文件 | 保持对话输出，不强制落盘；避免产生无人读取的文件 |
| F-15 | 09 输出把 roadmap 字段拆成三个“输出” | 合并为 `proposal-roadmap.md` 一个产物，字段级要求写在模板 |
| F-16 | 13c 的“测试用例/组件状态映射”未指定载体 | 明确为 `frontend-design.md` 的固定章节，13e 按章节引用 |

## 5. 建议的机制改造

1. **契约增加消费者字段**

   ```json
   {
     "outputs": [
       {
         "path": "docs/architecture/data-flows.md",
         "consumed_by": ["09-feature-design", "12-backend-detail-design"],
         "evidence_only": false
       }
     ]
   }
   ```

   对内容型输出，允许 `path` 指向文件章节，如 `openspec/changes/<change-id>/design.md#design-plan`。

2. **新增死输出检查**
   - 每个 `outputs` 必须有至少一个 `consumed_by`，或显式 `evidence_only: true`。
   - `consumed_by` 必须指向 DAG 中真实存在的后续阶段。
   - 下游 `inputs` 必须能反向找到上游输出（至少路径匹配）。
   - 接入 `check-package.py`，新增 `scripts/check-output-consumption.py`。

3. **统一追踪与页面权威**
   - `traceability.csv`：11 初始化，13b 追加 API→EVT/AC，13e 追加 TEST→AC/API/IO。
   - `page-inventory.csv`：11 批准后为唯一页面清单；06 的页面清单只作草案；12 只核对，不另建页面 ID。

4. **把“内容输出”改成“文件+章节输出”**
   - 13a：`design.md#design-plan`（任务分解/缺口）。
   - 13b：`design/api-traceability.csv`。
   - 13c：`frontend-design.md#test-plan`。
   - 这样下游可以按路径/章节核验，而不是依赖聊天内容。

## 6. 结论

当前流转不是“大量无价值输出”，而是**关键输出缺少明确消费者、内容输出缺少落盘位置、下游输入过粗**。优先修 F-01～F-07，再做 `consumed_by` 与死输出检查，可以显著降低“阶段做完了但下游没用上/没读到”的风险。P2 的留档型输出可以保留为证据，不必删除。

## 7. P0 修复记录（2026-11-06）

| 编号 | 修复 |
|---|---|
| F-01 | 新增 `design/design-plan.md`（模板 `templates/change-assets/design/design-plan.md`），13a 输出并写入任务分解/缺口/准入结论；10–13 输入明确读取 |
| F-02 | 新增 `design/api-traceability.csv`（模板 `templates/change-assets/design/api-traceability.csv`），13b 输出，13e 合并进唯一 `traceability.csv` |
| F-03 | 10/11/12/13e 的契约、Skill、Prompt 均加入 `design.md` 与 `design/design-plan.md` 输入 |
| F-04 | 13/15/16 的输入加入提案级 `design/user-stories.md`、`design/use-cases.md`（US/UC/AC） |
| F-05 | 05/09/10 的输入加入 `docs/product/open-questions.md`（只读） |
| F-06 | 13e/15 的输入加入 `docs/product/acceptance-policy.md` |
| F-07 | 09 的输入加入 `docs/project/baseline-audit-report.md` |

契约表、阶段总览、模板矩阵和 Prompt/Skill 已同步；`check-package.py`、`check-step-contracts.py`、`check-output-template-matrix.py`、`stage-io-report.py --check` 均已重新校验。

## 8. P1 修复记录（2026-11-06）

| 编号 | 修复 |
|---|---|
| F-08 | 09–12 的输入改为逐文件列出 system-context、domain-boundaries、containers、data-flows、logical-erd、technology-decisions、api/frontend/test conventions、ADR；13a–15 的 Change 产物输入也改为显式路径，不再只写“基线/详细设计” |
| F-09 | 明确页面权威顺序：06 prototype-build 页面清单是草案 → 11 page-inventory 是批准后的唯一权威 → 12 figma-audit 只核对映射，差异回 11 修订 |
| F-10 | `traceability.csv` 由 11 初始化，13b 写 `api-traceability.csv`，13e 合并；三者契约、Prompt/Skill、模板矩阵已统一 |
| F-11 | 明确 specs 是规范行为唯一来源；UC/US 只保留场景、AC 与追踪 ID，不复制完整规格（阶段 05 Prompt/Skill 与两个模板已注明） |
| F-12 | 契约新增 `output_consumption` 映射（58 个文件输出），新增 `scripts/check-output-consumption.py` 并接入 `check-package.py`；每个文件输出必须有下游消费者或显式 `evidence_only` |

`stage-io-report.py` 的逐阶段明细现在会显示每个文件的消费阶段；总览已重新生成。

## 9. P2 修复记录（2026-11-06）

| 编号 | 修复 |
|---|---|
| F-13 | 01 `toolchain-report.md` 已作为工具链/测试命令/环境约束输入到 05，不再是无人消费的留档 |
| F-14 | 00 的下一阶段判定报告改为“对话展示、不强制落盘”，不再产生无人读取的 `next-step-report.md` |
| F-15 | 09 的三个输出合并为一个 `docs/product/proposal-roadmap.md`（范围/依赖/价值/基线适用域/潜在修订都作为该文件的字段） |
| F-16 | 13c 的“测试用例/组件状态映射”固定为 `frontend-design.md` 的章节，不再作为无路径内容输出 |

消费映射现为 59 个文件输出（含 07 重新声明的 2 个基线产物）；无 evidence-only 输出（所有文件输出都有明确消费者或属于运行时/未来阶段）。

## 10. 2026-11-10 当前 01–10 拓扑修复记录

> 本节记录当前拓扑下的第二轮流转审查与修复；第 1–9 节保留旧 17 阶段分析历史。

| 编号 | 问题 | 修复 |
|---|---|---|
| R-01 | 当前阶段的 `pending_approvals` 会阻塞自身 `transition`，且没有解除入口 | `workflow.py transition` 允许在 evidence 中提交已批准审批并原子清除该阶段待审批；未批准仍拒绝 |
| R-02 | 多 Change 没有迭代入口 | 新增 `workflow.py next-change`：归档 05–10 到 `completed_changes`，切换 `active_change_id` 并从 05 重开 |
| R-03 | 09 失败 / 10 驳回没有回退路径 | 新增 `workflow.py reopen`：按依赖闭包回退，清理相关审批/阻断并记录 `reopen_history` |
| R-04 | `transition` 不校验契约声明的输出是否完整 | 按 `STEP-ARTIFACT-CONTRACTS.json` 核对 evidence；条件不适用项必须 `status=n/a` + `waiver_reason` |
| R-05 | 01/03、05/07 等共同产物的合法下游更新会破坏上游交接哈希 | handoff manifest 自动写入 `mutable_by_design`，这类产物只核验存在性 |
| R-06 | 02 契约漏登 `BASELINE-INDEX.md` | 补入 02 outputs 与消费记录 |
| R-07 | 10 更新 `decisions.md`/`assumptions.md`/`id-conventions.md` 但未声明读取 | 补入 10 inputs 与消费记录 |
| R-08 | 06 的 `prototype.md`/`design-spec.json`/`figma-handoff.*` 实际被 08/09/10 读取但未登记 | 补齐 5 条 `consumed_by`；`check-output-consumption.py` 增加反向校验 |
| R-09 | 旧拓扑 handoff 残留在 project 目录 | 移入 `workflow/handoffs/legacy/` |
| R-10 | workflow-orchestrator 仍要求手工改 `completed_steps`/`current_step` | 改为必须通过 `transition` |
| R-11 | 阶段完成后没有“待评审”状态，Agent 可直接继续下一阶段 | 新增 `workflow.py request-review`（冻结 `current_step`、写 `pending_approvals`）与 `approve`（写 `approvals_history`）；`transition` 对 02–10 强制要求审批记录；08/09 也设为人工审批；PreToolUse hook 在待评审期间拒绝跨阶段写入 |
| R-11 | Figma 设计输入没有统一定义 | 在阶段 06/07 Prompt/Skill、Figma 审计与交接模板、契约和逐阶段表统一为：`figma-audit.md` + `figma-code/`（设计代码（get_design_context 落盘））+ `figma-layout.csv`（运行态断言映射）+ 真实图片/SVG 资产 + 项目设计规范；不使用参考截图，`check-figma-audit.py --strict` 强制节点完整性与断言子集 |

并行阶段 03 工作已同步修正约束来源章节：当前 22 条约束的 `file`/`section` 全部可定位，`audit --require-frozen` 不再报告来源缺失。

验证：`check-package.py`、`check-step-contracts.py`、`check-output-consumption.py`、`stage-io-report.py --check`、`test-workflow-runtime.py`（15 项）均通过；`baseline-governance.py audit` 为 `BASELINE_VALID`。2026-11-10 晚些时候阶段 03 已完成人工审批、22 条约束置为 ACTIVE 并冻结，`audit --require-frozen` 返回 `BASELINE_FROZEN_AND_VALID`；`transition` 按新的 14 项输出完整性规则推进到 04，`check-entry 04` 为 `ENTRY_READY`。本节第 3 节逐阶段表已同步更新为当前 01–10 拓扑，旧表保留在 3.1。

## 11. 2026-11-11 阶段 06 收敛与流转修复

> 依据用户明确规则：原型输出只有 `prototype.pen`，原型评审后的输出只有 HTML；后续界面输入来自 Figma MCP，必要时把 MCP 读取结果落盘为文件。

| 编号 | 问题 | 修复 |
|---|---|---|
| R-12 | 06a 产出 `prototype.md`、`manifest.json`、初始 `traceability.csv`，与“原型只有 pen、评审后只有 HTML”不符 | 06 契约、Prompt、Skill、模板矩阵与 `check-stage06a.py` 收敛为 `prototype.pen` + `PAGE-*.html`；`build-figma-source.py` 去掉 manifest，直接校验 HTML 与 pen 的新鲜度和标记完整性 |
| R-13 | `design-tokens.json` 被 06b/07 强制读取但没有任何阶段产出 | 移出流程：视觉规范改取 `frontend-conventions.md` 第 9 节 + Figma MCP `get_variable_defs` 读取结果；当前 Change 文件归档到 `design/legacy/2026-11-11-pre-figma-mcp-redesign/` |
| R-14 | `prototype.pen` 被 manifest/build 脚本依赖但不是契约输出 | 明确为 06 输出，consumed_by=GATE；评审后 HTML 是唯一下游 UI 结构与内容基线 |
| R-15 | 07/09 Prompt 读取 `BASELINE-BRIEF.md` / `acceptance-policy.md` 但契约未登记 | 补入 07/09 inputs 与 `output_consumption` |
| R-16 | 10 的 baseline_interaction 声称可直接更新 `baseline-status.md`；规则仍写阶段 10 创建基线影响清单 | 改为只写 `lessons/decisions/assumptions`，基线变更走 `open-amendment/close-amendment`；基线影响清单归属阶段 05 |
| R-17 | 冻结基线 `frontend-conventions.md` 在阶段 06 期间被直接修改，`BASELINE_INVALID` | 走基线修订流程重新冻结，并为在途 Change 记录 NO_IMPACT rebase 复核；详见 `docs/architecture/baseline-status.md` |
| R-18 | `OUTPUT-FLOW-AUDIT.md` 第 3 节仍描述旧 06 产物 | 已同步为当前 `prototype.pen` + `PAGE-*.html` + `figma-audit.md` 模型 |

验证以本轮 `check-package.py`、`check-step-contracts.py`、`check-output-consumption.py`、`stage-io-report.py --check`、`baseline-governance.py audit` 的实际输出为准。

## 12. 2026-11-11 阶段 06 改为 Figma-only

> 依据用户明确指令“改 Figma-only”：阶段 06 不再经过 pen.dev 原型与 HTML 交接，Figma 成为唯一设计工具与唯一 UI 权威。

| 编号 | 问题 | 修复 |
|---|---|---|
| R-19 | 06a 的 `prototype.pen` 与 `PAGE-*.html` 形成“两次设计、两套工具链”，且 HTML 只是被 Figma 生成消费的中间物 | 阶段 06 收敛为 `06-figma-design-review`：唯一产物 `design/figma-audit.md`（Figma MCP 生成/读取快照 + PAGE 清单与映射 + UI 评审 APPROVED）；删除 `check-stage06a.py` 与 `build-figma-source.py` 门禁（归档到 `scripts/legacy/`）；07–10 只消费 figma-audit 与实时 Figma |
| R-20 | `figma-audit.md` 原先只校验 HTML 存在的 PAGE，无法独立定义页面集合 | `check-figma-audit.py` 改为从 `## 页面覆盖` 解析 PAGE ID，要求每个 PAGE 在节点映射中闭合；`check-test-cases.py` 也从 figma-audit 读取 PAGE |
| R-21 | `frontend-conventions.md` §11/§13 与 `acceptance-policy.md` 仍引用 06a HTML | 通过 `BCR-2026-11-11-FIGMA-ONLY` 修订 frontend/product 基线并重新冻结；旧版本 v1.0.1 → v1.0.2 |

## 13. 2026-11-12 UI 一致性流程收敛

依据用户指令（合并 Figma 落盘文件、按“导出一次、下游离线消费”改造流程；版本控制与 MCP 中断由用户保证，限流需流程规避）：

- 06 唯一 UI 契约收敛为 `design/figma-audit.md`（token 实际值、文字样式、每 PAGE 区块规格、设计代码、断言范围、状态覆盖与决策、资产清单、MCP 读取记录、UI 评审 APPROVED）与 `design/figma-code/`（设计代码（get_design_context 落盘））、`design/figma-layout.csv`（运行态断言映射）；不再拆分每页/每状态子目录或生成分散 token/contract JSON；**不使用截图，不保存参考图**。
- 06 一次性完整导出（`get_variable_defs` 全程一次、`get_metadata` 每 PAGE 一次、`get_design_context` 按需）；07/08 默认离线消费，仅在 Figma 文件版本变化或页面有歧义时按页批量重读（串行、避免限流）。
- 07 必须建 token → CSS 变量/Element Plus 主题/字体映射、填满 `figma-layout.csv` 的 route/dom_selector 并定义响应式规则；08 必须落地全局 token 层与字体，运行 `check-figma-layout.py`（Figma 节点几何 vs 1440×900 运行态 DOM）与 `check-design-tokens.py`，在 `code-review.md` 的 `## UI fidelity` 写逐 PAGE 数值表与 `figma-layout-check.json`；09 在 `layout_checks` 独立核验；10 直接对照运行系统与 Figma 文件在 `## UI acceptance` 逐 PAGE 人工签收；**全流程不使用截图**。
- 机器门禁：`check-figma-audit.py --strict`（06，节点/断言映射完整性）、`check-design-sections.py`（07，route/dom_selector 与响应式规则）、`check-figma-layout.py` + `check-design-tokens.py` + `check-code-review.py --strict`（08）、`check-independent-verification.py`（09 `layout_checks`）、`check-acceptance.py`（10 UI acceptance 运行入口/签收）；缺失任一 UI 数值证据阻断推进/归档；截图不作为门禁证据。
- 契约与模板已同步：`docs/STEP-ARTIFACT-CONTRACTS.json/.md`、`docs/STAGE-IO-OVERVIEW.md`、`docs/OUTPUT-TEMPLATE-MATRIX.csv`、`templates/change-assets/design/figma-audit.md`、`templates/change-assets/evidence/code-review.md`、`templates/change-assets/evidence/acceptance.md`、`templates/change-assets/design/independent-verification-report.md` 及其 schema。
