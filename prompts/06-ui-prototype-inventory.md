# Prompt：原型、页面与交互清单

```text
执行 `@ui-prototype-inventory`，Change：<change-id>。

提案需求与 AC：<proposal-and-user-stories-paths>
项目业务流程/RD 矩阵：<product-paths>
前端规范：<frontend-conventions>
基线绑定：openspec/changes/<change-id>/design/baseline-binding.json

先读已批准的 proposal/specs/user-stories 与项目 FLOW/NODE/DO/BR，确定本 Change 的页面范围。原型是可选步骤：使用 pen.dev 时，在 `design/prototype.md` 登记 PAGE ID 草案、页面→AC/FLOW/BR 映射和 MCP 调用记录，逐页绘制并用 `get_app_state` 核验真实渲染；MCP 不可用时如实标记 blocked，不得伪造链接或页面。随后在同一文件写评审结论：逐页核对默认、加载、空、成功、失败、无权限、禁用、边界值、重复提交、返回/取消/关闭/刷新/未保存提示和表单校验，登记差异、决策、负责人和待确认项。

生成 `design/page-inventory.csv`、`block-inventory.csv`、`interaction-map.csv` 与 `traceability.csv`。page-inventory 是批准后的唯一权威页面清单；层级固定为 PAGE → BLOCK → ELEM/EVT；每个页面至少一个功能区块，每个按钮/可交互元素必须且只能归属一个区块；事件登记触发元素、输入、前置条件、步骤、输出、状态变化、导航、错误处理和权限，涉及 API 时引用 operationId（未冻结时标候选）。`traceability.csv` 由本阶段初始化 PAGE/BLOCK/ELEM/EVT → AC 追踪行，下游只追加。

涉及 UI 时，必须执行 Figma 审计：通过 Figma MCP 实际读取真实 Figma 文件/节点/组件/变量（使用 `get_design_context`、`get_metadata`、`get_variable_defs`、`get_screenshot` 等实际可用工具），以本阶段三份清单为唯一权威建立 node/component/variable 映射，输出 `design/figma-audit.md` 并登记实际读取到的 node/component/variable 与差异。MCP 不可用或读不到真实设计时阻断，不得用截图或臆造替代。需要结构化几何/交接时生成 `design/design-spec.json`：按 page_id 登记画板尺寸与角色外壳，按 block_id 登记布局（direction/order 为 must，间距/高度按 should/free 分档）与元素几何；只引用 PAGE/BLOCK/ELEM ID，不复制页面名称/路由/需求/AC；states 覆盖清单；颜色/字号只写 `token:` 路径；装饰性原语可省略 elementId。优先从 pen.dev `.pen` 经 pencil MCP `execute` 导出几何；MCP 不可用则阻断，不得用截图替代。随后运行 `python scripts/check-design-spec.py --change <change-id> --strict`，再用 `python scripts/build-figma-handoff.py --change <change-id> --write` 生成只读 `design/generated/figma-handoff.json/md`，并用 `--check` 复核未过期。不新增/重命名 PAGE/BLOCK，差异回到本阶段修订清单。无 UI 时保留三份清单模板并说明原因，用 `--no-ui --reason "<原因>" --strict` 验证。

完成后运行 `python scripts/check-prototype-build.py --change <change-id> --strict` 与 `python scripts/check-inventory.py --change <change-id> --strict`；涉及 UI 时必须运行 `python scripts/check-figma-audit.py --change <change-id> --strict`；需要几何/交接时再运行 `python scripts/check-design-spec.py --change <change-id> --strict` 与 `python scripts/build-figma-handoff.py --change <change-id> --check`。退出码必须为 0。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：先读 `BASELINE-BRIEF.md`，再按页面/前端影响读取相关基线；页面、元素、事件不得绕过已批准约束。发现冲突时记录约束 ID 并提交例外/BCR，不得自行修改 `baseline-binding.json`。完成后执行 `python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：本阶段为功能级，必须填写真实 Change ID。
- 加载 Skill：按当前 Agent 的真实机制加载 `.claude/skills/ui-prototype-inventory/SKILL.md`，不能只把 Skill 名字当普通文本。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`；无法加载时明确报告并按本 Prompt 执行。
- **Superpowers：** 需要澄清交互时可用 `brainstorming`；先确认真实安装与可调用方式，不可用时说明并执行等价步骤。
- **OpenSpec：** 运行 `openspec status --change <id>` 并读取已批准 specs；本阶段不归档 Change。命令须真实执行并报告退出码/结果。
- **pen.dev / Figma MCP：** 先 `read_skill` 加载指引、`get_app_state` 核验状态，再 `execute` 绘制或读取；涉及 UI 时必须通过 Figma MCP 实际读取 Figma 文件/节点/组件/变量，每次调用结果如实登记。MCP 不可用或读不到真实设计时阻断，不得伪造或用截图替代。
- **状态与门禁：** 仅在产物写入指定路径且脚本检查通过后更新 `workflow-state.json`；遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用工具、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="ui-prototype-inventory"` 的记录。

- 输入核验：已批准提案需求与 AC；项目业务流程/数据对象/RD 矩阵/业务规则；前端规范；`design/baseline-impact.md` 与 `design/baseline-binding.json`；pen.dev/Figma MCP 实际能力（涉及 UI 时必须；MCP 不可用或读不到真实设计时阻断）。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design/prototype.md；openspec/changes/<change-id>/design/page-inventory.csv；openspec/changes/<change-id>/design/block-inventory.csv；openspec/changes/<change-id>/design/interaction-map.csv；openspec/changes/<change-id>/traceability.csv（初始化）；涉及 UI 时 design/figma-audit.md 必填；需要几何/交接时 design/design-spec.json、design/generated/figma-handoff.json/md。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：PAGE/BLOCK/ELEM/EVT 权威清单、区块归属、状态/跳转、事件与 AC/operationId 的关联；`traceability.csv` 由本阶段初始化，07 只追加合并。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。

## 阶段结束审计（必须执行）

- 逐页核对状态与交互覆盖；逐条核对 AC/FLOW/BR 是否都有页面/事件承载。
- 检查 ID 唯一、页面/区块/元素引用闭合、区块归属一致、AC 覆盖和未定义内容；每个页面至少一个区块。
- 把差异、决策、负责人、日期和原型版本写入 `design/prototype.md`；未决问题转入 open-questions。
- 运行 `python scripts/check-prototype-build.py --change <change-id> --strict` 与 `python scripts/check-inventory.py --change <change-id> --strict`，退出码必须为 0；审计结论写入交接报告。
