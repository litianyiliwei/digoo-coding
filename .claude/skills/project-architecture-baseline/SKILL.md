---
name: project-architecture-baseline
description: 项目总体架构设计。合并架构、数据/领域与公共契约基线，输出数据流转与逻辑 ERD，并在阶段结束审计中冻结基线。
---

# 项目总体架构设计

## 何时使用
当流程进入“项目总体架构设计”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
已批准的 `docs/product/requirements-analysis.md`、`workflows.md`、`data-objects.csv`、`rd-matrix.csv`、`business-rules.md`、`glossary.md`、`acceptance-policy.md`、`open-questions.md`（只读）；`BASELINE-BRIEF.md`、`role-permission-matrix.csv`、`change-sizing.md`、`decisions.md`、`assumptions.md`、`id-conventions.md`、`BASELINE-INDEX.md`（常驻基线，先读简报）；现有仓库结构/技术约束；非功能需求；用户/技术负责人明确的技术选型偏好（本阶段必须显式询问，不得默认或自行拍板）。

## 执行流程
1. **强制技术选型与平台边界访谈（前置门禁）：** 在产出任何技术决策前，必须向用户逐项询问希望采用的选型及其约束，至少覆盖：后端语言/框架、前端框架/UI 组件库、数据库与存储、缓存/消息/任务调度、部署与运行环境（云/自托管/容器/信创）、认证与权限、构建/测试/CI 工具、既有系统集成、许可与成本、团队熟悉度与运维能力。还必须完成平台与集成边界访谈：客户端形态（Web/H5、微信小程序、Android、iOS、HarmonyOS、PDA/手持机、平板、桌面）；跨端方案（原生双端、Flutter、React Native、uni-app、Taro、混合）；若选 uni-app，逐项记录目标平台、原生插件清单、JS Bridge 接口（名称/参数/返回/错误/回调/超时）、平台差异矩阵、权限拒绝/降级、离线缓存/同步冲突、推送/深链、热更新/商店合规、插件许可/版本；设备/物联网协议（BLE/Modbus/LoRa/MQTT/HTTP）；第三方平台（GIS、天气、支付、短信、实名、政府溯源、物流）；接口边界（UI↔API、App↔Native、App↔Device、Backend↔Third-party、Backend↔IoT、异步事件、文件/对象存储）。每条边界记录协议、鉴权、契约、错误语义、超时/重试/幂等、版本兼容、测试/真机、责任人。先给出候选方案与权衡，再请用户确认；用户表示“无偏好”时也必须记录，并把推荐方案列为待确认候选。结果写入 `technology-decisions.md` 的“平台与集成边界访谈记录”，并在 `api-conventions.md` 增加“跨边界接口与集成约定”、`frontend-conventions.md` 增加“多端与原生能力”、`data-flows.md` 增加客户端/原生/设备数据流。还必须完成系统来源与现有代码/第三方接口访谈：明确新系统、基于现有系统二开，还是混合；若基于现有系统二开，要求代码地址（仓库 URL/本地路径/分支/commit），实际探索代码结构与技术栈、模块边界、API/数据模型、构建/测试/发布命令、既有规范与技术债，写入 `technology-decisions.md` 的“现有系统二开约束”，并转换为 `constraint-registry.json` 的 `LEGACY-*` 约束（含来源章节、等级、范围、执行方式、责任人）；代码不可访问时 BLOCKED，不得凭记忆假设。无论是否二开，都必须列出依赖的第三方接口：提供方、用途、协议、鉴权、SLA/配额、沙箱/测试账号、审批、数据共享/隐私、错误/超时、责任人，写入“第三方接口依赖清单”、`data-flows.md` 的 EXTERNAL 数据流和 `api-conventions.md` 的“第三方接口与集成约定”；无第三方接口写 NONE + 理由。
2. 绘制系统上下文、模块/容器、部署和主要信任边界；技术决策写 ADR，记录用户确认结果、确认人和日期。
3. **数据流转（强制）：** 按 `DF-xxx` 登记跨系统/跨模块/关键业务的同步请求、异步消息、数据读写、外部调用、事务边界、失败与补偿；每条数据流引用相关 FLOW/NODE/DO 与 RD 矩阵条目。
4. **数据与领域基线（并入本阶段）：** 识别核心概念、领域边界、实体/值对象、生命周期和数据所有权；绘制逻辑 ERD，标注关系、基数、跨领域引用；定义命名、ID、审计字段、时间、删除、并发版本与保留规范；明确事务边界、唯一性/完整性规则、并发控制和一致性策略。逻辑 ERD 不是物理 DDL。
5. **公共契约基线（并入本阶段）：** 约定 API 版本、operationId、认证授权、错误模型、分页、幂等和兼容策略；前端目录、路由、API 调用层、状态管理、表单与错误展示原则；测试层级、契约测试、集成测试、E2E、测试数据与环境策略；安全扫描、代码规范、日志隐私、可访问性和性能门禁。
6. 区分强制规则、推荐规则和可申请例外的规则；区分稳定约束与提案级字段细节，共享领域边界改变必须发起基线变更评审。
7. 交叉检查术语、角色权限、系统边界、核心领域、数据流转、API 错误模型和测试策略的一致性；按阻断/高/中/低风险列出矛盾、缺失和未决事项。
8. **阶段结束审计与冻结（强制）：** 运行 `scripts/check-required-files.sh --strict`；核对 Manifest 与 Constraint Registry；由负责人执行 `baseline-governance.py freeze`，再执行 `audit --require-frozen`；审计报告写入 `docs/project/baseline-audit-report.md`。存在阻断项时不得建议冻结。

## 输出
`docs/architecture/system-context.md`、`domain-boundaries.md`、`containers-and-deployment.md`、`data-flows.md`（数据流转 + 客户端/原生/设备数据流 + 第三方 EXTERNAL 数据流）、`logical-erd.md`、`technology-decisions.md`（含技术选型访谈记录、平台/集成边界访谈记录、现有系统二开约束、第三方接口依赖清单）、`api-conventions.md`（含跨边界接口与集成约定、第三方接口与集成约定）、`frontend-conventions.md`（含多端与原生能力）、`test-strategy.md`（含原生桥接/设备/第三方测试策略）、`docs/adr/README.md`、`baseline-status.md`、`baseline-manifest.json`、`constraint-registry.json`（含 LEGACY-*/EXT-* 约束）、`docs/project/baseline-audit-report.md`。

## 质量与安全边界
图和文字对同一边界的描述一致；选择有理由；关键非功能需求能被后续验证；数据流转引用闭合；未显式询问用户技术偏好或用户尚未确认的选型，不得标记为已批准；未决项必须写明负责人和阻塞条件，阶段不得完成。审批状态有负责人/证据；存在阻断项时不得冻结。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- Figma MCP 的输入必须基于实际可访问的链接、节点和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-required-files.sh --strict`；`python scripts/check-architecture-baseline.py --strict`（现有系统二开约束/第三方接口依赖清单/LEGACY-*/EXT-*）；`scripts/baseline-governance.py audit --require-frozen`

## 实际工具调用要求

- **Superpowers：** `brainstorming` 的 stage-scoped 模式用于比较架构、平台与集成边界备选，澄清领域边界和一致性取舍，并记录问题/备选/决策；问题/决策必须覆盖“新系统/现有系统/代码地址/第三方接口”四个主题；结论写入 `technology-decisions.md` 等阶段既有产物，不另写独立设计文档。必须按当前宿主 Agent 的真实机制检查、读取或调用技能；不可用时用 `mode=equivalent` 并写 `reason`。阶段 evidence 必须写 `methods` 并运行 `python scripts/check-method-evidence.py --step 03-project-architecture-baseline --evidence <evidence.json>`。
- **OpenSpec：** 检查既有 specs、架构文档和 ADR；若 CLI 可用，执行 `openspec list --specs` 和 `openspec list --changes`，核对基线与现有规格的关系。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="project-architecture-baseline"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准的 docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md、open-questions.md（只读）；docs/product/BASELINE-BRIEF.md、role-permission-matrix.csv、change-sizing.md、decisions.md、assumptions.md、id-conventions.md、BASELINE-INDEX.md（常驻基线）；现有仓库结构/技术约束；非功能需求；用户/技术负责人技术选型偏好。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** docs/architecture/system-context.md；domain-boundaries.md；containers-and-deployment.md；data-flows.md；logical-erd.md；technology-decisions.md；api-conventions.md；frontend-conventions.md；test-strategy.md；docs/adr/README.md；baseline-status.md；baseline-manifest.json；constraint-registry.json；docs/project/baseline-audit-report.md。按模板生成并落盘。
- **下游交接：** 冻结的项目总体架构基线、数据流转、逻辑 ERD、公共契约/测试策略、ACTIVE 约束目录、审计报告与审批记录。明确指出阶段 04/05 消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。

## 阶段结束审计与冻结（强制）

- `docs/architecture/baseline-manifest.json` 是版本/状态/审批/文件哈希的机器权威来源；`constraint-registry.json` 是稳定约束 ID 的机器权威来源；`baseline-status.md` 仅为人类可读镜像。
- 冻结前逐条审查所有约束，确认来源章节、等级、适用范围、执行方法和审批人；正式批准的规则设为 ACTIVE，未决规则保持 DRAFT；不得由 AI 填造真实审批身份。
- **初次冻结顺序：**
  1. 完成 Manifest 的 project_id、总体版本、六个域的文件清单；各域填写 owner/approver/approved_at/effective_revision/approval_evidence，并在各域确已批准后设为 `FROZEN`；总体 `status` 暂时保持 `DRAFT`。
  2. 完成 Constraint Registry：逐条审查 ID、来源章节、等级、范围、执行类型和 validator；正式批准的规则设为 `ACTIVE` 并填写 owner/approved_by/approved_at；明确废弃的设为 `RETIRED`；至少有一条 ACTIVE 约束。
  3. 真实审批证据文件落盘后执行 `python scripts/baseline-governance.py refresh-hashes`。
  4. 由负责人执行 `python scripts/baseline-governance.py freeze --approved-by <负责人> --approved-at <ISO日期> --evidence <审批证据路径>`。
  5. 再执行 `python scripts/baseline-governance.py audit --require-frozen`；通过后才能提交阶段 03 Evidence。
- 阶段 03 转换的 Evidence 必须包含 Manifest 与 Constraint Registry 两个输出；`workflow.py transition` 会再次进行冻结门禁。
- 审计报告必须区分“基线正文已更新”“Change 局部记录”“待批准修订”，并检查 OpenSpec 主规格与项目设计基线是否一致。
- 冻结后不得直接改文件；必须先 `open-amendment`。

## 阶段边界与评审停等（强制）

- 开始前运行 `python scripts/workflow.py check-entry --step 03-project-architecture-baseline [--change-id <id>]`；退出码非 0 时立即停止并报告，不得绕过。
- 产物写完、检查通过只代表可送审：运行 `python scripts/workflow.py request-review --step 03-project-architecture-baseline --summary "<摘要>"`，按 `templates/workflow/step-handoff-report.md` 展示交接报告后**立即结束回合**；禁止在同一会话读取/执行下一阶段 Prompt/Skill 或创建下一阶段产物。
- 只有用户明确回复“评审通过 03-project-architecture-baseline”后，才可运行 `python scripts/workflow.py approve --step 03-project-architecture-baseline --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>` 并执行 `transition`。不得自行填写 approver/approved_at，不得把自检通过当作批准。
- `pending_approvals` 非空时禁止推进；`workflow-state.json` 只能通过 `check-entry`/`request-review`/`approve`/`transition` 等命令管理，禁止直接编辑。
- Claude Code 的 PreToolUse hook 会拒绝写入当前阶段之后的阶段产物（共享产物除外）与直接编辑状态文件；待评审期间同样拒绝。遇到拒绝必须停止并说明，不得更换路径或禁用 hook 绕过。
