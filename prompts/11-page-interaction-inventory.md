# Prompt：页面、元素、按钮与交互事件清单

```text
执行 `@page-interaction-inventory`，Change：<change-id>。

规格：<spec-paths>
pen.dev：<prototype-link-or-export>

生成/更新 `openspec/changes/<change-id>/design/page-inventory.csv` 与 `interaction-map.csv`，并按模板更新该 Change 的 `traceability.csv`。页面用 PAGE-xxx、业务元素用 ELEM-xxx、事件用 EVT-xxx；记录路由、权限、可见/禁用条件、入参、前置条件、步骤、输出、错误、状态变化及 operationId（若适用）。检查 ID 唯一、引用闭合、AC 覆盖和未定义内容。如果本 Change 明确不涉及 UI，仍保留 Change 内两份清单模板并说明原因，用 `--no-ui --reason "<原因>" --strict` 验证。不要将每个纯视觉图层都列为业务元素。完成后按范围运行：涉及 UI 时执行 `python3 scripts/check-inventory.py --change <change-id> --strict`；明确无 UI 时执行 `python3 scripts/check-inventory.py --change <change-id> --no-ui --reason "<原因>" --strict`。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@page-interaction-inventory`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按设计复杂度使用 Superpowers `brainstorming` 审视方案；不要将它当成接口/设计模板的替代品。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 先检查 Change 状态：`openspec status --change <id>`；读取已批准 specs/design。若发现需求变化，暂停并回到 OpenSpec 更新规格，不能只改辅助设计文档。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="page-interaction-inventory"` 的记录。

- 输入核验：已批准 Change proposal/specs；关联 US/AC 与业务流程；项目级 UI/前端规范。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design/page-inventory.csv；openspec/changes/<change-id>/design/interaction-map.csv。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：PAGE/ELEM/EVT 清单、状态/跳转、事件与需求/operationId 的关联。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。
