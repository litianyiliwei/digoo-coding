# 阶段输入输出总览

> 状态：DERIVED（由权威契约自动生成，请勿手工编辑）
> Change ID：N/A（项目级流程总览）
> 来源基线：`docs/STEP-ARTIFACT-CONTRACTS.json`（输入/输出/审批/门禁）、`docs/WORKFLOW-STAGES.json`（依赖 DAG）
> 关联需求/AC：N/A（流程文档）
> 生成版本：`src-sha256:c7283d36f36a`

> 本文件只汇总阶段交接面。字段级产物模板见 `docs/OUTPUT-TEMPLATE-MATRIX.csv`；流程入口见 `prompts/00-next-step.md`。
> 修改阶段交接必须先改两份 JSON 源文件，再执行 `python scripts/stage-io-report.py --out docs/STAGE-IO-OVERVIEW.md` 重新生成；`scripts/check-package.py` 会检查本文件是否过期。

共 17 个契约阶段：16 个 DAG 阶段 + 00 下一步编排（非 DAG 阶段）。

## 阶段分组

| 分组 | 阶段链路 | 说明 |
|---|---|---|
| 项目基线链 | 00 → 01 → 02 → 03 → 04 | 需求业务梳理 → 总体架构/数据/公共契约 → 结束审计冻结 → 路线图 |
| 提案交付链 | 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11/12 → 13 → 14 → 15 → 16 | 提案需求 → 原型 → 页面清单 → Figma → 详细设计 → 实现 → 独立验证 → 验收 |

## 总览

> 总览把输入/输出合并展示；逐阶段明细再拆分为“内容/材料”和“文档/文件”。

| 阶段 | 名称 | 范围 | Skill | 依赖（DAG） | 输入 | 输出 |
|---|---|---|---|---|---|---|
| 00 | 下一步编排 | 项目级与功能级通用 | `workflow-orchestrator` | N/A（编排入口，不属于 DAG 阶段） | workflow-state.json<br>docs/PROCESS-MAP.md<br>docs/STEP-ARTIFACT-CONTRACTS.json<br>docs/OUTPUT-TEMPLATE-MATRIX.csv<br>真实产物与审批记录<br>OpenSpec CLI 当前状态（如已初始化） | 下一阶段判定报告（对话展示；不强制落盘）<br>workflow-state.json（仅在真实状态变化时更新） |
| 01 | 项目初始化与工具链检查 | 项目级 | `project-bootstrap` | 无（流程起点） | 用户提供的项目目标与仓库位置<br>仓库现有目录/配置/AGENTS.md（若存在） | AGENTS.md（仅缺失时创建或经批准修改）<br>workflow-state.json<br>docs/architecture/baseline-status.md（依据 templates/project-baseline/baseline-status.md）<br>docs/project/toolchain-report.md（依据 templates/project-baseline/toolchain-report.md） |
| 02 | 需求业务梳理 | 项目级 | `requirements-analysis` | `01-project-bootstrap` | 访谈/业务材料/旧系统资料<br>项目目标、用户、角色、约束<br>既有 docs/product/*（若存在）<br>既有 OpenSpec specs（只读） | docs/product/requirements-analysis.md<br>docs/product/workflows.md（每个 FLOW 必须含完整节点表：节点角色、输入/输出数据对象、前置条件、处理动作、异常/分支、下一节点）<br>docs/product/data-objects.csv（业务数据对象目录）<br>docs/product/rd-matrix.csv（需求-数据对象矩阵：需求/规则 → 流程节点 → 角色 → 数据对象）<br>docs/product/business-rules.md<br>docs/product/glossary.md<br>docs/product/acceptance-policy.md<br>docs/product/open-questions.md |
| 03 | 项目总体架构设计 | 项目级 | `project-architecture-baseline` | `02-requirements-analysis` | 已批准的 docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md<br>现有仓库结构/技术约束<br>非功能需求<br>用户/技术负责人明确的技术选型偏好（本阶段必须显式询问并记录，不得默认或自行假设）<br>docs/product/open-questions.md（只读；未决问题不得由架构阶段擅自关闭）<br>docs/project/toolchain-report.md（工具链、测试命令与环境约束） | docs/architecture/system-context.md<br>docs/architecture/domain-boundaries.md<br>docs/architecture/containers-and-deployment.md<br>docs/architecture/data-flows.md（数据流转：DF ID、同步/异步、事务边界、失败与补偿）<br>docs/architecture/logical-erd.md（逻辑实体、关系、数据所有权、领域不变量）<br>docs/architecture/technology-decisions.md（含技术选型访谈记录、候选比较、用户确认人与日期）<br>docs/architecture/api-conventions.md<br>docs/architecture/frontend-conventions.md<br>docs/architecture/test-strategy.md<br>docs/adr/README.md<br>docs/architecture/baseline-status.md（经本阶段结束审计的各域版本/冻结状态）<br>docs/architecture/baseline-manifest.json（机器权威版本/冻结状态/域文件 SHA-256）<br>docs/architecture/constraint-registry.json（稳定约束 ID 与审批状态）<br>docs/project/baseline-audit-report.md（本阶段结束审计报告） |
| 04 | 提案拆分、依赖排序与路线图 | 项目级到功能级 | `proposal-planning` | `03-project-architecture-baseline` | 已批准并冻结的项目总体架构与基线：docs/architecture/baseline-manifest.json、constraint-registry.json、baseline-status.md、docs/project/baseline-audit-report.md<br>docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md（需求业务梳理全量输入）<br>已知技术债与依赖<br>docs/architecture/baseline-status.md<br>相关架构/数据/API/前端/测试基线版本与审批信息<br>docs/product/open-questions.md（未决问题与阻塞条件）<br>docs/project/baseline-audit-report.md（阶段 03 审计发现的缺口、待批项与冻结结论） | docs/product/proposal-roadmap.md（含每个候选 Change 的范围/依赖/价值/基线适用域与潜在修订摘要） |
| 05 | 提案级需求分析 | 单个功能 Change | `feature-requirements` | `04-proposal-planning` | docs/product/proposal-roadmap.md（当前 Change 所在行与依赖）、当前 Change 范围<br>docs/architecture/baseline-status.md 与相关架构/数据/公共契约/测试基线<br>docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md（关联 FLOW/BR/AC 与 RD 矩阵）<br>openspec/specs/**（只读）<br>docs/architecture/baseline-manifest.json 与 docs/architecture/constraint-registry.json（机器权威来源）<br>docs/product/open-questions.md（只读；提案需求不得替用户决策） | openspec/changes/<change-id>/proposal.md<br>openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）<br>openspec/changes/<change-id>/tasks.md（初步任务）<br>openspec/changes/<change-id>/design.md（有设计决策时）<br>openspec/changes/<change-id>/design/user-stories.md（提案级用户故事与 AC）<br>openspec/changes/<change-id>/design/use-cases.md（提案级功能用例）<br>openspec/changes/<change-id>/design/baseline-impact.md（依据 templates/change-assets/design/baseline-impact.md）<br>openspec/changes/<change-id>/design/baseline-binding.json（依据当前冻结基线自动生成，逐条绑定 ACTIVE Constraint ID）<br>提案级 UC/US 只保留场景、AC 与追踪 ID，不复制 specs 的完整行为描述；specs 是规范行为的唯一来源 |
| 06 | 提案原型生成与评审 | 单个功能 Change | `prototype-generation` | `05-feature-requirements` | openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、design/user-stories.md、design/use-cases.md（已批准的提案级需求）<br>docs/product/open-questions.md（只读，生成时不擅自决策）<br>pen.dev MCP 实际可访问能力（pencil 工具）<br>openspec/changes/<change-id>/design/baseline-binding.json（只读继承） | openspec/changes/<change-id>/design/prototype-build.md<br>openspec/changes/<change-id>/design/prototype-audit.md<br>pen.dev 原型页面（链接登记到构建记录；导出快照若支持） |
| 07 | 页面、功能区块、元素与交互事件清单 | 单个功能 Change | `page-interaction-inventory` | `06-prototype-generation` | openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、design/user-stories.md、design/use-cases.md（已批准的提案级需求）<br>已批准的提案原型构建记录与评审结论（openspec/changes/<change-id>/design/prototype-build.md、prototype-audit.md）<br>docs/product/workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md（业务流程/数据对象/RD 矩阵）；docs/architecture/frontend-conventions.md（UI/前端规范）<br>openspec/changes/<change-id>/design/baseline-binding.json（阶段 05 已审批的约束绑定；本阶段只读继承） | openspec/changes/<change-id>/design/page-inventory.csv<br>openspec/changes/<change-id>/design/block-inventory.csv<br>openspec/changes/<change-id>/design/interaction-map.csv<br>openspec/changes/<change-id>/traceability.csv（初始化 PAGE/BLOCK/ELEM/EVT → US/UC/AC 追踪行） |
| 08 | Figma UI 设计与 MCP 审计 | 单个功能 Change | `figma-ui-audit` | `07-page-interaction-inventory` | openspec/changes/<change-id>/design/page-inventory.csv、block-inventory.csv、interaction-map.csv（含 block_id 归属）<br>openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（已批准功能规格与 AC）<br>Figma 文件/节点与可访问 MCP 输出<br>项目级设计规范<br>openspec/changes/<change-id>/design/baseline-binding.json（阶段 05 已审批的约束绑定；本阶段只读继承）<br>以 11 的 page/block 清单为唯一权威；Figma 审计只做 node/component 映射与差异核对，不新增/重命名 PAGE/BLOCK | openspec/changes/<change-id>/design/figma-audit.md<br>Figma 设计链接/节点映射及导出资源引用 |
| 09 | 功能详细设计总控 | 单个功能 Change | `feature-design` | `08-figma-ui-audit` | openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design/user-stories.md、design/use-cases.md、tasks.md（提案级需求与任务）<br>openspec/changes/<change-id>/design/page-inventory.csv、block-inventory.csv、interaction-map.csv、figma-audit.md（页面/交互清单与 Figma 审计，适用时）<br>docs/architecture/system-context.md、domain-boundaries.md、containers-and-deployment.md、data-flows.md、logical-erd.md、technology-decisions.md、api-conventions.md、frontend-conventions.md、test-strategy.md、docs/adr/README.md 与 docs/adr/*（逐文件读取，不得只看聚合描述）<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批） | openspec/changes/<change-id>/design.md<br>openspec/changes/<change-id>/design/design-plan.md（设计范围、任务分解、接口范围草案、设计缺口与准入结论） |
| 10 | OpenAPI 与接口逻辑设计 | 单个功能 Change | `api-contract-design` | `09-feature-design` | openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（功能规格与 AC）；design/page-inventory.csv、block-inventory.csv、interaction-map.csv（页面/区块/交互清单）<br>openspec/changes/<change-id>/design.md（09 统一设计决策与约束）<br>openspec/changes/<change-id>/design/design-plan.md（设计范围、接口范围与缺口）<br>openspec/changes/<change-id>/design/figma-audit.md（Figma 交互/状态差异，适用时）<br>docs/architecture/api-conventions.md、system-context.md、domain-boundaries.md、data-flows.md、docs/adr/*（API 相关基线）<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批） | openspec/changes/<change-id>/api/openapi.yaml<br>openspec/changes/<change-id>/design/api-traceability.csv（operationId → PAGE/EVT/AC 映射，供 13 合并） |
| 11 | 前端详细设计 | 单个功能 Change | `frontend-detail-design` | `10-api-contract-design` | openspec/changes/<change-id>/api/openapi.yaml（或 x-api-scope: none）<br>openspec/changes/<change-id>/design/page-inventory.csv、block-inventory.csv、interaction-map.csv（含 block_id 归属）、figma-audit.md<br>docs/architecture/frontend-conventions.md、containers-and-deployment.md、data-flows.md、docs/adr/*（前端相关基线）<br>openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（AC）<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）<br>openspec/changes/<change-id>/design.md（09 统一设计决策）<br>openspec/changes/<change-id>/design/design-plan.md（设计任务与缺口）<br>openspec/changes/<change-id>/design/api-traceability.csv（operationId → EVT/AC 映射） | openspec/changes/<change-id>/design/frontend-design.md（含 PAGE→BLOCK→组件树、组件状态与测试映射章节） |
| 12 | 后端详细设计 | 单个功能 Change | `backend-detail-design` | `10-api-contract-design` | openspec/changes/<change-id>/api/openapi.yaml<br>openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（AC）<br>docs/architecture/system-context.md、domain-boundaries.md、logical-erd.md、data-flows.md、technology-decisions.md、api-conventions.md、docs/adr/README.md 与 docs/adr/*（后端相关基线）<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）<br>openspec/changes/<change-id>/design.md（09 统一设计决策）<br>openspec/changes/<change-id>/design/design-plan.md（设计任务与缺口）<br>openspec/changes/<change-id>/design/api-traceability.csv（operationId → EVT/AC 映射）<br>openspec/changes/<change-id>/design/interaction-map.csv（页面事件/operationId 关联） | openspec/changes/<change-id>/design/backend-design.md<br>openspec/changes/<change-id>/design/api-io-mapping.csv<br>openspec/changes/<change-id>/design/io-catalog.csv |
| 13 | 测试设计与追踪矩阵 | 单个功能 Change | `test-design` | `11-frontend-detail-design`、`12-backend-detail-design` | 已批准的提案级 US/UC/AC：design/user-stories.md、design/use-cases.md<br>openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（AC）<br>openspec/changes/<change-id>/design.md 与 design/design-plan.md<br>openspec/changes/<change-id>/api/openapi.yaml、design/api-traceability.csv<br>openspec/changes/<change-id>/design/frontend-design.md、backend-design.md<br>openspec/changes/<change-id>/design/api-io-mapping.csv、io-catalog.csv<br>docs/architecture/test-strategy.md 与 docs/product/acceptance-policy.md（验收口径）<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）<br>openspec/changes/<change-id>/traceability.csv（11 初始化的页面追踪行；合并前读取）<br>openspec/changes/<change-id>/design/page-inventory.csv、block-inventory.csv（页面/区块覆盖） | openspec/changes/<change-id>/design/test-design.md<br>openspec/changes/<change-id>/traceability.csv（合并 11 的页面追踪、10 的 api-traceability 与测试映射；唯一追踪聚合文件） |
| 14 | 实现、TDD、验证与代码审查 | 单个功能 Change | `implementation-orchestrator` | `13-test-design` | openspec/changes/<change-id>/tasks.md、design.md（已批准）<br>openspec/changes/<change-id>/design/frontend-design.md、backend-design.md、api/openapi.yaml、design/api-io-mapping.csv、design/io-catalog.csv<br>openspec/changes/<change-id>/design/test-design.md、traceability.csv<br>docs/architecture/frontend-conventions.md、api-conventions.md、test-strategy.md<br>openspec/changes/<change-id>/design/baseline-impact.md（已批准的基线快照）<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定） | 实际源代码/迁移/配置<br>自动化测试代码与运行结果<br>openspec/changes/<change-id>/design/evidence/code-review.md<br>实现/验证证据<br>条件适用：基线变更请求/ADR 草案（发现冲突时；未经批准不更新冻结基线） |
| 15 | 独立验证与验收证据 | 功能级 | `independent-verifier` | `14-implementation-orchestrator` | 已实现代码及 revision/diff 指纹<br>openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、tasks.md、design/user-stories.md、design/use-cases.md（已批准需求与设计）<br>已批准基线快照与 baseline-impact.md<br>openspec/changes/<change-id>/api/openapi.yaml、design/api-io-mapping.csv、design/io-catalog.csv（适用时）<br>openspec/changes/<change-id>/design/frontend-design.md、backend-design.md、test-design.md、evidence/code-review.md、Builder 测试与验证证据<br>openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定）<br>openspec/changes/<change-id>/design/user-stories.md、design/use-cases.md（提案级 US/UC/AC）<br>openspec/changes/<change-id>/traceability.csv（追踪矩阵） | openspec/changes/<change-id>/design/evidence/independent-verification-report.md<br>openspec/changes/<change-id>/design/evidence/independent-verification.json |
| 16 | 人工验收、归档与基线回写 | 单个功能 Change | `acceptance-audit` | `15-independent-verification` | openspec/changes/<change-id>/design/evidence/independent-verification-report.md 与 independent-verification.json（必须 PASS，revision 必须与当前验收代码一致）<br>已实现代码与测试证据<br>openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md、design/use-cases.md、traceability.csv（已批准 AC/规格/追踪）<br>openspec/changes/<change-id>/design/evidence/code-review.md<br>部署/演示或验收环境证据<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（所有适用约束有最终验证证据）<br>openspec/changes/<change-id>/design/user-stories.md、design/use-cases.md（提案级 US/UC/AC）<br>docs/product/acceptance-policy.md（项目级验收口径）<br>openspec/changes/<change-id>/design/test-design.md（测试覆盖依据） | openspec/changes/<change-id>/design/evidence/acceptance.md<br>验收报告与批准记录<br>OpenSpec archive 结果及更新后的主规格（仅批准后）<br>项目路线图/基线状态回写（适用时）<br>条件适用：更新项目级基线文档与 baseline-status.md（仅批准/实现/验证完成后） |

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

**输出消费者**

- AGENTS.md → ALL
- workflow-state.json → SYSTEM
- docs/architecture/baseline-status.md → 04、05、09、10、11、12、13、14、16
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

**输出消费者**

- docs/product/requirements-analysis.md → 03、04、05
- docs/product/workflows.md → 03、04、05、07
- docs/product/data-objects.csv → 03、04、05、07
- docs/product/rd-matrix.csv → 03、04、05、07
- docs/product/business-rules.md → 03、04、05、07
- docs/product/glossary.md → 03、04、05
- docs/product/acceptance-policy.md → 03、04、13、16
- docs/product/open-questions.md → 03、04、05、06

**下游交接**

- 业务流程与节点级角色/数据对象、业务数据对象目录、RD 矩阵、业务规则、术语与验收政策、未决问题

**审批与门禁**

- 审批：业务/产品负责人确认业务流程完整性、节点数据对象与角色、RD 矩阵覆盖
- 门禁：scripts/check-requirements.py --strict（FLOW/NODE/DO/RD/BR 结构、引用闭合与节点覆盖）

---

### 03 项目总体架构设计

- 范围：项目级
- Skill：`project-architecture-baseline`
- Prompt：`prompts/03-project-architecture-baseline.md`
- 依赖（DAG）：`02-requirements-analysis`

**输入（内容/材料）**

- 现有仓库结构/技术约束
- 非功能需求
- 用户/技术负责人明确的技术选型偏好（本阶段必须显式询问并记录，不得默认或自行假设）

**输入（文档/文件）**

- 已批准的 docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md
- docs/product/open-questions.md（只读；未决问题不得由架构阶段擅自关闭）
- docs/project/toolchain-report.md（工具链、测试命令与环境约束）

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

**输出消费者**

- docs/architecture/system-context.md → 09、10、12
- docs/architecture/domain-boundaries.md → 09、10、12
- docs/architecture/containers-and-deployment.md → 09、11
- docs/architecture/data-flows.md → 09、10、11、12
- docs/architecture/logical-erd.md → 09、12
- docs/architecture/technology-decisions.md → 09、12
- docs/architecture/api-conventions.md → 09、10、12、14
- docs/architecture/frontend-conventions.md → 07、09、11、14
- docs/architecture/test-strategy.md → 09、13、14
- docs/adr/README.md → 09、12
- docs/architecture/baseline-status.md → 04、05、09、10、11、12、13、14、16
- docs/architecture/baseline-manifest.json → 04、05
- docs/architecture/constraint-registry.json → 04、05
- docs/project/baseline-audit-report.md → 04

**下游交接**

- 冻结的项目总体架构基线、数据流转、逻辑 ERD、公共契约/测试策略、ACTIVE 约束目录、审计报告与审批记录

**审批与门禁**

- 审批：产品/架构/技术负责人共同确认系统边界、数据流转与公共契约，并批准基线冻结
- 门禁：scripts/check-required-files.sh --strict；跨文档一致性审计（系统边界/数据流转/ERD/公共契约/术语）；scripts/baseline-governance.py audit --require-frozen（阶段结束冻结审计）

---

### 04 提案拆分、依赖排序与路线图

- 范围：项目级到功能级
- Skill：`proposal-planning`
- Prompt：`prompts/04-proposal-planning.md`
- 依赖（DAG）：`03-project-architecture-baseline`

**输入（内容/材料）**

- 已知技术债与依赖
- 相关架构/数据/API/前端/测试基线版本与审批信息

**输入（文档/文件）**

- 已批准并冻结的项目总体架构与基线：docs/architecture/baseline-manifest.json、constraint-registry.json、baseline-status.md、docs/project/baseline-audit-report.md
- docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md（需求业务梳理全量输入）
- docs/architecture/baseline-status.md
- docs/product/open-questions.md（未决问题与阻塞条件）
- docs/project/baseline-audit-report.md（阶段 03 审计发现的缺口、待批项与冻结结论）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- docs/product/proposal-roadmap.md（含每个候选 Change 的范围/依赖/价值/基线适用域与潜在修订摘要）

**输出消费者**

- docs/product/proposal-roadmap.md → 05

**下游交接**

- 经批准的 Change 列表、优先级、依赖顺序

**审批与门禁**

- 审批：产品与技术负责人批准路线图及首个 Change
- 门禁：scripts/check-roadmap.py --strict；不在此阶段伪造 Change 验证

**基线交互**

- 只读：docs/architecture/baseline-status.md；相关产品/架构/数据/公共契约/测试基线；openspec/specs/**
- 产出/复核：docs/product/proposal-roadmap.md 中每个 Change 的基线适用域和候选修订

---

### 05 提案级需求分析

- 范围：单个功能 Change
- Skill：`feature-requirements`
- Prompt：`prompts/05-feature-requirements.md`
- 依赖（DAG）：`04-proposal-planning`

**输入（内容/材料）**

- N/A

**输入（文档/文件）**

- docs/product/proposal-roadmap.md（当前 Change 所在行与依赖）、当前 Change 范围
- docs/architecture/baseline-status.md 与相关架构/数据/公共契约/测试基线
- docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md（关联 FLOW/BR/AC 与 RD 矩阵）
- openspec/specs/**（只读）
- docs/architecture/baseline-manifest.json 与 docs/architecture/constraint-registry.json（机器权威来源）
- docs/product/open-questions.md（只读；提案需求不得替用户决策）

**输出（内容/材料）**

- 提案级 UC/US 只保留场景、AC 与追踪 ID，不复制 specs 的完整行为描述；specs 是规范行为的唯一来源

**输出（文档/文件）**

- openspec/changes/<change-id>/proposal.md
- openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）
- openspec/changes/<change-id>/tasks.md（初步任务）
- openspec/changes/<change-id>/design.md（有设计决策时）
- openspec/changes/<change-id>/design/user-stories.md（提案级用户故事与 AC）
- openspec/changes/<change-id>/design/use-cases.md（提案级功能用例）
- openspec/changes/<change-id>/design/baseline-impact.md（依据 templates/change-assets/design/baseline-impact.md）
- openspec/changes/<change-id>/design/baseline-binding.json（依据当前冻结基线自动生成，逐条绑定 ACTIVE Constraint ID）

**输出消费者**

- openspec/changes/<change-id>/proposal.md → 06、07、09、15
- openspec/changes/<change-id>/specs/<capability>/spec.md → 06、07、08、09、10、11、12、13、15、16
- openspec/changes/<change-id>/tasks.md → 09、14、15
- openspec/changes/<change-id>/design.md → 06、07、10、11、12、13、14、15、16
- openspec/changes/<change-id>/design/user-stories.md → 06、07、08、09、10、11、12、13、15、16
- openspec/changes/<change-id>/design/use-cases.md → 06、07、09、13、15、16
- templates/change-assets/design/baseline-impact.md → 09、10、11、12、13、14、15、16
- openspec/changes/<change-id>/design/baseline-binding.json → 06、07、08、09、10、11、12、13、14、15、16

**下游交接**

- 已批准的提案级 US/UC/AC、场景与业务规则、范围边界、需求追踪 ID、基线快照与约束绑定
- specs 为规范行为唯一来源；UC/US 用于场景、AC 与追踪，不作为重复规格

**审批与门禁**

- 审批：产品负责人批准提案级需求与验收标准；技术负责人确认范围与基线影响
- 门禁：scripts/check-requirements.py --change <change-id> --strict（提案级 UC/US/AC 结构与引用闭合）；openspec validate <change-id> --strict；scripts/check-baseline-impact.py <change-id>；scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement

**基线交互**

- 只读：docs/architecture/baseline-status.md；相关产品/架构/数据/API/前端/测试基线；相关 openspec/specs/**
- 产出/复核：openspec/changes/<change-id>/design/baseline-impact.md
- 门禁：若功能设计依赖未批准的架构/数据/公共契约/质量基线变化，阻断进入详细设计/实现

---

### 06 提案原型生成与评审

- 范围：单个功能 Change
- Skill：`prototype-generation`
- Prompt：`prompts/06-prototype-generation.md`
- 依赖（DAG）：`05-feature-requirements`

**输入（内容/材料）**

- pen.dev MCP 实际可访问能力（pencil 工具）

**输入（文档/文件）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、design/user-stories.md、design/use-cases.md（已批准的提案级需求）
- docs/product/open-questions.md（只读，生成时不擅自决策）
- openspec/changes/<change-id>/design/baseline-binding.json（只读继承）

**输出（内容/材料）**

- pen.dev 原型页面（链接登记到构建记录；导出快照若支持）

**输出（文档/文件）**

- openspec/changes/<change-id>/design/prototype-build.md
- openspec/changes/<change-id>/design/prototype-audit.md

**输出消费者**

- openspec/changes/<change-id>/design/prototype-build.md → 07
- openspec/changes/<change-id>/design/prototype-audit.md → 07

**下游交接**

- 已批准原型链接/导出物、PAGE→UC/US/FLOW/BR 映射、原型评审结论与需求澄清；原型页面清单仅作草案，批准后的权威页面清单由 11 生成

**审批与门禁**

- 审批：产品/设计负责人确认原型与需求差异；原型与需求修订在阶段结束审计中一并批准
- 门禁：scripts/check-prototype-build.py --change <change-id> --strict（构建记录 + 页面映射 + 原型评审记录）；MCP 不可用时如实阻断

---

### 07 页面、功能区块、元素与交互事件清单

- 范围：单个功能 Change
- Skill：`page-interaction-inventory`
- Prompt：`prompts/07-page-interaction-inventory.md`
- 依赖（DAG）：`06-prototype-generation`

**输入（内容/材料）**

- N/A

**输入（文档/文件）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、design/user-stories.md、design/use-cases.md（已批准的提案级需求）
- 已批准的提案原型构建记录与评审结论（openspec/changes/<change-id>/design/prototype-build.md、prototype-audit.md）
- docs/product/workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md（业务流程/数据对象/RD 矩阵）；docs/architecture/frontend-conventions.md（UI/前端规范）
- openspec/changes/<change-id>/design/baseline-binding.json（阶段 05 已审批的约束绑定；本阶段只读继承）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/page-inventory.csv
- openspec/changes/<change-id>/design/block-inventory.csv
- openspec/changes/<change-id>/design/interaction-map.csv
- openspec/changes/<change-id>/traceability.csv（初始化 PAGE/BLOCK/ELEM/EVT → US/UC/AC 追踪行）

**输出消费者**

- openspec/changes/<change-id>/design/page-inventory.csv → 08、09、10、11、13
- openspec/changes/<change-id>/design/block-inventory.csv → 08、09、10、11、13
- openspec/changes/<change-id>/design/interaction-map.csv → 08、09、10、11、12
- openspec/changes/<change-id>/traceability.csv → 11、12、13、14、15、16

**下游交接**

- PAGE/BLOCK/ELEM/EVT 权威清单、页面内区块顺序与职责、每个按钮/元素唯一所属区块、状态/跳转、事件与需求/operationId 的关联；page-inventory.csv 为唯一权威页面清单，12 只核对映射、不重定义 PAGE ID
- traceability.csv 由 11 初始化，10/13 只追加，不重建

**审批与门禁**

- 审批：产品负责人确认页面与交互覆盖
- 门禁：scripts/check-inventory.py --change <change-id> --strict；workflow.py 自动复核 baseline-binding.json（requirement phase）

---

### 08 Figma UI 设计与 MCP 审计

- 范围：单个功能 Change
- Skill：`figma-ui-audit`
- Prompt：`prompts/08-figma-ui-audit.md`
- 依赖（DAG）：`07-page-interaction-inventory`

**输入（内容/材料）**

- 项目级设计规范
- 以 11 的 page/block 清单为唯一权威；Figma 审计只做 node/component 映射与差异核对，不新增/重命名 PAGE/BLOCK

**输入（文档/文件）**

- openspec/changes/<change-id>/design/page-inventory.csv、block-inventory.csv、interaction-map.csv（含 block_id 归属）
- openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（已批准功能规格与 AC）
- Figma 文件/节点与可访问 MCP 输出
- openspec/changes/<change-id>/design/baseline-binding.json（阶段 05 已审批的约束绑定；本阶段只读继承）

**输出（内容/材料）**

- Figma 设计链接/节点映射及导出资源引用

**输出（文档/文件）**

- openspec/changes/<change-id>/design/figma-audit.md

**输出消费者**

- openspec/changes/<change-id>/design/figma-audit.md → 09、10、11

**下游交接**

- 页面/区块/组件/状态的 UI 设计依据、区块覆盖差异与待确认项；差异回到 11 修订清单

**审批与门禁**

- 审批：设计/产品负责人批准 UI
- 门禁：记录实际可读取的 node/component；MCP 不可用时不得声称已审计；workflow.py 自动复核 baseline-binding.json（requirement phase）

---

### 09 功能详细设计总控

- 范围：单个功能 Change
- Skill：`feature-design`
- Prompt：`prompts/09-feature-design.md`
- 依赖（DAG）：`08-figma-ui-audit`

**输入（内容/材料）**

- N/A

**输入（文档/文件）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design/user-stories.md、design/use-cases.md、tasks.md（提案级需求与任务）
- openspec/changes/<change-id>/design/page-inventory.csv、block-inventory.csv、interaction-map.csv、figma-audit.md（页面/交互清单与 Figma 审计，适用时）
- docs/architecture/system-context.md、domain-boundaries.md、containers-and-deployment.md、data-flows.md、logical-erd.md、technology-decisions.md、api-conventions.md、frontend-conventions.md、test-strategy.md、docs/adr/README.md 与 docs/adr/*（逐文件读取，不得只看聚合描述）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design.md
- openspec/changes/<change-id>/design/design-plan.md（设计范围、任务分解、接口范围草案、设计缺口与准入结论）

**输出消费者**

- openspec/changes/<change-id>/design.md → 10、11、12、13、14、15、16
- openspec/changes/<change-id>/design/design-plan.md → 10、11、12、13

**下游交接**

- 统一设计约束、接口范围、前后端/测试设计任务与缺口，见 design.md 与 design/design-plan.md

**审批与门禁**

- 审批：技术负责人确认设计范围和重大方案
- 门禁：scripts/check-change.sh <change-id>；辅助设计文件完整性检查；python3 scripts/baseline-governance.py check-change --change-id <id> --phase design

**基线交互**

- 只读：当前 Change 的 design/baseline-impact.md；docs/architecture/baseline-status.md；本设计域适用的项目基线
- 产出/复核：更新 baseline-impact.md 的复核结论/受影响域/NO_IMPACT 或 REBASE_REQUIRED
- 门禁：发现冲突必须提出基线修订；受影响设计在审批前不得冻结

---

### 10 OpenAPI 与接口逻辑设计

- 范围：单个功能 Change
- Skill：`api-contract-design`
- Prompt：`prompts/10-api-contract-design.md`
- 依赖（DAG）：`09-feature-design`

**输入（内容/材料）**

- N/A

**输入（文档/文件）**

- openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（功能规格与 AC）；design/page-inventory.csv、block-inventory.csv、interaction-map.csv（页面/区块/交互清单）
- openspec/changes/<change-id>/design.md（09 统一设计决策与约束）
- openspec/changes/<change-id>/design/design-plan.md（设计范围、接口范围与缺口）
- openspec/changes/<change-id>/design/figma-audit.md（Figma 交互/状态差异，适用时）
- docs/architecture/api-conventions.md、system-context.md、domain-boundaries.md、data-flows.md、docs/adr/*（API 相关基线）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/api/openapi.yaml
- openspec/changes/<change-id>/design/api-traceability.csv（operationId → PAGE/EVT/AC 映射，供 13 合并）

**输出消费者**

- openspec/changes/<change-id>/api/openapi.yaml → 11、12、13、14、15
- openspec/changes/<change-id>/design/api-traceability.csv → 11、12、13

**下游交接**

- 唯一 OpenAPI 契约、operationId、请求响应/错误/权限定义、operationId → 页面事件/AC 追踪行

**审批与门禁**

- 审批：API 契约经前后端共同评审
- 门禁：scripts/validate-openapi.sh <openapi-file>；有 API 时 scripts/check-traceability.py --file openspec/changes/<change-id>/design/api-traceability.csv --strict；x-api-scope: none 时在 design.md 记录 N/A + 理由；scripts/baseline-governance.py check-change --change-id <id> --phase design

**基线交互**

- 只读：当前 Change 的 design/baseline-impact.md；docs/architecture/baseline-status.md；本设计域适用的项目基线
- 产出/复核：更新 baseline-impact.md 的复核结论/受影响域/NO_IMPACT 或 REBASE_REQUIRED
- 门禁：发现冲突必须提出基线修订；受影响设计在审批前不得冻结

---

### 11 前端详细设计

- 范围：单个功能 Change
- Skill：`frontend-detail-design`
- Prompt：`prompts/11-frontend-detail-design.md`
- 依赖（DAG）：`10-api-contract-design`

**输入（内容/材料）**

- N/A

**输入（文档/文件）**

- openspec/changes/<change-id>/api/openapi.yaml（或 x-api-scope: none）
- openspec/changes/<change-id>/design/page-inventory.csv、block-inventory.csv、interaction-map.csv（含 block_id 归属）、figma-audit.md
- docs/architecture/frontend-conventions.md、containers-and-deployment.md、data-flows.md、docs/adr/*（前端相关基线）
- openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（AC）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）
- openspec/changes/<change-id>/design.md（09 统一设计决策）
- openspec/changes/<change-id>/design/design-plan.md（设计任务与缺口）
- openspec/changes/<change-id>/design/api-traceability.csv（operationId → EVT/AC 映射）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/frontend-design.md（含 PAGE→BLOCK→组件树、组件状态与测试映射章节）

**输出消费者**

- openspec/changes/<change-id>/design/frontend-design.md → 13、14、15

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

### 12 后端详细设计

- 范围：单个功能 Change
- Skill：`backend-detail-design`
- Prompt：`prompts/12-backend-detail-design.md`
- 依赖（DAG）：`10-api-contract-design`

**输入（内容/材料）**

- N/A

**输入（文档/文件）**

- openspec/changes/<change-id>/api/openapi.yaml
- openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（AC）
- docs/architecture/system-context.md、domain-boundaries.md、logical-erd.md、data-flows.md、technology-decisions.md、api-conventions.md、docs/adr/README.md 与 docs/adr/*（后端相关基线）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）
- openspec/changes/<change-id>/design.md（09 统一设计决策）
- openspec/changes/<change-id>/design/design-plan.md（设计任务与缺口）
- openspec/changes/<change-id>/design/api-traceability.csv（operationId → EVT/AC 映射）
- openspec/changes/<change-id>/design/interaction-map.csv（页面事件/operationId 关联）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/backend-design.md
- openspec/changes/<change-id>/design/api-io-mapping.csv
- openspec/changes/<change-id>/design/io-catalog.csv

**输出消费者**

- openspec/changes/<change-id>/design/backend-design.md → 13、14、15
- openspec/changes/<change-id>/design/api-io-mapping.csv → 13、14、15
- openspec/changes/<change-id>/design/io-catalog.csv → 13、14、15

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

### 13 测试设计与追踪矩阵

- 范围：单个功能 Change
- Skill：`test-design`
- Prompt：`prompts/13-test-design.md`
- 依赖（DAG）：`11-frontend-detail-design`、`12-backend-detail-design`

**输入（内容/材料）**

- N/A

**输入（文档/文件）**

- 已批准的提案级 US/UC/AC：design/user-stories.md、design/use-cases.md
- openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（AC）
- openspec/changes/<change-id>/design.md 与 design/design-plan.md
- openspec/changes/<change-id>/api/openapi.yaml、design/api-traceability.csv
- openspec/changes/<change-id>/design/frontend-design.md、backend-design.md
- openspec/changes/<change-id>/design/api-io-mapping.csv、io-catalog.csv
- docs/architecture/test-strategy.md 与 docs/product/acceptance-policy.md（验收口径）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）
- openspec/changes/<change-id>/traceability.csv（11 初始化的页面追踪行；合并前读取）
- openspec/changes/<change-id>/design/page-inventory.csv、block-inventory.csv（页面/区块覆盖）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/test-design.md
- openspec/changes/<change-id>/traceability.csv（合并 11 的页面追踪、10 的 api-traceability 与测试映射；唯一追踪聚合文件）

**输出消费者**

- openspec/changes/<change-id>/design/test-design.md → 14、15、16
- openspec/changes/<change-id>/traceability.csv → 14、15、16

**下游交接**

- TEST ID、覆盖的 AC/API/IO、测试数据/环境/命令、预期结果；traceability.csv 为唯一追踪聚合文件

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
- 依赖（DAG）：`13-test-design`

**输入（内容/材料）**

- N/A

**输入（文档/文件）**

- openspec/changes/<change-id>/tasks.md、design.md（已批准）
- openspec/changes/<change-id>/design/frontend-design.md、backend-design.md、api/openapi.yaml、design/api-io-mapping.csv、design/io-catalog.csv
- openspec/changes/<change-id>/design/test-design.md、traceability.csv
- docs/architecture/frontend-conventions.md、api-conventions.md、test-strategy.md
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

**输出消费者**

- openspec/changes/<change-id>/design/evidence/code-review.md → 15、16

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

### 15 独立验证与验收证据

- 范围：功能级
- Skill：`independent-verifier`
- Prompt：`prompts/15-independent-verification.md`
- 依赖（DAG）：`14-implementation-orchestrator`

**输入（内容/材料）**

- 已实现代码及 revision/diff 指纹

**输入（文档/文件）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、tasks.md、design/user-stories.md、design/use-cases.md（已批准需求与设计）
- 已批准基线快照与 baseline-impact.md
- openspec/changes/<change-id>/api/openapi.yaml、design/api-io-mapping.csv、design/io-catalog.csv（适用时）
- openspec/changes/<change-id>/design/frontend-design.md、backend-design.md、test-design.md、evidence/code-review.md、Builder 测试与验证证据
- openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定）
- openspec/changes/<change-id>/design/user-stories.md、design/use-cases.md（提案级 US/UC/AC）
- openspec/changes/<change-id>/traceability.csv（追踪矩阵）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md
- openspec/changes/<change-id>/design/evidence/independent-verification.json

**输出消费者**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md → 16
- openspec/changes/<change-id>/design/evidence/independent-verification.json → 16

**下游交接**

- 独立验证报告与 JSON 证据
- AC 逐项验证结果
- 测试命令与退出码
- 发现项和未执行项

**审批与门禁**

- 审批：独立验证 PASS；Verifier 不得是本次 Builder 的同一执行上下文；失败/阻断退回实现阶段
- 门禁：scripts/check-independent-verification.py；所有适用 AC PASS、测试退出码 0、revision 稳定、只读、无 BLOCKER/CRITICAL；baseline-governance.py check-change --phase implementation

---

### 16 人工验收、归档与基线回写

- 范围：单个功能 Change
- Skill：`acceptance-audit`
- Prompt：`prompts/16-acceptance-audit.md`
- 依赖（DAG）：`15-independent-verification`

**输入（内容/材料）**

- 已实现代码与测试证据
- 部署/演示或验收环境证据

**输入（文档/文件）**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md 与 independent-verification.json（必须 PASS，revision 必须与当前验收代码一致）
- openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md、design/use-cases.md、traceability.csv（已批准 AC/规格/追踪）
- openspec/changes/<change-id>/design/evidence/code-review.md
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（所有适用约束有最终验证证据）
- openspec/changes/<change-id>/design/user-stories.md、design/use-cases.md（提案级 US/UC/AC）
- docs/product/acceptance-policy.md（项目级验收口径）
- openspec/changes/<change-id>/design/test-design.md（测试覆盖依据）

**输出（内容/材料）**

- 验收报告与批准记录
- OpenSpec archive 结果及更新后的主规格（仅批准后）
- 项目路线图/基线状态回写（适用时）
- 条件适用：更新项目级基线文档与 baseline-status.md（仅批准/实现/验证完成后）

**输出（文档/文件）**

- openspec/changes/<change-id>/design/evidence/acceptance.md

**输出消费者**

- openspec/changes/<change-id>/design/evidence/acceptance.md → FUTURE

**下游交接**

- 已验收并归档的能力规格、验收证据、后续 Change 依赖

**审批与门禁**

- 审批：产品责任人明确批准后才可归档；不得用 -y 绕过
- 门禁：scripts/check-acceptance.py；verify-before-completion.sh；openspec validate/archive 真实执行；阶段 15 独立验证必须 PASS 且 revision 未变化；baseline-governance.py check-change --phase acceptance

**基线交互**

- 只读：design/baseline-impact.md；当前基线状态；已批准的 ADR/基线变更请求
- 产出/复核：条件性更新项目基线文档和 baseline-status.md；在途 Change 影响复核清单
- 门禁：只回写已批准/已实现/已验证的跨功能决策；功能细节留在 Change

---
