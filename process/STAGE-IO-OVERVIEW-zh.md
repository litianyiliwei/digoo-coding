# 阶段输入输出总览

> 语言：简体中文 ｜ [English](STAGE-IO-OVERVIEW.md)

> 状态：DERIVED（由权威契约自动生成，请勿手工编辑）
> Change ID：N/A（项目级流程总览）
> 来源基线：`process/STEP-ARTIFACT-CONTRACTS.json`（输入/输出/审批/门禁）、`process/WORKFLOW-STAGES.json`（依赖 DAG）
> 关联需求/AC：N/A（流程文档）
> 生成版本：`src-sha256:befa54a31f0d`

> 本文件只汇总阶段交接面。字段级产物模板见 `process/OUTPUT-TEMPLATE-MATRIX.csv`；流程入口见 `prompts/00-next-step.md`。
> 本文件是英文主文件的中文译本；权威生成文件为 `process/STAGE-IO-OVERVIEW.md`，修改契约后先运行 `python scripts/stage-io-report.py --out process/STAGE-IO-OVERVIEW.md` 重新生成英文主文件，再同步更新本译本。

共 11 个契约阶段：10 个 DAG 阶段 + 00 下一步编排（非 DAG 阶段）。

## 阶段分组

| 分组 | 阶段链路 | 说明 |
|---|---|---|
| 项目基线链 | 00 → 01 → 02 → 03 → 04 | 初始化 → 需求业务梳理 → 总体架构/基线冻结 → 路线图 |
| 提案交付链 | 04 → 05 → 06 → 07 → 08 → 09 → 10 | 提案需求 → Figma 设计/评审 → 详细设计（含接口/测试） → 实现 → 独立验证 → 验收 |

## 总览

> 总览把输入/输出合并展示；逐阶段明细再拆分为“内容/材料”和“文档/文件”。
> 总览“精简输入”列是每阶段默认读取组；完整契约审计集与按需输入见逐阶段明细。

| 阶段 | 名称 | 范围 | Skill | 依赖（DAG） | 精简输入（默认读取） | 输出 | 按需输入（触发后） |
|---|---|---|---|---|---|---|---|
| 00 | 下一步编排 | 项目级与功能级通用 | `workflow-orchestrator` | N/A（编排入口，不属于 DAG 阶段） | workflow-state.json<br>process/PROCESS-MAP.md<br>process/STEP-ARTIFACT-CONTRACTS.json<br>process/WORKFLOW-STAGES.json<br>process/BASELINE-FEATURE-INTERACTION.md<br>process/OUTPUT-TEMPLATE-MATRIX.csv<br>真实产物与审批记录<br>OpenSpec CLI 当前状态（如已初始化） | 下一阶段判定报告（对话展示；不强制落盘）<br>workflow-state.json（仅在真实状态变化时更新） | N/A |
| 01 | 项目初始化与工具链检查 | 项目级 | `project-bootstrap` | 无（流程起点） | 用户提供的项目目标与仓库位置<br>仓库现有目录/配置/AGENTS.md（若存在） | AGENTS.md（仅缺失时创建或经批准修改）<br>workflow-state.json<br>docs/architecture/baseline-status.md（依据 templates/project-baseline/baseline-status.md）<br>docs/project/toolchain-report.md（依据 templates/project-baseline/toolchain-report.md） | N/A |
| 02 | 需求业务梳理 | 项目级 | `requirements-analysis` | `01-project-bootstrap` | 用户提供访谈/业务/旧系统资料及项目目标、用户、角色、约束<br>阶段 02 契约与模板对应行<br>阶段 02 Prompt/Skill 规则<br>存在时读取 BASELINE-BRIEF 与开放问题（只读相关项）<br>既有需求/流程/数据/规则仅按命中 ID/章节读取<br>用户指定的参考产品或匹配研究问题的官方来源<br>存在时读取 change-sizing 与 id-conventions 相关规则 | docs/product/requirements-analysis.md<br>docs/product/workflows.md（每个 FLOW 必须含完整节点表：节点角色、输入/输出数据对象、前置条件、处理动作、异常/分支、下一节点）<br>docs/product/data-objects.csv（业务数据对象目录）<br>docs/product/rd-matrix.csv（需求-数据对象矩阵：需求/规则 → 流程节点 → 角色 → 数据对象）<br>docs/product/business-rules.md<br>docs/product/glossary.md<br>docs/product/acceptance-policy.md<br>docs/product/open-questions.md<br>docs/product/BASELINE-BRIEF.md（一页式基线入口，约 1 页；阶段 03–05 常驻上下文）<br>docs/product/role-permission-matrix.csv（角色-能力-数据范围-访问级别）<br>docs/product/change-sizing.md（Change 切片预算与完成定义）<br>docs/product/decisions.md（DEC 决策日志）<br>docs/product/assumptions.md（ASM 假设登记）<br>docs/product/lessons.md（教训/反模式；验收后由阶段 10 追加）<br>docs/product/id-conventions.md（项目级/Change 级 ID 与并行分配规则）<br>docs/product/BASELINE-INDEX.md（由 scripts/gen-baseline-index.py 生成的常驻基线索引）<br>docs/product/reference-research.md（参考产品与互联网调研：研究问题/参考产品（存在参考产品时至少含一个同类产品）/来源记录/对比/结论/影响映射/同类产品偏差确认，重大偏差须用户确认） | 6 项（见明细） |
| 03 | 项目总体架构设计 | 项目级 | `project-architecture-baseline` | `02-requirements-analysis` | docs/product/BASELINE-BRIEF.md（先读，约 1 页）<br>docs/product/reference-research.md（技术选型/第三方判断）<br>docs/product/open-questions.md（仅相关条目）<br>docs/project/toolchain-report.md（工具链/测试命令）<br>docs/architecture/baseline-status.md（初始基线）<br>现有系统代码库地址/第三方接口清单（用户提供）<br>命中的 FLOW/NODE/DO/RD/BR 行（按 ID 定向读取） | docs/architecture/system-context.md<br>docs/architecture/domain-boundaries.md<br>docs/architecture/containers-and-deployment.md<br>docs/architecture/data-flows.md（数据流转：DF ID、同步/异步、事务边界、失败与补偿）<br>docs/architecture/logical-erd.md（逻辑实体、关系、数据所有权、领域不变量）<br>docs/architecture/technology-decisions.md（含技术选型访谈记录、候选比较、用户确认人与日期）<br>docs/architecture/api-conventions.md<br>docs/architecture/frontend-conventions.md<br>docs/architecture/test-strategy.md<br>docs/architecture/code-layout.json（代码布局策略（module-packages | footprint | none）、roots、package_pattern、integration_paths、frozen_paths、module_card 与 dependency_rules；随架构基线冻结，仅通过基线变更流程修改；策略 module-packages 启用能力/模块注册表、切片与 footprint 门禁）<br>docs/architecture/quality-gates.json（条件适用：项目采用静态分析时；机器可读静态分析门禁：栈根目录、工具命令、配置路径、严重度与豁免政策；阶段 03 仅校验结构，因为从零仓库可能尚无栈目录；批准来自冻结的 test_quality 基线域，而非文件自身；未采用时省略文件、evidence 标记 n/a 并记录决策）<br>docs/adr/README.md<br>docs/architecture/baseline-status.md（经本阶段结束审计的各域版本/冻结状态）<br>docs/architecture/baseline-manifest.json（机器权威版本/冻结状态/域文件 SHA-256）<br>docs/architecture/constraint-registry.json（稳定约束 ID 与审批状态）<br>docs/project/baseline-audit-report.md（本阶段结束审计报告） | 13 项（见明细） |
| 04 | 提案拆分、依赖排序与路线图 | 项目级到功能级 | `proposal-planning` | `03-project-architecture-baseline` | docs/product/BASELINE-BRIEF.md<br>docs/product/change-sizing.md<br>docs/architecture/baseline-manifest.json<br>docs/architecture/constraint-registry.json<br>docs/architecture/baseline-status.md<br>docs/project/baseline-audit-report.md<br>docs/product/open-questions.md（仅相关条目）<br>命中的 FLOW/NODE/DO/BR 行 | docs/product/proposal-roadmap.md（含每个候选 Change 的范围/依赖/价值/基线适用域与潜在修订摘要，并含模块列：Primary Capability、Owner Module、Related Modules、Slice Type、Slice Coverage、Code Target、Demo Path、Slice Budget）<br>docs/product/capabilities.csv（能力进度注册表：capability_slug、capability_name、domain_id、owner_module、related_modules、status、delivered_slices、remaining_slices、active_changes、notes；04 创建、05 更新、10 回写）<br>docs/product/modules.csv（模块归属注册表：module_slug、module_name、domain_id、frontend_paths、backend_paths、shared_paths、capabilities、status、notes；04 创建、10 回写） | 6 项（见明细） |
| 05 | 提案级需求分析 | 单个功能 Change | `feature-requirements` | `04-proposal-planning` | docs/product/BASELINE-BRIEF.md<br>docs/product/change-sizing.md、id-conventions.md<br>docs/product/proposal-roadmap.md（当前行）<br>docs/architecture/baseline-status.md、baseline-manifest.json、constraint-registry.json<br>命中的 FLOW/NODE/DO/RD/BR/ROLE/CAP 行<br>openspec/specs/**（仅相关 capability）<br>docs/product/open-questions.md（仅相关条目）<br>docs/product/reference-research.md（仅范围/场景需要时） | openspec/changes/<change-id>/proposal.md<br>openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）<br>openspec/changes/<change-id>/tasks.md（初步任务；08 更新勾选状态）<br>openspec/changes/<change-id>/design/user-stories.md（用户故事与 AC；AC 是测试与验证的唯一锚点）<br>openspec/changes/<change-id>/design/baseline-impact.md（依据 templates/change-assets/design/baseline-impact.md；07 更新设计复核结论）<br>openspec/changes/<change-id>/design/baseline-binding.json（依据当前冻结基线自动生成，按 manifest governance_profile 绑定约束：standard 全部 ACTIVE，lite 仅 critical；07 写入设计证据）<br>docs/product/capabilities.csv（更新能力进度注册表：status、delivered_slices、remaining_slices 与 active_changes）<br>docs/product/modules.csv（更新模块归属注册表：为当前 Change 新增或更新模块及其能力）<br>docs/product/proposal-roadmap.md（当接受主表之外的迟到提案时追加 Roadmap Amendments 记录：Reason、Requester、Approver、Date、Baseline Impact；该后续阶段输出声明使 04 handoff 将路线图标记为 mutable_by_design） | 9 项（见明细） |
| 06 | Figma 设计与评审（Figma-only） | 单个功能 Change | `figma-design-review` | `05-feature-requirements` | 当前 Change 的 proposal/specs/design/user-stories<br>当前 Change 的 design/baseline-impact.md、baseline-binding.json<br>docs/architecture/frontend-conventions.md 第 9 节、technology-decisions.md<br>docs/architecture/baseline-status.md<br>docs/product/BASELINE-BRIEF.md、id-conventions.md<br>命中的 FLOW/NODE/DO/RD/BR/ROLE/PAGE 行<br>docs/product/open-questions.md（仅页面相关）<br>Figma MCP 可访问性 | openspec/changes/<change-id>/design/figma-audit.md（唯一 UI 契约（单文件）：Figma 文件/版本、目标框架/转码说明、PAGE 清单、token 实际值、文字样式、每 PAGE 区块规格、设计代码说明、断言范围、状态覆盖与决策、资产清单、MCP 读取记录、差异与待确认、UI 评审 APPROVED；无 UI 时 N/A + 理由）<br>openspec/changes/<change-id>/design/figma-code/（README.md + 每 PAGE 一个 PAGE-00N.vue（React 栈为 .tsx）；06 按总体技术选型转码的目标框架设计代码；08 直接移植只补业务逻辑）<br>openspec/changes/<change-id>/design/figma-layout.csv（精简断言表：page_id/route/element_id/figma_node_id/x/y/width/height/dom_selector/assert_geometry/assert_text/tolerance_px/text_content/font_size/font_weight/notes；06 可留 route/dom_selector 为 PENDING，07 填满）<br>openspec/changes/<change-id>/design/figma-assets/README.md（仅当有真实图片/SVG 资产时生成；不保存参考截图） | 11 项（见明细） |
| 07 | 详细设计、接口与测试设计 | 单个功能 Change | `detailed-design` | `06-figma-design-review` | openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design/user-stories.md、tasks.md、design.md<br>openspec/changes/<change-id>/design/baseline-impact.md、baseline-binding.json<br>现有功能代码地址/第三方接口清单（用户提供）<br>涉及 UI 时：openspec/changes/<change-id>/design/figma-audit.md、figma-code/、figma-layout.csv、Figma 评审稿<br>docs/architecture/technology-decisions.md、docs/architecture/api-conventions.md、docs/architecture/frontend-conventions.md#9、docs/architecture/test-strategy.md（按设计域）<br>docs/architecture/baseline-status.md<br>docs/product/BASELINE-BRIEF.md、docs/product/id-conventions.md<br>命中的 FLOW/NODE/DO/RD/BR/ROLE/CAP/PAGE 行（按 ID 定向读取） | openspec/changes/<change-id>/design.md（统一设计：设计决策、接口、前端、后端、测试五节；`## Design Decisions` 下含 `### Implementation Slice`：主能力、归属/关联模块、切片类型/覆盖、代码包、拥有/集成路径、模块卡动作，以及可选的 Frozen approvals/out-of-context 声明；切片是本文件中的内容，不是单独文件）<br>openspec/changes/<change-id>/design/figma-layout.csv（07 填满每行 route/dom_selector，并据此定义响应式规则；几何/文本/字体值以目标框架设计代码与 metadata 为准）<br>openspec/changes/<change-id>/design.md 的 ### PAGE→BLOCK→组件映射（以 figma-code 目标框架设计代码为基线，仅登记业务化适配与 UI-DEVIATION，不重新设计样式/布局/文案）<br>openspec/changes/<change-id>/design/ui-actions.csv（交互控件清单：每个功能按钮/图标/链接/菜单/标签页映射到跳转（地址+入参）、API（operationId 存在于 api/openapi.yaml）或用户已确认（确认人+日期）的本地动作）<br>openspec/changes/<change-id>/design/baseline-impact.md（07 更新设计复核结论：NO_IMPACT/REBASE_REQUIRED 与设计证据）<br>openspec/changes/<change-id>/design/baseline-binding.json（07 写入逐条约束的设计证据）<br>openspec/changes/<change-id>/design/test-cases.csv（TEST ID → AC/PAGE/API/IO 的测试用例矩阵，含失败注入/替身环境/人工原因；BLOCK 可选，不适用写 N/A）<br>openspec/changes/<change-id>/api/openapi.yaml（条件适用：有 API 时）<br>openspec/changes/<change-id>/design/api-io-mapping.csv（条件适用：有 API 时）<br>openspec/changes/<change-id>/design/io-catalog.csv（条件适用：有 API 时）<br>openspec/changes/<change-id>/design/interface-catalog.csv（跨边界接口目录：HTTP/原生桥接/设备/第三方/异步/文件；条件适用：有跨边界接口时）<br>openspec/changes/<change-id>/design/static-waivers.json（条件适用：需要静态分析豁免时；Change 级文件+规则豁免，含理由/责任人/审批人/批准日期/过期时间；绝不存入冻结门禁文件；无需豁免时省略文件或保留空列表）<br>openspec/changes/<change-id>/traceability.csv（合并 API 与测试映射；唯一追踪聚合文件） | 14 项（见明细） |
| 08 | 实现、TDD、验证与代码审查 | 单个功能 Change | `implementation-orchestrator` | `07-detailed-design` | 当前 Change 的 tasks.md、design.md、specs、user-stories、test-cases.csv、traceability.csv<br>适用时的 api/openapi.yaml、api-io-mapping.csv、io-catalog.csv、interface-catalog.csv<br>涉及 UI 的 figma-audit.md、figma-code/、figma-layout.csv<br>当前 Change 的 design/baseline-impact.md、baseline-binding.json、baseline-status.md<br>设计域命中的架构章节：system-context/domain-boundaries/logical-erd/data-flows/technology-decisions/api-conventions/frontend-conventions/test-strategy<br>docs/product/BASELINE-BRIEF.md<br>docs/product/open-questions.md（仅相关条目）<br>现有功能代码地址（若修改现有功能） | 实际源代码/迁移/配置<br>自动化测试代码与运行结果<br>openspec/changes/<change-id>/design/evidence/code-review.md（涉及 UI 时含 ## UI fidelity 逐 PAGE 数值表：Figma node/断言元素数/最大偏差/布局证据/差异/结论/审批人；数值直接取自 figma-layout-check.json，仅差异/UI-DERIVED PAGE 需人工说明与审批；启用质量门禁时含 ## Static analysis 表，从 static-analysis.json 逐行复制：各栈/工具命令、配置路径 @ SHA-256、结果、字面 exit 0 及生效豁免与审批人）<br>openspec/changes/<change-id>/design/evidence/static-analysis.json（启用质量门禁时；由 scripts/run-quality-gates.py 生成：各 blocking 栈/工具命令、工作目录、退出码、配置 SHA-256、门禁文件 SHA-256、源码 revision、生效豁免、结论）<br>openspec/changes/<change-id>/design/evidence/static-analysis-logs/（启用质量门禁时；每个 blocking 栈/工具一份捕获日志；日志文件名由净化后的栈根目录加工具 id 派生）<br>openspec/changes/<change-id>/design/evidence/figma-layout-check.json（scripts/check-figma-layout.py 的逐元素 expected/actual/delta 证据）<br>openspec/changes/<change-id>/design/evidence/implementation-base.json（脚本生成的入口快照：git HEAD、逐文件 SHA-256 与指纹；由 scripts/implementation-snapshot.py 写入；implementation-snapshot 始终写入入口基线，即使 code-layout 策略为 none）<br>openspec/changes/<change-id>/design/context-manifest.json（scripts/code-context.py 生成的检索闭包：read_set/not_needed/missing；不是门禁；strategy none 时不写文件）<br>模块卡 `<module_path>/MODULE.md`：为本切片创建或更新的每个模块创建/更新（无固定路径；由模块注册表检查校验）<br>openspec/changes/<change-id>/design/evidence/implementation-diff.json（已验证 revision 的 commit/diff SHA-256 与变更路径）<br>实现/验证证据<br>条件适用：基线变更请求/ADR 草案（发现冲突时；未经批准不更新冻结基线） | 10 项（见明细） |
| 09 | 独立验证与验收证据 | 功能级 | `independent-verifier` | `08-implementation-orchestrator` | 已实现代码及 revision/diff 指纹<br>当前 Change 的 proposal/specs/design/user-stories/tasks<br>适用时的 api/openapi.yaml、api-io-mapping.csv、io-catalog.csv、interface-catalog.csv<br>涉及 UI 的 figma-audit.md、figma-layout.csv、figma-layout-check.json<br>test-cases.csv、traceability.csv、code-review.md、Builder 测试证据<br>docs/product/BASELINE-BRIEF.md<br>docs/product/acceptance-policy.md<br>当前 Change 的 baseline-impact.md、baseline-binding.json、baseline-status.md | openspec/changes/<change-id>/design/evidence/independent-verification-report.md<br>openspec/changes/<change-id>/design/evidence/independent-verification.json<br>openspec/changes/<change-id>/design/evidence/static-analysis-independent.json（启用质量门禁时；verifier 与 builder 身份不同的独立重跑证据；由 scripts/run-quality-gates.py --independent 生成） | 10 项（见明细） |
| 10 | 人工验收、归档与基线回写 | 单个功能 Change | `acceptance-audit` | `09-independent-verification` | independent-verification-report.md 与 independent-verification.json<br>当前 Change 的 specs、user-stories、traceability.csv、design.md、code-review.md<br>涉及 UI 的 figma-audit.md、figma-layout.csv、figma-layout-check.json<br>test-cases.csv、interface-catalog.csv<br>当前 Change 的 baseline-impact.md、baseline-binding.json、baseline-status.md<br>docs/product/acceptance-policy.md、BASELINE-BRIEF.md、change-sizing.md<br>docs/product/decisions.md、assumptions.md、id-conventions.md<br>运行中的验收环境入口 | openspec/changes/<change-id>/design/evidence/acceptance.md（涉及 UI 时含 ## UI acceptance 逐 PAGE 签收：Figma node/运行系统入口/差异审批/验收方式（机器证据/并排核对）/评审人；启用质量门禁时含 ## Static analysis，从 static-analysis.json 与 static-analysis-independent.json 核对：各栈/工具命令、结果、字面 exit 0 及每个生效豁免与审批人）<br>docs/product/lessons.md（追加本次可复用教训；无则 N/A + 理由）<br>docs/product/decisions.md（受验收结果影响的状态更新）<br>docs/product/assumptions.md（受验收结果影响的状态更新）<br>docs/product/capabilities.csv（能力进度回写：status、delivered_slices、remaining_slices 与 active_changes；由 scripts/check-capabilities.py --completed <change-id> 校验）<br>docs/product/modules.csv（模块归属回写：模块 status/capabilities；Change 完成某个模块时由 scripts/check-modules.py --completed <module-slug> 校验）<br>验收报告与批准记录<br>OpenSpec archive 结果及更新后的主规格（仅批准后） | 7 项（见明细） |

## 逐阶段明细

### 00 下一步编排

- 范围：项目级与功能级通用
- Skill：`workflow-orchestrator`
- Prompt：`prompts/00-next-step.md`
- 依赖（DAG）：N/A（编排入口，不属于 DAG 阶段）

**完整契约输入（内容/材料，审计集）**

- 真实产物与审批记录
- OpenSpec CLI 当前状态（如已初始化）

**完整契约输入（文档/文件，审计集）**

- workflow-state.json
- process/PROCESS-MAP.md
- process/STEP-ARTIFACT-CONTRACTS.json
- process/WORKFLOW-STAGES.json
- process/BASELINE-FEATURE-INTERACTION.md
- process/OUTPUT-TEMPLATE-MATRIX.csv

**输出（内容/材料）**

- 下一阶段判定报告（对话展示；不强制落盘）

**输出（文档/文件）**

- workflow-state.json（仅在真实状态变化时更新）

**输出消费者**

- workflow-state.json → SYSTEM

**下游交接**

- 所选阶段的 Input Contract 中全部文件

**审批与门禁**

- 审批：不得越过 pending_approvals、blocked_items、缺失输入或失败门禁
- 门禁：核验真实文件/审批/CLI；只选择一个阶段

---

### 01 项目初始化与工具链检查

- 范围：项目级
- Skill：`project-bootstrap`
- Prompt：`prompts/01-project-bootstrap.md`
- 依赖（DAG）：无（流程起点）

**完整契约输入（内容/材料，审计集）**

- 用户提供的项目目标与仓库位置

**完整契约输入（文档/文件，审计集）**

- 仓库现有目录/配置/AGENTS.md（若存在）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- AGENTS.md（仅缺失时创建或经批准修改）
- workflow-state.json
- docs/architecture/baseline-status.md（依据 templates/project-baseline/baseline-status.md）
- docs/project/toolchain-report.md（依据 templates/project-baseline/toolchain-report.md）

**输出消费者**

- AGENTS.md → ALL
- workflow-state.json → SYSTEM
- docs/architecture/baseline-status.md → 03、04、05、06、07、08、09、10
- docs/project/toolchain-report.md → 03

**下游交接**

- 仓库约定与工具链报告
- workflow-state.json

**审批与门禁**

- 审批：覆盖/修改既有 AGENTS.md 或配置前需批准
- 门禁：仓库盘点、Skill/CLI 可用性检查、基础文件检查

---

### 02 需求业务梳理

- 范围：项目级
- Skill：`requirements-analysis`
- Prompt：`prompts/02-requirements-analysis.md`
- 依赖（DAG）：`01-project-bootstrap`

**默认精简输入（最多 8 组）**

- 用户提供的访谈、业务/旧系统资料，以及项目目标、用户、角色、约束和成功标准；不扫描无关路径。
- 只读 Stage 02 契约记录与 `OUTPUT-TEMPLATE-MATRIX.csv` 对应模板行，以及 Stage 02 Prompt/Skill。
- `BASELINE-BRIEF.md`（存在时；首次 Stage 02 可在本阶段创建）和 `open-questions.md` 中未决/相关决策项（存在时）。
- 既有需求、流程、数据、规则、角色、术语和验收材料只按命中 ID/章节读取；默认不加载完整 `docs/product/*`。
- 用户指定的参考产品或与研究问题匹配的官方来源；记录真实查询、URL、访问日期和发现。
- `change-sizing.md` 与 `id-conventions.md` 中相关规则（存在时）。

**按需输入**

- 只有出现冲突或需要全面重审基线时，才读完整 `docs/product/*`，并记录触发原因和章节。
- 需要更新/核对旧研究时读 `reference-research.md`；需要判断实现或研究可行性时读 `toolchain-report.md`。
- 执行 `openspec list --specs`；只读相关规格。若无规格，记录 N/A，不搜索无关 Change。
- 只有产品要求受架构约束或存在决策冲突时，才读相关架构章节/ADR。
- 法规、业务或旧系统材料仅从用户为本项目提供的位置/来源读取。

**完整契约输入（内容/材料，审计集）**

- 访谈/业务材料/旧系统资料
- 项目目标、用户、角色、约束
- 用户提供的参考产品（名称/链接/截图/账号；无则 NONE + 理由）
- 互联网调研工具与真实来源（WebSearch/WebFetch 或宿主等价能力；记录查询、URL、访问日期）

**完整契约输入（文档/文件，审计集）**

- 既有 docs/product/*（若存在）
- 既有 OpenSpec specs（只读）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- docs/product/requirements-analysis.md
- docs/product/workflows.md（每个 FLOW 必须含完整节点表：节点角色、输入/输出数据对象、前置条件、处理动作、异常/分支、下一节点）
- docs/product/data-objects.csv（业务数据对象目录）
- docs/product/rd-matrix.csv（需求-数据对象矩阵：需求/规则 → 流程节点 → 角色 → 数据对象）
- docs/product/business-rules.md
- docs/product/glossary.md
- docs/product/acceptance-policy.md
- docs/product/open-questions.md
- docs/product/BASELINE-BRIEF.md（一页式基线入口，约 1 页；阶段 03–05 常驻上下文）
- docs/product/role-permission-matrix.csv（角色-能力-数据范围-访问级别）
- docs/product/change-sizing.md（Change 切片预算与完成定义）
- docs/product/decisions.md（DEC 决策日志）
- docs/product/assumptions.md（ASM 假设登记）
- docs/product/lessons.md（教训/反模式；验收后由阶段 10 追加）
- docs/product/id-conventions.md（项目级/Change 级 ID 与并行分配规则）
- docs/product/BASELINE-INDEX.md（由 scripts/gen-baseline-index.py 生成的常驻基线索引）
- docs/product/reference-research.md（参考产品与互联网调研：研究问题/参考产品（存在参考产品时至少含一个同类产品）/来源记录/对比/结论/影响映射/同类产品偏差确认，重大偏差须用户确认）

**输出消费者**

- docs/product/requirements-analysis.md → 03、04、05
- docs/product/reference-research.md → 03、04、05、06
- docs/product/workflows.md → 03、04、05、06、07
- docs/product/data-objects.csv → 03、04、05、06、07
- docs/product/rd-matrix.csv → 03、04、05、06、07
- docs/product/business-rules.md → 03、04、05、06、07
- docs/product/glossary.md → 03、04、05
- docs/product/acceptance-policy.md → 03、04、05、07、09、10
- docs/product/open-questions.md → 03、04、05、06、07、08、09、10
- docs/product/BASELINE-BRIEF.md → 03、04、05、07、10
- docs/product/role-permission-matrix.csv → 03、04、05、06、07
- docs/product/change-sizing.md → 03、04、05、10
- docs/product/decisions.md → 03、04、05、10
- docs/product/assumptions.md → 03、04、05、10
- docs/product/lessons.md → 04、05、10
- docs/product/id-conventions.md → 03、04、05、06、07、10
- docs/product/BASELINE-INDEX.md → 03

**下游交接**

- 业务流程与节点级角色/数据对象、业务数据对象目录、RD 矩阵、业务规则、术语与验收政策、未决问题
- 常驻基线简报、角色权限矩阵、Change 切片规则、决策/假设登记、ID 约定与基线索引

**审批与门禁**

- 审批：业务/产品负责人确认业务流程完整性、节点数据对象与角色、RD 矩阵覆盖
- 门禁：scripts/check-requirements.py --strict（FLOW/NODE/DO/RD/BR 结构、引用闭合与节点覆盖）；scripts/gen-baseline-index.py --check（常驻基线索引未过期）；python scripts/check-reference-research.py --strict（参考产品与互联网调研：≥3 个研究问题、≥3 条来源、≥2 条对比、存在参考产品时至少一个同类产品、≥2 条同类产品偏差行、影响映射与审批；重大偏差未取得用户确认（确认人+日期）时不通过）

---

### 03 项目总体架构设计

- 范围：项目级
- Skill：`project-architecture-baseline`
- Prompt：`prompts/03-project-architecture-baseline.md`
- 依赖（DAG）：`02-requirements-analysis`

**精简输入（默认读取，建议预算）**

- docs/product/BASELINE-BRIEF.md（先读，约 1 页）
- docs/product/reference-research.md（技术选型/第三方判断）
- docs/product/open-questions.md（仅相关条目）
- docs/project/toolchain-report.md（工具链/测试命令）
- docs/architecture/baseline-status.md（初始基线）
- 现有系统代码库地址/第三方接口清单（用户提供）
- 命中的 FLOW/NODE/DO/RD/BR 行（按 ID 定向读取）

> 预算（建议值）：7/8 条；超出时缩小范围或记录多读原因。

**按需输入（触发后读取，不计入默认预算）**

- docs/product/requirements-analysis.md
- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/rd-matrix.csv
- docs/product/business-rules.md
- docs/product/glossary.md
- docs/product/acceptance-policy.md
- docs/product/role-permission-matrix.csv
- docs/product/change-sizing.md
- docs/product/decisions.md
- docs/product/assumptions.md
- docs/product/id-conventions.md
- docs/adr/*

**完整契约输入（内容/材料，审计集）**

- 现有仓库结构/技术约束
- 现有系统代码库地址与可访问性（若基于现有系统二开；含仓库/本地路径/分支/commit）
- 用户确认的第三方接口清单（提供方/用途/协议/鉴权/SLA/沙箱/审批；无则 NONE + 理由）
- 非功能需求
- 用户/技术负责人明确的技术选型偏好（本阶段必须显式询问并记录，不得默认或自行假设）

**完整契约输入（文档/文件，审计集）**

- 已批准的 docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md
- docs/product/BASELINE-BRIEF.md、role-permission-matrix.csv、change-sizing.md、decisions.md、assumptions.md、id-conventions.md、BASELINE-INDEX.md（常驻基线；先读简报，细节按需加载）
- docs/product/reference-research.md（参考产品与互联网调研结论；用于技术选型、边界与第三方判断）
- docs/product/open-questions.md（只读；未决问题不得由架构阶段擅自关闭）
- docs/project/toolchain-report.md（工具链、测试命令与环境约束）
- docs/architecture/baseline-status.md（阶段 01 的初始基线与模板状态；本阶段更新为冻结候选）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- docs/architecture/system-context.md
- docs/architecture/domain-boundaries.md
- docs/architecture/containers-and-deployment.md
- docs/architecture/data-flows.md（数据流转：DF ID、同步/异步、事务边界、失败与补偿）
- docs/architecture/logical-erd.md（逻辑实体、关系、数据所有权、领域不变量）
- docs/architecture/technology-decisions.md（含技术选型访谈记录、候选比较、用户确认人与日期）
- docs/architecture/api-conventions.md
- docs/architecture/frontend-conventions.md
- docs/architecture/test-strategy.md
- docs/architecture/code-layout.json（代码布局策略（module-packages | footprint | none）、roots、package_pattern、integration_paths、frozen_paths、module_card 与 dependency_rules；随架构基线冻结，仅通过基线变更流程修改；策略 module-packages 启用能力/模块注册表、切片与 footprint 门禁）
- docs/architecture/quality-gates.json（条件适用：项目采用静态分析时；机器可读静态分析门禁：栈根目录、工具命令、配置路径、严重度与豁免政策；阶段 03 仅校验结构，因为从零仓库可能尚无栈目录；批准来自冻结的 test_quality 基线域，而非文件自身；未采用时省略文件、evidence 标记 n/a 并记录决策）
- docs/adr/README.md
- docs/architecture/baseline-status.md（经本阶段结束审计的各域版本/冻结状态）
- docs/architecture/baseline-manifest.json（机器权威版本/冻结状态/域文件 SHA-256）
- docs/architecture/constraint-registry.json（稳定约束 ID 与审批状态）
- docs/project/baseline-audit-report.md（本阶段结束审计报告）

**输出消费者**

- docs/architecture/system-context.md → 07、08
- docs/architecture/domain-boundaries.md → 07、08
- docs/architecture/containers-and-deployment.md → 07
- docs/architecture/data-flows.md → 07、08
- docs/architecture/logical-erd.md → 07、08
- docs/architecture/technology-decisions.md → 06、07、08
- docs/architecture/api-conventions.md → 07、08
- docs/architecture/frontend-conventions.md → 06、07、08
- docs/architecture/test-strategy.md → 07、08
- docs/architecture/code-layout.json → 04、05、07、08
- docs/architecture/quality-gates.json → 05、07、08、09、10
- docs/adr/README.md → 07、08、09、10
- docs/architecture/baseline-status.md → 04、05、06、07、08、09、10
- docs/architecture/baseline-manifest.json → 04、05
- docs/architecture/constraint-registry.json → 04、05
- docs/project/baseline-audit-report.md → 04

**下游交接**

- 冻结的项目总体架构基线、数据流转、逻辑 ERD、公共契约/测试策略、ACTIVE 约束目录、审计报告与审批记录

**审批与门禁**

- 审批：产品/架构/技术负责人共同确认系统边界、数据流转与公共契约，并批准基线冻结
- 门禁：scripts/check-required-files.sh --strict；跨文档一致性审计（系统边界/数据流转/ERD/公共契约/术语）；python scripts/check-quality-gates.py --root . --strict（采用时：quality-gates.json 结构与选型，阶段 03 不要求已物化；文件不存在时报告 NOT_ADOPTED 并通过）；python scripts/check-method-evidence.py --step 03-project-architecture-baseline --evidence <evidence>（必需方法技能、真实证据路径与产物落点）；python scripts/check-architecture-baseline.py --strict（现有系统二开约束/第三方接口依赖清单/LEGACY-*/EXT-*）；docs/architecture/technology-decisions.md 必须含“现有系统二开约束”与“第三方接口依赖清单”；scripts/baseline-governance.py audit --require-frozen（阶段结束冻结审计，同时作为门禁文件的批准）；docs/architecture/code-layout.json 的结构、策略枚举与路径合法性在 04/05 首次消费时由 scripts/check-capabilities.py、scripts/check-modules.py 与 scripts/check-roadmap.py 校验（gate_common.strategy 对格式错误的布局 fail-closed）

---

### 04 提案拆分、依赖排序与路线图

- 范围：项目级到功能级
- Skill：`proposal-planning`
- Prompt：`prompts/04-proposal-planning.md`
- 依赖（DAG）：`03-project-architecture-baseline`

**精简输入（默认读取，建议预算）**

- docs/product/BASELINE-BRIEF.md
- docs/product/change-sizing.md
- docs/architecture/baseline-manifest.json
- docs/architecture/constraint-registry.json
- docs/architecture/baseline-status.md
- docs/project/baseline-audit-report.md
- docs/product/open-questions.md（仅相关条目）
- 命中的 FLOW/NODE/DO/BR 行

> 预算（建议值）：8/8 条；超出时缩小范围或记录多读原因。

**按需输入（触发后读取，不计入默认预算）**

- docs/product/requirements-analysis.md
- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/rd-matrix.csv
- docs/product/business-rules.md
- docs/adr/*

**完整契约输入（内容/材料，审计集）**

- 已知技术债与依赖
- 相关架构/数据/API/前端/测试基线版本与审批信息

**完整契约输入（文档/文件，审计集）**

- 已批准并冻结的项目总体架构与基线：docs/architecture/baseline-manifest.json、constraint-registry.json、baseline-status.md、docs/project/baseline-audit-report.md
- docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md（需求业务梳理全量输入）
- docs/product/BASELINE-BRIEF.md、role-permission-matrix.csv、change-sizing.md、decisions.md、assumptions.md、lessons.md、id-conventions.md（基线常驻层与经验回写）
- docs/product/reference-research.md（参考产品与互联网调研结论；用于 Change 拆分与依赖判断）
- docs/architecture/baseline-status.md
- docs/product/open-questions.md（未决问题与阻塞条件）
- docs/architecture/code-layout.json（策略、roots、模块包模式、集成/冻结路径，用于路线图模块列与注册表路径）
- docs/project/baseline-audit-report.md（阶段 03 审计发现的缺口、待批项与冻结结论）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- docs/product/proposal-roadmap.md（含每个候选 Change 的范围/依赖/价值/基线适用域与潜在修订摘要，并含模块列：Primary Capability、Owner Module、Related Modules、Slice Type、Slice Coverage、Code Target、Demo Path、Slice Budget）
- docs/product/capabilities.csv（能力进度注册表：capability_slug、capability_name、domain_id、owner_module、related_modules、status、delivered_slices、remaining_slices、active_changes、notes；04 创建、05 更新、10 回写）
- docs/product/modules.csv（模块归属注册表：module_slug、module_name、domain_id、frontend_paths、backend_paths、shared_paths、capabilities、status、notes；04 创建、10 回写）

**输出消费者**

- docs/product/proposal-roadmap.md → 05
- docs/product/capabilities.csv → 05、07、08、10
- docs/product/modules.csv → 05、07、08、10

**下游交接**

- 经批准的 Change 列表、优先级、依赖顺序、模块化路线图列、能力进度注册表与模块归属注册表

**审批与门禁**

- 审批：产品与技术负责人批准路线图及首个 Change
- 门禁：scripts/check-roadmap.py --strict；python scripts/check-capabilities.py；python scripts/check-modules.py；不在此阶段伪造 Change 验证

**基线交互**

- 只读：docs/architecture/baseline-status.md；相关产品/架构/数据/公共契约/测试基线；openspec/specs/**
- 产出/复核：docs/product/proposal-roadmap.md 中每个 Change 的基线适用域和候选修订

---

### 05 提案级需求分析

- 范围：单个功能 Change
- Skill：`feature-requirements`
- Prompt：`prompts/05-feature-requirements.md`
- 依赖（DAG）：`04-proposal-planning`

**精简输入（默认读取，建议预算）**

- docs/product/BASELINE-BRIEF.md
- docs/product/change-sizing.md、id-conventions.md
- docs/product/proposal-roadmap.md（当前行）
- docs/architecture/baseline-status.md、baseline-manifest.json、constraint-registry.json
- 命中的 FLOW/NODE/DO/RD/BR/ROLE/CAP 行
- openspec/specs/**（仅相关 capability）
- docs/product/open-questions.md（仅相关条目）
- docs/product/reference-research.md（仅范围/场景需要时）

> 预算（建议值）：8/8 条；超出时缩小范围或记录多读原因。

**按需输入（触发后读取，不计入默认预算）**

- docs/product/requirements-analysis.md
- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/rd-matrix.csv
- docs/product/business-rules.md
- docs/product/glossary.md
- docs/product/acceptance-policy.md
- docs/product/role-permission-matrix.csv
- docs/adr/*

**完整契约输入（内容/材料，审计集）**

- N/A

**完整契约输入（文档/文件，审计集）**

- docs/product/proposal-roadmap.md（当前 Change 所在行与依赖）、当前 Change 范围
- docs/product/capabilities.csv 与 docs/product/modules.csv（当前能力进度与模块归属注册表；新增或更新能力/模块前先读取）
- docs/architecture/code-layout.json（模块包模式与集成/冻结路径，用于校验模块路径）
- docs/product/BASELINE-BRIEF.md（先读，约 1 页）、change-sizing.md（切片预算与 DoD）、role-permission-matrix.csv、decisions.md、assumptions.md、lessons.md、id-conventions.md
- docs/product/reference-research.md（参考产品与互联网调研结论；用于提案范围与场景完整性）
- docs/architecture/baseline-status.md 与相关架构/数据/公共契约/测试基线
- docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md（关联 FLOW/BR/AC 与 RD 矩阵；AC 与验收政策对齐）
- openspec/specs/**（只读）
- docs/architecture/baseline-manifest.json 与 docs/architecture/constraint-registry.json（机器权威来源）
- docs/architecture/quality-gates.json（已启用时；从 Change 基线影响清单引用的适用静态分析门禁）
- docs/product/open-questions.md（只读；提案需求不得替用户决策）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/proposal.md
- openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）
- openspec/changes/<change-id>/tasks.md（初步任务）
- openspec/changes/<change-id>/design.md（初始设计决策；约 1 页；接口/前端/后端/测试细节留到 07）
- openspec/changes/<change-id>/design/user-stories.md（用户故事与 AC；AC 是测试与验证的唯一锚点）
- openspec/changes/<change-id>/design/baseline-impact.md（依据 templates/change-assets/design/baseline-impact.md；07 更新设计复核结论）
- openspec/changes/<change-id>/design/baseline-binding.json（依据当前冻结基线自动生成，按 manifest governance_profile 绑定约束：standard 全部 ACTIVE，lite 仅 critical；07 写入设计证据）
- docs/product/capabilities.csv（更新能力进度注册表：status、delivered_slices、remaining_slices 与 active_changes）
- docs/product/modules.csv（更新模块归属注册表：为当前 Change 新增或更新模块及其能力）
- docs/product/proposal-roadmap.md（当接受主表之外的迟到提案时追加 Roadmap Amendments 记录：Reason、Requester、Approver、Date、Baseline Impact；该后续阶段输出声明使 04 handoff 将路线图标记为 mutable_by_design）

**输出消费者**

- openspec/changes/<change-id>/proposal.md → 06、07、09
- openspec/changes/<change-id>/specs/<capability>/spec.md → 06、07、08、09、10
- openspec/changes/<change-id>/tasks.md → 07、08、09
- openspec/changes/<change-id>/design.md → 06、07、08、09、10
- openspec/changes/<change-id>/design/user-stories.md → 06、07、08、09、10
- openspec/changes/<change-id>/design/baseline-impact.md → 06、07、08、09、10
- openspec/changes/<change-id>/design/baseline-binding.json → 06、07、08、09、10
- docs/product/proposal-roadmap.md → FUTURE
- docs/product/capabilities.csv → 07、08、10
- docs/product/modules.csv → 07、08、10

**下游交接**

- 已批准的提案级 US/AC、场景与业务规则、范围边界、需求追踪 ID、基线快照、约束绑定与更新后的能力/模块注册表
- specs 为规范行为唯一来源；user-stories 只保留场景、AC 与追踪 ID

**审批与门禁**

- 审批：产品负责人批准提案级需求与验收标准；技术负责人确认范围与基线影响
- 门禁：scripts/check-requirements.py --change <change-id> --strict（US/AC 结构与引用闭合）；openspec validate <change-id> --strict；scripts/check-baseline-impact.py <change-id>；scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement；python scripts/check-capabilities.py；python scripts/check-modules.py；python scripts/check-roadmap.py --strict（写入了 Roadmap Amendments 行时）

**基线交互**

- 只读：docs/architecture/baseline-status.md；相关产品/架构/数据/API/前端/测试基线；相关 openspec/specs/**
- 产出/复核：openspec/changes/<change-id>/design/baseline-impact.md
- 门禁：若功能设计依赖未批准的架构/数据/公共契约/质量基线变化，阻断进入详细设计/实现

---

### 06 Figma 设计与评审（Figma-only）

- 范围：单个功能 Change
- Skill：`figma-design-review`
- Prompt：`prompts/06-figma-design-review.md`
- 依赖（DAG）：`05-feature-requirements`

**精简输入（默认读取，建议预算）**

- 当前 Change 的 proposal/specs/design/user-stories
- 当前 Change 的 design/baseline-impact.md、baseline-binding.json
- docs/architecture/frontend-conventions.md 第 9 节、technology-decisions.md
- docs/architecture/baseline-status.md
- docs/product/BASELINE-BRIEF.md、id-conventions.md
- 命中的 FLOW/NODE/DO/RD/BR/ROLE/PAGE 行
- docs/product/open-questions.md（仅页面相关）
- Figma MCP 可访问性

> 预算（建议值）：8/8 条；超出时缩小范围或记录多读原因。

**按需输入（触发后读取，不计入默认预算）**

- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/rd-matrix.csv
- docs/product/business-rules.md
- docs/product/role-permission-matrix.csv
- docs/product/reference-research.md
- docs/architecture/system-context.md
- docs/architecture/domain-boundaries.md
- docs/architecture/api-conventions.md
- docs/architecture/test-strategy.md
- docs/adr/*

**完整契约输入（内容/材料，审计集）**

- Figma MCP 实际可访问能力（生成并回读真实 Figma 设计必须；不可用或读不到真实文件/节点时阻断，不得伪造）

**完整契约输入（文档/文件，审计集）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、design/user-stories.md（已批准的提案级需求与 AC）
- docs/product/workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、role-permission-matrix.csv、id-conventions.md（业务流程/数据对象/RD 矩阵/角色权限/ID 约定）；docs/architecture/frontend-conventions.md（UI/前端规范，视觉权威取第 9 节）；docs/architecture/technology-decisions.md（总体技术选型，确定目标前端框架/组件库）
- docs/product/open-questions.md（只读，生成时不擅自决策）
- docs/product/reference-research.md（参考产品与互联网调研结论；用于页面与状态参考）
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-impact.md（已批准的基线快照）
- openspec/changes/<change-id>/design/baseline-binding.json（阶段 05 已审批的约束绑定；本阶段只读继承）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/figma-audit.md（唯一 UI 契约（单文件）：Figma 文件/版本、目标框架/转码说明、PAGE 清单、token 实际值、文字样式、每 PAGE 区块规格、设计代码说明、断言范围、状态覆盖与决策、资产清单、MCP 读取记录、差异与待确认、UI 评审 APPROVED；无 UI 时 N/A + 理由）
- openspec/changes/<change-id>/design/figma-code/（README.md + 每 PAGE 一个 PAGE-00N.vue（React 栈为 .tsx）；06 按总体技术选型转码的目标框架设计代码；08 直接移植只补业务逻辑）
- openspec/changes/<change-id>/design/figma-layout.csv（精简断言表：page_id/route/element_id/figma_node_id/x/y/width/height/dom_selector/assert_geometry/assert_text/tolerance_px/text_content/font_size/font_weight/notes；06 可留 route/dom_selector 为 PENDING，07 填满）
- openspec/changes/<change-id>/design/figma-assets/README.md（仅当有真实图片/SVG 资产时生成；不保存参考截图）

**输出消费者**

- openspec/changes/<change-id>/design/figma-audit.md → 07、08、09、10
- openspec/changes/<change-id>/design/figma-assets/README.md → evidence-only
- openspec/changes/<change-id>/design/figma-code/ → 07、08、09、10
- openspec/changes/<change-id>/design/figma-layout.csv → 07、08、09、10

**下游交接**

- design/figma-audit.md（目标框架/转码说明、token 实际值、PAGE 规格、状态决策）、design/figma-code/（06 按总体技术选型转码的目标框架设计代码）与 design/figma-layout.csv（运行态断言表）是 07/08/09/10 的唯一界面输入；07/08 默认离线消费，仅在文件版本变化或页面有歧义时按页批量重读 Figma（串行，避免限流）
- PAGE ID 与页面集合在 06 冻结；07 初始化 traceability.csv 的 PAGE→AC，08–10 只读，不新增或重命名 PAGE
- 视觉规范取 docs/architecture/frontend-conventions.md 第 9 节与 figma-audit.md 的 token 实际值；Figma 评审稿与 figma-code/ 是视觉/组件/变量的最终参考；不维护 design-tokens.json 或分散 token/contract JSON；截图不是门禁证据

**审批与门禁**

- 审批：用户（设计负责人）在真实 Figma 评审稿上完成 UI 评审并 APPROVED，且 Figma MCP 审计通过
- 门禁：scripts/check-figma-audit.py --change <change-id> --strict --require-framework（目标框架/转码 + token 实际值 + 每 PAGE 规格 + figma-code/ 每 PAGE 代码 + figma-layout.csv 断言表几何/文本/选择器完整性 + 状态决策 + UI 评审 APPROVED）；workflow.py 自动复核 baseline-binding.json（requirement phase）

---

### 07 详细设计、接口与测试设计

- 范围：单个功能 Change
- Skill：`detailed-design`
- Prompt：`prompts/07-detailed-design.md`
- 依赖（DAG）：`06-figma-design-review`

**精简输入（默认读取，建议预算）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design/user-stories.md、tasks.md、design.md
- openspec/changes/<change-id>/design/baseline-impact.md、baseline-binding.json
- 现有功能代码地址/第三方接口清单（用户提供）
- 涉及 UI 时：openspec/changes/<change-id>/design/figma-audit.md、figma-code/、figma-layout.csv、Figma 评审稿
- docs/architecture/technology-decisions.md、docs/architecture/api-conventions.md、docs/architecture/frontend-conventions.md#9、docs/architecture/test-strategy.md（按设计域）
- docs/architecture/baseline-status.md
- docs/product/BASELINE-BRIEF.md、docs/product/id-conventions.md
- 命中的 FLOW/NODE/DO/RD/BR/ROLE/CAP/PAGE 行（按 ID 定向读取）

> 预算（建议值）：8/8 条；超出时缩小范围或记录多读原因。

**按需输入（触发后读取，不计入默认预算）**

- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/rd-matrix.csv
- docs/product/business-rules.md
- docs/product/acceptance-policy.md
- docs/product/role-permission-matrix.csv
- docs/product/open-questions.md
- docs/architecture/system-context.md
- docs/architecture/domain-boundaries.md
- docs/architecture/containers-and-deployment.md
- docs/architecture/data-flows.md
- docs/architecture/logical-erd.md
- docs/adr/*
- docs/product/reference-research.md

**完整契约输入（内容/材料，审计集）**

- 现有功能代码地址与可访问性（若修改现有功能代码；含仓库/路径/分支/commit）
- 03 基线中的第三方接口清单与沙箱/契约/测试替身要求

**完整契约输入（文档/文件，审计集）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、design/user-stories.md（提案需求、AC 与初始设计决策）
- openspec/changes/<change-id>/tasks.md（任务范围）
- openspec/changes/<change-id>/design/figma-audit.md（目标框架/转码说明、token 实际值、文字样式、每 PAGE 区块规格、状态决策；默认离线消费，仅在版本变化/歧义时按页重读）、design/figma-code/（06 按总体技术选型转码的目标框架设计代码）与 design/figma-layout.csv（断言映射；07 填满 route/dom_selector）
- Figma 评审稿（视觉/组件/变量权威）与 docs/architecture/frontend-conventions.md 第 9 节（视觉规范）；不维护 design-tokens.json，token 实际值见 figma-audit.md
- docs/product/workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、acceptance-policy.md、role-permission-matrix.csv、id-conventions.md、open-questions.md（关联 FLOW/NODE/DO/BR、验收口径、权限与 ID 约定；open-questions 只读）
- docs/product/capabilities.csv、docs/product/modules.csv、docs/architecture/code-layout.json（模块归属、模块路径与集成/冻结路径，用于声明并校验 ### Implementation Slice）
- docs/architecture/system-context.md、domain-boundaries.md、containers-and-deployment.md、data-flows.md、logical-erd.md、technology-decisions.md、api-conventions.md、frontend-conventions.md、test-strategy.md、docs/adr/README.md 与 docs/adr/*（按设计域按需读取）；docs/product/BASELINE-BRIEF.md（先读）
- docs/architecture/quality-gates.json（已启用时；用于规划的冻结静态分析门禁与豁免政策）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design.md（统一设计：设计决策、接口、前端、后端、测试五节；`## Design Decisions` 下含 `### Implementation Slice`：主能力、归属/关联模块、切片类型/覆盖、代码包、拥有/集成路径、模块卡动作，以及可选的 Frozen approvals/out-of-context 声明；切片是本文件中的内容，不是单独文件）
- openspec/changes/<change-id>/design/figma-layout.csv（07 填满每行 route/dom_selector，并据此定义响应式规则；几何/文本/字体值以目标框架设计代码与 metadata 为准）<br>openspec/changes/<change-id>/design.md 的 ### PAGE→BLOCK→组件映射（以 figma-code 目标框架设计代码为基线，仅登记业务化适配与 UI-DEVIATION，不重新设计样式/布局/文案）
- openspec/changes/<change-id>/design/ui-actions.csv（交互控件清单：每个功能按钮/图标/链接/菜单/标签页映射到跳转（地址+入参）、API（operationId 存在于 api/openapi.yaml）或用户已确认（确认人+日期）的本地动作）
- openspec/changes/<change-id>/design/baseline-impact.md（07 更新设计复核结论：NO_IMPACT/REBASE_REQUIRED 与设计证据）
- openspec/changes/<change-id>/design/baseline-binding.json（07 写入逐条约束的设计证据）
- openspec/changes/<change-id>/design/test-cases.csv（TEST ID → AC/PAGE/API/IO 的测试用例矩阵，含失败注入/替身环境/人工原因；BLOCK 可选，不适用写 N/A）
- openspec/changes/<change-id>/api/openapi.yaml（条件适用：有 API 时）
- openspec/changes/<change-id>/design/api-io-mapping.csv（条件适用：有 API 时）
- openspec/changes/<change-id>/design/io-catalog.csv（条件适用：有 API 时）
- openspec/changes/<change-id>/design/interface-catalog.csv（跨边界接口目录：HTTP/原生桥接/设备/第三方/异步/文件；条件适用：有跨边界接口时）
- openspec/changes/<change-id>/design/static-waivers.json（条件适用：需要静态分析豁免时；Change 级文件+规则豁免，含理由/责任人/审批人/批准日期/过期时间；绝不存入冻结门禁文件；无需豁免时省略文件或保留空列表）
- openspec/changes/<change-id>/traceability.csv（合并 API 与测试映射；唯一追踪聚合文件）

**输出消费者**

- openspec/changes/<change-id>/design/baseline-impact.md → 08、09、10
- openspec/changes/<change-id>/design/baseline-binding.json → 08、09、10
- openspec/changes/<change-id>/design.md → 08、09、10
- openspec/changes/<change-id>/api/openapi.yaml → 08、09
- openspec/changes/<change-id>/design/api-io-mapping.csv → 08、09
- openspec/changes/<change-id>/design/io-catalog.csv → 08、09
- openspec/changes/<change-id>/design/interface-catalog.csv → 08、09、10
- openspec/changes/<change-id>/design/static-waivers.json → 08、09、10
- openspec/changes/<change-id>/traceability.csv → 08、09、10
- openspec/changes/<change-id>/design/test-cases.csv → 08、09、10
- openspec/changes/<change-id>/design/figma-layout.csv → 08、09、10
- openspec/changes/<change-id>/design/ui-actions.csv → 08、09

**下游交接**

- 统一设计决策、`### Implementation Slice`（主能力、归属/关联模块、切片类型/覆盖、代码包、拥有/集成路径、模块卡动作）、接口契约、前后端实现约束、测试用例矩阵、figma-layout.csv 断言映射、ui-actions.csv 控件动作映射与唯一追踪矩阵

**审批与门禁**

- 审批：技术负责人确认设计范围、接口与测试方案
- 门禁：scripts/check-change.sh <change-id>；scripts/check-design-assets.sh <change-id> --strict --lint-api（涉及 UI 时同时校验 figma-audit 与 ui-actions）；scripts/check-design-sections.py --change <change-id>（含 ### 现有代码变更影响、figma-layout.csv route/dom_selector 填满、ui-actions.csv 存在与响应式规则）；scripts/check-design-sections.py --change <change-id> --slice-only 与 scripts/check-change-footprint.py <change-id> --declaration-only（07→08 Implementation Slice 硬门禁；workflow.py transition 自动运行 slice-only 检查）；涉及 UI 时 scripts/check-ui-actions.py --change <change-id> --strict（每个功能按钮/图标/链接/菜单/标签页映射到跳转地址+入参或 OpenAPI operationId，否则须用户确认本地动作）；scripts/check-test-cases.py --change <change-id> --strict；scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict；有 API 时 scripts/check-api-traceability.py --change <change-id>；有跨边界接口时 scripts/check-interface-catalog.py --change <change-id> --strict；python scripts/check-method-evidence.py --step 07-detailed-design --evidence <evidence>（必需方法技能、真实证据路径与产物落点）；python3 scripts/baseline-governance.py check-change --change-id <id> --phase design

**基线交互**

- 只读：当前 Change 的 design/baseline-impact.md；docs/architecture/baseline-status.md；本设计域适用的项目基线
- 产出/复核：更新 baseline-impact.md 的复核结论/受影响域/NO_IMPACT 或 REBASE_REQUIRED
- 门禁：发现冲突必须提出基线修订；受影响设计在审批前不得冻结

---

### 08 实现、TDD、验证与代码审查

- 范围：单个功能 Change
- Skill：`implementation-orchestrator`
- Prompt：`prompts/08-implementation-orchestrator.md`
- 依赖（DAG）：`07-detailed-design`

**精简输入（默认读取，建议预算）**

- 当前 Change 的 tasks.md、design.md、specs、user-stories、test-cases.csv、traceability.csv
- 适用时的 api/openapi.yaml、api-io-mapping.csv、io-catalog.csv、interface-catalog.csv
- 涉及 UI 的 figma-audit.md、figma-code/、figma-layout.csv
- 当前 Change 的 design/baseline-impact.md、baseline-binding.json、baseline-status.md
- 设计域命中的架构章节：system-context/domain-boundaries/logical-erd/data-flows/technology-decisions/api-conventions/frontend-conventions/test-strategy
- docs/product/BASELINE-BRIEF.md
- docs/product/open-questions.md（仅相关条目）
- 现有功能代码地址（若修改现有功能）

> 预算（建议值）：8/8 条；超出时缩小范围或记录多读原因。

**按需输入（触发后读取，不计入默认预算）**

- docs/product/acceptance-policy.md
- docs/architecture/system-context.md
- docs/architecture/domain-boundaries.md
- docs/architecture/logical-erd.md
- docs/architecture/data-flows.md
- docs/architecture/technology-decisions.md
- docs/architecture/api-conventions.md
- docs/architecture/frontend-conventions.md
- docs/architecture/test-strategy.md
- docs/adr/*

**完整契约输入（内容/材料，审计集）**

- N/A

**完整契约输入（文档/文件，审计集）**

- openspec/changes/<change-id>/tasks.md、design.md（已批准；实现依据其中的 `### Implementation Slice`：主能力、归属/关联模块、切片类型/覆盖、代码包、拥有/集成路径与模块卡动作）
- docs/product/capabilities.csv、docs/product/modules.csv、docs/architecture/code-layout.json（模块归属与切片/集成/冻结路径规则，供快照、上下文清单与 footprint 检查使用）
- openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（AC）
- openspec/changes/<change-id>/api/openapi.yaml、design/api-io-mapping.csv、design/io-catalog.csv、design/interface-catalog.csv（适用时）
- openspec/changes/<change-id>/design/test-cases.csv（按 TEST ID 实现与执行测试）
- openspec/changes/<change-id>/design/figma-audit.md（涉及 UI 时读取目标框架/转码说明、token 实际值/PAGE 规格/状态决策；06 冻结 PAGE 清单）、design/figma-code/（06 按总体技术选型转码的目标框架设计代码）与 design/figma-layout.csv（断言映射）
- openspec/changes/<change-id>/traceability.csv
- docs/architecture/quality-gates.json（已启用时；冻结静态分析门禁）与 openspec/changes/<change-id>/design/static-waivers.json（存在时；由运行器与检查器应用的 Change 级豁免）
- docs/architecture/system-context.md、domain-boundaries.md、logical-erd.md、data-flows.md、technology-decisions.md、api-conventions.md、frontend-conventions.md、test-strategy.md、docs/adr/README.md（实现约束）；docs/product/open-questions.md（只读；实现不得擅自关闭未决问题）
- openspec/changes/<change-id>/design/baseline-impact.md（已批准的基线快照）
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定）

**输出（内容/材料）**

- 实际源代码/迁移/配置
- 自动化测试代码与运行结果
- 实现/验证证据
- 条件适用：基线变更请求/ADR 草案（发现冲突时；未经批准不更新冻结基线）

**输出（文档/文件）**

- openspec/changes/<change-id>/design/evidence/code-review.md（涉及 UI 时含 ## UI fidelity 逐 PAGE 数值表：Figma node/断言元素数/最大偏差/布局证据/差异/结论/审批人；数值直接取自 figma-layout-check.json，仅差异/UI-DERIVED PAGE 需人工说明与审批；启用质量门禁时含 ## Static analysis 表，从 static-analysis.json 逐行复制：各栈/工具命令、配置路径 @ SHA-256、结果、字面 exit 0 及生效豁免与审批人）
- openspec/changes/<change-id>/design/evidence/static-analysis.json（启用质量门禁时；由 scripts/run-quality-gates.py 生成：各 blocking 栈/工具命令、工作目录、退出码、配置 SHA-256、门禁文件 SHA-256、源码 revision、生效豁免、结论）
- openspec/changes/<change-id>/design/evidence/static-analysis-logs/（启用质量门禁时；每个 blocking 栈/工具一份捕获日志；日志文件名由净化后的栈根目录加工具 id 派生）
- openspec/changes/<change-id>/design/evidence/figma-layout-check.json（scripts/check-figma-layout.py 的逐元素 expected/actual/delta 证据）
- openspec/changes/<change-id>/design/evidence/implementation-base.json（脚本生成的入口快照：git HEAD、逐文件 SHA-256 与指纹；由 scripts/implementation-snapshot.py 写入；implementation-snapshot 始终写入入口基线，即使 code-layout 策略为 none）
- openspec/changes/<change-id>/design/context-manifest.json（scripts/code-context.py 生成的检索闭包：read_set/not_needed/missing；不是门禁；strategy none 时不写文件）
- 模块卡 `<module_path>/MODULE.md`：为本切片创建或更新的每个模块创建/更新（无固定路径；由模块注册表检查校验）
- openspec/changes/<change-id>/design/evidence/implementation-diff.json（被验证修订的 commit/diff SHA-256 与变更路径）

**输出消费者**

- openspec/changes/<change-id>/design/evidence/code-review.md → 09、10
- openspec/changes/<change-id>/design/evidence/static-analysis.json → 09、10
- openspec/changes/<change-id>/design/evidence/static-analysis-logs/ → evidence-only
- openspec/changes/<change-id>/design/evidence/figma-layout-check.json → 09、10
- openspec/changes/<change-id>/design/evidence/implementation-base.json → 09
- openspec/changes/<change-id>/design/context-manifest.json → evidence-only
- openspec/changes/<change-id>/design/evidence/implementation-diff.json → 09、10

**下游交接**

- 代码差异、入口快照与 footprint 证据（design/evidence/implementation-base.json 与 implementation-diff.json）、模块卡、测试报告、审查结论、未解决问题、figma-layout-check.json 与 token 检查结果
- 启用质量门禁时：openspec/changes/<change-id>/design/evidence/static-analysis.json、openspec/changes/<change-id>/design/evidence/static-analysis-logs/ 与 design/evidence/code-review.md 的 ## Static analysis 节

**审批与门禁**

- 审批：代码审查阻断项关闭；合并按项目权限单独审批
- 门禁：TDD；scripts/test-all.sh；scripts/verify-before-completion.sh；python scripts/implementation-snapshot.py <change-id>（08 入口快照；返工时 --force --reason）与 python scripts/code-context.py <change-id>（检索清单，开始前读取其 read_set）；python scripts/check-change-footprint.py <change-id>（写入 implementation-diff.json；08→09 硬门禁在 transition 时自动运行 --verify）；`docs/architecture/quality-gates.json` 存在时：`python scripts/check-quality-gates.py --root . --strict --require-materialized`；`python scripts/run-quality-gates.py <change-id> --output openspec/changes/<change-id>/design/evidence/static-analysis.json --identity <builder>`；`python scripts/check-static-analysis.py --change <change-id> --strict`（阶段 08 的权威静态分析转换命令）；scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900；scripts/check-design-tokens.py --change <change-id> --tokens <token.css>；scripts/check-code-review.py --change <change-id> --strict（UI Change 的 ## UI fidelity 数值直接取自 figma-layout-check.json，仅差异/UI-DERIVED PAGE 需人工说明；启用门禁时 ## Static analysis 行从 static-analysis.json 复制）；baseline-governance.py check-change --phase implementation

**基线交互**

- 只读：已批准的 design/baseline-impact.md；当前 docs/architecture/baseline-status.md 版本
- 产出/复核：实现中发现的基线冲突记录、适用时的基线变更请求/ADR
- 门禁：不得直接修改冻结基线；未批准时暂停受影响任务；批准后刷新 Change 快照并重新验证

---

### 09 独立验证与验收证据

- 范围：功能级
- Skill：`independent-verifier`
- Prompt：`prompts/09-independent-verification.md`
- 依赖（DAG）：`08-implementation-orchestrator`

**精简输入（默认读取，建议预算）**

- 已实现代码及 revision/diff 指纹
- 当前 Change 的 proposal/specs/design/user-stories/tasks
- 适用时的 api/openapi.yaml、api-io-mapping.csv、io-catalog.csv、interface-catalog.csv
- 涉及 UI 的 figma-audit.md、figma-layout.csv、figma-layout-check.json
- test-cases.csv、traceability.csv、code-review.md、Builder 测试证据
- docs/product/BASELINE-BRIEF.md
- docs/product/acceptance-policy.md
- 当前 Change 的 baseline-impact.md、baseline-binding.json、baseline-status.md

> 预算（建议值）：8/8 条；超出时缩小范围或记录多读原因。

**按需输入（触发后读取，不计入默认预算）**

- docs/architecture/system-context.md
- docs/architecture/domain-boundaries.md
- docs/architecture/logical-erd.md
- docs/architecture/data-flows.md
- docs/architecture/technology-decisions.md
- docs/architecture/api-conventions.md
- docs/architecture/frontend-conventions.md
- docs/architecture/test-strategy.md
- docs/adr/*
- docs/product/open-questions.md

**完整契约输入（内容/材料，审计集）**

- 已实现代码及 revision/diff 指纹

**完整契约输入（文档/文件，审计集）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、tasks.md、design/user-stories.md（已批准需求、设计与 AC）
- openspec/changes/<change-id>/api/openapi.yaml、design/api-io-mapping.csv、design/io-catalog.csv、design/interface-catalog.csv（适用时）
- openspec/changes/<change-id>/design/figma-audit.md（涉及 UI 时对照目标框架/转码说明、token 实际值/PAGE 规格/状态决策）、design/figma-code/（06 按总体技术选型转码的目标框架设计代码）与 design/figma-layout.csv（断言映射）
- docs/product/acceptance-policy.md（项目级验收口径）
- openspec/changes/<change-id>/design/test-cases.csv（测试用例与执行结果核对）
- openspec/changes/<change-id>/design/evidence/code-review.md、Builder 测试与验证证据；docs/product/open-questions.md（只读；验证不得擅自关闭未决问题）
- openspec/changes/<change-id>/traceability.csv（追踪矩阵）
- docs/architecture/quality-gates.json 与 openspec/changes/<change-id>/design/static-waivers.json（已启用时；冻结门禁与 Change 级豁免独立复核）
- openspec/changes/<change-id>/design/evidence/static-analysis.json（启用质量门禁时；08 Builder 证据与 builder 身份；09 独立重跑门禁）
- 已批准基线快照与 baseline-impact.md
- openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定）
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/evidence/figma-layout-check.json（08 实测；09 必须独立重跑 check-figma-layout.py）
- openspec/changes/<change-id>/design/evidence/implementation-base.json（入口快照，用于独立重算差异）
- openspec/changes/<change-id>/design/evidence/implementation-diff.json（被验证修订的 commit/diff SHA-256 与变更路径）
- docs/adr/README.md 与 docs/adr/*（按需读取已批准的架构决策）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md
- openspec/changes/<change-id>/design/evidence/independent-verification.json
- openspec/changes/<change-id>/design/evidence/static-analysis-independent.json（启用质量门禁时；verifier 与 builder 身份不同的独立重跑证据；由 scripts/run-quality-gates.py --independent 生成）

**输出消费者**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md → 10
- openspec/changes/<change-id>/design/evidence/independent-verification.json → 10
- openspec/changes/<change-id>/design/evidence/static-analysis-independent.json → 10

**下游交接**

- 独立验证报告与 JSON 证据（启用质量门禁时含 static_checks）
- 启用质量门禁时的 static-analysis-independent.json
- AC 逐项验证结果
- 测试命令与退出码
- layout_checks（逐 PAGE 断言元素数/最大偏差/容差/缺失元素/判定/证据）
- 发现项和未执行项

**审批与门禁**

- 审批：独立验证 PASS；Verifier 不得是本次 Builder 的同一执行上下文；失败/阻断退回实现阶段
- 门禁：scripts/check-independent-verification.py；所有适用 AC PASS、测试退出码 0、revision 稳定、只读、无 BLOCKER/CRITICAL；`docs/architecture/quality-gates.json` 存在时：`python scripts/run-quality-gates.py <change-id> --independent --identity <verifier> --builder-identity <08 builder> --output openspec/changes/<change-id>/design/evidence/static-analysis-independent.json`；`python scripts/check-static-analysis.py --change <change-id> --expect-independent`（全部 static_checks PASS、无门禁漂移、无过期/无效豁免）；scripts/check-change-footprint.py <change-id> --verify（08→09 硬门禁：对照 implementation-base.json 重算工作区差异，与 implementation-diff.json 比较排序后的 changed-path 集合与 diff_sha256，并重跑切片分类；workflow.py transition 自动运行）；涉及 UI 时 layout_checks 全部 PASS 且 test_runs 含独立重跑的 check-figma-layout.py exit 0、check-design-tokens.py exit 0；人工视觉抽查仅限差异/UI-DERIVED/未断言 PAGE；baseline-governance.py check-change --phase implementation

---

### 10 人工验收、归档与基线回写

- 范围：单个功能 Change
- Skill：`acceptance-audit`
- Prompt：`prompts/10-acceptance-audit.md`
- 依赖（DAG）：`09-independent-verification`

**精简输入（默认读取，建议预算）**

- independent-verification-report.md 与 independent-verification.json
- 当前 Change 的 specs、user-stories、traceability.csv、design.md、code-review.md
- 涉及 UI 的 figma-audit.md、figma-layout.csv、figma-layout-check.json
- test-cases.csv、interface-catalog.csv
- 当前 Change 的 baseline-impact.md、baseline-binding.json、baseline-status.md
- docs/product/acceptance-policy.md、BASELINE-BRIEF.md、change-sizing.md
- docs/product/decisions.md、assumptions.md、id-conventions.md
- 运行中的验收环境入口

> 预算（建议值）：8/8 条；超出时缩小范围或记录多读原因。

**按需输入（触发后读取，不计入默认预算）**

- design/figma-code/
- docs/adr/*
- docs/product/requirements-analysis.md
- docs/product/workflows.md
- docs/product/data-objects.csv
- docs/product/business-rules.md
- docs/product/lessons.md

**完整契约输入（内容/材料，审计集）**

- 已实现代码与测试证据
- 运行中的验收环境入口（URL/路由；人工 UI 验收无差异 PAGE 按机器证据签收，差异/UI-DERIVED PAGE 并排核对，不使用截图）

**完整契约输入（文档/文件，审计集）**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md 与 independent-verification.json（必须 PASS，revision 必须与当前验收代码一致）
- openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md、traceability.csv（已批准 AC/规格/追踪）
- openspec/changes/<change-id>/design.md（设计依据）
- openspec/changes/<change-id>/design/evidence/code-review.md
- docs/architecture/quality-gates.json 与 openspec/changes/<change-id>/design/static-waivers.json（已启用时；检查门禁文件有效性与 Change 级豁免是否过期）
- openspec/changes/<change-id>/design/evidence/static-analysis.json 与 openspec/changes/<change-id>/design/evidence/static-analysis-independent.json（启用质量门禁时；验收以这两份证据核对 ## Static analysis，并在非 PASS、门禁漂移或豁免过期/无效时阻断）
- openspec/changes/<change-id>/design/figma-audit.md（涉及 UI 时验收目标框架/转码说明、token 实际值/PAGE 规格/状态与 Figma 评审稿一致性）、design/figma-code/（06 按总体技术选型转码的目标框架设计代码）、design/figma-layout.csv（断言映射）与 design/evidence/figma-layout-check.json（必须 PASS）
- openspec/changes/<change-id>/design/test-cases.csv（验收测试覆盖证据）
- openspec/changes/<change-id>/design/interface-catalog.csv（跨边界接口验收证据）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（所有适用约束有最终验证证据）
- docs/product/acceptance-policy.md（项目级验收口径）
- docs/product/BASELINE-BRIEF.md、change-sizing.md（DoD）、lessons.md、open-questions.md（常驻基线、完成定义、历史教训与未决问题；open-questions 只读）
- docs/product/decisions.md、assumptions.md（待验收结果更新的决策与假设登记）
- docs/product/capabilities.csv、docs/product/modules.csv（验收后待回写的能力进度与模块归属注册表）
- docs/product/id-conventions.md（回写基线与 Change ID 的分配规则）
- docs/adr/README.md 与 docs/adr/*（按需读取已批准的架构决策）

**输出（内容/材料）**

- 验收报告与批准记录
- OpenSpec archive 结果及更新后的主规格（仅批准后）

**输出（文档/文件）**

- openspec/changes/<change-id>/design/evidence/acceptance.md（涉及 UI 时含 ## UI acceptance 逐 PAGE 签收：Figma node/运行系统入口/差异审批/验收方式（机器证据/并排核对）/评审人；启用质量门禁时含 ## Static analysis，从 static-analysis.json 与 static-analysis-independent.json 核对：各栈/工具命令、结果、字面 exit 0 及每个生效豁免与审批人）
- docs/product/lessons.md（追加本次可复用教训；无则 N/A + 理由）
- docs/product/decisions.md（受验收结果影响的状态更新）
- docs/product/assumptions.md（受验收结果影响的状态更新）
- docs/product/capabilities.csv（能力进度回写：status、delivered_slices、remaining_slices 与 active_changes；由 scripts/check-capabilities.py --completed <change-id> 校验）
- docs/product/modules.csv（模块归属回写：模块 status/capabilities；Change 完成某个模块时由 scripts/check-modules.py --completed <module-slug> 校验）

**输出消费者**

- openspec/changes/<change-id>/design/evidence/acceptance.md → evidence-only
- docs/product/lessons.md → FUTURE
- docs/product/decisions.md → FUTURE
- docs/product/assumptions.md → FUTURE
- docs/product/capabilities.csv → FUTURE
- docs/product/modules.csv → FUTURE

**下游交接**

- 已验收并归档的能力规格、验收证据、后续 Change 依赖

**审批与门禁**

- 审批：产品责任人明确批准后才可归档；不得用 -y 绕过
- 门禁：scripts/check-acceptance.py（UI Change 校验 ## UI acceptance 逐 PAGE 运行入口/签收与 figma-layout-check.json PASS；无差异 PAGE 可机器证据批量签收，差异/UI-DERIVED PAGE 并排核对）；python scripts/check-capabilities.py --completed <change-id>；python scripts/check-modules.py --completed <module-slug>（Change 完成某个模块时）；`docs/architecture/quality-gates.json` 存在时：verify-before-completion.sh（默认运行静态门禁）并在 ## Static analysis 核对静态证据；非 PASS、门禁漂移或豁免过期/无效时阻断验收；openspec validate/archive 真实执行；阶段 09 独立验证必须 PASS 且 revision 未变化；baseline-governance.py check-change --phase acceptance

**基线交互**

- 只读：design/baseline-impact.md；当前基线状态；已批准的 ADR/基线变更请求
- 产出/复核：更新 docs/product/lessons.md、decisions.md、assumptions.md（仅回写已批准、已实现、已验证的跨功能决策）；在途 Change 影响复核清单；需要更新冻结基线时，提交基线修订请求并按 open-amendment/close-amendment 流程执行，不直接编写基线文件
- 门禁：只回写已批准/已实现/已验证的跨功能决策；功能细节留在 Change

---
