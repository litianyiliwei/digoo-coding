# Prompt：项目总体架构设计

```text
执行 `@project-architecture-baseline`，Change：N/A。

需求业务梳理：<product-paths>
未决问题：<open-questions>
技术约束/环境：<constraints>
非功能要求：<nfr>

合并输出项目总体架构设计：系统上下文、领域边界、部署、数据流转、逻辑 ERD、技术选型决策、API/前端/测试公共契约，并在阶段结束审计中冻结项目基线。
技术要求：
1. 先做技术选型访谈，逐项询问并记录用户/技术负责人的确认人与日期；不得默认或自行假设。必须同时完成“平台与集成边界访谈”，与技术选型访谈同表记录：
   - 客户端形态：Web/H5、微信小程序、Android、iOS、HarmonyOS、PDA/手持机、平板、桌面；
   - 跨端方案：原生双端、Flutter、React Native、uni-app、Taro、混合；记录候选、取舍、确认人/日期；
   - 若选 uni-app：目标平台、原生插件清单、JS Bridge 接口（名称/参数/返回/错误/回调/超时）、平台差异矩阵、权限拒绝/降级、离线缓存/同步冲突、推送/深链、热更新/商店合规、插件许可/版本；
   - 设备/物联网：传感器、摄像头、无人机、农机、网关；协议 BLE/Modbus/LoRa/MQTT/HTTP；边缘/云同步；断网缓存；
   - 第三方平台：GIS/地图、天气、支付、短信、实名、政府溯源、物流；
   - 接口边界：UI↔API、App↔Native、App↔Device、Backend↔Third-party、Backend↔IoT、异步事件、文件/对象存储。
   每条边界记录：协议、鉴权、契约、错误语义、超时/重试/幂等、版本兼容、测试/真机、责任人；结果写入 `technology-decisions.md` 的“平台与集成边界访谈记录”，并在 `api-conventions.md` 增加“跨边界接口与集成约定”、`frontend-conventions.md` 增加“多端与原生能力”、`data-flows.md` 增加客户端/原生/设备数据流。
1a. 系统来源与现有代码/第三方接口访谈（强制）：明确是新系统、基于现有系统二开，还是混合。若基于现有系统二开，要求用户给出代码地址（仓库 URL/本地路径/分支/commit），实际探索代码结构与技术栈、模块边界、API/数据模型、构建/测试/发布命令、既有规范与技术债，写入 `technology-decisions.md` 的“现有系统二开约束”，并转换为 `constraint-registry.json` 的 `LEGACY-*` 约束（含来源章节、等级、范围、执行方式、责任人）；代码不可访问时标记 BLOCKED，不得凭记忆假设。无论是否二开，都必须列出依赖的第三方接口：提供方、用途、协议、鉴权、SLA/配额、沙箱/测试账号、审批、数据共享/隐私、错误/超时、责任人，写入“第三方接口依赖清单”、`data-flows.md` 的 EXTERNAL 数据流和 `api-conventions.md` 的“第三方接口与集成约定”；无第三方接口写 NONE + 理由。
2. 数据流转必须按 DF-xxx 完整登记：同步/异步、事务边界、失败与补偿，并引用 FLOW/NODE/DO/RD 条目。
3. 逻辑 ERD 必须覆盖 data-objects.csv 的业务数据对象与 rd-matrix.csv 的读写关系；区分逻辑模型与物理 DDL。
4. API/前端/测试公共契约只写跨功能复用规则；功能级 schema/页面/物理表留在 Change。测试策略必须说明原生桥接、设备、第三方边界的测试层级与真机/模拟器/替身策略。
5. 阶段结束审计：运行 `bash scripts/check-required-files.sh --strict`，并运行 `python scripts/check-architecture-baseline.py --strict`（校验“现有系统二开约束”“第三方接口依赖清单”、`LEGACY-*`/`EXT-*` 约束与第三方数据流/API 约定）；完成 baseline-status/manifest/registry，执行 `python scripts/baseline-governance.py refresh-hashes`、负责人 `freeze`，再执行 `python scripts/baseline-governance.py audit --require-frozen`；存在阻断项不得冻结。
6. 审计报告写入 docs/project/baseline-audit-report.md，区分已更新基线、Change 局部记录和待批准修订。
7. 方法证据：阶段 evidence 必须写 `methods`，至少记录 4 个平台/集成澄清问题、2 个备选方案、1 个决策，且问题/决策必须覆盖“新系统/现有系统/代码地址/第三方接口”四个主题；结果落点写 `docs/architecture/technology-decisions.md#现有系统二开约束` 或 `#1. 技术选型访谈记录`；运行 `python scripts/check-method-evidence.py --step 03-project-architecture-baseline --evidence <evidence.json>`。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：本阶段为项目级，写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的环境中使用 `@project-architecture-baseline`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 使用 `brainstorming` 的 stage-scoped 模式比较架构、平台与集成边界备选，记录问题/备选/决策；结论写入 `technology-decisions.md` 等阶段既有产物，不另写独立设计文档。先确认技能真实安装/可发现；不可用时用 `mode=equivalent` 并写 `reason`。阶段 evidence 必须写 `methods` 并运行 `python scripts/check-method-evidence.py --step 03-project-architecture-baseline --evidence <evidence.json>`。
- **OpenSpec：** 若 CLI 可用，运行 `openspec list --specs`、`openspec list --changes` 核对基线与现有规格关系；本阶段不创建功能 Change。命令须真实执行并报告退出码/结果。
- **Figma MCP：** 仅作为可访问的参考输入；不把不可读取内容当作已审查。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当产物写入指定路径、脚本与冻结审计通过且所需审批完成后，才将阶段记为完成。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="project-architecture-baseline"` 的记录。

- 输入核验：已批准的 requirements-analysis/workflows/data-objects/rd-matrix/business-rules/glossary/acceptance-policy/open-questions；BASELINE-BRIEF/role-permission-matrix/change-sizing/decisions/assumptions/id-conventions/BASELINE-INDEX（常驻基线）；现有仓库结构/技术约束；非功能需求；技术选型偏好。逐项报告存在、版本和批准状态；不满足时暂停。
- 必须输出：docs/architecture/system-context.md；domain-boundaries.md；containers-and-deployment.md；data-flows.md；logical-erd.md；technology-decisions.md；api-conventions.md；frontend-conventions.md；test-strategy.md；docs/adr/README.md；baseline-status.md；baseline-manifest.json；constraint-registry.json；docs/project/baseline-audit-report.md。按模板写入仓库。
- 下一步输入：冻结的项目总体架构基线、数据流转、逻辑 ERD、公共契约/测试策略、ACTIVE 约束目录、审计报告与审批记录。在报告中明确阶段 04/05 如何消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- **阶段边界（强制）：** 阶段完成 ≠ 可进入下一阶段。产物写完、检查通过后运行 `python scripts/workflow.py request-review --step 03-project-architecture-baseline --summary "<送审摘要>"`（流程冻结为待评审），按交接模板展示报告后**立即结束回合**；用户明确回复“评审通过 03-project-architecture-baseline”前，禁止读取/执行下一阶段 Prompt/Skill、禁止创建下一阶段产物。批准后运行 `python scripts/workflow.py approve --step 03-project-architecture-baseline --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>`，再执行 `transition`。不得自行填写 approver/approved_at，不得把产物完成或自检通过当作批准。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。

## 阶段结束审计与冻结（必须执行）

- 运行 `bash scripts/check-required-files.sh --strict`，退出码必须为 0。
- 完成 Manifest/Registry 后依次执行：
  `python scripts/baseline-governance.py refresh-hashes`
  `python scripts/baseline-governance.py freeze --approved-by <负责人> --approved-at <ISO日期> --evidence <审批证据路径>`
  `python scripts/baseline-governance.py audit --require-frozen`
- Evidence 必须包含 `docs/architecture/baseline-manifest.json` 与 `docs/architecture/constraint-registry.json` 两个输出；未冻结、哈希不匹配或缺少产物时不得推进。
- 审计报告写入 `docs/project/baseline-audit-report.md`；存在阻断项时不得建议冻结。
