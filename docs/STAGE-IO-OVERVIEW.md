# 阶段输入输出总览

> 状态：DERIVED（由权威契约自动生成，请勿手工编辑）
> Change ID：N/A（项目级流程总览）
> 来源基线：`docs/STEP-ARTIFACT-CONTRACTS.json`（输入/输出/审批/门禁）、`docs/WORKFLOW-STAGES.json`（依赖 DAG）
> 关联需求/AC：N/A（流程文档）
> 生成版本：`src-sha256:590da80e3a61`

> 本文件只汇总阶段交接面。字段级产物模板见 `docs/OUTPUT-TEMPLATE-MATRIX.csv`；流程入口见 `prompts/00-next-step.md`。
> 修改阶段交接必须先改两份 JSON 源文件，再执行 `python scripts/stage-io-report.py --out docs/STAGE-IO-OVERVIEW.md` 重新生成；`scripts/check-package.py` 会检查本文件是否过期。

共 11 个契约阶段：10 个 DAG 阶段 + 00 下一步编排（非 DAG 阶段）。

## 阶段分组

| 分组 | 阶段链路 | 说明 |
|---|---|---|
| 项目基线链 | 00 → 01 → 02 → 03 → 04 | 初始化 → 需求业务梳理 → 总体架构/基线冻结 → 路线图 |
| 提案交付链 | 04 → 05 → 06 → 07 → 08 → 09 → 10 | 提案需求 → 原型/页面清单 → 详细设计（含接口/测试） → 实现 → 独立验证 → 验收 |

## 总览

> 总览把输入/输出合并展示；逐阶段明细再拆分为“内容/材料”和“文档/文件”。

| 阶段 | 名称 | 范围 | Skill | 依赖（DAG） | 输入 | 输出 |
|---|---|---|---|---|---|---|
| 00 | 下一步编排 | 项目级与功能级通用 | `workflow-orchestrator` | N/A（编排入口，不属于 DAG 阶段） | workflow-state.json<br>docs/PROCESS-MAP.md<br>docs/STEP-ARTIFACT-CONTRACTS.json<br>docs/WORKFLOW-STAGES.json<br>docs/BASELINE-FEATURE-INTERACTION.md<br>docs/OUTPUT-TEMPLATE-MATRIX.csv<br>真实产物与审批记录<br>OpenSpec CLI 当前状态（如已初始化） | 下一阶段判定报告（对话展示；不强制落盘）<br>workflow-state.json（仅在真实状态变化时更新） |
| 01 | 项目初始化与工具链检查 | 项目级 | `project-bootstrap` | 无（流程起点） | 用户提供的项目目标与仓库位置<br>仓库现有目录/配置/AGENTS.md（若存在） | AGENTS.md（仅缺失时创建或经批准修改）<br>workflow-state.json<br>docs/architecture/baseline-status.md（依据 templates/project-baseline/baseline-status.md）<br>docs/project/toolchain-report.md（依据 templates/project-baseline/toolchain-report.md） |
| 02 | 需求业务梳理 | 项目级 | `requirements-analysis` | `01-project-bootstrap` | 访谈/业务材料/旧系统资料<br>项目目标、用户、角色、约束<br>既有 docs/product/*（若存在）<br>既有 OpenSpec specs（只读） | docs/product/requirements-analysis.md<br>docs/product/workflows.md（每个 FLOW 必须含完整节点表：节点角色、输入/输出数据对象、前置条件、处理动作、异常/分支、下一节点）<br>docs/product/data-objects.csv（业务数据对象目录）<br>docs/product/rd-matrix.csv（需求-数据对象矩阵：需求/规则 → 流程节点 → 角色 → 数据对象）<br>docs/product/business-rules.md<br>docs/product/glossary.md<br>docs/product/acceptance-policy.md<br>docs/product/open-questions.md<br>docs/product/BASELINE-BRIEF.md（一页式基线入口，≤1 页；阶段 03–05 常驻上下文）<br>docs/product/role-permission-matrix.csv（角色-能力-数据范围-访问级别）<br>docs/product/change-sizing.md（Change 切片预算与完成定义）<br>docs/product/decisions.md（DEC 决策日志）<br>docs/product/assumptions.md（ASM 假设登记）<br>docs/product/lessons.md（教训/反模式；验收后由阶段 10 追加）<br>docs/product/id-conventions.md（项目级/Change 级 ID 与并行分配规则）<br>docs/product/BASELINE-INDEX.md（由 scripts/gen-baseline-index.py 生成的常驻基线索引） |
| 03 | 项目总体架构设计 | 项目级 | `project-architecture-baseline` | `02-requirements-analysis` | 已批准的 docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md<br>docs/product/BASELINE-BRIEF.md、role-permission-matrix.csv、change-sizing.md、decisions.md、assumptions.md、id-conventions.md、BASELINE-INDEX.md（常驻基线；先读简报，细节按需加载）<br>现有仓库结构/技术约束<br>非功能需求<br>用户/技术负责人明确的技术选型偏好（本阶段必须显式询问并记录，不得默认或自行假设）<br>docs/product/open-questions.md（只读；未决问题不得由架构阶段擅自关闭）<br>docs/project/toolchain-report.md（工具链、测试命令与环境约束）<br>docs/architecture/baseline-status.md（阶段 01 的初始基线与模板状态；本阶段更新为冻结候选） | docs/architecture/system-context.md<br>docs/architecture/domain-boundaries.md<br>docs/architecture/containers-and-deployment.md<br>docs/architecture/data-flows.md（数据流转：DF ID、同步/异步、事务边界、失败与补偿）<br>docs/architecture/logical-erd.md（逻辑实体、关系、数据所有权、领域不变量）<br>docs/architecture/technology-decisions.md（含技术选型访谈记录、候选比较、用户确认人与日期）<br>docs/architecture/api-conventions.md<br>docs/architecture/frontend-conventions.md<br>docs/architecture/test-strategy.md<br>docs/adr/README.md<br>docs/architecture/baseline-status.md（经本阶段结束审计的各域版本/冻结状态）<br>docs/architecture/baseline-manifest.json（机器权威版本/冻结状态/域文件 SHA-256）<br>docs/architecture/constraint-registry.json（稳定约束 ID 与审批状态）<br>docs/project/baseline-audit-report.md（本阶段结束审计报告） |
| 04 | 提案拆分、依赖排序与路线图 | 项目级到功能级 | `proposal-planning` | `03-project-architecture-baseline` | 已批准并冻结的项目总体架构与基线：docs/architecture/baseline-manifest.json、constraint-registry.json、baseline-status.md、docs/project/baseline-audit-report.md<br>docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md（需求业务梳理全量输入）<br>docs/product/BASELINE-BRIEF.md、role-permission-matrix.csv、change-sizing.md、decisions.md、assumptions.md、lessons.md、id-conventions.md（基线常驻层与经验回写）<br>已知技术债与依赖<br>docs/architecture/baseline-status.md<br>相关架构/数据/API/前端/测试基线版本与审批信息<br>docs/product/open-questions.md（未决问题与阻塞条件）<br>docs/project/baseline-audit-report.md（阶段 03 审计发现的缺口、待批项与冻结结论） | docs/product/proposal-roadmap.md（含每个候选 Change 的范围/依赖/价值/基线适用域与潜在修订摘要） |
| 05 | 提案级需求分析 | 单个功能 Change | `feature-requirements` | `04-proposal-planning` | docs/product/proposal-roadmap.md（当前 Change 所在行与依赖）、当前 Change 范围<br>docs/product/BASELINE-BRIEF.md（先读，≤1 页）、change-sizing.md（切片预算与 DoD）、role-permission-matrix.csv、decisions.md、assumptions.md、lessons.md、id-conventions.md<br>docs/architecture/baseline-status.md 与相关架构/数据/公共契约/测试基线<br>docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md（关联 FLOW/BR/AC 与 RD 矩阵；AC 与验收政策对齐）<br>openspec/specs/**（只读）<br>docs/architecture/baseline-manifest.json 与 docs/architecture/constraint-registry.json（机器权威来源）<br>docs/product/open-questions.md（只读；提案需求不得替用户决策） | openspec/changes/<change-id>/proposal.md<br>openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）<br>openspec/changes/<change-id>/tasks.md（初步任务）<br>openspec/changes/<change-id>/design.md（初始设计决策；07 阶段继续更新）<br>openspec/changes/<change-id>/design/user-stories.md（用户故事与 AC；AC 是测试与验证的唯一锚点）<br>openspec/changes/<change-id>/design/baseline-impact.md（依据 templates/change-assets/design/baseline-impact.md）<br>openspec/changes/<change-id>/design/baseline-binding.json（依据当前冻结基线自动生成，逐条绑定 ACTIVE Constraint ID） |
| 06 | Figma 设计与评审（Figma-only） | 单个功能 Change | `figma-design-review` | `05-feature-requirements` | openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、design/user-stories.md（已批准的提案级需求与 AC）<br>docs/product/workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、role-permission-matrix.csv、id-conventions.md（业务流程/数据对象/RD 矩阵/角色权限/ID 约定）；docs/architecture/frontend-conventions.md（UI/前端规范，视觉权威取第 9 节）<br>docs/product/open-questions.md（只读，生成时不擅自决策）<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-impact.md（已批准的基线快照）<br>openspec/changes/<change-id>/design/baseline-binding.json（阶段 05 已审批的约束绑定；本阶段只读继承）<br>Figma MCP 实际可访问能力（生成并回读真实 Figma 设计必须；不可用或读不到真实文件/节点时阻断，不得伪造） | openspec/changes/<change-id>/design/figma-audit.md（唯一 UI 产物：Figma 文件/页面/节点/组件/变量、PAGE 清单与 PAGE → node/component/variable 映射、状态覆盖、差异与待确认、MCP 读取记录、UI 评审 APPROVED；无 UI 时 N/A + 理由） |
| 07 | 详细设计、接口与测试设计 | 单个功能 Change | `detailed-design` | `06-figma-design-review` | openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、design/user-stories.md（提案需求、AC 与初始设计决策）<br>openspec/changes/<change-id>/tasks.md（任务范围）<br>openspec/changes/<change-id>/design/figma-audit.md（06 通过 Figma MCP 实际读取并落盘的界面输入；涉及 UI 时必须读取，可用时重新读取真实 Figma 文件/节点/组件/变量）<br>Figma 设计输入（涉及 UI 时）：Figma 评审稿（视觉/组件/变量权威，经 Figma MCP 读取）、docs/architecture/frontend-conventions.md 第 9 节（视觉规范）；不单独维护 token 文件<br>docs/product/workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、acceptance-policy.md、role-permission-matrix.csv、id-conventions.md、open-questions.md（关联 FLOW/NODE/DO/BR、验收口径、权限与 ID 约定；open-questions 只读）<br>docs/architecture/system-context.md、domain-boundaries.md、containers-and-deployment.md、data-flows.md、logical-erd.md、technology-decisions.md、api-conventions.md、frontend-conventions.md、test-strategy.md、docs/adr/README.md 与 docs/adr/*（按设计域按需读取）；docs/product/BASELINE-BRIEF.md（先读）<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批） | openspec/changes/<change-id>/design.md（统一设计：设计决策、接口、前端、后端、测试五节）<br>openspec/changes/<change-id>/design/test-cases.csv（TEST ID → AC/PAGE/API/IO 的测试用例矩阵，含失败注入/替身环境/人工原因；BLOCK 可选，不适用写 N/A）<br>openspec/changes/<change-id>/api/openapi.yaml（条件适用：有 API 时）<br>openspec/changes/<change-id>/design/api-io-mapping.csv（条件适用：有 API 时）<br>openspec/changes/<change-id>/design/io-catalog.csv（条件适用：有 API 时）<br>openspec/changes/<change-id>/traceability.csv（合并 API 与测试映射；唯一追踪聚合文件） |
| 08 | 实现、TDD、验证与代码审查 | 单个功能 Change | `implementation-orchestrator` | `07-detailed-design` | openspec/changes/<change-id>/tasks.md、design.md（已批准）<br>openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（AC）<br>openspec/changes/<change-id>/api/openapi.yaml、design/api-io-mapping.csv、design/io-catalog.csv（适用时）<br>openspec/changes/<change-id>/design/test-cases.csv（按 TEST ID 实现与执行测试）<br>openspec/changes/<change-id>/design/figma-audit.md（涉及 UI 时按 Figma 评审稿实现；06 冻结 PAGE 清单）<br>openspec/changes/<change-id>/traceability.csv<br>docs/architecture/system-context.md、domain-boundaries.md、logical-erd.md、data-flows.md、technology-decisions.md、api-conventions.md、frontend-conventions.md、test-strategy.md、docs/adr/README.md（实现约束）；docs/product/open-questions.md（只读；实现不得擅自关闭未决问题）<br>openspec/changes/<change-id>/design/baseline-impact.md（已批准的基线快照）<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定） | 实际源代码/迁移/配置<br>自动化测试代码与运行结果<br>openspec/changes/<change-id>/design/evidence/code-review.md<br>实现/验证证据<br>条件适用：基线变更请求/ADR 草案（发现冲突时；未经批准不更新冻结基线） |
| 09 | 独立验证与验收证据 | 功能级 | `independent-verifier` | `08-implementation-orchestrator` | 已实现代码及 revision/diff 指纹<br>openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、tasks.md、design/user-stories.md（已批准需求、设计与 AC）<br>openspec/changes/<change-id>/api/openapi.yaml、design/api-io-mapping.csv、design/io-catalog.csv（适用时）<br>openspec/changes/<change-id>/design/figma-audit.md（涉及 UI 时对照 Figma MCP 落盘快照/真实 Figma 评审稿验证）<br>docs/product/acceptance-policy.md（项目级验收口径）<br>openspec/changes/<change-id>/design/test-cases.csv（测试用例与执行结果核对）<br>openspec/changes/<change-id>/design/evidence/code-review.md、Builder 测试与验证证据；docs/product/open-questions.md（只读；验证不得擅自关闭未决问题）<br>openspec/changes/<change-id>/traceability.csv（追踪矩阵）<br>已批准基线快照与 baseline-impact.md<br>openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定）<br>docs/architecture/baseline-status.md（当前版本） | openspec/changes/<change-id>/design/evidence/independent-verification-report.md<br>openspec/changes/<change-id>/design/evidence/independent-verification.json |
| 10 | 人工验收、归档与基线回写 | 单个功能 Change | `acceptance-audit` | `09-independent-verification` | openspec/changes/<change-id>/design/evidence/independent-verification-report.md 与 independent-verification.json（必须 PASS，revision 必须与当前验收代码一致）<br>已实现代码与测试证据<br>openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md、traceability.csv（已批准 AC/规格/追踪）<br>openspec/changes/<change-id>/design.md（设计依据）<br>openspec/changes/<change-id>/design/evidence/code-review.md<br>openspec/changes/<change-id>/design/figma-audit.md（涉及 UI 时验收 UI 与 Figma 评审稿一致性）<br>openspec/changes/<change-id>/design/test-cases.csv（验收测试覆盖证据）<br>部署/演示或验收环境证据<br>openspec/changes/<change-id>/design/baseline-impact.md<br>docs/architecture/baseline-status.md（当前版本）<br>openspec/changes/<change-id>/design/baseline-binding.json（所有适用约束有最终验证证据）<br>docs/product/acceptance-policy.md（项目级验收口径）<br>docs/product/BASELINE-BRIEF.md、change-sizing.md（DoD）、lessons.md、open-questions.md（常驻基线、完成定义、历史教训与未决问题；open-questions 只读）<br>docs/product/decisions.md、assumptions.md（待验收结果更新的决策与假设登记）<br>docs/product/id-conventions.md（回写基线与 Change ID 的分配规则） | openspec/changes/<change-id>/design/evidence/acceptance.md<br>docs/product/lessons.md（追加本次可复用教训；无则 N/A + 理由）<br>docs/product/decisions.md（受验收结果影响的状态更新）<br>docs/product/assumptions.md（受验收结果影响的状态更新）<br>验收报告与批准记录<br>OpenSpec archive 结果及更新后的主规格（仅批准后） |

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
- docs/WORKFLOW-STAGES.json
- docs/BASELINE-FEATURE-INTERACTION.md
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
- docs/product/BASELINE-BRIEF.md（一页式基线入口，≤1 页；阶段 03–05 常驻上下文）
- docs/product/role-permission-matrix.csv（角色-能力-数据范围-访问级别）
- docs/product/change-sizing.md（Change 切片预算与完成定义）
- docs/product/decisions.md（DEC 决策日志）
- docs/product/assumptions.md（ASM 假设登记）
- docs/product/lessons.md（教训/反模式；验收后由阶段 10 追加）
- docs/product/id-conventions.md（项目级/Change 级 ID 与并行分配规则）
- docs/product/BASELINE-INDEX.md（由 scripts/gen-baseline-index.py 生成的常驻基线索引）

**输出消费者**

- docs/product/requirements-analysis.md → 03、04、05
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
- 门禁：scripts/check-requirements.py --strict（FLOW/NODE/DO/RD/BR 结构、引用闭合与节点覆盖）；scripts/gen-baseline-index.py --check（常驻基线索引未过期）

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
- docs/product/BASELINE-BRIEF.md、role-permission-matrix.csv、change-sizing.md、decisions.md、assumptions.md、id-conventions.md、BASELINE-INDEX.md（常驻基线；先读简报，细节按需加载）
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
- docs/architecture/technology-decisions.md → 07、08
- docs/architecture/api-conventions.md → 07、08
- docs/architecture/frontend-conventions.md → 06、07、08
- docs/architecture/test-strategy.md → 07、08
- docs/adr/README.md → 07、08
- docs/architecture/baseline-status.md → 04、05、06、07、08、09、10
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
- docs/product/BASELINE-BRIEF.md、role-permission-matrix.csv、change-sizing.md、decisions.md、assumptions.md、lessons.md、id-conventions.md（基线常驻层与经验回写）
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
- docs/product/BASELINE-BRIEF.md（先读，≤1 页）、change-sizing.md（切片预算与 DoD）、role-permission-matrix.csv、decisions.md、assumptions.md、lessons.md、id-conventions.md
- docs/architecture/baseline-status.md 与相关架构/数据/公共契约/测试基线
- docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md（关联 FLOW/BR/AC 与 RD 矩阵；AC 与验收政策对齐）
- openspec/specs/**（只读）
- docs/architecture/baseline-manifest.json 与 docs/architecture/constraint-registry.json（机器权威来源）
- docs/product/open-questions.md（只读；提案需求不得替用户决策）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/proposal.md
- openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）
- openspec/changes/<change-id>/tasks.md（初步任务）
- openspec/changes/<change-id>/design.md（初始设计决策；07 阶段继续更新）
- openspec/changes/<change-id>/design/user-stories.md（用户故事与 AC；AC 是测试与验证的唯一锚点）
- openspec/changes/<change-id>/design/baseline-impact.md（依据 templates/change-assets/design/baseline-impact.md）
- openspec/changes/<change-id>/design/baseline-binding.json（依据当前冻结基线自动生成，逐条绑定 ACTIVE Constraint ID）

**输出消费者**

- openspec/changes/<change-id>/proposal.md → 06、07、09
- openspec/changes/<change-id>/specs/<capability>/spec.md → 06、07、08、09、10
- openspec/changes/<change-id>/tasks.md → 07、08、09
- openspec/changes/<change-id>/design.md → 06、07、08、09、10
- openspec/changes/<change-id>/design/user-stories.md → 06、07、08、09、10
- openspec/changes/<change-id>/design/baseline-impact.md → 06、07、08、09、10
- openspec/changes/<change-id>/design/baseline-binding.json → 06、07、08、09、10

**下游交接**

- 已批准的提案级 US/AC、场景与业务规则、范围边界、需求追踪 ID、基线快照与约束绑定
- specs 为规范行为唯一来源；user-stories 只保留场景、AC 与追踪 ID

**审批与门禁**

- 审批：产品负责人批准提案级需求与验收标准；技术负责人确认范围与基线影响
- 门禁：scripts/check-requirements.py --change <change-id> --strict（US/AC 结构与引用闭合）；openspec validate <change-id> --strict；scripts/check-baseline-impact.py <change-id>；scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement

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

**输入（内容/材料）**

- Figma MCP 实际可访问能力（生成并回读真实 Figma 设计必须；不可用或读不到真实文件/节点时阻断，不得伪造）

**输入（文档/文件）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、design/user-stories.md（已批准的提案级需求与 AC）
- docs/product/workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、role-permission-matrix.csv、id-conventions.md（业务流程/数据对象/RD 矩阵/角色权限/ID 约定）；docs/architecture/frontend-conventions.md（UI/前端规范，视觉权威取第 9 节）
- docs/product/open-questions.md（只读，生成时不擅自决策）
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-impact.md（已批准的基线快照）
- openspec/changes/<change-id>/design/baseline-binding.json（阶段 05 已审批的约束绑定；本阶段只读继承）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/figma-audit.md（唯一 UI 产物：Figma 文件/页面/节点/组件/变量、PAGE 清单与 PAGE → node/component/variable 映射、状态覆盖、差异与待确认、MCP 读取记录、UI 评审 APPROVED；无 UI 时 N/A + 理由）

**输出消费者**

- openspec/changes/<change-id>/design/figma-audit.md → 07、08、09、10

**下游交接**

- design/figma-audit.md 是 07/08/09/10 的唯一界面输入：可实时访问时重新读取真实 Figma 文件/节点/组件/变量；无法访问时以该落盘快照为稳定输入
- PAGE ID 与页面集合在 06 冻结；07 初始化 traceability.csv 的 PAGE→AC，08–10 只读，不新增或重命名 PAGE
- 视觉规范取 docs/architecture/frontend-conventions.md 第 9 节与 Figma 变量/样式；Figma 评审稿是视觉/组件/变量的最终权威；不再单独维护 design-tokens.json
- 不再使用 pen.dev、prototype.pen、PAGE-*.html、prototype.md、manifest.json 或 06 初始化的 traceability.csv

**审批与门禁**

- 审批：用户（设计负责人）在真实 Figma 评审稿上完成 UI 评审并 APPROVED，且 Figma MCP 审计通过
- 门禁：scripts/check-figma-audit.py --change <change-id> --strict（Figma MCP 实际生成/读取 + PAGE 覆盖与映射 + UI 评审 APPROVED）；workflow.py 自动复核 baseline-binding.json（requirement phase）

---

### 07 详细设计、接口与测试设计

- 范围：单个功能 Change
- Skill：`detailed-design`
- Prompt：`prompts/07-detailed-design.md`
- 依赖（DAG）：`06-figma-design-review`

**输入（内容/材料）**

- N/A

**输入（文档/文件）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、design/user-stories.md（提案需求、AC 与初始设计决策）
- openspec/changes/<change-id>/tasks.md（任务范围）
- openspec/changes/<change-id>/design/figma-audit.md（06 通过 Figma MCP 实际读取并落盘的界面输入；涉及 UI 时必须读取，可用时重新读取真实 Figma 文件/节点/组件/变量）
- Figma 设计输入（涉及 UI 时）：Figma 评审稿（视觉/组件/变量权威，经 Figma MCP 读取）、docs/architecture/frontend-conventions.md 第 9 节（视觉规范）；不单独维护 token 文件
- docs/product/workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、acceptance-policy.md、role-permission-matrix.csv、id-conventions.md、open-questions.md（关联 FLOW/NODE/DO/BR、验收口径、权限与 ID 约定；open-questions 只读）
- docs/architecture/system-context.md、domain-boundaries.md、containers-and-deployment.md、data-flows.md、logical-erd.md、technology-decisions.md、api-conventions.md、frontend-conventions.md、test-strategy.md、docs/adr/README.md 与 docs/adr/*（按设计域按需读取）；docs/product/BASELINE-BRIEF.md（先读）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design.md（统一设计：设计决策、接口、前端、后端、测试五节）
- openspec/changes/<change-id>/design/test-cases.csv（TEST ID → AC/PAGE/API/IO 的测试用例矩阵，含失败注入/替身环境/人工原因；BLOCK 可选，不适用写 N/A）
- openspec/changes/<change-id>/api/openapi.yaml（条件适用：有 API 时）
- openspec/changes/<change-id>/design/api-io-mapping.csv（条件适用：有 API 时）
- openspec/changes/<change-id>/design/io-catalog.csv（条件适用：有 API 时）
- openspec/changes/<change-id>/traceability.csv（合并 API 与测试映射；唯一追踪聚合文件）

**输出消费者**

- openspec/changes/<change-id>/design.md → 08、09、10
- openspec/changes/<change-id>/api/openapi.yaml → 08、09
- openspec/changes/<change-id>/design/api-io-mapping.csv → 08、09
- openspec/changes/<change-id>/design/io-catalog.csv → 08、09
- openspec/changes/<change-id>/traceability.csv → 08、09、10
- openspec/changes/<change-id>/design/test-cases.csv → 08、09、10

**下游交接**

- 统一设计决策、接口契约、前后端实现约束、测试用例矩阵与唯一追踪矩阵

**审批与门禁**

- 审批：技术负责人确认设计范围、接口与测试方案
- 门禁：scripts/check-change.sh <change-id>；scripts/check-design-assets.sh <change-id> --strict --lint-api（涉及 UI 时同时校验 figma-audit）；scripts/check-design-sections.py --change <change-id>；scripts/check-test-cases.py --change <change-id> --strict；scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict；有 API 时 scripts/check-api-traceability.py --change <change-id>；python3 scripts/baseline-governance.py check-change --change-id <id> --phase design

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

**输入（内容/材料）**

- N/A

**输入（文档/文件）**

- openspec/changes/<change-id>/tasks.md、design.md（已批准）
- openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md（AC）
- openspec/changes/<change-id>/api/openapi.yaml、design/api-io-mapping.csv、design/io-catalog.csv（适用时）
- openspec/changes/<change-id>/design/test-cases.csv（按 TEST ID 实现与执行测试）
- openspec/changes/<change-id>/design/figma-audit.md（涉及 UI 时按 Figma 评审稿实现；06 冻结 PAGE 清单）
- openspec/changes/<change-id>/traceability.csv
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

- openspec/changes/<change-id>/design/evidence/code-review.md

**输出消费者**

- openspec/changes/<change-id>/design/evidence/code-review.md → 09、10

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

### 09 独立验证与验收证据

- 范围：功能级
- Skill：`independent-verifier`
- Prompt：`prompts/09-independent-verification.md`
- 依赖（DAG）：`08-implementation-orchestrator`

**输入（内容/材料）**

- 已实现代码及 revision/diff 指纹

**输入（文档/文件）**

- openspec/changes/<change-id>/proposal.md、specs/<capability>/spec.md、design.md、tasks.md、design/user-stories.md（已批准需求、设计与 AC）
- openspec/changes/<change-id>/api/openapi.yaml、design/api-io-mapping.csv、design/io-catalog.csv（适用时）
- openspec/changes/<change-id>/design/figma-audit.md（涉及 UI 时对照 Figma MCP 落盘快照/真实 Figma 评审稿验证）
- docs/product/acceptance-policy.md（项目级验收口径）
- openspec/changes/<change-id>/design/test-cases.csv（测试用例与执行结果核对）
- openspec/changes/<change-id>/design/evidence/code-review.md、Builder 测试与验证证据；docs/product/open-questions.md（只读；验证不得擅自关闭未决问题）
- openspec/changes/<change-id>/traceability.csv（追踪矩阵）
- 已批准基线快照与 baseline-impact.md
- openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定）
- docs/architecture/baseline-status.md（当前版本）

**输出（内容/材料）**

- N/A

**输出（文档/文件）**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md
- openspec/changes/<change-id>/design/evidence/independent-verification.json

**输出消费者**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md → 10
- openspec/changes/<change-id>/design/evidence/independent-verification.json → 10

**下游交接**

- 独立验证报告与 JSON 证据
- AC 逐项验证结果
- 测试命令与退出码
- 发现项和未执行项

**审批与门禁**

- 审批：独立验证 PASS；Verifier 不得是本次 Builder 的同一执行上下文；失败/阻断退回实现阶段
- 门禁：scripts/check-independent-verification.py；所有适用 AC PASS、测试退出码 0、revision 稳定、只读、无 BLOCKER/CRITICAL；baseline-governance.py check-change --phase implementation

---

### 10 人工验收、归档与基线回写

- 范围：单个功能 Change
- Skill：`acceptance-audit`
- Prompt：`prompts/10-acceptance-audit.md`
- 依赖（DAG）：`09-independent-verification`

**输入（内容/材料）**

- 已实现代码与测试证据
- 部署/演示或验收环境证据

**输入（文档/文件）**

- openspec/changes/<change-id>/design/evidence/independent-verification-report.md 与 independent-verification.json（必须 PASS，revision 必须与当前验收代码一致）
- openspec/changes/<change-id>/specs/<capability>/spec.md、design/user-stories.md、traceability.csv（已批准 AC/规格/追踪）
- openspec/changes/<change-id>/design.md（设计依据）
- openspec/changes/<change-id>/design/evidence/code-review.md
- openspec/changes/<change-id>/design/figma-audit.md（涉及 UI 时验收 UI 与 Figma 评审稿一致性）
- openspec/changes/<change-id>/design/test-cases.csv（验收测试覆盖证据）
- openspec/changes/<change-id>/design/baseline-impact.md
- docs/architecture/baseline-status.md（当前版本）
- openspec/changes/<change-id>/design/baseline-binding.json（所有适用约束有最终验证证据）
- docs/product/acceptance-policy.md（项目级验收口径）
- docs/product/BASELINE-BRIEF.md、change-sizing.md（DoD）、lessons.md、open-questions.md（常驻基线、完成定义、历史教训与未决问题；open-questions 只读）
- docs/product/decisions.md、assumptions.md（待验收结果更新的决策与假设登记）
- docs/product/id-conventions.md（回写基线与 Change ID 的分配规则）

**输出（内容/材料）**

- 验收报告与批准记录
- OpenSpec archive 结果及更新后的主规格（仅批准后）

**输出（文档/文件）**

- openspec/changes/<change-id>/design/evidence/acceptance.md
- docs/product/lessons.md（追加本次可复用教训；无则 N/A + 理由）
- docs/product/decisions.md（受验收结果影响的状态更新）
- docs/product/assumptions.md（受验收结果影响的状态更新）

**输出消费者**

- openspec/changes/<change-id>/design/evidence/acceptance.md → evidence-only
- docs/product/lessons.md → FUTURE
- docs/product/decisions.md → FUTURE
- docs/product/assumptions.md → FUTURE

**下游交接**

- 已验收并归档的能力规格、验收证据、后续 Change 依赖

**审批与门禁**

- 审批：产品责任人明确批准后才可归档；不得用 -y 绕过
- 门禁：scripts/check-acceptance.py；verify-before-completion.sh；openspec validate/archive 真实执行；阶段 09 独立验证必须 PASS 且 revision 未变化；baseline-governance.py check-change --phase acceptance

**基线交互**

- 只读：design/baseline-impact.md；当前基线状态；已批准的 ADR/基线变更请求
- 产出/复核：更新 docs/product/lessons.md、decisions.md、assumptions.md（仅回写已批准、已实现、已验证的跨功能决策）；在途 Change 影响复核清单；需要更新冻结基线时，提交基线修订请求并按 open-amendment/close-amendment 流程执行，不直接编写基线文件
- 门禁：只回写已批准/已实现/已验证的跨功能决策；功能细节留在 Change

---
