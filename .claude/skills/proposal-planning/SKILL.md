---
name: proposal-planning
description: 提案拆分、依赖排序与路线图。按独立可验收的业务能力划分 OpenSpec Change 并排序。
---

# 提案拆分、依赖排序与路线图

## 何时使用
当流程进入“提案拆分、依赖排序与路线图”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
已审基线、用户故事、流程、风险、依赖和产品优先级。

## 执行流程
1. 按用户可感知且可独立验收的业务能力切分 Change，不按前端/后端/数据库横向切分。
2. 每项明确价值、目标、非目标、用户故事、AC、依赖、数据迁移、风险与发布策略。
3. 优先选纵向切片，尽早贯穿 UI/API/domain/persistence/test。
4. 识别基础设施型 Change 的独立理由和前置依赖。
5. 排序时解释业务价值、风险、解锁关系和可并行性。
6. 检查每项大小是否能被清晰设计、实施和验收；过大的 Change 继续拆分。

## 输出
提案路线图、依赖 Mermaid 图、Change 清单和排序依据。

## 质量与安全边界
每个 Change 有独立验收条件；无循环依赖；不把未知依赖藏在备注里。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-roadmap.py`


## 实际工具调用要求

- **Superpowers：** `brainstorming`，先比较切分方案、依赖和风险，审批后再创建 Change。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 先运行 `openspec list --specs`、`openspec list --changes`；提案获批后才可运行 `openspec new change <id>`。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="proposal-planning"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已冻结项目基线；产品需求/用户故事/AC；已知技术债与依赖。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** docs/product/proposal-roadmap.md；每个候选 Change 的范围/依赖/价值说明。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 经批准的 Change 列表、优先级、依赖顺序。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
