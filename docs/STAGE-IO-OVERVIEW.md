# 阶段输入输出总览

> 状态：DERIVED（由权威契约自动生成，请勿手工编辑）
> Change ID：N/A（项目级流程总览）
> 来源基线：`docs/STEP-ARTIFACT-CONTRACTS.json`（输入/输出/审批/门禁）、`docs/WORKFLOW-STAGES.json`（依赖 DAG）
> 关联需求/AC：N/A（流程文档）
> 生成版本：`src-sha256:a9223e946cc3`

> 本文件只汇总阶段交接面。字段级产物模板见 `docs/OUTPUT-TEMPLATE-MATRIX.csv`；流程入口见 `prompts/00-next-step.md`。
> 修改阶段交接必须先改两份 JSON 源文件，再执行 `python scripts/stage-io-report.py --out docs/STAGE-IO-OVERVIEW.md` 重新生成；`scripts/check-package.py` 会检查本文件是否过期。

共 17 个契约阶段：16 个 DAG 阶段 + 00 下一步编排（非 DAG 阶段）。

## 阶段分组

| 分组 | 阶段链路 | 说明 |
|---|---|---|
| 项目基线链 | 00 → 01 → 02 → 05 → 09 | 需求业务梳理 → 总体架构/数据/公共契约 → 结束审计冻结 → 路线图 |
| 提案交付链 | 09 → 10 → 10b → 11 → 12 → 13a → 13b → 13c/13d → 13e → 14 → 14b → 15 | 提案需求 → 原型 → 页面清单 → Figma → 详细设计 → 实现 → 独立验证 → 验收 |

## 总览

> 总览把输入/输出合并展示；逐阶段明细再拆分为“内容/材料”和“文档/文件”。

| 阶段 | 名称 | 范围 | Skill | 依赖（DAG） | 输入 | 输出 |
|---|---|---|---|---|---|---|
| 00 | 下一步编排 | 项目级与功能级通用 | `workflow-orchestrator` | N/A（编排入口，不属于 DAG 阶段） | workflow-state.json<br>docs/PROCESS-MAP.md<br>docs/STEP-ARTIFACT-CONTRACTS.json<br>docs/OUTPUT-TEMPLATE-MATRIX.csv<br>真实产物与审批记录<br>OpenSpec CLI 当前状态（如已初始化） | 下一阶段判定报告（对话展示；必要时写入 docs/workflow/next-step-report.md）<br>workflow-state.json（仅在真实状态变化时更新） |
| 01 | 项目初始化与工具链检查 | 项目级 | `project-bootstrap` | 无（流程起点） | 用户提供的项目目标与仓库位置<br>仓库现有目录/配置/AGENTS.md（若存在） | AGENTS.md（仅缺失时创建或经批准修改）<br>workflow-state.json<br>docs/architecture/baseline-status.md（依据 templates/project-baseline/baseline-status.md）<br>docs/project/toolchain-report.md（依据 templates/project-baseline/toolchain-report.md） |
| 02 | 需求业务梳理 | 项目级 | `requirements-analysis` | `01-project-bootstrap` | 访谈/业务材料/旧系统资料<br>项目目标、用户、角色、约束<br>既有 docs/product/*（若存在）<br>既有 OpenSpec specs（只读） | docs/product/requirements-analysis.md<br>docs/product/workflows.md（每个 FLOW 必须含完整节点表：节点角色、输入/输出数据对象、前置条件、处理动作、异常/分支、下一节点）<br>docs/product/data-objects.csv（业务数据对象目录）<br>docs/product/rd-matrix.csv（需求-数据对象矩阵：需求/规则 → 流程节点 → 角色 → 数据对象）<br>docs/product/business-rules.md<br>docs/product/glossary.md<br>docs/product/acceptance-policy.md<br>docs/product/open-questions.md |
| 05 | 项目总体架构设计 | 项目级 | `project-architecture-baseline` | `02-requirements-analysis` | 已批准的 docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md<br>现有仓库结构/技术约束<br>非功能需求<br>用户/技术负责人明确的技术选型偏好（本阶段必须显式询问并记录，不得默认或自行假设） | docs/architecture/system-context.md<br>docs/architecture/domain-boundaries.md<br>docs/architecture/containers-and-deployment.md<br>docs/architecture/data-flows.md（数据流转：DF ID、同步/异步、事务边界、失败与补偿）<br>docs/architecture/logical-erd.md（逻辑实体、关系、数据所有权、领域不变量）<br>docs/architecture/technology-decisions.md（含技术选型访谈记录、候选比较、用户确认人与日期）<br>docs/architecture/api-conventions.md<br>docs/architecture/frontend-conventions.md<br>docs/architecture/test-strategy.md<br>docs/adr/README.md<br>docs/architecture/baseline-status.md（经本阶段结束审计的各域版本/冻结状态）<br>docs/architecture/baseline-manifest.json（机器权威版本/冻结状态/域文件 SHA-256）<br>docs/architecture/constraint-registry.json（稳定约束 ID 与审批状态）<br>docs/project/baseline-audit-report.md（本阶段结束审计报告） |
| 09 | 提案拆分、依赖排序与路线图 | 项目级到功能级 | `proposal-planning` | `05-project-architecture-baseline` | 已批准并冻结的项目总体架构与基线（阶段 05 结束审计）<br>需求业务梳理、RD 矩阵、业务规则与验收政策<br>已知技术债与依赖<br>docs/architecture/baseline-status.md<br>相关架构/数据/API/前端/测试基线版本与审批信息 | docs/product/proposal-roadmap.md<br>每个候选 Change 的范围/依赖/价值说明<br>候选 Change 基线适用域/潜在修订摘要（写入 docs/product/proposal-roadmap.md） |
| 10 | 提案级需求分析 | 单个功能 Change | `feature-requirements` | `09-proposal-planning` | 已批准路线图/当前 Change 范围<br>docs/architecture/baseline-status.md 与相关架构/数据/公共契约/测试基线<br>关联 FLOW/BR/AC 与项目 RD 矩阵<br>现有 OpenSpec specs<br>docs/architecture/baseline-manifest.json 与 docs/architecture/constraint-registry.json（机器权威来源） | openspec/changes/<change-id>/proposal.md<br>openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）<br>openspec/changes/<change-id>/tasks.md（初步任务）<br>openspec/changes/<change-id>/design.md（有设计决策时）<br>openspec/changes/<change-id>/design/user-stories.md（提案级用户故事与 AC）<br>openspec/changes/<change-id>/design/use-cases.md（提案级功能用例）<br>openspec/changes/<change-id>/design/baseline-impact.md（依据 templates/change-assets/design/baseline-impact.md）<br>openspec/changes/<change-id>/design/baseline-binding.json（依据当前冻结基线自动生成，逐条绑定 ACTIVE Constraint ID） |
| 10b | 提案原型生成与评审 | 单个功能 Change | `prototype-generation` | `10-feature-requirements` | 已批准的提案级需求（proposal/specs/design/user-stories/use-cases）<br>docs/product/open-questions.md（只读，生成时不擅自决策）<br>pen.dev MCP 实际可访问能力（pencil 工具）<br>openspec/changes/<change-id>/design/baseline-binding.json（只读继承） | openspec/changes/<change-id>/design/prototype-build.md<br>openspec/changes/<change-id>/design/prototype-audit.md<br>pen.dev 原型页面（链接登记到构建记录；导出快照若支持） |
| 11 | 页面、功能区块、元素与交互事件清单 | 单个功能 Change | `page-interaction-inventory` | `10b-prototype-generation` | 已批准的提案级需求（proposal/specs/design/user-stories/use-cases）<br>已批准的提案原型构建记录与评审结论（openspec/changes/<change-id>/design/prototype-build.md、prototype-audit.md）<br>项目级业务流程/数据对象/RD 矩阵与 UI/前端规范<br>openspec/changes/<change-id>/design/baseline-binding.json（阶段 10 已审批的约束绑定；本阶段只读继承） | openspec/changes/<change-id>/design/page-inventory.csv<br>openspec/changes/<change-id>/design/block-inventory.csv<br>openspec/changes/<change-id>/design/interaction-map.csv |
| 12 | Figma UI 设计与 MCP 审计 | 单个功能 Change | `figma-ui-audit` | `11-page-interaction-inventory` | 已批准页面/区块/交互清单（含 block_id 归属）<br>已批准功能规格<br>Figma 文件/节点与可访问 MCP 输出<br>项目级设计规范<br>openspec/changes/<change-id>/design/baseline-binding.json（阶段 10 已审批的约束绑定；本阶段只读继承） | openspec/changes/<change-id>/design/figma-audit.md<br>Figma 设计链接/节点映射及导出资源引用 |
| 13a | 功能详细设计总控 | 单个功能 Change | `feature-design` | `12-figma-ui-audit` | 已批准 proposal/specs<br>页面/交互清单与 Figma 审计（适用时）<br>项目级架构/数据/公共契约基线<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批） | openspec/changes/<change-id>/design.md<br>功能详细设计任务分解与设计缺口清单 |
| 13b | OpenAPI 与接口逻辑设计 | 单个功能 Change | `api-contract-design` | `13a-feature-design` | 已批准功能规格与页面交互清单<br>Figma 交互（适用时）<br>项目级 API/鉴权/错误码约定<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批） | openspec/changes/<change-id>/api/openapi.yaml<br>operationId 到页面事件/AC 的追踪关系 |
| 13c | 前端详细设计 | 单个功能 Change | `frontend-detail-design` | `13b-api-contract-design` | 已批准 OpenAPI（或 x-api-scope: none）<br>页面/区块/交互清单（含 block_id 归属）与 Figma 审计<br>前端工程规范<br>功能规格与 AC<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批） | openspec/changes/<change-id>/design/frontend-design.md<br>前端测试用例/组件状态映射 |
| 13d | 后端详细设计 | 单个功能 Change | `backend-detail-design` | `13b-api-contract-design` | 已批准 OpenAPI<br>功能规格与 AC<br>项目级架构/领域/数据模型/公共 Client 规范<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批） | openspec/changes/<change-id>/design/backend-design.md<br>openspec/changes/<change-id>/design/api-io-mapping.csv<br>openspec/changes/<change-id>/design/io-catalog.csv |
| 13e | 测试设计与追踪矩阵 | 单个功能 Change | `test-design` | `13c-frontend-detail-design`、`13d-backend-detail-design` | 已批准功能规格/AC<br>OpenAPI<br>前后端详细设计<br>API→IO 映射与 IO 契约<br>项目级测试策略<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批） | openspec/changes/<change-id>/design/test-design.md<br>openspec/changes/<change-id>/traceability.csv |
| 14 | 实现、TDD、验证与代码审查 | 单个功能 Change | `implementation-orchestrator` | `13e-test-design` | 已批准 tasks.md/design.md<br>前后端详细设计、OpenAPI、IO 契约<br>test-design.md 与 traceability.csv<br>项目级工程规范/测试策略<br>openspec/changes/<change-id>/design/baseline-impact.md（已批准的基线快照）<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定） | 实际源代码/迁移/配置<br>自动化测试代码与运行结果<br>openspec/changes/<change-id>/design/evidence/code-review.md<br>实现/验证证据<br>条件适用：基线变更请求/ADR 草案（发现冲突时；未经批准不更新冻结基线） |
| 14b | 独立验证与验收证据 | 功能级 | `independent-verifier` | `14-implementation-orchestrator` | 已实现代码及 revision/diff 指纹<br>已批准 proposal/specs/design/tasks<br>已批准基线快照与 baseline-impact.md<br>OpenAPI、API-IO 映射、IO catalog（适用时）<br>前后端详细设计、测试设计、Builder 测试和审查报告<br>openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定） | openspec/changes/<change-id>/design/evidence/independent-verification-report.md<br>openspec/changes/<change-id>/design/evidence/independent-verification.json |
| 15 | 人工验收、归档与基线回写 | 单个功能 Change | `acceptance-audit` | `14b-independent-verification` | 阶段 14b 的 independent-verification-report.md 与 independent-verification.json（必须 PASS，revision 必须与当前验收代码一致）<br>已实现代码与测试证据<br>已批准 AC/规格/追踪矩阵<br>代码审查记录<br>部署/演示或验收环境证据<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（所有适用约束有最终验证证据） | openspec/changes/<change-id>/design/evidence/acceptance.md<br>验收报告与批准记录<br>OpenSpec archive 结果及更新后的主规格（仅批准后）<br>项目路线图/基线状态回写（适用时）<br>条件适用：更新项目级基线文档与 baseline-status.md（仅批准/实现/验证完成后） |

## 逐阶段明细

### 00 下一步编排

- 范围：项目级与功能级通用
- Skill：`workflow-orchestrator`
- Prompt：`prompts/00-next-step.md`
- 依赖（DAG）：N/A（编排入口，不属于 DAG 阶段）

**输入（内容/材料）**

- 真实产物与审批记录
- OpenSpec CLI 当前状态（如已初始化）

**输入（文档/文件）**

- workflow-state.json
- docs/PROCESS-MAP.md
- docs/STEP-ARTIFACT-CONTRACTS.json
- docs/OUTPUT-TEMPLATE-MATRIX.csv

**输出（内容/材料）**

- 下一阶段判定报告（对话展示；必要时写入 docs/workflow/next-step-report.md）

**输出（文档/文件）**

- workflow-state.json（仅在真实状态变化时更新）

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

**输入（内容/材料）**

- 用户提供的项目目标与仓库位置

**输入（文档/文件）**

- 仓库现有目录/配置/AGENTS.md（若存在）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- AGENTS.md（仅缺失时创建或经批准修改）
- workflow-state.json
- docs/architecture/baseline-status.md（依据 templates/project-baseline/baseline-status.md）
- docs/project/toolchain-report.md（依据 templates/project-baseline/toolchain-report.md）

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

**输入（内容/材料）**

- 访谈/业务材料/旧系统资料
- 项目目标、用户、角色、约束

**输入（文档/文件）**

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

**下游交接**

- 业务流程与节点级角色/数据对象、业务数据对象目录、RD 矩阵、业务规则、术语与验收政策、未决问题

**审批与门禁**

- 审批：业务/产品负责人确认业务流程完整性、节点数据对象与角色、RD 矩阵覆盖
- 门禁：scripts/check-requirements.py --strict（FLOW/NODE/DO/RD/BR 结构、引用闭合与节点覆盖）

---

### 05 项目总体架构设计

- 范围：项目级
- Skill：`project-architecture-baseline`
- Prompt：`prompts/05-project-architecture-baseline.md`
- 依赖（DAG）：`02-requirements-analysis`

**输入（内容/材料）**

- 现有仓库结构/技术约束
- 非功能需求
- 用户/技术负责人明确的技术选型偏好（本阶段必须显式询问并记录，不得默认或自行假设）

**输入（文档/文件）**

- 已批准的 docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md

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
- docs/adr/README.md
- docs/architecture/baseline-status.md（经本阶段结束审计的各域版本/冻结状态）
- docs/architecture/baseline-manifest.json（机器权威版本/冻结状态/域文件 SHA-256）
- docs/architecture/constraint-registry.json（稳定约束 ID 与审批状态）
- docs/project/baseline-audit-report.md（本阶段结束审计报告）

**下游交接**

- 冻结的项目总体架构基线、数据流转、逻辑 ERD、公共契约/测试策略、ACTIVE 约束目录、审计报告与审批记录

**审批与门禁**

- 审批：产品/架构/技术负责人共同确认系统边界、数据流转与公共契约，并批准基线冻结
- 门禁：scripts/check-required-files.sh --strict；跨文档一致性审计（系统边界/数据流转/ERD/公共契约/术语）；scripts/baseline-governance.py audit --require-frozen（阶段结束冻结审计）

---

### 09 提案拆分、依赖排序与路线图

- 范围：项目级到功能级
- Skill：`proposal-planning`
- Prompt：`prompts/09-proposal-planning.md`
- 依赖（DAG）：`05-project-architecture-baseline`

**输入（内容/材料）**

- 已批准并冻结的项目总体架构与基线（阶段 05 结束审计）
- 需求业务梳理、RD 矩阵、业务规则与验收政策
- 已知技术债与依赖
- 相关架构/数据/API/前端/测试基线版本与审批信息

**输入（文档/文件）**

- docs/architecture/baseline-status.md

**输出（内容/材料）**

- 每个候选 Change 的范围/依赖/价值说明

**输出（文档/文件）**

- docs/product/proposal-roadmap.md
- 候选 Change 基线适用域/潜在修订摘要（写入 docs/product/proposal-roadmap.md）

**下游交接**

- 经批准的 Change 列表、优先级、依赖顺序

**审批与门禁**

- 审批：产品与技术负责人批准路线图及首个 Change
- 门禁：scripts/check-roadmap.py --strict；不在此阶段伪造 Change 验证

**基线交互**

- 只读：docs/architecture/baseline-status.md；相关产品/架构/数据/公共契约/测试基线；openspec/specs/**
- 产出/复核：docs/product/proposal-roadmap.md 中每个 Change 的基线适用域和候选修订

---

### 10 提案级需求分析

- 范围：单个功能 Change
- Skill：`feature-requirements`
- Prompt：`prompts/10-feature-requirements.md`
- 依赖（DAG）：`09-proposal-planning`

**输入（内容/材料）**

- 已批准路线图/当前 Change 范围
- 关联 FLOW/BR/AC 与项目 RD 矩阵

**输入（文档/文件）**

- docs/architecture/baseline-status.md 与相关架构/数据/公共契约/测试基线
- 现有 OpenSpec specs
- docs/architecture/baseline-manifest.json 与 docs/architecture/constraint-registry.json（机器权威来源）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/proposal.md
- openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）
- openspec/changes/<change-id>/tasks.md（初步任务）
- openspec/changes/<change-id>/design.md（有设计决策时）
- openspec/changes/<change-id>/design/user-stories.md（提案级用户故事与 AC）
- openspec/changes/<change-id>/design/use-cases.md（提案级功能用例）
- openspec/changes/<change-id>/design/baseline-impact.md（依据 templates/change-assets/design/baseline-impact.md）
- openspec/changes/<change-id>/design/baseline-binding.json（依据当前冻结基线自动生成，逐条绑定 ACTIVE Constraint ID）

**下游交接**

- 已批准的提案级 US/UC/AC、场景与业务规则、范围边界、需求追踪 ID、基线快照与约束绑定

**审批与门禁**

- 审批：产品负责人批准提案级需求与验收标准；技术负责人确认范围与基线影响
- 门禁：scripts/check-requirements.py --change <change-id> --strict（提案级 UC/US/AC 结构与引用闭合）；openspec validate <change-id> --strict；scripts/check-baseline-impact.py <change-id>；scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement

**基线交互**

- 只读：docs/architecture/baseline-status.md；相关产品/架构/数据/API/前端/测试基线；相关 openspec/specs/**
- 产出/复核：openspec/changes/<change-id>/design/baseline-impact.md
- 门禁：若功能设计依赖未批准的架构/数据/公共契约/质量基线变化，阻断进入详细设计/实现

---

### 10b 提案原型生成与评审

- 范围：单个功能 Change
- Skill：`prototype-generation`
- Prompt：`prompts/10b-prototype-generation.md`
- 依赖（DAG）：`10-feature-requirements`

**输入（内容/材料）**

- 已批准的提案级需求（proposal/specs/design/user-stories/use-cases）
- pen.dev MCP 实际可访问能力（pencil 工具）

**输入（文档/文件）**

- docs/product/open-questions.md（只读，生成时不擅自决策）
- openspec/changes/<change-id>/design/baseline-binding.json（只读继承）

**输出（内容/材料）**

- pen.dev 原型页面（链接登记到构建记录；导出快照若支持）

**输出（文档/文件）**

- openspec/changes/<change-id>/design/prototype-build.md
- openspec/changes/<change-id>/design/prototype-audit.md

**下游交接**

- 已批准原型链接/导出物、PAGE→UC/US/FLOW/BR 映射、原型评审结论与需求澄清

**审批与门禁**

- 审批：产品/设计负责人确认原型与需求差异；原型与需求修订在阶段结束审计中一并批准
- 门禁：scripts/check-prototype-build.py --change <change-id> --strict（构建记录 + 页面映射 + 原型评审记录）；MCP 不可用时如实阻断

---

### 11 页面、功能区块、元素与交互事件清单

- 范围：单个功能 Change
- Skill：`page-interaction-inventory`
- Prompt：`prompts/11-page-interaction-inventory.md`
- 依赖（DAG）：`10b-prototype-generation`

**输入（内容/材料）**

- 已批准的提案级需求（proposal/specs/design/user-stories/use-cases）
- 项目级业务流程/数据对象/RD 矩阵与 UI/前端规范

**输入（文档/文件）**

- 已批准的提案原型构建记录与评审结论（openspec/changes/<change-id>/design/prototype-build.md、prototype-audit.md）
- openspec/changes/<change-id>/design/baseline-binding.json（阶段 10 已审批的约束绑定；本阶段只读继承）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/page-inventory.csv
- openspec/changes/<change-id>/design/block-inventory.csv
- openspec/changes/<change-id>/design/interaction-map.csv

**下游交接**

- PAGE/BLOCK/ELEM/EVT 清单、页面内区块顺序与职责、每个按钮/元素唯一所属区块、状态/跳转、事件与需求/operationId 的关联

**审批与门禁**

- 审批：产品负责人确认页面与交互覆盖
- 门禁：scripts/check-inventory.py --change <change-id> --strict；workflow.py 自动复核 baseline-binding.json（requirement phase）

---

### 12 Figma UI 设计与 MCP 审计

- 范围：单个功能 Change
- Skill：`figma-ui-audit`
- Prompt：`prompts/12-figma-ui-audit.md`
- 依赖（DAG）：`11-page-interaction-inventory`

**输入（内容/材料）**

- 已批准页面/区块/交互清单（含 block_id 归属）
- 已批准功能规格
- 项目级设计规范

**输入（文档/文件）**

- Figma 文件/节点与可访问 MCP 输出
- openspec/changes/<change-id>/design/baseline-binding.json（阶段 10 已审批的约束绑定；本阶段只读继承）

**输出（内容/材料）**

- Figma 设计链接/节点映射及导出资源引用

**输出（文档/文件）**

- openspec/changes/<change-id>/design/figma-audit.md

**下游交接**

- 页面/区块/组件/状态的 UI 设计依据、区块覆盖差异与待确认项

**审批与门禁**

- 审批：设计/产品负责人批准 UI
- 门禁：记录实际可读取的 node/component；MCP 不可用时不得声称已审计；workflow.py 自动复核 baseline-binding.json（requirement phase）

---

### 13a 功能详细设计总控

- 范围：单个功能 Change
- Skill：`feature-design`
- Prompt：`prompts/13a-feature-design.md`
- 依赖（DAG）：`12-figma-ui-audit`

**输入（内容/材料）**

- 已批准 proposal/specs
- 页面/交互清单与 Figma 审计（适用时）
- 项目级架构/数据/公共契约基线

**输入（文档/文件）**

- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）

**输出（内容/材料）**

- 功能详细设计任务分解与设计缺口清单

**输出（文档/文件）**

- openspec/changes/<change-id>/design.md

**下游交接**

- 统一设计约束、接口范围、前后端/测试设计任务

**审批与门禁**

- 审批：技术负责人确认设计范围和重大方案
- 门禁：scripts/check-change.sh <change-id>；辅助设计文件完整性检查；python3 scripts/baseline-governance.py check-change --change-id <id> --phase design

**基线交互**

- 只读：当前 Change 的 design/baseline-impact.md；docs/architecture/baseline-status.md；本设计域适用的项目基线
- 产出/复核：更新 baseline-impact.md 的复核结论/受影响域/NO_IMPACT 或 REBASE_REQUIRED
- 门禁：发现冲突必须提出基线修订；受影响设计在审批前不得冻结

---

### 13b OpenAPI 与接口逻辑设计

- 范围：单个功能 Change
- Skill：`api-contract-design`
- Prompt：`prompts/13b-api-contract-design.md`
- 依赖（DAG）：`13a-feature-design`

**输入（内容/材料）**

- 已批准功能规格与页面交互清单
- Figma 交互（适用时）
- 项目级 API/鉴权/错误码约定

**输入（文档/文件）**

- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）

**输出（内容/材料）**

- operationId 到页面事件/AC 的追踪关系

**输出（文档/文件）**

- openspec/changes/<change-id>/api/openapi.yaml

**下游交接**

- 唯一 OpenAPI 契约、operationId、请求响应/错误/权限定义

**审批与门禁**

- 审批：API 契约经前后端共同评审
- 门禁：scripts/validate-openapi.sh <file>；无 API 时声明 x-api-scope: none；python3 scripts/baseline-governance.py check-change --change-id <id> --phase design

**基线交互**

- 只读：当前 Change 的 design/baseline-impact.md；docs/architecture/baseline-status.md；本设计域适用的项目基线
- 产出/复核：更新 baseline-impact.md 的复核结论/受影响域/NO_IMPACT 或 REBASE_REQUIRED
- 门禁：发现冲突必须提出基线修订；受影响设计在审批前不得冻结

---

### 13c 前端详细设计

- 范围：单个功能 Change
- Skill：`frontend-detail-design`
- Prompt：`prompts/13c-frontend-detail-design.md`
- 依赖（DAG）：`13b-api-contract-design`

**输入（内容/材料）**

- 页面/区块/交互清单（含 block_id 归属）与 Figma 审计
- 前端工程规范
- 功能规格与 AC

**输入（文档/文件）**

- 已批准 OpenAPI（或 x-api-scope: none）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）

**输出（内容/材料）**

- 前端测试用例/组件状态映射

**输出（文档/文件）**

- openspec/changes/<change-id>/design/frontend-design.md

**下游交接**

- PAGE→BLOCK→组件树、区块与元素归属、组件职责、状态管理、API 调用映射、错误/加载/空状态、测试 ID

**审批与门禁**

- 审批：前端负责人评审
- 门禁：前端设计文件完整性与 operationId 对齐检查；python3 scripts/baseline-governance.py check-change --change-id <id> --phase design

**基线交互**

- 只读：当前 Change 的 design/baseline-impact.md；docs/architecture/baseline-status.md；本设计域适用的项目基线
- 产出/复核：更新 baseline-impact.md 的复核结论/受影响域/NO_IMPACT 或 REBASE_REQUIRED
- 门禁：发现冲突必须提出基线修订；受影响设计在审批前不得冻结

---

### 13d 后端详细设计

- 范围：单个功能 Change
- Skill：`backend-detail-design`
- Prompt：`prompts/13d-backend-detail-design.md`
- 依赖（DAG）：`13b-api-contract-design`

**输入（内容/材料）**

- 功能规格与 AC
- 项目级架构/领域/数据模型/公共 Client 规范

**输入（文档/文件）**

- 已批准 OpenAPI
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/backend-design.md
- openspec/changes/<change-id>/design/api-io-mapping.csv
- openspec/changes/<change-id>/design/io-catalog.csv

**下游交接**

- API→IO 映射、每个 IO 契约、事务/幂等/超时/重试/错误映射、测试 ID

**审批与门禁**

- 审批：后端负责人/架构负责人评审 IO 边界与事务一致性
- 门禁：scripts/check-api-io-mapping.py 与 scripts/check-design-assets.sh --strict；每 operationId 对应一个或多个真实 IO，例外需批准；python3 scripts/baseline-governance.py check-change --change-id <id> --phase design

**基线交互**

- 只读：当前 Change 的 design/baseline-impact.md；docs/architecture/baseline-status.md；本设计域适用的项目基线
- 产出/复核：更新 baseline-impact.md 的复核结论/受影响域/NO_IMPACT 或 REBASE_REQUIRED
- 门禁：发现冲突必须提出基线修订；受影响设计在审批前不得冻结

---

### 13e 测试设计与追踪矩阵

- 范围：单个功能 Change
- Skill：`test-design`
- Prompt：`prompts/13e-test-design.md`
- 依赖（DAG）：`13c-frontend-detail-design`、`13d-backend-detail-design`

**输入（内容/材料）**

- 已批准功能规格/AC
- 前后端详细设计
- API→IO 映射与 IO 契约
- 项目级测试策略

**输入（文档/文件）**

- OpenAPI
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/test-design.md
- openspec/changes/<change-id>/traceability.csv

**下游交接**

- TEST ID、覆盖的 AC/API/IO、测试数据/环境/命令、预期结果

**审批与门禁**

- 审批：测试负责人确认覆盖范围与质量门禁
- 门禁：scripts/check-traceability.py --file ... --strict；设计完整性检查；python3 scripts/baseline-governance.py check-change --change-id <id> --phase design

**基线交互**

- 只读：当前 Change 的 design/baseline-impact.md；docs/architecture/baseline-status.md；本设计域适用的项目基线
- 产出/复核：更新 baseline-impact.md 的复核结论/受影响域/NO_IMPACT 或 REBASE_REQUIRED
- 门禁：发现冲突必须提出基线修订；受影响设计在审批前不得冻结

---

### 14 实现、TDD、验证与代码审查

- 范围：单个功能 Change
- Skill：`implementation-orchestrator`
- Prompt：`prompts/14-implementation-orchestrator.md`
- 依赖（DAG）：`13e-test-design`

**输入（内容/材料）**

- 项目级工程规范/测试策略

**输入（文档/文件）**

- 已批准 tasks.md/design.md
- 前后端详细设计、OpenAPI、IO 契约
- test-design.md 与 traceability.csv
- openspec/changes/<change-id>/design/baseline-impact.md（已批准的基线快照）
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定）

**输出（内容/材料）**

- 实际源代码/迁移/配置
- 自动化测试代码与运行结果
- 实现/验证证据
- 条件适用：基线变更请求/ADR 草案（发现冲突时；未经批准不更新冻结基线）

**输出（文档/文件）**

- openspec/changes/<change-id>/design/evidence/code-review.md

**下游交接**

- 代码差异、测试报告、审查结论、未解决问题

**审批与门禁**

- 审批：代码审查阻断项关闭；合并按项目权限单独审批
- 门禁：TDD；scripts/test-all.sh；scripts/verify-before-completion.sh；真实命令退出码；baseline-governance.py check-change --phase implementation

**基线交互**

- 只读：已批准的 design/baseline-impact.md；当前 docs/architecture/baseline-status.md 版本
- 产出/复核：实现中发现的基线冲突记录、适用时的基线变更请求/ADR
- 门禁：不得直接修改冻结基线；未批准时暂停受影响任务；批准后刷新 Change 快照并重新验证

---

### 14b 独立验证与验收证据

- 范围：功能级
- Skill：`independent-verifier`
- Prompt：`prompts/14b-independent-verification.md`
- 依赖（DAG）：`14-implementation-orchestrator`

**输入（内容/材料）**

- 已实现代码及 revision/diff 指纹
- 已批准 proposal/specs/design/tasks
- 前后端详细设计、测试设计、Builder 测试和审查报告

**输入（文档/文件）**

- 已批准基线快照与 baseline-impact.md
- OpenAPI、API-IO 映射、IO catalog（适用时）
- openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md
- openspec/changes/<change-id>/design/evidence/independent-verification.json

**下游交接**

- 独立验证报告与 JSON 证据
- AC 逐项验证结果
- 测试命令与退出码
- 发现项和未执行项

**审批与门禁**

- 审批：独立验证 PASS；Verifier 不得是本次 Builder 的同一执行上下文；失败/阻断退回实现阶段
- 门禁：scripts/check-independent-verification.py；所有适用 AC PASS、测试退出码 0、revision 稳定、只读、无 BLOCKER/CRITICAL；baseline-governance.py check-change --phase implementation

---

### 15 人工验收、归档与基线回写

- 范围：单个功能 Change
- Skill：`acceptance-audit`
- Prompt：`prompts/15-acceptance-audit.md`
- 依赖（DAG）：`14b-independent-verification`

**输入（内容/材料）**

- 已实现代码与测试证据
- 已批准 AC/规格/追踪矩阵
- 代码审查记录
- 部署/演示或验收环境证据

**输入（文档/文件）**

- 阶段 14b 的 independent-verification-report.md 与 independent-verification.json（必须 PASS，revision 必须与当前验收代码一致）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（所有适用约束有最终验证证据）

**输出（内容/材料）**

- 验收报告与批准记录
- OpenSpec archive 结果及更新后的主规格（仅批准后）
- 项目路线图/基线状态回写（适用时）
- 条件适用：更新项目级基线文档与 baseline-status.md（仅批准/实现/验证完成后）

**输出（文档/文件）**

- openspec/changes/<change-id>/design/evidence/acceptance.md

**下游交接**

- 已验收并归档的能力规格、验收证据、后续 Change 依赖

**审批与门禁**

- 审批：产品责任人明确批准后才可归档；不得用 -y 绕过
- 门禁：scripts/check-acceptance.py；verify-before-completion.sh；openspec validate/archive 真实执行；阶段 14b 独立验证必须 PASS 且 revision 未变化；baseline-governance.py check-change --phase acceptance

**基线交互**

- 只读：design/baseline-impact.md；当前基线状态；已批准的 ADR/基线变更请求
- 产出/复核：条件性更新项目基线文档和 baseline-status.md；在途 Change 影响复核清单
- 门禁：只回写已批准/已实现/已验证的跨功能决策；功能细节留在 Change

---
