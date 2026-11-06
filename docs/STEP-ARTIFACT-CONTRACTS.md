# 每一步的输入、输出与交接契约

> 本文件是工作流交接的权威索引；机器可读版本为 `docs/STEP-ARTIFACT-CONTRACTS.json`。文件路径按模板包约定，实际项目可在初始化时配置，但不得静默改变。

## 强制交接规则

1. 每个阶段开始时，先读取本文件和 JSON 中该 Skill 对应的唯一记录。
2. 输入必须来自真实文件；聊天内容只有在明确保存并评审后才能成为正式产物。
3. 每项输入必须核验存在性、版本/更新时间、批准状态及与当前 Change 的关联。
4. 输出必须写入约定路径；禁止只在聊天窗口输出而不落盘（纯讨论/澄清阶段除外，且需明确标记草案）。
5. 阶段结束时展示：输出文件路径、每份文件摘要、追踪关系、自检命令及退出码、未执行项、待审批项、下一阶段将读取的文件。
6. 只有门禁通过且所需审批完成，才更新 `workflow-state.json` 并允许“下一步”。
7. 不适用的产物必须写 `N/A` + 理由 + 批准人；不能用空文件或虚构数据满足检查。
8. OpenSpec Change 产物与项目级基线分开维护；功能 Change 引用项目基线，不复制整份基线。


## 项目基线与功能 Change 的双向交互（强制）

- 权威规则：`docs/BASELINE-FEATURE-INTERACTION.md`；机器权威：`docs/architecture/baseline-manifest.json` 与 `docs/architecture/constraint-registry.json`；功能级人类影响清单：`baseline-impact.md`；功能级机器绑定：`baseline-binding.json`。
- 阶段 09 拆分 Change 时，初步识别适用基线域和潜在基线修订；阶段 10 必须为每个 Change 建立版本化的基线影响清单。
- 阶段 05 的项目总体架构设计结束审计负责冻结：`baseline-governance.py audit --require-frozen`；阶段 09 和所有功能阶段入口都再次验证 Manifest、文件哈希与约束注册表。
- 阶段 10 每个 Change 必须生成 `design/baseline-binding.json`，覆盖全部 ACTIVE Constraint ID；阶段 13a–13e、14/14b、15 分别检查设计、实现和验收证据。
- 阶段 10 前必须检查基线状态、产品规则、系统/模块边界和相关 OpenSpec specs；再按功能影响深入读取数据、API、前端、部署、测试等基线。
- 阶段 13a–13e 在设计时复核基线版本和约束；基线版本变化必须记录 `NO_IMPACT` 或 `REBASE_REQUIRED`。
- 阶段 14 实现中不准直接修改冻结基线。发现冲突时记录并暂停受影响任务，走基线变更请求/ADR；批准后刷新功能快照、设计、测试。
- 阶段 15 仅把已批准、已实现、已验证且跨功能复用的决策回写基线；功能特有的 API、页面、物理表迁移、IO 与测试保留在 Change。
- 基线修改必须先 `open-amendment`；修订窗口期间功能门禁全部阻断。完成版本升级、哈希刷新与审批后由 `close-amendment` 重新冻结。
- 基线变更与 OpenSpec 主规格归档是两种独立动作：前者治理共享设计约束，后者维护可观察行为规格。

| 时点 | 必须读取 | 允许写入 | 禁止行为 |
|---|---|---|---|
| 功能开发前（09/10） | 基线状态、相关产品/架构/数据/公共契约/测试约束、相关 specs | `design/baseline-impact.md`、Change proposal/spec | 未批准基线变化前冻结依赖它的设计 |
| 详细设计（13a–13e） | 基线快照与当前版本、各设计域约束 | Change 详细设计、基线修订请求/ADR 草案 | 在功能设计里隐式绕过公共约束 |
| 实施（14） | 已批准基线、Change 基线快照 | 代码、迁移、测试、基线问题记录/BCR 草案 | 直接编辑冻结基线或自行批准 BCR |
| 验收归档（15） | BCR/ADR 审批证据、实际实现/测试结果 | 已批准的基线文档、版本登记、在途 Change 复核 | 将功能局部实现自动升级为全局规范 |

## 阶段契约总表

| 阶段 | Skill / Prompt | 输入（必须核验） | 输出（必须落盘） | 下一步消费内容 | 人工批准点 |
|---|---|---|---|---|---|
| 00 下一步编排 | `workflow-orchestrator`<br>`prompts/00-next-step.md` | `workflow-state.json`<br>`docs/PROCESS-MAP.md`<br>`docs/STEP-ARTIFACT-CONTRACTS.json`<br>`docs/OUTPUT-TEMPLATE-MATRIX.csv`<br>`真实产物与审批记录`<br>`OpenSpec CLI 当前状态（如已初始化）` | `下一阶段判定报告（对话展示；必要时写入 docs/workflow/next-step-report.md）`<br>`workflow-state.json（仅在真实状态变化时更新）` | `所选阶段的 Input Contract 中全部文件` | 不得越过 pending_approvals、blocked_items、缺失输入或失败门禁 |
| 01 项目初始化与工具链检查 | `project-bootstrap`<br>`prompts/01-project-bootstrap.md` | `用户提供的项目目标与仓库位置`<br>`仓库现有目录/配置/AGENTS.md（若存在）` | `AGENTS.md（仅缺失时创建或经批准修改）`<br>`workflow-state.json`<br>`docs/architecture/baseline-status.md（依据 templates/project-baseline/baseline-status.md）`<br>`docs/project/toolchain-report.md（依据 templates/project-baseline/toolchain-report.md）` | `仓库约定与工具链报告`<br>`workflow-state.json` | 覆盖/修改既有 AGENTS.md 或配置前需批准 |
| 02 需求业务梳理 | `requirements-analysis`<br>`prompts/02-requirements-analysis.md` | `访谈/业务材料/旧系统资料`<br>`项目目标、用户、角色、约束`<br>`既有 docs/product/*（若存在）`<br>`既有 OpenSpec specs（只读）` | `docs/product/requirements-analysis.md`<br>`docs/product/workflows.md（每个 FLOW 必须含完整节点表：节点角色、输入/输出数据对象、前置条件、处理动作、异常/分支、下一节点）`<br>`docs/product/data-objects.csv（业务数据对象目录）`<br>`docs/product/rd-matrix.csv（需求-数据对象矩阵：需求/规则 → 流程节点 → 角色 → 数据对象）`<br>`docs/product/business-rules.md`<br>`docs/product/glossary.md`<br>`docs/product/acceptance-policy.md`<br>`docs/product/open-questions.md` | `业务流程与节点级角色/数据对象、业务数据对象目录、RD 矩阵、业务规则、术语与验收政策、未决问题` | 业务/产品负责人确认业务流程完整性、节点数据对象与角色、RD 矩阵覆盖 |
| 05 项目总体架构设计 | `project-architecture-baseline`<br>`prompts/05-project-architecture-baseline.md` | `已批准的 docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md`<br>`现有仓库结构/技术约束`<br>`非功能需求`<br>`用户/技术负责人明确的技术选型偏好（本阶段必须显式询问并记录，不得默认或自行假设）` | `docs/architecture/system-context.md`<br>`docs/architecture/domain-boundaries.md`<br>`docs/architecture/containers-and-deployment.md`<br>`docs/architecture/data-flows.md（数据流转：DF ID、同步/异步、事务边界、失败与补偿）`<br>`docs/architecture/logical-erd.md（逻辑实体、关系、数据所有权、领域不变量）`<br>`docs/architecture/technology-decisions.md（含技术选型访谈记录、候选比较、用户确认人与日期）`<br>`docs/architecture/api-conventions.md`<br>`docs/architecture/frontend-conventions.md`<br>`docs/architecture/test-strategy.md`<br>`docs/adr/README.md`<br>`docs/architecture/baseline-status.md（经本阶段结束审计的各域版本/冻结状态）`<br>`docs/architecture/baseline-manifest.json（机器权威版本/冻结状态/域文件 SHA-256）`<br>`docs/architecture/constraint-registry.json（稳定约束 ID 与审批状态）`<br>`docs/project/baseline-audit-report.md（本阶段结束审计报告）` | `冻结的项目总体架构基线、数据流转、逻辑 ERD、公共契约/测试策略、ACTIVE 约束目录、审计报告与审批记录` | 产品/架构/技术负责人共同确认系统边界、数据流转与公共契约，并批准基线冻结 |
| 09 提案拆分、依赖排序与路线图 | `proposal-planning`<br>`prompts/09-proposal-planning.md` | `已批准并冻结的项目总体架构与基线（阶段 05 结束审计）`<br>`需求业务梳理、RD 矩阵、业务规则与验收政策`<br>`已知技术债与依赖`<br>`docs/architecture/baseline-status.md`<br>`相关架构/数据/API/前端/测试基线版本与审批信息` | `docs/product/proposal-roadmap.md`<br>`每个候选 Change 的范围/依赖/价值说明`<br>`候选 Change 基线适用域/潜在修订摘要（写入 docs/product/proposal-roadmap.md）` | `经批准的 Change 列表、优先级、依赖顺序` | 产品与技术负责人批准路线图及首个 Change |
| 10 提案级需求分析 | `feature-requirements`<br>`prompts/10-feature-requirements.md` | `已批准路线图/当前 Change 范围`<br>`docs/architecture/baseline-status.md 与相关架构/数据/公共契约/测试基线`<br>`关联 FLOW/BR/AC 与项目 RD 矩阵`<br>`现有 OpenSpec specs`<br>`docs/architecture/baseline-manifest.json 与 docs/architecture/constraint-registry.json（机器权威来源）` | `openspec/changes/<change-id>/proposal.md`<br>`openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）`<br>`openspec/changes/<change-id>/tasks.md（初步任务）`<br>`openspec/changes/<change-id>/design.md（有设计决策时）`<br>`openspec/changes/<change-id>/design/user-stories.md（提案级用户故事与 AC）`<br>`openspec/changes/<change-id>/design/use-cases.md（提案级功能用例）`<br>`openspec/changes/<change-id>/design/baseline-impact.md（依据 templates/change-assets/design/baseline-impact.md）`<br>`openspec/changes/<change-id>/design/baseline-binding.json（依据当前冻结基线自动生成，逐条绑定 ACTIVE Constraint ID）` | `已批准的提案级 US/UC/AC、场景与业务规则、范围边界、需求追踪 ID、基线快照与约束绑定` | 产品负责人批准提案级需求与验收标准；技术负责人确认范围与基线影响 |
| 10b 提案原型生成与评审 | `prototype-generation`<br>`prompts/10b-prototype-generation.md` | `已批准的提案级需求（proposal/specs/design/user-stories/use-cases）`<br>`docs/product/open-questions.md（只读，生成时不擅自决策）`<br>`pen.dev MCP 实际可访问能力（pencil 工具）`<br>`openspec/changes/<change-id>/design/baseline-binding.json（只读继承）` | `openspec/changes/<change-id>/design/prototype-build.md`<br>`openspec/changes/<change-id>/design/prototype-audit.md`<br>`pen.dev 原型页面（链接登记到构建记录；导出快照若支持）` | `已批准原型链接/导出物、PAGE→UC/US/FLOW/BR 映射、原型评审结论与需求澄清` | 产品/设计负责人确认原型与需求差异；原型与需求修订在阶段结束审计中一并批准 |
| 11 页面、功能区块、元素与交互事件清单 | `page-interaction-inventory`<br>`prompts/11-page-interaction-inventory.md` | `已批准的提案级需求（proposal/specs/design/user-stories/use-cases）`<br>`已批准的提案原型构建记录与评审结论（openspec/changes/<change-id>/design/prototype-build.md、prototype-audit.md）`<br>`项目级业务流程/数据对象/RD 矩阵与 UI/前端规范`<br>`openspec/changes/<change-id>/design/baseline-binding.json（阶段 10 已审批的约束绑定；本阶段只读继承）` | `openspec/changes/<change-id>/design/page-inventory.csv`<br>`openspec/changes/<change-id>/design/block-inventory.csv`<br>`openspec/changes/<change-id>/design/interaction-map.csv` | `PAGE/BLOCK/ELEM/EVT 清单、页面内区块顺序与职责、每个按钮/元素唯一所属区块、状态/跳转、事件与需求/operationId 的关联` | 产品负责人确认页面与交互覆盖 |
| 12 Figma UI 设计与 MCP 审计 | `figma-ui-audit`<br>`prompts/12-figma-ui-audit.md` | `已批准页面/区块/交互清单（含 block_id 归属）`<br>`已批准功能规格`<br>`Figma 文件/节点与可访问 MCP 输出`<br>`项目级设计规范`<br>`openspec/changes/<change-id>/design/baseline-binding.json（阶段 10 已审批的约束绑定；本阶段只读继承）` | `openspec/changes/<change-id>/design/figma-audit.md`<br>`Figma 设计链接/节点映射及导出资源引用` | `页面/区块/组件/状态的 UI 设计依据、区块覆盖差异与待确认项` | 设计/产品负责人批准 UI |
| 13a 功能详细设计总控 | `feature-design`<br>`prompts/13a-feature-design.md` | `已批准 proposal/specs`<br>`页面/交互清单与 Figma 审计（适用时）`<br>`项目级架构/数据/公共契约基线`<br>`openspec/changes/<change-id>/design/baseline-impact.md`<br>`docs/architecture/baseline-status.md（当前版本）`<br>`openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）` | `openspec/changes/<change-id>/design.md`<br>`功能详细设计任务分解与设计缺口清单` | `统一设计约束、接口范围、前后端/测试设计任务` | 技术负责人确认设计范围和重大方案 |
| 13b OpenAPI 与接口逻辑设计 | `api-contract-design`<br>`prompts/13b-api-contract-design.md` | `已批准功能规格与页面交互清单`<br>`Figma 交互（适用时）`<br>`项目级 API/鉴权/错误码约定`<br>`openspec/changes/<change-id>/design/baseline-impact.md`<br>`docs/architecture/baseline-status.md（当前版本）`<br>`openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）` | `openspec/changes/<change-id>/api/openapi.yaml`<br>`operationId 到页面事件/AC 的追踪关系` | `唯一 OpenAPI 契约、operationId、请求响应/错误/权限定义` | API 契约经前后端共同评审 |
| 13c 前端详细设计 | `frontend-detail-design`<br>`prompts/13c-frontend-detail-design.md` | `已批准 OpenAPI（或 x-api-scope: none）`<br>`页面/区块/交互清单（含 block_id 归属）与 Figma 审计`<br>`前端工程规范`<br>`功能规格与 AC`<br>`openspec/changes/<change-id>/design/baseline-impact.md`<br>`docs/architecture/baseline-status.md（当前版本）`<br>`openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）` | `openspec/changes/<change-id>/design/frontend-design.md`<br>`前端测试用例/组件状态映射` | `PAGE→BLOCK→组件树、区块与元素归属、组件职责、状态管理、API 调用映射、错误/加载/空状态、测试 ID` | 前端负责人评审 |
| 13d 后端详细设计 | `backend-detail-design`<br>`prompts/13d-backend-detail-design.md` | `已批准 OpenAPI`<br>`功能规格与 AC`<br>`项目级架构/领域/数据模型/公共 Client 规范`<br>`openspec/changes/<change-id>/design/baseline-impact.md`<br>`docs/architecture/baseline-status.md（当前版本）`<br>`openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）` | `openspec/changes/<change-id>/design/backend-design.md`<br>`openspec/changes/<change-id>/design/api-io-mapping.csv`<br>`openspec/changes/<change-id>/design/io-catalog.csv` | `API→IO 映射、每个 IO 契约、事务/幂等/超时/重试/错误映射、测试 ID` | 后端负责人/架构负责人评审 IO 边界与事务一致性 |
| 13e 测试设计与追踪矩阵 | `test-design`<br>`prompts/13e-test-design.md` | `已批准功能规格/AC`<br>`OpenAPI`<br>`前后端详细设计`<br>`API→IO 映射与 IO 契约`<br>`项目级测试策略`<br>`openspec/changes/<change-id>/design/baseline-impact.md`<br>`docs/architecture/baseline-status.md（当前版本）`<br>`openspec/changes/<change-id>/design/baseline-binding.json（逐条约束、设计证据和例外审批）` | `openspec/changes/<change-id>/design/test-design.md`<br>`openspec/changes/<change-id>/traceability.csv` | `TEST ID、覆盖的 AC/API/IO、测试数据/环境/命令、预期结果` | 测试负责人确认覆盖范围与质量门禁 |
| 14 实现、TDD、验证与代码审查 | `implementation-orchestrator`<br>`prompts/14-implementation-orchestrator.md` | `已批准 tasks.md/design.md`<br>`前后端详细设计、OpenAPI、IO 契约`<br>`test-design.md 与 traceability.csv`<br>`项目级工程规范/测试策略`<br>`openspec/changes/<change-id>/design/baseline-impact.md（已批准的基线快照）`<br>`docs/architecture/baseline-status.md（当前版本）`<br>`openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定）` | `实际源代码/迁移/配置`<br>`自动化测试代码与运行结果`<br>`openspec/changes/<change-id>/design/evidence/code-review.md`<br>`实现/验证证据`<br>`条件适用：基线变更请求/ADR 草案（发现冲突时；未经批准不更新冻结基线）` | `代码差异、测试报告、审查结论、未解决问题` | 代码审查阻断项关闭；合并按项目权限单独审批 |
| 14b 独立验证与验收证据 | `independent-verifier`<br>`prompts/14b-independent-verification.md` | `已实现代码及 revision/diff 指纹`<br>`已批准 proposal/specs/design/tasks`<br>`已批准基线快照与 baseline-impact.md`<br>`OpenAPI、API-IO 映射、IO catalog（适用时）`<br>`前后端详细设计、测试设计、Builder 测试和审查报告`<br>`openspec/changes/<change-id>/design/baseline-binding.json（已批准约束绑定）` | `openspec/changes/<change-id>/design/evidence/independent-verification-report.md`<br>`openspec/changes/<change-id>/design/evidence/independent-verification.json` | `独立验证报告与 JSON 证据`<br>`AC 逐项验证结果`<br>`测试命令与退出码`<br>`发现项和未执行项` | 独立验证 PASS；Verifier 不得是本次 Builder 的同一执行上下文；失败/阻断退回实现阶段 |
| 15 人工验收、归档与基线回写 | `acceptance-audit`<br>`prompts/15-acceptance-audit.md` | `阶段 14b 的 independent-verification-report.md 与 independent-verification.json（必须 PASS，revision 必须与当前验收代码一致）`<br>`已实现代码与测试证据`<br>`已批准 AC/规格/追踪矩阵`<br>`代码审查记录`<br>`部署/演示或验收环境证据`<br>`openspec/changes/<change-id>/design/baseline-impact.md`<br>`docs/architecture/baseline-status.md（当前版本）`<br>`openspec/changes/<change-id>/design/baseline-binding.json（所有适用约束有最终验证证据）` | `openspec/changes/<change-id>/design/evidence/acceptance.md`<br>`验收报告与批准记录`<br>`OpenSpec archive 结果及更新后的主规格（仅批准后）`<br>`项目路线图/基线状态回写（适用时）`<br>`条件适用：更新项目级基线文档与 baseline-status.md（仅批准/实现/验证完成后）` | `已验收并归档的能力规格、验收证据、后续 Change 依赖` | 产品责任人明确批准后才可归档；不得用 -y 绕过 |

## 每阶段结束时必须展示的交接报告

使用 `templates/workflow/step-handoff-report.md`。报告必须区分：已生成、已修改、仅建议、待确认、未执行。不能把建议路径说成已生成文件，也不能把工具不可用说成校验通过。

## 状态更新规则

`workflow-state.json` 的 `completed_steps` 只记录门禁通过且所需审批完成的阶段；`last_completed_outputs` 记录真实存在的文件路径；`pending_approvals` 与 `blocked_items` 未清空时，`scripts/next-step.py` 不得建议越过阻断阶段。
