---
name: figma-ui-audit
description: Figma UI 设计与 MCP 审计。将 UI 节点、组件、变量与需求中的页面元素映射并检查差异。
---

# Figma UI 设计与 MCP 审计

## 何时使用
当流程进入“Figma UI 设计与 MCP 审计”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
页面/区块/交互事件清单（page-inventory.csv、block-inventory.csv、interaction-map.csv）、已确认需求、Figma 链接/组件库/设计 token、可用 MCP 工具。

## 执行流程
1. 先复用已有 Design System、组件、变量和风格；避免创造重复组件。
2. 用实际可用的 Figma MCP 读取文件/节点/组件/变量；先检查权限与返回字段，不臆造 MCP 结果。
3. 建立 PAGE/BLOCK/ELEMENT ID 与 Figma 页面、区块容器（frame/section）、节点、组件的映射；区块是审计的最小布局单元，元素/按钮必须能在其 `block_id` 对应的区块容器内找到。
4. 逐页核对区块覆盖：每个 BLOCK 是否存在、顺序与职责是否一致、区块内是否包含清单登记的全部按钮/元素且没有多余或错位归属。
5. 检查加载/空/错误/成功/禁用/无权限/响应式状态，以及键盘和可访问性要求。
6. 列出与需求、事件清单、公共设计系统之间的差异；业务冲突回到需求审批。
7. 记录文件/页面版本或导出时间，确保设计输入可追溯。

## 输出
`openspec/changes/<change-id>/design/figma-audit.md`（含 PAGE→BLOCK→ELEMENT 节点映射与区块覆盖表）、节点映射、设计差异、复用组件与待确认问题。

## 质量与安全边界
不可访问的 Figma 项标为未检查；不能只凭一张静态截图声称完整覆盖全部状态。缺区块、区块内缺按钮或按钮归属与清单不一致时，必须列为差异，不得直接修改清单或让 Figma 视觉稿覆盖已批准行为。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-inventory.py --change <change-id> --strict + 人工设计评审`


## 实际工具调用要求

- **Superpowers：** 若可用，加载 Figma MCP 对应工具/技能；Superpowers `brainstorming` 仅用于设计冲突澄清。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 运行 `openspec status --change <id>`，确保视觉差异没有被误写成业务需求变更。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="figma-ui-audit"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准页面/区块/交互清单（含 block_id 归属）；已批准功能规格；Figma 文件/节点与可访问 MCP 输出；项目级设计规范。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** openspec/changes/<change-id>/design/figma-audit.md（含 PAGE→BLOCK→ELEMENT 映射与区块覆盖）；Figma 设计链接/节点映射及导出资源引用。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 页面/区块/组件/状态的 UI 设计依据、区块覆盖差异与待确认项。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。

## 项目基线约束（只读继承）
- 执行前读取 Manifest、Constraint Registry 和 Change 的 `design/baseline-binding.json`；本阶段必须沿用已批准的 requirement 级约束绑定。
- Figma 视觉稿不能覆盖产品行为、权限、API、安全、无障碍和前端公共规范等 ACTIVE 约束。
- 发现设计与基线冲突时，记录差异并退回需求/设计评审或申请 Change 级例外；不得直接修改项目基线或 binding。
- 完成后重跑 `python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`。
