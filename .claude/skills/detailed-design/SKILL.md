---
name: detailed-design
description: 详细设计、接口与测试设计。合并设计总控、OpenAPI、前端/后端详细设计与测试设计；统一写入 design.md 五节，测试用例写入 test-cases.csv，并维护唯一追踪矩阵。
---

# 详细设计、接口与测试设计

## 何时使用
当流程进入阶段 07「详细设计、接口与测试设计」时加载本 Skill。一次处理一个 Change；不要提前实现。

## 输入
已批准的 proposal/specs/user-stories、初始 `design.md`；本阶段初始化 `traceability.csv`；涉及 UI 时必须读取 `design/figma-audit.md`（目标框架/转码说明、token 实际值、文字样式、PAGE 规格、状态决策）、`design/figma-code/`（06 已按总体技术选型转码的目标框架设计代码）与 `design/figma-layout.csv`（断言映射）并核对文件版本；同时读取 `docs/architecture/technology-decisions.md`，确认目标框架与 06 转码一致；Figma 评审稿是视觉与结构权威；视觉规范取自已冻结的 `docs/architecture/frontend-conventions.md` 第 9 节；项目业务流程/数据对象/RD/业务规则/验收政策；按设计域按需读取的项目架构基线；当前 Change 的 `design/baseline-impact.md` 与 `design/baseline-binding.json`。默认离线消费导出包，仅在版本变化或页面有歧义时按页批量重读 Figma。**不使用参考截图或实现截图。**

## 方法与工具（强制）

- 先运行 `openspec status --change <id>` 与 `openspec instructions design --change <id> --json`，读取当前 OpenSpec design 指引和已批准 specs；`design.md` 不能反向覆盖已批准行为。
- 使用 Superpowers `brainstorming` 对关键设计取舍（数据模型、接口形态、状态流转、测试策略）做方案比较，记录备选、取舍理由与未决项。
- 使用 Superpowers `writing-plans` 把已批准 spec/AC 转成设计任务分解与测试计划，对应 `### 设计任务分解与接口范围` 与 `## 测试设计`。
- 技能不可用时执行等价步骤并说明；阶段结束必须显式运行 `openspec validate <change-id> --strict`，不能只依赖 `check-change.sh` 内部调用。
- 交接报告与阶段 evidence 的 checks 记录 `superpowers-methods`（技能加载、产出、证据）和 `openspec-validate-design`（命令、退出码、日志）。

## 执行流程

1. **统一设计范围（`## 设计决策`）**：必须含 `### 范围与非目标`、`### 关键决策与权衡`、`### 设计任务分解与接口范围`、`### 设计缺口与准入结论`；写设计范围、非目标、关键权衡、接口范围草案、任务分解、设计缺口与准入结论；先冻结共享接口契约，再细化前端/后端，未决决策必须有责任人与截止条件，任务从设计逐项分解。先读 `BASELINE-BRIEF.md`，再按受影响设计域读取具体基线文件，不要求逐文件全量阅读。
2. **接口设计（有 API 时，`## 接口设计`）**：必须含 `### 接口清单`、`### 契约与错误语义`、`### 接口追踪`；列出 operationId、路径/方法、鉴权、请求/响应 schema（类型/必填/范围/枚举/格式/分页）、示例、错误 envelope、权限、幂等/并发冲突与版本兼容；列出各 operationId 需要的 IO 类型（DB/文件/Feign/Redis/MQ/Search），供后端映射。无 API 时写 `x-api-scope: none` 并说明理由。`### 接口追踪` 写 operationId → PAGE/EVT/AC，并在 `traceability.csv` 建 API 追踪行。接口测试至少覆盖成功、边界、校验、认证、授权、404/冲突、依赖失败和幂等；OpenAPI 提供请求/响应示例。
3. **前端详细设计（涉及 UI，`## 前端详细设计`）**：必须含 `### 路由与组件树`、`### 设计令牌与实现映射`、`### PAGE→BLOCK→Figma 规格`、`### PAGE→BLOCK→组件映射`、`### 组件职责与状态`、`### 事件处理`、`### 状态覆盖`、`### 测试映射`、`### 响应式与视口规则`、`### 页面几何与保真断言`；读取 `figma-audit.md` 的目标框架/转码说明与 token 实际值、每 PAGE 区块规格，以及 `figma-code/` / `figma-layout.csv`，逐行写 Figma 值 → CSS 变量/目标组件库主题/字体（Vue 栈为 Element Plus + Noto Sans SC），禁止只写变量名；`### PAGE→BLOCK→组件映射` 必须以 `figma-code/` 的目标框架设计代码为基线，写明 PAGE/BLOCK → 设计代码文件 → 落地组件路径，并只登记必要的业务化适配（路由、API 调用、事件、状态、权限），不得重新设计样式、布局或文案；确需视觉偏差时登记 `UI-DEVIATION`（原因、影响、审批人）并同步更新 `figma-layout.csv` 与 `## 差异与待确认`。每 PAGE 写真实尺寸/间距/padding/gap/圆角/字体与状态；PAGE 清单与 PAGE ID 以 figma-audit.md 为准并由 06 冻结，不得新增或重命名 PAGE；Figma 未定义的弹窗/抽屉/状态必须新增 Figma 画板，或以 `UI-DERIVED` 记录视觉规格、审批人与理由；默认离线消费导出包，仅在版本变化或歧义时按页重读 Figma。**必须把 `figma-layout.csv` 每行的 `route` 与 `dom_selector` 填满**（选择器优先使用稳定的 `data-test` / `data-figma-node` 属性），并在 `### 响应式与视口规则` 明确 1440×900 基准、≥1440 与 <1440 的规则（比例伸缩/固定宽度/断点）。写组件树、职责/Props/Emits、跨页面参数、状态流转、API 调用、加载/错误/空/成功/禁用/无权限状态、表单校验/防重复提交和测试 ID；区分服务器状态/本地 UI 状态/URL 状态，覆盖 figma-audit.md 的 PAGE 结构与关键区块/可访问性；每个交互事件要写处理函数输入/返回/副作用/失败路径并关联 operationId；不得凭截图或臆造。
4. **后端详细设计（`## 后端详细设计`）**：必须含 `### API 执行链`、`### API→IO 映射`、`### IO 契约`、`### 数据模型与迁移`、`### 非数据库 IO`、`### 领域类型与方法`、`### 错误与一致性`、`### 共享关注点`、`### 测试覆盖`、`### 未决决策`。覆盖 Controller → 应用服务 → 领域操作、DDL/Mapper/SQL、事务/锁/幂等、File/Feign/Redis/MQ/Search 等非数据库 IO、错误映射、审计/日志/指标/trace、数据隐私/保留/脱敏、性能、迁移 forward/rollback/backward compatibility/deploy order 和 TEST ID；每个 operationId 必须在 `design/api-io-mapping.csv` 映射到至少一个 IO ID，所有 IO 在 `design/io-catalog.csv` 登记契约与测试 ID；timeout/retry 不适用时写 0/none，不要写 N/A（严格门禁把 N/A 视为未填）。
5. **测试设计（`## 测试设计` + `design/test-cases.csv`）**：必须含 `### 测试策略`、`### 测试环境与替身`、`### 人工验证`。把每条 AC 映射到 unit/component/contract/integration/E2E/人工测试，并逐行写入 `design/test-cases.csv`（TEST ID → AC/PAGE/API/IO，BLOCK 可选，含前置条件、数据、步骤、预期、失败注入、替身/环境、人工原因、自动化、清理与状态）。每个 AC、页面、operationId、IO 至少一个 TEST；断言必须验证用户可观察行为或业务不变量，不可只断言方法被调用；外部依赖写替身/集成环境，TEST ID 写入唯一 `traceability.csv`。
6. **一致性检查**：每个设计项关联 REQ/AC/PAGE/EVT 或写明 N/A + 理由；前后端字段与 OpenAPI 一致；不得各自发明字段。发现基线冲突时记录并走 ADR/基线修订，不得静默绕过。

## 输出
`design.md`（统一设计五节）、`design/figma-layout.csv`（07 填满 route/dom_selector）、`design/test-cases.csv`（测试用例矩阵）、`api/openapi.yaml`（条件适用）、`design/api-io-mapping.csv`、`design/io-catalog.csv`（条件适用）、`traceability.csv`（唯一追踪聚合文件）、`design/baseline-impact.md`（07 更新设计复核结论）、`design/baseline-binding.json`（07 写入设计证据）。

## 质量与安全边界
`design.md` 必须包含 `## 设计决策`、`## 接口设计`、`## 前端详细设计`、`## 后端详细设计`、`## 测试设计` 五节；每节若整体不适用，写 `N/A + 理由`，否则必须包含上文列出的固定子节。涉及 UI 时前端节必须引用 `figma-audit.md` 的目标框架/转码说明与 token 实际值、`figma-code/` 的目标框架设计代码与节点几何、`figma-layout.csv` 的断言映射，并填满每行 `route`/`dom_selector`；目标框架必须与 `technology-decisions.md` 一致，缺少实际值/断言映射/框架一致性不得进入实现；06 批准的 Figma 评审稿是 UI 最终权威，前端设计必须按其完成，样式/布局/文案不得在 07 重新设计。每个 operationId 至少映射一个 IO；每条 AC、每个页面、每个 operationId、每个 IO 至少映射一个 TEST（BLOCK 可选，不适用写 N/A + 理由）。未知项写 PENDING + 原因，不猜测。**不使用截图作为设计输入或验收依据。**

## 与 OpenSpec / Superpowers 的边界
- specs 是外部可观察行为的唯一来源；`design.md` 与详细设计实现细节不能反向覆盖已批准行为。
- 必须使用 Superpowers `brainstorming` 比较关键设计取舍，并使用 `writing-plans` 完成设计任务与测试计划拆解；只有确认真实安装且实际调用后才声称使用。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`bash scripts/check-change.sh <change-id>`；`bash scripts/check-design-assets.sh <change-id> --strict --lint-api`；`python scripts/check-design-sections.py --change <change-id>`；`python scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict`；`python scripts/check-test-cases.py --change <change-id> --strict`；有 API 时 `python scripts/check-api-traceability.py --change <change-id>`；`openspec validate <change-id> --strict`；`python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。

## 实际工具调用要求
- **Superpowers：** 必须使用 `brainstorming` 比较关键设计取舍，并使用 `writing-plans` 拆解设计任务与测试计划；不可用时说明并执行等价方案比较/拆解步骤，不能把“可用”当作“已使用”。
- **OpenSpec：** 运行 `openspec status --change <id>`、`openspec instructions design --change <id> --json` 并读取已批准规格/design；阶段结束运行 `openspec validate <change-id> --strict`。发现需求变化时暂停并回到规格更新，不能只改设计文档。
- **状态更新：** 仅在产物落盘且门禁通过后更新 `workflow-state.json`。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="detailed-design"` 的契约记录。

- **本阶段输入：** 已批准 proposal/specs/user-stories/design.md；涉及 UI 时必须读取的 `figma-audit.md`（目标框架/转码说明、token 实际值、文字样式、PAGE 规格、状态决策）、`design/figma-code/`（目标框架设计代码）与 `design/figma-layout.csv`（断言映射）并核对文件版本；`docs/architecture/technology-decisions.md`（确认目标框架与 06 转码一致）；Figma 评审稿是视觉与结构权威，视觉规范取 `docs/architecture/frontend-conventions.md` 第 9 节；项目业务流程/数据对象/RD/业务规则/验收政策；角色权限矩阵、ID 约定与未决问题（role-permission-matrix、id-conventions、open-questions，open-questions 只读）；`docs/product/BASELINE-BRIEF.md` 与按需读取的架构基线；`design/baseline-impact.md`、`baseline-status.md`、`baseline-binding.json`。逐项核验存在、版本与批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** `design.md`（统一设计五节，含 `### 响应式与视口规则` 与 `### 页面几何与保真断言`）；`design/figma-layout.csv`（每行 `route`/`dom_selector` 已填）；`design/test-cases.csv`（TEST 矩阵）；`api/openapi.yaml`（条件适用）；`design/api-io-mapping.csv`、`design/io-catalog.csv`（条件适用）；`traceability.csv`（合并页面/API/测试映射）；`design/baseline-impact.md`（07 更新设计复核结论）；`design/baseline-binding.json`（07 写入设计证据）。
- **下游交接：** 统一设计决策、接口契约、前后端实现约束、测试方案与唯一追踪矩阵。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。

## 项目基线约束（只读继承）
- 执行前读取当前 Change 的 `design/baseline-impact.md` 与 `baseline-binding.json`；逐条约束须有 COMPLIANT 或 EXCEPTION_APPROVED 结论及设计证据。
- 基线版本变化必须记录 `NO_IMPACT` 或 `REBASE_REQUIRED`；发现冲突必须提出基线修订，受影响设计在审批前不得冻结。
- 通过前执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。
