# Prompt：详细设计、接口与测试设计

```text
执行 `@detailed-design`，Change：<change-id>。

提案需求与 AC：<proposal-spec-and-ac-paths>
UI 基线：openspec/changes/<change-id>/design/figma-audit.md（目标框架/转码说明、token 实际值/PAGE 规格/状态）、design/figma-code/（06 已按总体技术选型转码的目标框架设计代码）与 design/figma-layout.csv（断言映射；07 填满 route/dom_selector；默认离线消费，版本变化/歧义时按页重读）；同时读取 docs/architecture/technology-decisions.md 确认目标框架一致
初始追踪：由本阶段初始化 openspec/changes/<change-id>/traceability.csv（PAGE→AC + API/测试）
项目基线：<baseline-paths>

先读 `docs/product/BASELINE-BRIEF.md`，再按受影响设计域读取具体架构/数据/API/前端/测试基线，不要求逐文件全量阅读。把设计写入唯一的 `design.md`，至少包含五节：`## 设计决策`、`## 接口设计`、`## 前端详细设计`、`## 后端详细设计`、`## 测试设计`。每节若整体不适用写 `N/A + 理由`，否则必须包含规定的子节。

方法与工具（强制）：
- 先运行 `openspec status --change <id>` 与 `openspec instructions design --change <id> --json`，读取当前 OpenSpec design 指引和已批准 specs；设计不得反向覆盖已批准行为。
- 使用 Superpowers `brainstorming` 对关键设计取舍（数据模型、接口形态、接口边界、现有代码变更、状态流转、测试策略）做方案比较，记录备选、取舍理由和未决项；必须覆盖“现有功能/新功能/代码地址/第三方接口”四个主题。技能不可用时执行等价比较步骤并说明。
- 使用 Superpowers `writing-plans` 把已批准 spec/AC 转成设计任务分解与测试计划，对应 `### 设计任务分解与接口范围` 与 `## 测试设计`；技能不可用时执行等价拆解步骤。
- 阶段结束必须显式运行 `openspec validate <change-id> --strict`，不能只依赖 `check-change.sh` 的内部调用。

`## 设计决策` 必须含 `### 范围与非目标`、`### 关键决策与权衡`、`### 现有代码变更影响`、`### 设计任务分解与接口范围`、`### 设计缺口与准入结论`；先冻结共享接口契约，再细化前端/后端，未决决策写责任人与截止条件。现有代码变更沟通（强制）：先问本 Change 是修改现有功能代码，还是新功能开发；若修改现有功能代码，要求代码地址（仓库/路径/分支/commit），实际探索相关文件/类/函数/数据结构/测试/迁移，写入 `### 现有代码变更影响`，逐项登记文件/类/函数/接口/表/测试、修改策略、兼容性、迁移/回滚、风险与验证方式；代码不可访问时标记 BLOCKED。若是新功能开发，写 `N/A + 理由`。第三方接口沟通（强制）：与 03 的第三方接口清单核对；每个第三方接口在 `design/interface-catalog.csv` 建 `THIRD_PARTY_API` 行，记录 provider、协议、鉴权、输入/输出、错误、超时/重试/幂等、SLA/配额、沙箱、数据共享/隐私、test_ids、owner；测试在 `test-cases.csv` 的 `interface_ids`/`fakes_env` 中覆盖沙箱、模拟器或人工验证。`## 接口设计` 必须含 `### 接口清单`、`### 接口边界清单`、`### 契约与错误语义`、`### 接口追踪`。`### 接口清单` 生成 `api/openapi.yaml`，定义稳定 operationId、路径/方法、鉴权、请求/响应 schema（类型/必填/范围/枚举/格式/分页）、示例、错误 envelope、权限、幂等/并发冲突与版本兼容；列出各 operationId 需要的 IO 类型（DB/文件/Feign/Redis/MQ/Search）；无 API 时写 `x-api-scope: none`，接口追踪写 operationId → PAGE/EVT/AC 并同步 traceability。`### 接口边界清单` 必须覆盖本 Change 的全部跨边界接口：HTTP API、App↔Native（uni-app/Flutter/React Native/原生桥接）、App↔Device、Backend↔Third-party、Backend↔IoT、异步事件、文件/对象存储。每条接口记录 interface_id、类型、source/target、协议、operation/方法、输入/输出契约、鉴权、错误语义、timeout/retry/idempotency、versioning、test_ids、owner，并写入 `design/interface-catalog.csv`。若总体选型为 uni-app/Flutter/React Native/原生 App，必须至少有一条 `NATIVE_BRIDGE` 行，并运行 `python scripts/check-interface-catalog.py --change <change-id> --strict --require-native`；否则运行 `--strict`。无跨边界接口时，`### 接口边界清单` 写 `N/A + 理由`，并在 evidence 把 `design/interface-catalog.csv` 标记 `n/a` + `waiver_reason`。接口问题清单至少询问：端形态/跨端方案、原生插件与 JS Bridge、设备协议、第三方平台、离线/弱网/权限降级、同步/异步、文件/对象存储、版本兼容与测试替身/真机。

`## 前端详细设计` 必须含 `### 路由与组件树`、`### 设计令牌与实现映射`、`### PAGE→BLOCK→Figma 规格`、`### PAGE→BLOCK→组件映射`、`### 组件职责与状态`、`### 事件处理`、`### 状态覆盖`、`### 测试映射`、`### 响应式与视口规则`、`### 页面几何与保真断言`。涉及 UI 时必须读取 `figma-audit.md` 的目标框架/转码说明与 token **实际值**、每 PAGE 区块规格，以及 `design/figma-code/` 与 `design/figma-layout.csv`；`### 设计令牌与实现映射` 逐行写 Figma 值 → CSS 变量/目标组件库主题/字体（Vue 栈为 Element Plus + Noto Sans SC 等字体栈），并声明全局 token 文件路径（供 `check-design-tokens.py` 比对）；`### PAGE→BLOCK→组件映射` 必须以 `figma-code/` 的目标框架设计代码为基线，写明 PAGE/BLOCK → 设计代码文件 → 落地组件路径，并只登记必要的业务化适配（路由、API、事件、状态、权限），不得重新设计样式/布局/文案；确需视觉偏差时登记 `UI-DEVIATION`（原因、影响、审批人）并同步更新 `figma-layout.csv` 与 `## 差异与待确认`。`### PAGE→BLOCK→Figma 规格` 逐 PAGE 写真实尺寸/间距/padding/gap/圆角/字体与状态，不得只写“顶栏、侧栏、列表”。PAGE 清单与 PAGE ID 以 figma-audit.md 为准并由 06 冻结，不得新增或重命名 PAGE；Figma 未定义的弹窗/抽屉/状态必须新增 Figma 画板，或以 `UI-DERIVED` 记录具体视觉规格、审批人与理由，不得悄悄臆造。**必须把 `figma-layout.csv` 每行的 `route` 与 `dom_selector` 填满**，并在 `### 响应式与视口规则` 明确 1440×900 基准与 ≥1440 / <1440 的规则。默认离线消费导出包，仅在文件版本变化或页面有歧义时重新读取 Figma（串行、按页批量，避免限流）。写组件树、职责/Props/Emits、跨页面参数、状态流转、API 调用、加载/错误/空/成功/禁用/无权限状态、表单校验/防重复提交和测试 ID；区分服务器/本地 UI/URL 状态，覆盖 figma-audit.md 的 PAGE 结构与关键区块/可访问性；每个交互事件写处理函数输入/返回/副作用/失败路径并关联 operationId；不得凭截图或臆造。**不使用参考截图或实现截图。**

`## 后端详细设计` 必须含 `### API 执行链`、`### API→IO 映射`、`### IO 契约`、`### 数据模型与迁移`、`### 非数据库 IO`、`### 领域类型与方法`、`### 错误与一致性`、`### 共享关注点`、`### 测试覆盖`、`### 未决决策`。覆盖 Controller → 应用服务 → 领域操作、DDL/Mapper/SQL、事务/锁/幂等、File/Feign/Redis/MQ/Search 等非数据库 IO、错误映射、审计/日志/指标/trace、数据隐私/保留/脱敏、性能、迁移 forward/rollback/backward compatibility/deploy order 和 TEST ID；每个 operationId 必须在 `design/api-io-mapping.csv` 映射到至少一个 IO ID，所有 IO 在 `design/io-catalog.csv` 登记契约与测试 ID；timeout/retry 不适用时写 0/none，不要写 N/A。

`## 测试设计` 必须含 `### 测试策略`、`### 测试环境与替身`、`### 人工验证`。把每条 AC 映射到 unit/component/contract/integration/E2E/人工测试，并逐行写入 `design/test-cases.csv`（TEST ID → AC/PAGE/API/IO，BLOCK 可选，含前置条件、数据、步骤、预期、失败注入、替身/环境、人工原因、自动化、清理与状态）；每个 AC、页面、operationId、IO 至少一个 TEST；断言验证用户可观察行为或业务不变量，不可只断言方法被调用；外部依赖写替身/集成环境。

初始化并合并 `traceability.csv`：本阶段建立 PAGE→AC 追踪并追加 API 追踪、TEST ID 与测试映射；API 行使用 `source_type=API, source_id=<operationId>, target_type=PAGE/AC, target_id=<ID>`。每条 AC、页面、operationId、IO、接口边界至少一个 TEST（BLOCK 可选），否则写 `N/A + 原因`。确保设计项均关联 REQ/AC/PAGE/EVT 或写明 N/A 原因，前后端字段与 OpenAPI 一致。完成后运行 `bash scripts/check-change.sh <change-id>`、`bash scripts/check-design-assets.sh <change-id> --strict --lint-api`、`python scripts/check-design-sections.py --change <change-id>`、`python scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict`、`python scripts/check-test-cases.py --change <change-id> --strict`，有 API 时再运行 `python scripts/check-api-traceability.py --change <change-id>`，有跨边界接口时运行 `python scripts/check-interface-catalog.py --change <change-id> --strict`，并显式运行 `openspec validate <change-id> --strict`；退出码必须为 0。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：重新核验 `design/baseline-impact.md` 与当前 `baseline-status.md`；任何基线版本变化都要写明 `NO_IMPACT` 或 `REBASE_REQUIRED`。违反基线的方案必须先走 ADR/基线修订审批，批准后才能冻结详细设计。完成复核后运行 `python3 scripts/check-baseline-impact.py <change-id> --strict` 与 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：本阶段为功能级，必须填写真实 Change ID。
- 加载 Skill：按当前 Agent 的真实机制加载 `.claude/skills/detailed-design/SKILL.md`，不能只把 Skill 名字当普通文本。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`；无法加载时明确报告并按本 Prompt 执行。
- **Superpowers：** 必须使用 `brainstorming` 比较关键设计取舍，并使用 `writing-plans` 完成设计任务与测试计划拆解；先确认真实安装与可调用方式，不可用时说明并执行等价步骤，不能把“可用”当作“已使用”。
- **OpenSpec：** 运行 `openspec status --change <id>`、`openspec instructions design --change <id> --json`，读取已批准 specs/design；阶段结束运行 `openspec validate <change-id> --strict`。发现需求变化时暂停并回到规格更新，不能只改设计文档。命令须真实执行并报告退出码/结果。
- **状态与门禁：** 仅在产物写入指定路径且脚本检查通过后更新 `workflow-state.json`；遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用工具、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="detailed-design"` 的记录。

- 输入核验：已批准 proposal/specs/user-stories/design.md；涉及 UI 时必须读取 `figma-audit.md`（目标框架/转码说明、token 实际值、文字样式、PAGE 规格、状态决策）、`design/figma-code/`（目标框架设计代码）与 `design/figma-layout.csv`（断言映射）并核对文件版本；`docs/architecture/technology-decisions.md`（确认目标框架与 06 转码一致）；Figma 评审稿是视觉与结构权威，视觉规范取 `docs/architecture/frontend-conventions.md` 第 9 节；业务流程/数据对象/RD/业务规则/验收政策；角色权限矩阵、ID 约定与未决问题（role-permission-matrix、id-conventions、open-questions，open-questions 只读）；`docs/product/BASELINE-BRIEF.md` 与按需读取的架构基线；`design/baseline-impact.md`、`baseline-status.md`、`baseline-binding.json`。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design.md（统一设计五节，含 `### 响应式与视口规则` 与 `### 页面几何与保真断言`）；`design/figma-layout.csv`（每行 `route`/`dom_selector` 已填）；`design/test-cases.csv`（TEST 矩阵）；条件适用时 `api/openapi.yaml`、`design/api-io-mapping.csv`、`design/io-catalog.csv`；`traceability.csv`（合并页面/API/测试映射）；`design/baseline-impact.md`（07 更新设计复核结论）；`design/baseline-binding.json`（07 写入设计证据）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：统一设计决策、接口契约、前后端实现约束、测试用例矩阵、`figma-layout.csv` 断言映射与唯一追踪矩阵；08 阶段据此实现并运行几何断言。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- **阶段边界（强制）：** 阶段完成 ≠ 可进入下一阶段。产物写完、检查通过后运行 `python scripts/workflow.py request-review --step 07-detailed-design --summary "<送审摘要>"`（流程冻结为待评审），按交接模板展示报告后**立即结束回合**；用户明确回复“评审通过 07-detailed-design”前，禁止读取/执行下一阶段 Prompt/Skill、禁止创建下一阶段产物。批准后运行 `python scripts/workflow.py approve --step 07-detailed-design --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>`，再执行 `transition`。不得自行填写 approver/approved_at，不得把产物完成或自检通过当作批准。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。

## 阶段结束审计（必须执行）

- `design.md` 五节齐全；无 API/前端/后端的节写 N/A + 理由。
- 每个 operationId 至少映射一个 IO；每条 AC 至少映射一个测试或 N/A + 理由；`traceability.csv` 是唯一追踪聚合文件。
- 前后端字段、错误码、权限与 OpenAPI 一致；设计项均关联 REQ/AC/PAGE/EVT 或写明 N/A 原因。
- 方法证据：交接报告与阶段 evidence 的 checks 必须记录 `superpowers-methods`（brainstorming/writing-plans 的实际加载、产出与证据）和 `openspec-validate-design`（status/instructions/validate 的命令、退出码与日志）。阶段 evidence 必须写 `methods`：`brainstorming` 至少 4 个问题、2 个备选、1 个决策，且覆盖“现有功能/新功能/代码地址/第三方接口”四个主题；`writing-plans` 至少 1 个决策；结果落点写 `design.md` 的 `### 关键决策与权衡`、`### 现有代码变更影响` 与 `### 设计任务分解与接口范围`；运行 `python scripts/check-method-evidence.py --step 07-detailed-design --evidence <evidence.json>`。
- 运行 `bash scripts/check-change.sh <change-id>`、`bash scripts/check-design-assets.sh <change-id> --strict --lint-api`、`python scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict` 与 `openspec validate <change-id> --strict`，退出码必须为 0。
