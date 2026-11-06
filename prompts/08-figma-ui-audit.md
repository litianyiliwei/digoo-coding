# Prompt：Figma UI 设计与 MCP 审计

```text
执行 `@figma-ui-audit`，Change：<change-id>。

页面/区块/事件清单：<inventory-paths>
Figma 文件：<figma-url>
设计系统/风格参考：<design-system>

如果本 Change 涉及 UI，先运行 `python scripts/check-inventory.py --change <change-id> --strict`，再使用当前可用 Figma MCP 读取真实文件/节点/组件/变量。以 11 的 page/block 清单为唯一权威，按 PAGE → BLOCK → ELEMENT 三层建立映射：每个页面核对功能区区块是否存在，每个按钮/元素核对是否位于其 `block_id` 对应的区块容器内。检查区块顺序/职责、状态覆盖、组件复用、响应式和可访问性。Figma 只做映射与差异核对，不新增/重命名 PAGE/BLOCK；差异回到 11 修订清单。如果本 Change 明确不涉及 UI，运行 inventory 的 `--no-ui --reason "<原因>" --strict` 检查并在审计文档中说明 N/A，不要虚构 Figma 检查。输出 `openspec/changes/<change-id>/design/figma-audit.md` 及需求差异；缺区块、区块内缺按钮或归属不一致必须列为差异。不可读取的字段标记未检查，不得虚构 MCP 结果或让设计稿自行覆盖已批准业务规则。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@figma-ui-audit`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按设计复杂度使用 Superpowers `brainstorming` 审视方案；不要将它当成接口/设计模板的替代品。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 先检查 Change 状态：`openspec status --change <id>`；读取已批准 specs/design。若发现需求变化，暂停并回到 OpenSpec 更新规格，不能只改辅助设计文档。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="figma-ui-audit"` 的记录。

- 输入核验：已批准页面/区块/交互清单（含 block_id 归属）；已批准功能规格；Figma 文件/节点与可访问 MCP 输出；项目级设计规范。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design/figma-audit.md（含 PAGE→BLOCK→ELEMENT 映射与区块覆盖表）；Figma 设计链接/节点映射及导出资源引用。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：页面/区块/组件/状态的 UI 设计依据、区块覆盖差异与待确认项。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。

**项目基线约束（只读继承）：** 执行前读取当前 Change 的 `design/baseline-binding.json`、Manifest 和 Constraint Registry。Figma 视觉稿不得覆盖 ACTIVE 产品、权限、API、安全、无障碍或前端规范。发现冲突时记录约束 ID 和节点证据，退回评审或申请 Change 级例外；不得自行修改项目基线或 binding。完成后执行 `python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`，失败不得推进。
