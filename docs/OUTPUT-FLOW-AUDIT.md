# 阶段输出流转审计

> 编号说明：本文记录重编号前的分析过程（旧编号 05/09/10/10b/11/12/13a–e/14b/15）。新编号映射：05→03、09→04、10→05、10b→06、11→07、12→08、13a→09、13b→10、13c→11、13d→12、13e→13、14b→15、15→16；以 `docs/WORKFLOW-STAGES.json` 为准。
> 2026-11-09 vibe 重构说明：阶段已进一步合并为 01–10（06=原型/页面清单，07=详细设计/接口/测试，08=实现，09=独立验证，10=验收），旧产物拆分（use-cases/design-plan/frontend-design/backend-design/test-design/api-traceability）已并入新载体。本文的阶段编号与产物清单仅保留历史分析价值；当前权威以 `docs/STAGE-IO-OVERVIEW.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 为准。

- Change ID：N/A（流程审计）
- 状态：DRAFT（分析报告，不改变阶段契约）
- 来源基线：`docs/STEP-ARTIFACT-CONTRACTS.json`、`docs/WORKFLOW-STAGES.json`、`docs/OUTPUT-TEMPLATE-MATRIX.csv`
- 关联需求/AC：N/A（流程文档）
- 生成日期：2026-11-06
- 版本：v0.1

## 1. 判定口径

| 状态 | 含义 |
|---|---|
| 已消费 | 下游阶段的 `inputs` 明确列出该文件/内容，或门禁脚本直接读取 |
| 间接消费 | 只被下游用“项目级基线/前后端详细设计”等聚合措辞引用，未列具体文件 |
| 仅留档 | 只作为阶段证据、审批记录或交接哈希存在，没有下游读取 |
| 未落盘 | 契约把“内容”列为输出，但没有指定文件路径，下游无法稳定消费 |

## 2. 总体结论

主链路（02 → 05 → 09 → 10 → 06 → 11 → 12 → 09–13 → 14 → 15 → 15）的输出基本闭合，需求和设计产物能被后续阶段使用。主要问题不是“大量无效输出”，而是四类流转缺陷：

1. **内容型输出没有落盘**：13a 的任务分解/缺口清单、13b 的 operationId 追踪关系、13c 的测试/组件状态映射只写成“内容”，没有固定文件或章节，下游无法可靠读取。
2. **关键输出没进下游输入**：`design.md`、提案级 `user-stories.md`/`use-cases.md`、`acceptance-policy.md`、`open-questions.md`、`baseline-audit-report.md` 已产出，但多数后续阶段没有明确列为输入。
3. **下游输入写得太粗**：09–12 只用“项目级架构/数据/公共契约基线”概括，无法验证 Agent 是否真的读取了 system-context、data-flows、ERD、ADR、技术选型等具体文件。
4. **同一事实有多份载体**：page 清单有 prototype-build、page-inventory、figma-audit 三处；追踪关系分散在 13b 内容和 13e `traceability.csv`；UC/US 与 specs 也可能重复描述同一行为。

## 3. 逐阶段流转表

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

消费映射现为 57 个文件输出；无 evidence-only 输出（所有文件输出都有明确消费者或属于运行时/未来阶段）。
