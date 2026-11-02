---
name: frontend-detail-design
description: 前端详细设计。定义路由、组件、状态、函数、事件与 API 调用映射。
---

# 前端详细设计

## 何时使用
当流程进入“前端详细设计”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
OpenAPI、页面/元素/事件清单、Figma 审计和前端工程基线。

## 执行流程
1. 沿用项目路由、目录、请求层和状态管理规范；偏离时注明原因。
2. 定义页面/组件树、组件职责、Props/Emits（或框架等价机制）、状态流和跨页面参数。
3. 为每个 EVT 定义处理函数的输入/返回/副作用/失败路径，并关联 operationId。
4. 定义 loading/empty/error/success/disabled 状态、表单校验与防重复提交。
5. 区分服务器状态、本地 UI 状态和 URL 状态；避免无必要的重复状态源。
6. 指定组件、页面、API mock 和 E2E 测试。

## 输出
`design/frontend-design.md`、组件树、状态图、函数表与 API 映射。

## 质量与安全边界
不得重复定义或擅自修改 OpenAPI；函数职责单一、状态完整、可测试。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`阶段 13a–13e 全部设计产物完成后运行 scripts/check-design-assets.sh <change-id>`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 仅用于澄清组件/状态设计取舍；保持 API 契约为单一来源。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 读取 Change 状态和批准的 OpenAPI/规格；不得单方面修改契约。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="frontend-detail-design"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准 OpenAPI（或 x-api-scope: none）；页面/交互清单与 Figma 审计；前端工程规范；功能规格与 AC。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** openspec/changes/<change-id>/design/frontend-design.md；前端测试用例/组件状态映射。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 组件职责、状态管理、API 调用映射、错误/加载/空状态、测试 ID。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
