# Prompt：页面、元素、按钮与交互事件清单

```text
执行 `@page-interaction-inventory`，Change：<change-id>。

规格：<proposal-and-user-story-paths>
提案原型：<prototype-build-and-audit-path>

生成/更新 `openspec/changes/<change-id>/design/page-inventory.csv`、`block-inventory.csv`、`interaction-map.csv` 与 `traceability.csv`（初始化 PAGE/BLOCK/ELEM/EVT → US/UC/AC 追踪行）。page-inventory.csv 是批准后的唯一权威页面清单；12 只做 Figma 映射核对，不重定义 PAGE ID。页面从已批准的提案原型（prototype-build.md/prototype-audit.md）与提案级 UC/US 推导；页面用 PAGE-xxx、功能区块用 BLOCK-xxx、业务元素用 ELEM-xxx、事件用 EVT-xxx；先为每个页面拆出功能区块（导航/筛选/表单/列表/详情/统计/操作区/弹窗/空态等）并登记区块名称、类型、职责和页面内顺序，再在 `interaction-map.csv` 的 `block_id` 中登记每个按钮/可交互元素唯一所属的区块；不得跨页或跨区块归属。记录路由、权限、可见/禁用条件、入参、前置条件、步骤、输出、错误、状态变化及 operationId（若适用）。检查 ID 唯一、页面/区块/元素引用闭合、区块归属一致、AC 覆盖和未定义内容，且每个页面至少有一个区块。

在清单闭合后生成 `design-spec.json`（几何层）：按 page_id 登记画板尺寸与角色外壳，按 block_id 登记布局（direction/order 为 must，间距/高度按 should/free 分档）与元素几何；只引用 PAGE/BLOCK/ELEM ID，不复制页面名称、路由、角色、需求与 AC。states 必须覆盖清单 states，并把原型评审缺口（如加载、空态、校验、无权限、重复提交）补入；颜色与字号只写 `token:` 路径，不写色值；装饰性原语可省略 elementId。优先从 pen.dev `.pen` 经 pencil MCP `execute` 遍历节点导出几何并归一化；MCP 不可用时按构建记录与评审结论手工补写，并在构建记录登记 blocked，不得伪造几何，也不得用原型截图代替结构化几何。

随后运行 `python scripts/check-design-spec.py --change <change-id> --strict`，再用 `python scripts/build-figma-handoff.py --change <change-id> --write` 生成 `generated/figma-handoff.json/md`；交接包只读、禁止手改，并用 `--check` 复核未过期。如果本 Change 明确不涉及 UI，仍保留 Change 内清单模板并说明原因，用 `--no-ui --reason "<原因>" --strict` 验证，并跳过 design-spec 与交接包。不要将每个纯视觉图层都列为业务元素，也不要按视觉图层切分功能区块。完成后按范围运行：涉及 UI 时执行 `python scripts/check-inventory.py --change <change-id> --strict`、`python scripts/check-design-spec.py --change <change-id> --strict` 与 `python scripts/build-figma-handoff.py --change <change-id> --check`；明确无 UI 时执行两个 checker 的 `--no-ui --reason "<原因>" --strict`。
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

- 输入核验：已批准 Change proposal/specs；关联 US/AC 与业务流程；已批准原型与 pen.dev 实际可读能力；项目级 UI/前端规范与设计 token 来源。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design/page-inventory.csv；openspec/changes/<change-id>/design/block-inventory.csv；openspec/changes/<change-id>/design/interaction-map.csv；openspec/changes/<change-id>/design/design-spec.json；openspec/changes/<change-id>/design/generated/figma-handoff.json；openspec/changes/<change-id>/design/generated/figma-handoff.md。按模板写入仓库，不要只在聊天中展示；generated 文件只能由脚本生成。
- 下一步输入：PAGE/BLOCK/ELEM/EVT 清单、每个区块包含的元素/按钮、状态/跳转、事件与需求/operationId 的关联；design-spec.json 与 generated/figma-handoff.json/md 是 08 的 Figma 生成输入，三份清单仍是唯一权威。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。

**项目基线约束（只读继承）：** 执行前读取当前 Change 的 `design/baseline-binding.json`、Manifest 和 Constraint Registry。页面/元素/事件只能在已批准约束范围内细化；不得自行修改约束适用性、规则或审批状态。发现冲突时记录约束 ID、冲突证据并暂停相关设计，提交例外或 BCR。完成后执行 `python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`，失败不得推进。
