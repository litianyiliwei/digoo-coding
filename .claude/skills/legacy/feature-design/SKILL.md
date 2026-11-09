---
name: feature-design
description: 功能详细设计总控。协调 API、前端、后端和测试设计，确认契约一致。
---

# 功能详细设计总控

## 何时使用
当流程进入“功能详细设计总控”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
已批准的 Change specs、页面事件清单、Figma 审计、项目级技术/领域/接口基线。

## 执行流程
1. 先确认规格与原型无阻断差异；将详细设计划分为 API、前端、后端和测试子文档。
2. 先冻结共享 API 契约，再完成前后端细化；双方不得各自猜请求/响应字段。
3. 确保每个设计元素关联 REQ/AC/PAGE/EVT 或明确 N/A 原因；所有 L1 产物按 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板生成。
4. 后端详细设计必须对 OpenAPI 中每一个 operationId 建立 1..N 个具体 IO ID 映射，并由 `scripts/check-api-io-mapping.py` 验证；每个 IO ID 都要有完整 IO 契约和测试 ID。
5. 记录新增与复用的组件、领域对象、数据变更、外部 IO 和测试层级。
6. 在 `design/design-plan.md` 写设计范围、任务分解、接口范围草案、设计缺口/决策和准入结论；10–13 必须读取该文件。
7. 对任何打破项目基线的方案提出 ADR/审批，不在功能设计中隐式绕过。

## 输出
`design.md` 总设计、`design/design-plan.md`（任务分解/缺口/准入结论），以及链接到 API、前端、后端、测试子文档的设计目录。

## 质量与安全边界
设计文件之间使用唯一契约来源；未决项有责任人；任务能从设计逐项分解。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-change.sh <change-id>`；设计完成后运行 `scripts/check-design-assets.sh <change-id> --strict --lint-api`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 检查设计方案、依赖与未决选择。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 运行 `openspec status --change <id>` 并读取批准的 specs/design；任何行为变更回到规格评审。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 基线约束复核（强制）

- 设计开始前重新核验 Change 的 `design/baseline-impact.md` 与 `docs/architecture/baseline-status.md`；不能只相信功能需求阶段的快照。
- API 设计必须遵守 `api-conventions.md`；前端设计必须遵守 `frontend-conventions.md`；后端设计必须遵守模块边界、逻辑 ERD、数据所有权和数据流约束；测试设计必须遵守 `test-strategy.md`。
- 若当前基线版本已变化，按变化域复核并写明 `NO_IMPACT` 或 `REBASE_REQUIRED`；后者必须更新设计并重新评审。
- 若设计要求打破基线，创建/更新基线变更请求/ADR；受影响的详细设计不得在批准前冻结。
- 详细规则见 `docs/BASELINE-FEATURE-INTERACTION.md`。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="feature-design"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** openspec/changes/<change-id>/design/baseline-impact.md 与当前 docs/architecture/baseline-status.md；已批准 proposal/specs；页面/交互清单与 Figma 审计（适用时）；项目级架构/数据/公共契约基线。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** openspec/changes/<change-id>/design.md；复核后的 openspec/changes/<change-id>/design/baseline-impact.md；openspec/changes/<change-id>/design/design-plan.md（设计范围、任务分解、接口范围草案、设计缺口与准入结论）。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 统一设计约束、接口范围、前后端/测试设计任务与缺口。明确指出 10–13 消费哪些文件/章节。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。


## 设计阶段的机器基线门禁（强制）

- `design/baseline-binding.json` 必须覆盖当前全部 ACTIVE 约束；逐条填写 COMPLIANT / NOT_APPLICABLE / EXCEPTION_APPROVED，并关联仓库内真实设计证据。
- EXCEPTION_APPROVED 必须记录例外编号、范围、理由、批准人、日期及证据；Change 级例外不改变项目基线。
- 阶段 09 转出前、10–13 交接前运行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。
- 基线版本或指纹变化必须有当前 fingerprint 对应的 NO_IMPACT 证据，或完成 REBASE_COMPLETED 后执行 refresh-binding 并重新审批。
