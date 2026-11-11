# Prompt：Figma 设计与评审（Figma-only）

```text
执行 `@figma-design-review`，Change：<change-id>。

提案需求与 AC：<proposal-and-user-stories-paths>
项目业务流程/RD 矩阵：<product-paths>
前端规范：<frontend-conventions>（视觉规范取第 9 节）
基线绑定：openspec/changes/<change-id>/design/baseline-binding.json
Figma MCP：<figma-file-link-or-file-key>（必须实际可访问）

先读已批准的 proposal/specs/user-stories 与项目 FLOW/NODE/DO/BR，确定本 Change 的页面范围。

阶段 06 为 Figma-only，不再经过 pen.dev 原型或 PAGE HTML 交接：
- 唯一 UI 产物是 `openspec/changes/<change-id>/design/figma-audit.md`：Figma 文件/页面/节点/组件/变量、PAGE 清单与 PAGE → node/component/variable 映射、状态覆盖、差异与待确认、MCP 读取记录、UI 评审 APPROVED。
- 设计输入：已批准需求与 AC、产品业务流程/数据对象/RD 矩阵/业务规则、`docs/architecture/frontend-conventions.md` 第 9 节、当前 Change 的 `design/baseline-impact.md` 与 `design/baseline-binding.json`。
- 不维护 `design/design-tokens.json`；视觉规范以 Figma 变量/样式（通过 `get_variable_defs` 等读取并登记）与 frontend-conventions 第 9 节为准。
- 无 UI 时：在 `figma-audit.md` 的“设计来源与选择”写入 `- 设计来源状态：N/A` 与 `- 无 UI 理由：<原因>`，再运行 `--strict` 校验；也可使用 `--no-ui --reason "<原因>" --strict` 显式验证。不得用空文件或缺少理由的 N/A 掩盖遗漏。

执行步骤：
1. 先要求用户选择设计来源（默认 Figma MCP AI 自动设计；人工 Figma 设计仅在用户明确选择时），并在 figma-audit.md 的“设计来源与选择”记录；设计来源状态必须为 APPROVED。
2. 使用 Figma MCP（use_figma、get_design_context、get_metadata、get_variable_defs、get_screenshot 等实际可用工具）从已批准需求生成真实 Figma 设计；按 PAGE 清单逐页构建并回读真实文件/节点/组件/变量。
3. 在 figma-audit.md 建立 PAGE → node/component/variable 映射、页面覆盖、状态覆盖与差异/待确认；每个 PAGE 必须闭合。
4. 用户必须在真实 Figma 评审稿上完成 UI 评审，并在 `## UI 评审` 写入 `- UI 评审状态：APPROVED`、`- 评审人：...`、`- 评审证据：workflow/evidence/06-figma-ui-review.md`（文件必须真实存在）。
5. MCP 不可用或读不到真实设计时阻断，不得用截图、手写 HTML 或臆造替代。PAGE ID 由 06 冻结，07–10 不得新增或重命名 PAGE。
6. 完成后运行 `python scripts/check-figma-audit.py --change <change-id> --strict`，退出码必须为 0。

正式产物请遵循 docs/TEMPLATE-POLICY.md 与 docs/OUTPUT-TEMPLATE-MATRIX.csv 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：先读 BASELINE-BRIEF.md，再按页面/前端影响读取相关基线；页面、元素、事件不得绕过已批准约束。发现冲突时记录约束 ID 并提交例外/BCR，不得自行修改 baseline-binding.json。完成后执行 python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：本阶段为功能级，必须填写真实 Change ID。
- 加载 Skill：按当前 Agent 的真实机制加载 `.claude/skills/figma-design-review/SKILL.md`，不能只把 Skill 名字当普通文本。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`；无法加载时明确报告并按本 Prompt 执行。
- **Superpowers：** 需要澄清交互时可用 `brainstorming`；先确认真实安装与可调用方式，不可用时说明并执行等价步骤。
- **OpenSpec：** 运行 `openspec status --change <id>` 并读取已批准 specs；本阶段不归档 Change。命令须真实执行并报告退出码/结果。
- **Figma MCP：** 使用 `use_figma`、`get_design_context`、`get_metadata`、`get_variable_defs`、`get_screenshot` 等实际可用工具生成/读取 Figma 文件、节点、组件和变量；每次调用结果如实登记到 `figma-audit.md`。MCP 不可用或读不到真实设计时阻断，不得伪造或用截图替代。本阶段不使用 pen.dev。
- **状态与门禁：** 仅在产物写入指定路径且脚本检查通过后更新 `workflow-state.json`；遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用工具、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="figma-design-review"` 的记录。

- 输入核验：已批准 proposal/specs/design/user-stories；项目业务流程/数据对象/RD 矩阵/业务规则/角色权限/ID 约定（workflows、data-objects、rd-matrix、business-rules、role-permission-matrix、id-conventions）；`docs/product/open-questions.md`（只读）；`docs/architecture/frontend-conventions.md` 第 9 节；`docs/architecture/baseline-status.md`；`design/baseline-impact.md` 与 `design/baseline-binding.json`；Figma MCP 实际可访问能力（涉及 UI 时必须）。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：`openspec/changes/<change-id>/design/figma-audit.md`（唯一 UI 产物：Figma MCP 读取快照 + PAGE 清单与映射 + 状态覆盖 + 差异与待确认 + UI 评审 APPROVED；无 UI 时 N/A + 理由）。不再输出 `prototype.pen`、`PAGE-*.html`、`prototype.md`、`manifest.json`、`design-tokens.json` 或 06 初始化的 `traceability.csv`。
- 下一步输入：`figma-audit.md` 是 07/08/09/10 的唯一界面输入；可实时访问时重新读取真实 Figma 文件/节点/组件/变量，无法访问时以该落盘快照为稳定输入。PAGE ID 与页面集合在 06 冻结；`traceability.csv` 由 07 初始化 PAGE → AC 并合并 API/测试映射。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。
- 若 `workflow-state.json` 中本阶段存在 `blocked_items`，`transition` 证据必须增加 `resolved_blockers`（含 `step_id`、`resolution` 与现有证据路径），否则 `transition` 仍会被阻断。

## 阶段结束审计（必须执行）

- `figma-audit.md` 必须包含 `## 设计来源与选择`、`## 设计输入与风格参考`、`## Figma 文件`、`## 节点映射`、`## 页面覆盖`、`## 差异与待确认`、`## MCP 读取记录`、`## UI 评审`。
- 每个 PAGE 必须有真实 Figma node 与 node/component/variable 映射；页面集合与图稿一致，不新增或重命名 PAGE。
- MCP 读取记录必须包含实际成功的 Figma MCP 调用；不得只登记工具名或“未执行”。
- UI 评审必须由设计负责人在真实 Figma 评审稿上完成，并写入 `- UI 评审状态：APPROVED`、评审人与存在的评审证据文件。
- 运行 `python scripts/check-figma-audit.py --change <change-id> --strict`，退出码必须为 0；审计结论写入交接报告。
