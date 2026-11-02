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

## 阶段契约总表

| 阶段 | Skill / Prompt | 输入（必须核验） | 输出（必须落盘） | 下一步消费内容 | 人工批准点 |
| 00 下一步编排 | `workflow-orchestrator`<br>`prompts/00-next-step.md` | `workflow-state.json`<br>`docs/PROCESS-MAP.md`<br>`docs/STEP-ARTIFACT-CONTRACTS.json`<br>`docs/OUTPUT-TEMPLATE-MATRIX.csv`<br>`真实产物与审批记录`<br>`OpenSpec CLI 当前状态（如已初始化）` | `下一阶段判定报告（对话展示；必要时写入 docs/workflow/next-step-report.md）`<br>`workflow-state.json（仅在真实状态变化时更新）` | `所选阶段的 Input Contract 中全部文件` | 不得越过 pending_approvals、blocked_items、缺失输入或失败门禁 |
| 01 项目初始化与工具链检查 | `project-bootstrap`<br>`prompts/01-project-bootstrap.md` | `用户提供的项目目标与仓库位置`<br>`仓库现有目录/配置/AGENTS.md（若存在）` | `AGENTS.md（仅缺失时创建或经批准修改）`<br>`workflow-state.json`<br>`docs/architecture/baseline-status.md`<br>`docs/project/toolchain-report.md（依据 templates/project-baseline/toolchain-report.md）` | `仓库约定与工具链报告`<br>`workflow-state.json` | 覆盖/修改既有 AGENTS.md 或配置前需批准 |
| 02 需求发现与整理 | `requirements-analysis`<br>`prompts/02-requirements-analysis.md` | `访谈/业务材料/旧系统资料`<br>`项目目标、用户、角色、约束`<br>`既有 docs/product/*（若存在）`<br>`既有 OpenSpec specs（只读）` | `docs/product/requirements-analysis.md`<br>`docs/product/workflows.md`<br>`docs/product/use-cases.md`<br>`docs/product/user-stories.md`<br>`docs/product/business-rules.md`<br>`docs/product/open-questions.md` | `需求分析报告、流程、用例、故事、规则、未决问题` | 业务负责人确认关键流程、范围、规则与验收标准 |
| 03 pen.dev 原型评审与需求澄清 | `prototype-audit`<br>`prompts/03-prototype-audit.md` | `docs/product/* 需求产物`<br>`pen.dev 原型链接/导出物（必须实际可访问）`<br>`需求疑问与干系人反馈` | `docs/design/prototype-audit.md`<br>`docs/product/open-questions.md（更新）`<br>`docs/product/requirements-analysis.md（经确认的修订）` | `原型评审结论、已确认需求修订、未决问题` | 客户/产品负责人确认原型与需求差异 |
| 04 项目级产品基线 | `product-baseline`<br>`prompts/04-product-baseline.md` | `已确认需求产物`<br>`已批准原型审计与修订记录` | `docs/product/requirements-analysis.md`<br>`docs/product/workflows.md`<br>`docs/product/use-cases.md`<br>`docs/product/user-stories.md`<br>`docs/product/business-rules.md`<br>`docs/product/glossary.md`<br>`docs/product/acceptance-policy.md` | `已批准产品需求基线及稳定 ID` | 产品负责人批准产品基线版本 |
| 05 项目总体架构设计 | `project-architecture-baseline`<br>`prompts/05-project-architecture-baseline.md` | `已批准产品基线`<br>`现有仓库结构/技术约束`<br>`非功能需求` | `docs/architecture/system-context.md`<br>`docs/architecture/domain-boundaries.md`<br>`docs/architecture/containers-and-deployment.md`<br>`docs/architecture/data-flows.md`<br>`docs/architecture/technology-decisions.md`<br>`docs/adr/README.md` | `系统边界、模块职责、部署拓扑、技术决策、跨模块数据流` | 架构负责人批准重大技术选型与边界 |
| 06 项目级数据与领域基线 | `data-domain-baseline`<br>`prompts/06-data-domain-baseline.md` | `已批准产品基线`<br>`docs/architecture/* 架构基线`<br>`现有数据库/领域资料（若存在）` | `docs/architecture/logical-erd.md`<br>`docs/architecture/domain-boundaries.md（必要时修订）`<br>`docs/architecture/data-flows.md（必要时修订）` | `逻辑实体、关系、数据所有权、领域不变量、数据流` | 数据/架构负责人批准核心模型与所有权 |
| 07 项目级接口/前端/测试规范 | `project-contract-baseline`<br>`prompts/07-project-contract-baseline.md` | `已批准架构与数据领域基线`<br>`现有前后端工程规范`<br>`非功能要求` | `docs/architecture/api-conventions.md`<br>`docs/architecture/frontend-conventions.md`<br>`docs/architecture/test-strategy.md` | `API 公共约定、前端工程约定、测试策略与质量门禁` | 技术负责人批准公共工程规范 |
| 08 项目基线审计与冻结 | `baseline-audit`<br>`prompts/08-baseline-audit.md` | `产品基线`<br>`架构基线`<br>`数据/领域基线`<br>`公共契约/测试基线`<br>`未决问题清单` | `templates/project-baseline/baseline-audit-report.md 的项目实例（建议 docs/project/baseline-audit-report.md）`<br>`docs/architecture/baseline-status.md` | `冻结的项目基线版本、缺口/豁免、审批记录` | 产品/架构/技术负责人共同批准冻结 |
| 09 提案拆分、依赖排序与路线图 | `proposal-planning`<br>`prompts/09-proposal-planning.md` | `已冻结项目基线`<br>`产品需求/用户故事/AC`<br>`已知技术债与依赖` | `docs/product/proposal-roadmap.md`<br>`每个候选 Change 的范围/依赖/价值说明` | `经批准的 Change 列表、优先级、依赖顺序` | 产品与技术负责人批准路线图及首个 Change |
| 10 功能级 OpenSpec Change 与需求细化 | `feature-requirements`<br>`prompts/10-feature-requirements.md` | `已批准路线图/当前 Change 范围`<br>`项目级产品/架构/数据/公共契约基线`<br>`关联 US/AC/BR/FLOW/UC`<br>`现有 OpenSpec specs` | `openspec/changes/<change-id>/proposal.md`<br>`openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）`<br>`openspec/changes/<change-id>/tasks.md（初步任务）`<br>`openspec/changes/<change-id>/design.md（有设计决策时）` | `已批准 Change proposal/specs、范围边界、验收标准、需求追踪 ID` | 提案及功能范围经人工批准后才进入设计 |
| 11 页面、元素、按钮与交互事件清单 | `page-interaction-inventory`<br>`prompts/11-page-interaction-inventory.md` | `已批准 Change proposal/specs`<br>`关联 US/AC 与业务流程`<br>`项目级 UI/前端规范` | `openspec/changes/<change-id>/design/page-inventory.csv`<br>`openspec/changes/<change-id>/design/interaction-map.csv` | `PAGE/ELEM/EVT 清单、状态/跳转、事件与需求/operationId 的关联` | 产品负责人确认页面与交互覆盖 |
| 12 Figma UI 设计与 MCP 审计 | `figma-ui-audit`<br>`prompts/12-figma-ui-audit.md` | `已批准页面/交互清单`<br>`已批准功能规格`<br>`Figma 文件/节点与可访问 MCP 输出`<br>`项目级设计规范` | `openspec/changes/<change-id>/design/figma-audit.md`<br>`Figma 设计链接/节点映射及导出资源引用` | `页面/组件/状态的 UI 设计依据、差异与待确认项` | 设计/产品负责人批准 UI |
| 13a 功能详细设计总控 | `feature-design`<br>`prompts/13a-feature-design.md` | `已批准 proposal/specs`<br>`页面/交互清单与 Figma 审计（适用时）`<br>`项目级架构/数据/公共契约基线` | `openspec/changes/<change-id>/design.md`<br>`功能详细设计任务分解与设计缺口清单` | `统一设计约束、接口范围、前后端/测试设计任务` | 技术负责人确认设计范围和重大方案 |
| 13b OpenAPI 与接口逻辑设计 | `api-contract-design`<br>`prompts/13b-api-contract-design.md` | `已批准功能规格与页面交互清单`<br>`Figma 交互（适用时）`<br>`项目级 API/鉴权/错误码约定` | `openspec/changes/<change-id>/api/openapi.yaml`<br>`operationId 到页面事件/AC 的追踪关系` | `唯一 OpenAPI 契约、operationId、请求响应/错误/权限定义` | API 契约经前后端共同评审 |
| 13c 前端详细设计 | `frontend-detail-design`<br>`prompts/13c-frontend-detail-design.md` | `已批准 OpenAPI（或 x-api-scope: none）`<br>`页面/交互清单与 Figma 审计`<br>`前端工程规范`<br>`功能规格与 AC` | `openspec/changes/<change-id>/design/frontend-design.md`<br>`前端测试用例/组件状态映射` | `组件职责、状态管理、API 调用映射、错误/加载/空状态、测试 ID` | 前端负责人评审 |
| 13d 后端详细设计 | `backend-detail-design`<br>`prompts/13d-backend-detail-design.md` | `已批准 OpenAPI`<br>`功能规格与 AC`<br>`项目级架构/领域/数据模型/公共 Client 规范` | `openspec/changes/<change-id>/design/backend-design.md`<br>`openspec/changes/<change-id>/design/api-io-mapping.csv`<br>`openspec/changes/<change-id>/design/io-catalog.csv` | `API→IO 映射、每个 IO 契约、事务/幂等/超时/重试/错误映射、测试 ID` | 后端负责人/架构负责人评审 IO 边界与事务一致性 |
| 13e 测试设计与追踪矩阵 | `test-design`<br>`prompts/13e-test-design.md` | `已批准功能规格/AC`<br>`OpenAPI`<br>`前后端详细设计`<br>`API→IO 映射与 IO 契约`<br>`项目级测试策略` | `openspec/changes/<change-id>/design/test-design.md`<br>`openspec/changes/<change-id>/traceability.csv` | `TEST ID、覆盖的 AC/API/IO、测试数据/环境/命令、预期结果` | 测试负责人确认覆盖范围与质量门禁 |
| 14 实现、TDD、验证与代码审查 | `implementation-orchestrator`<br>`prompts/14-implementation-orchestrator.md` | `已批准 tasks.md/design.md`<br>`前后端详细设计、OpenAPI、IO 契约`<br>`test-design.md 与 traceability.csv`<br>`项目级工程规范/测试策略` | `实际源代码/迁移/配置`<br>`自动化测试代码与运行结果`<br>`openspec/changes/<change-id>/design/evidence/code-review.md`<br>`实现/验证证据` | `代码差异、测试报告、审查结论、未解决问题` | 代码审查阻断项关闭；合并按项目权限单独审批 |
| 15 人工验收、归档与基线回写 | `acceptance-audit`<br>`prompts/15-acceptance-audit.md` | `已实现代码与测试证据`<br>`已批准 AC/规格/追踪矩阵`<br>`代码审查记录`<br>`部署/演示或验收环境证据` | `openspec/changes/<change-id>/design/evidence/acceptance.md`<br>`验收报告与批准记录`<br>`OpenSpec archive 结果及更新后的主规格（仅批准后）`<br>`项目路线图/基线状态回写（适用时）` | `已验收并归档的能力规格、验收证据、后续 Change 依赖` | 产品责任人明确批准后才可归档；不得用 -y 绕过 |

## 每阶段结束时必须展示的交接报告

使用 `templates/workflow/step-handoff-report.md`。报告必须区分：已生成、已修改、仅建议、待确认、未执行。不能把建议路径说成已生成文件，也不能把工具不可用说成校验通过。

## 状态更新规则

`workflow-state.json` 的 `completed_steps` 只记录门禁通过且所需审批完成的阶段；`last_completed_outputs` 记录真实存在的文件路径；`pending_approvals` 与 `blocked_items` 未清空时，`scripts/next-step.py` 不得建议越过阻断阶段。
