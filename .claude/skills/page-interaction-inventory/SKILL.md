---
name: page-interaction-inventory
description: 页面、功能区块、元素、按钮与交互事件清单。建立 PAGE→BLOCK→ELEM→EVT 的稳定 ID 层级与需求追踪关系。
---

# 页面、元素、按钮与交互事件清单

## 何时使用
当流程进入“页面、元素、按钮与交互事件清单”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
批准的提案需求（proposal/specs/design/user-stories.md/use-cases.md）、已批准的提案原型（prototype-build.md、prototype-audit.md）、项目业务流程/RD 矩阵。

## 执行流程
1. 为页面、功能区块、业务相关元素、事件分配稳定 ID：PAGE-xxx、BLOCK-xxx、ELEM-xxx、EVT-xxx；层级固定为 PAGE → BLOCK → ELEM/EVT，不得跨层引用。
2. 页面清单记录路由/入口、权限、核心状态和关联需求；只纳入有业务/交互/测试意义的元素。
3. 每个页面必须拆出功能区块（BLOCK-xxx）并写入区块清单：区块名称、类型、职责说明、页面内顺序、关联需求。建议类型：导航、筛选、表单、列表/表格、详情、统计、操作区、弹窗/抽屉、空态/错误态、其他；按页面真实结构命名，不要按视觉图层切块。
4. 每个按钮/可交互元素（ELEM-xxx）必须且只能归属一个功能区块；事件清单用 `block_id` 记录归属，并校验区块属于同一页面。同一元素的多个事件可以存在，但不得被拆到不同区块。
5. 事件清单记录触发元素、所在区块、输入、前置条件、处理步骤、输出、状态变化、导航、错误处理和权限；区分纯前端事件、API 请求、异步/消息事件和外部跳转。
6. 若涉及 API，引用 operationId；在 API 尚未冻结时用候选 ID 并标明状态。
7. 检查重复 ID、悬空页面/区块/元素引用、无需求来源元素和未覆盖 AC；每个页面至少有一个区块。

## 输出
`openspec/changes/<change-id>/design/page-inventory.csv`、`block-inventory.csv`、`interaction-map.csv`、`traceability.csv` 和缺口报告。三份清单共同构成页面-区块-元素/事件的可追溯层级。

## 质量与安全边界
ID 稳定唯一；页面、区块、元素、事件引用闭合且跨页/跨区块归属一致；没有定义的行为明确标为待确认。若本 Change 确实没有 UI，保留 Change 内三份 CSV 仅含表头，并记录无 UI 原因；用 `scripts/check-inventory.py --change <change-id> --no-ui --reason "<原因>" --strict` 显式验证，不要用空清单掩盖遗漏。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-inventory.py --change <change-id> --strict`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 用于澄清不明确的交互，不要擅自决定业务行为。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 运行 `openspec status --change <id>` 并读取已批准规格；若发现需求变更，先更新 OpenSpec。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="page-interaction-inventory"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准的提案级需求（proposal/specs/design/user-stories/use-cases）；已批准的提案原型构建记录与评审结论；项目业务流程/数据对象/RD 矩阵与项目级 UI/前端规范。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** openspec/changes/<change-id>/design/page-inventory.csv；openspec/changes/<change-id>/design/block-inventory.csv；openspec/changes/<change-id>/design/interaction-map.csv。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** PAGE/BLOCK/ELEM/EVT 清单、区块内元素归属、状态/跳转、事件与需求/operationId 的关联。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。

## 项目基线约束（只读继承）
- 执行前读取 `docs/architecture/baseline-manifest.json`、`docs/architecture/constraint-registry.json` 和当前 Change 的 `design/baseline-binding.json`。
- 本阶段只消费已批准的 requirement 级绑定；页面、元素、事件不得绕过已批准产品/前端/权限约束。
- 若原型或用户故事与 ACTIVE 约束冲突，记录冲突并提交例外/BCR 评审；不得自行修改 binding、降低约束等级或将约束标记为 N/A。
- 通过前执行 `python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`。
