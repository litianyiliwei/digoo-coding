---
name: feature-requirements
description: 功能级 OpenSpec Change 与需求细化。把一项提案细化为可测试的行为规格，并检查基线影响。
---

# 功能级 OpenSpec Change 与需求细化

## 何时使用
当流程进入“功能级 OpenSpec Change 与需求细化”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
Change ID、项目基线、相关 openspec/specs 和已确认的 pen.dev 原型。

## 执行流程
1. 先运行 `openspec status --change <id>`、`openspec list --specs` 并读取相关规格全文；遵循当前 OpenSpec CLI/Schema 指引。
2. 完善 `proposal.md` 的 Why、What Changes、Capabilities、Impact；capability 路径使用 kebab-case 并复用既有路径。
3. 把外部可观察行为写入 `specs/<capability>/spec.md`，使用规范的 ADDED/MODIFIED/REMOVED/RENAMED Requirements 和 Scenario。
4. 把实现方法放进 `design.md`，任务只放进带复选框的 `tasks.md`。
5. 标注对应 US/AC/BR ID、权限、失败路径、边界条件与原型变化。
6. 超出基线范围时先提出 ADR/基线变更；无行为变化的纯文档/重构 Change 按 OpenSpec 约定使用 `skip_specs: true`，不能伪造需求。
7. 完成后执行 `openspec validate <change-id> --strict`，并处理所有错误/警告。

## 输出
OpenSpec proposal、delta specs、design、tasks、基线影响和待审批清单。

## 质量与安全边界
规格描述 WHAT，不夹带类名/框架等实现细节；每条 Requirement 至少有一个 Scenario；tasks 使用 `- [ ]`。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-change.sh <change-id>`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 检查需求边界；不得开始编码。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 真实执行 `openspec status --change <id>`、`openspec instructions <artifact> --change <id> --json`、`openspec validate <id> --strict`。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="feature-requirements"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准路线图/当前 Change 范围；项目级产品/架构/数据/公共契约基线；关联 US/AC/BR/FLOW/UC；现有 OpenSpec specs。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** openspec/changes/<change-id>/proposal.md；openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）；openspec/changes/<change-id>/tasks.md（初步任务）；openspec/changes/<change-id>/design.md（有设计决策时）。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 已批准 Change proposal/specs、范围边界、验收标准、需求追踪 ID。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
