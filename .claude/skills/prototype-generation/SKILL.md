---
name: prototype-generation
description: 提案原型生成与评审。根据提案级需求通过 pen.dev MCP 生成页面原型，并完成页面-需求映射与原型评审。
---

# 提案原型生成与评审

## 何时使用
当流程进入“提案原型生成与评审”时加载本 Skill。一次只处理一个明确 Change；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
已批准的提案级需求（proposal/specs/design/user-stories.md/use-cases.md）、项目业务流程与 RD 矩阵（只读）、未决问题清单（只读）、pen.dev MCP 的实际可访问能力。

## 执行流程
1. 通读已批准的提案级 US/UC/AC 与项目 FLOW/NODE/DO；从用例与业务流程推导本 Change 需要的页面清单，先在 `openspec/changes/<change-id>/design/prototype-build.md` 的页面清单中登记 PAGE ID、名称与状态。
2. 加载 pen.dev MCP 的设计指引（如 `read_skill`），按指引确认当前画布状态（`get_app_state`），再逐页绘制（`execute`）：布局、导航、核心控件优先，视觉细节从简。页面按功能区块组织（导航/筛选/表单/列表/详情/统计/操作区/弹窗等），区块名称与页面清单说明列保持一致，供阶段 11 拆解 BLOCK 清单。
3. 每页绘制后用 `get_app_state` 核验页面真实渲染；不把未验证的页面登记为已完成。
4. 页面必须覆盖提案级 UC/US 中每个入口/操作/结果路径；映射表逐行登记 PAGE ID → UC/US/FLOW/BR ID，并引用项目 NODE/DO ID（适用时）。
5. **原型评审（阶段结束审计）：** 逐页核对默认、加载、空数据、成功、失败、无权限、禁用、边界值和重复提交状态；核查返回/取消/关闭/刷新/未保存提示/导航/表单校验；列出原型有但需求没有的业务行为、需求有但原型缺失的页面/元素/状态；在 `design/prototype-audit.md` 记录差异、决策、负责人、日期与原型版本/快照标识。
6. pen.dev 工具不可用、返回失败或内容无法读取时，在构建记录中如实登记 blocked；不得声称已生成。
7. 在构建记录中登记每次 MCP 调用（工具/命令、用途、结果、时间）与导出快照（若支持）；原型与需求修订在本阶段审批中一并确认。

## 输出
`openspec/changes/<change-id>/design/prototype-build.md`、`openspec/changes/<change-id>/design/prototype-audit.md`、pen.dev 原型页面（链接登记到构建记录）、导出快照（若支持）。

## 质量与安全边界
每个页面能追溯到提案级 UC/US 与项目 FLOW/BR；不声称访问了不可访问的画布；未决需求不擅自决策，只登记到未决项；原型评审差异必须可追溯到需求 ID 或页面 ID。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-prototype-build.py --change <change-id> --strict`（构建记录 + 页面映射 + 原型评审记录；MCP 不可用时按预期阻断）

## 实际工具调用要求

- **Superpowers：** `brainstorming`（仅在页面方案或需求有歧义时）；必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 读取已批准 proposal/specs；本阶段不创建或归档功能 Change。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **pen.dev MCP（pencil 工具）：** 先 `read_skill` 加载画布设计指引，再 `get_app_state` 核验当前状态，用 `execute` 绘制页面；每次调用结果如实登记。MCP 不可用时在构建记录中标记 blocked 并停止，不得伪造链接或页面。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="prototype-generation"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准的提案级需求（proposal/specs/design/user-stories/use-cases）；docs/product/open-questions.md（只读）；pen.dev MCP 实际可访问能力；当前 Change 的 baseline-binding.json（只读继承）。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** openspec/changes/<change-id>/design/prototype-build.md；openspec/changes/<change-id>/design/prototype-audit.md；pen.dev 原型页面（链接登记到构建记录）。如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 已批准原型链接/导出物、PAGE→UC/US/FLOW/BR 映射、原型评审结论与需求澄清。明确指出阶段 11 消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成；原型批准发生在阶段 10b 结束审计。
