---
name: figma-design-review
description: Figma 设计与评审（Figma-only）。通过 Figma MCP 生成真实设计并把读取结果落盘为 figma-audit.md，作为 07–10 的唯一界面输入。
---

# Figma 设计与评审（Figma-only）

## 何时使用

当流程进入阶段 06「Figma 设计与评审」时加载本 Skill。一次处理一个 Change；不要提前执行详细设计或实现。

## 核心规则（强制）

- 阶段 06 为 Figma-only：唯一 UI 产物是 `openspec/changes/<change-id>/design/figma-audit.md`。
- 使用 Figma MCP AI 从已批准需求生成真实 Figma 设计；用户必须在真实 Figma 评审稿上完成 UI 评审。
- 设计完成后必须通过 Figma MCP 实际读取真实文件/节点/组件/变量，并把读取结果落盘到 `figma-audit.md`。
- Figma MCP 不可用或读不到真实设计时阻断，不得用截图、手写 HTML 或臆造替代。
- 不再使用 pen.dev、`prototype.pen`、`PAGE-*.html`、`prototype.md`、`manifest.json` 或 `design/design-tokens.json`。
- 无 UI 时：在 `figma-audit.md` 的“设计来源与选择”写入 `- 设计来源状态：N/A` 与 `- 无 UI 理由：<原因>`，再运行 `--strict` 校验；也可使用 `--no-ui --reason "<原因>" --strict` 显式验证。不得用空文件或缺少理由的 N/A 掩盖遗漏。

## 输入

已批准的提案级需求与 AC（proposal/specs/design/user-stories）；项目业务流程、数据对象、RD 矩阵、业务规则（workflows/data-objects/rd-matrix/business-rules）；`docs/product/open-questions.md`（只读，生成时不擅自决策）；`docs/architecture/frontend-conventions.md` 第 9 节（视觉规范）；`docs/architecture/baseline-status.md`；当前 Change 的 `design/baseline-impact.md` 与 `design/baseline-binding.json`；Figma MCP 的实际可访问能力（涉及 UI 时必须）。

## 执行流程

1. **核验输入**：逐项检查文件存在、版本与批准状态；缺失或未批准时停止并报告。
2. **确定页面范围**：根据已批准 proposal/specs/user-stories 与项目 FLOW/NODE/DO/BR 确定 PAGE 清单；PAGE ID 由本阶段冻结，07–10 不得新增或重命名。
3. **选择设计来源**：默认 Figma MCP AI 自动设计；人工 Figma 设计仅在用户明确选择时使用。把选择、选择人和日期记录到 `figma-audit.md` 的 `## 设计来源与选择`，并写入 `- 设计来源状态：APPROVED`。
4. **生成真实设计**：使用 Figma MCP（`use_figma` 等实际可用工具）按 PAGE 逐页构建可编辑画板；每页绘制后回读真实节点，确认节点非空。
5. **回读真实文件**：使用 `get_design_context`、`get_metadata`、`get_variable_defs`、`get_screenshot` 等实际可用工具读取真实 Figma 文件、节点、组件、变量与样式；把每次调用的工具、目标、返回、时间和状态登记到 `## MCP 读取记录`。
6. **建立映射**：在 `## 节点映射` 为每个 PAGE 写入真实 Figma node 与 node/component/variable 映射；在 `## 页面覆盖` 写入页面职责、关键区块、覆盖状态与差异；在 `## 差异与待确认` 登记未决项、负责人和后续处理。
7. **UI 评审**：设计负责人在真实 Figma 评审稿上完成评审，在 `## UI 评审` 写入 `- UI 评审状态：APPROVED`、`- 评审人：...`、`- 评审证据：workflow/evidence/06-figma-ui-review.md`；证据文件必须真实存在。
8. **门禁**：运行 `python scripts/check-figma-audit.py --change <change-id> --strict`，退出码必须为 0；失败时不得进入 07。
9. **无 UI 时**：在 `figma-audit.md` 的“设计来源与选择”写入 `- 设计来源状态：N/A` 与 `- 无 UI 理由：<原因>`，运行 `python scripts/check-figma-audit.py --change <change-id> --strict`；也可使用 `--no-ui --reason "<原因>" --strict` 显式验证。

## 输出

`openspec/changes/<change-id>/design/figma-audit.md`（唯一 UI 产物），包含：

- `## 设计来源与选择`：设计来源、选择人/日期、`- 设计来源状态：APPROVED`。
- `## 设计输入与风格参考`：需求与 AC、Figma MCP、设计规范第 9 节。
- `## Figma 文件`：真实 Figma 链接/fileKey、页面与画板范围、PAGE → node。
- `## MCP 读取记录`：实际成功的 Figma MCP 工具调用。
- `## 节点映射`：PAGE → node/component/variable/样式。
- `## 页面覆盖`：PAGE 职责、关键区块、覆盖状态、差异。
- `## 差异与待确认`：未决项、负责人、处理方式。
- `## UI 评审`：`- UI 评审状态：APPROVED`、评审人、评审证据。

不再输出 `prototype.pen`、`PAGE-*.html`、`prototype.md`、`manifest.json`、`design-tokens.json` 或 06 初始化的 `traceability.csv`。

## 质量与安全边界

- PAGE ID 稳定唯一；页面集合与 Figma 评审稿一致；每个 PAGE 在节点映射中闭合。
- MCP 读取记录必须对应真实成功的调用；工具名或“未执行”不算读取。
- 不得用截图、手写 HTML、臆造链接或空文件替代真实 Figma 设计。
- 页面、元素、事件不得绕过已批准产品/前端/权限约束；冲突时记录约束 ID 并提交例外/BCR，不得自行修改 binding。
- UI 评审未 APPROVED 不得进入 07。

## 与 OpenSpec / Superpowers 的边界

- OpenSpec 保存 proposal、delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 校验。
- 需要澄清交互时可用 Superpowers `brainstorming`；只有确认真实安装且可调用时才声称使用。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查

`python scripts/check-figma-audit.py --change <change-id> --strict`；无 UI 时在 `figma-audit.md` 写入 `- 设计来源状态：N/A` 与 `- 无 UI 理由：<原因>` 后运行同一命令，或使用 `--no-ui --reason "<原因>" --strict`。

## 实际工具调用要求

- **Superpowers：** `brainstorming`（若实际可用）；不可用时说明并执行等价澄清步骤。
- **OpenSpec：** 运行 `openspec status --change <id>` 并读取已批准规格；命令必须真实执行并报告退出码/结果。
- **Figma MCP：** 以实际可访问能力为准；必须实际生成/读取真实 Figma 文件、节点、组件和变量；不可用时标记“未执行/阻断”，不得伪造结果。本阶段不使用 pen.dev。
- **状态更新：** 仅在产物落盘且门禁通过后更新 `workflow-state.json`。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="figma-design-review"` 的契约记录。

- **本阶段输入：** 已批准 proposal/specs/design/user-stories；项目业务流程/数据对象/RD 矩阵/业务规则/角色权限/ID 约定（workflows、data-objects、rd-matrix、business-rules、role-permission-matrix、id-conventions）；`docs/product/open-questions.md`（只读）；frontend-conventions 第 9 节；`docs/architecture/baseline-status.md`；`design/baseline-impact.md` 与 `design/baseline-binding.json`；Figma MCP 实际能力（涉及 UI 时必须）。逐项核验存在、版本与批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** `openspec/changes/<change-id>/design/figma-audit.md`（唯一 UI 产物；无 UI 时 N/A + 理由）。
- **下游交接：** `figma-audit.md` 是 07/08/09/10 的唯一界面输入；可实时访问时重新读取真实 Figma，无法访问时以落盘快照为稳定输入；PAGE ID 与页面集合在 06 冻结；`traceability.csv` 由 07 初始化 PAGE → AC 并合并 API/测试映射。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **阻断项解除：** 若 `workflow-state.json` 中本阶段存在 `blocked_items`，`transition` 证据必须增加 `resolved_blockers`（含 `step_id`、`resolution` 与现有证据路径）；其他阶段的阻断项仍需先处理。

## 项目基线约束（只读继承）

- 执行前读取 `docs/architecture/baseline-manifest.json`、`docs/architecture/constraint-registry.json` 与当前 Change 的 `design/baseline-binding.json`。
- 页面、元素、事件不得绕过已批准产品/前端/权限约束；冲突时记录约束 ID 并提交例外/BCR，不得自行修改 binding。
- 通过前执行 `python scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`。
