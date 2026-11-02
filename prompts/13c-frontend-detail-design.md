# Prompt：前端详细设计

```text
执行 `@frontend-detail-design`，Change：<change-id>。

OpenAPI：<openapi-path>
页面/事件清单：<inventory-paths>
Figma 审计：<figma-audit>
前端基线：<frontend-conventions>

输出路由/目录、页面组件树、组件职责与传参、状态管理、事件处理函数入参/返回/副作用/错误处理，以及 operationId 映射。覆盖加载/空/错误/成功/禁用/无权限状态和组件/页面/E2E 测试。禁止重复定义 API 契约。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@frontend-detail-design`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按设计复杂度使用 Superpowers `brainstorming` 审视方案；不要将它当成接口/设计模板的替代品。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 先检查 Change 状态：`openspec status --change <id>`；读取已批准 specs/design。若发现需求变化，暂停并回到 OpenSpec 更新规格，不能只改辅助设计文档。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="frontend-detail-design"` 的记录。

- 输入核验：已批准 OpenAPI（或 x-api-scope: none）；页面/交互清单与 Figma 审计；前端工程规范；功能规格与 AC。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design/frontend-design.md；前端测试用例/组件状态映射。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：组件职责、状态管理、API 调用映射、错误/加载/空状态、测试 ID。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。
