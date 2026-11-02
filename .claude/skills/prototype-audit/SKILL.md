---
name: prototype-audit
description: pen.dev 原型评审与需求澄清。通过原型反查需求遗漏，并把未确认内容保留为问题。
---

# pen.dev 原型评审与需求澄清

## 何时使用
当流程进入“pen.dev 原型评审与需求澄清”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
已整理需求、pen.dev 页面草图/可访问链接/导出物、客户反馈。

## 执行流程
1. 按用户故事逐项定位入口页面、操作、结果页面和异常路径。
2. 逐页核对默认、加载、空数据、成功、失败、无权限、禁用、边界值和重复提交状态。
3. 核查返回/取消/关闭/刷新/未保存提示/导航/表单校验等交互。
4. 把原型中有但需求中没有的业务行为记为待确认；不要将视觉占位或设计师假设升级成业务事实。
5. 列出需求明确要求但原型缺失的页面、元素与状态；对 pen.dev 工具不可读取的内容标记为未检查。
6. 在客户确认后记录决策、负责人、日期与原型版本/快照标识。

## 输出
`docs/design/prototype-audit.md`、差异清单、客户澄清问题与需求追踪矩阵。

## 质量与安全边界
每个差异能追溯到需求 ID 或页面 ID；不声称访问了不可访问的原型。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`人工评审；可由 scripts/check-inventory.py 辅助`


## 实际工具调用要求

- **Superpowers：** `brainstorming`（仅在需求/原型有歧义时）；读取真实 pen.dev MCP 或用户提供的导出，不得臆造节点。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 读取相关已批准 specs；原型差异先形成问题清单，不直接偷偷修改 OpenSpec 规格。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="prototype-audit"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** docs/product/* 需求产物；pen.dev 原型链接/导出物（必须实际可访问）；需求疑问与干系人反馈。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** docs/design/prototype-audit.md；docs/product/open-questions.md（更新）；docs/product/requirements-analysis.md（经确认的修订）。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 原型评审结论、已确认需求修订、未决问题。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
