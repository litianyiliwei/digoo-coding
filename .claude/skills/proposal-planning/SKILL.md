---
name: proposal-planning
description: 提案拆分、依赖排序与路线图。按独立可验收的业务能力划分 OpenSpec Change 并排序。
---

# 提案拆分、依赖排序与路线图

## 何时使用
当流程进入“提案拆分、依赖排序与路线图”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
已审并冻结的项目总体架构基线、业务流程/节点/RD 矩阵、业务规则、验收政策、open-questions、`BASELINE-BRIEF.md`/`change-sizing.md`/`decisions.md`/`assumptions.md`/`lessons.md`/`id-conventions.md`（常驻基线）、阶段 03 基线审计报告、风险、依赖和产品优先级。

## 执行流程
1. 按用户可感知且可独立验收的业务能力切分 Change，不按前端/后端/数据库横向切分。
2. 每项明确价值、目标、非目标、关联 FLOW/NODE/DO/BR、预期验收方向、依赖、数据迁移、风险与发布策略；依赖必须显式检查平台/原生/设备/第三方前置条件（跨端方案、原生插件与 JS Bridge、设备/网关、地图/天气/支付/实名/溯源等第三方审批、离线同步），不得藏在备注里。提案级 UC/US/AC 在阶段 05 细化，不在本阶段伪造。
3. 读取 open-questions 与阶段 03 基线审计报告，把未决问题、审计缺口和待批项带入候选 Change 的风险/依赖/阻塞条件，不擅自关闭。
4. 优先选纵向切片，尽早贯穿 UI/API/domain/persistence/test。
5. 识别基础设施型 Change 的独立理由和前置依赖。
6. 排序时解释业务价值、风险、解锁关系和可并行性。
7. 检查每项大小是否能被清晰设计、实施和验收；过大的 Change 继续拆分。

## 输出
提案路线图、依赖 Mermaid 图、Change 清单和排序依据。

## 质量与安全边界
每个 Change 有独立验收条件；无循环依赖；不把未知依赖藏在备注里。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- Figma MCP 的输入必须基于实际可访问的链接、节点和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-roadmap.py`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 的 stage-scoped 模式，先比较切分方案、平台/原生依赖和风险，结论写入 `proposal-roadmap.md`，审批后再创建 Change。阶段 evidence 必须写 `methods`（至少 2 个问题、2 个备选、1 个决策）并运行 `python scripts/check-method-evidence.py --step 04-proposal-planning --evidence <evidence.json>`。必须按当前宿主 Agent 的真实机制检查、读取或调用技能；不可用时用 `mode=equivalent` 并写 `reason`。
- **OpenSpec：** 先运行 `openspec list --specs`、`openspec list --changes`；提案获批后才可运行 `openspec new change <id>`。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 项目基线与功能拆分的交互（强制）

- 在拆分每个 Change 时，读取 `docs/architecture/baseline-status.md` 和已冻结的产品/架构/数据/公共契约/测试基线；按候选功能的影响面检查相关章节。
- 在 `docs/product/proposal-roadmap.md` 为每个候选 Change 增加“基线适用域、需复用的基线约束、潜在基线冲突/修订、审批前置条件”列。
- 将变化初步分类为 `CHANGE_ONLY`、`BASELINE_CHANGE_REQUIRED`、`BASELINE_UPDATE_AFTER_ACCEPTANCE` 或 `N/A`。不要因为功能使用新组件/新字段/新 API 就自动提升为基线变更。
- 如果基线状态不是 FROZEN、存在未决修订或冲突，明确列为风险/阻断；不得把 DRAFT/PENDING 规则当作已批准约束。
- 详细规则见 `docs/BASELINE-FEATURE-INTERACTION.md`。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="proposal-planning"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已冻结项目基线；产品需求/用户故事/AC；docs/product/BASELINE-BRIEF.md、role-permission-matrix.csv、change-sizing.md、decisions.md、assumptions.md、lessons.md、id-conventions.md（基线常驻层与经验回写）；已知技术债与依赖。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** docs/product/proposal-roadmap.md；每个候选 Change 的范围/依赖/价值说明。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 经批准的 Change 列表、优先级、依赖顺序。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。


## 机器基线约束（强制）

- 路线图拆分前运行 `python3 scripts/baseline-governance.py audit --require-frozen`，读取 Manifest 与 Constraint Registry。
- 为每个候选 Change 记录可能适用的 Constraint ID、潜在例外和基线修订候选；不得把 DRAFT 约束当成现行规则，也不得跳过 ACTIVE 约束。
- 不得修改冻结基线；基线修订只能走 BCR/ADR 和 `open-amendment`。

## 阶段边界与评审停等（强制）

- 开始前运行 `python scripts/workflow.py check-entry --step 04-proposal-planning [--change-id <id>]`；退出码非 0 时立即停止并报告，不得绕过。
- 产物写完、检查通过只代表可送审：运行 `python scripts/workflow.py request-review --step 04-proposal-planning --summary "<摘要>"`，按 `templates/workflow/step-handoff-report.md` 展示交接报告后**立即结束回合**；禁止在同一会话读取/执行下一阶段 Prompt/Skill 或创建下一阶段产物。
- 只有用户明确回复“评审通过 04-proposal-planning”后，才可运行 `python scripts/workflow.py approve --step 04-proposal-planning --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>` 并执行 `transition`。不得自行填写 approver/approved_at，不得把自检通过当作批准。
- `pending_approvals` 非空时禁止推进；`workflow-state.json` 只能通过 `check-entry`/`request-review`/`approve`/`transition` 等命令管理，禁止直接编辑。
- Claude Code 的 PreToolUse hook 会拒绝写入当前阶段之后的阶段产物（共享产物除外）与直接编辑状态文件；待评审期间同样拒绝。遇到拒绝必须停止并说明，不得更换路径或禁用 hook 绕过。
