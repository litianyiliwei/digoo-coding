---
name: figma-design-review
description: Figma 设计与评审（Figma-only）。通过 Figma MCP 生成真实设计并把读取结果落盘为 figma-audit.md，作为 07–10 的唯一界面输入。
---

# Figma 设计与评审（Figma-only）

## 何时使用

当流程进入阶段 06「Figma 设计与评审」时加载本 Skill。一次处理一个 Change；不要提前执行详细设计或实现。

## 核心规则（强制）

- 阶段 06 为 Figma-only：唯一 UI 契约是单文件 `openspec/changes/<change-id>/design/figma-audit.md`（目标框架/转码说明、token 实际值/每 PAGE 规格/状态/UI 评审）与机器契约 `design/figma-code/`（每 PAGE 一个**目标框架对齐**的设计代码：Vue 栈为 `.vue` + 该端组件库（Web 为 Element Plus，移动端为 uni-app 组件库），React 栈为 `.tsx`/`.jsx`；08 直接移植，只补业务逻辑）和 `design/figma-layout.csv`（精简几何/文本/字体断言表）。
- **框架对齐转码（强制）**：06 在首次调用 `get_design_context` 前，先读取 `docs/architecture/technology-decisions.md` 与 `docs/architecture/frontend-conventions.md` 第 1 节，确定并记录目标前端框架/组件库；加载官方 `figma-design-to-code` Skill，并把 `get_design_context` 返回的参考实现转码为目标框架设计代码。目标框架为 Vue 时输出 `.vue`（使用该端组件库：Web 为 Element Plus，移动端为 uni-app 组件库，以及项目 token），为 React 时输出 `.tsx`/`.jsx`（项目组件库 + token）；不得把 React/Tailwind 原始参考实现直接作为交付代码。技术选型未定或与基线冲突时阻断，不得自行选型。
- 使用 Figma MCP AI 从已批准需求生成真实 Figma 设计；用户必须在真实 Figma 评审稿上完成 UI 评审。
- 设计完成后必须通过 Figma MCP 实际读取真实文件/节点/组件/变量，并把读取结果落盘；节点几何来自 `get_metadata`，不得只写摘要或手写坐标。
- **不使用截图**：参考截图、实现截图、像素截图都不是设计契约或门禁证据；`get_design_context` 返回的渲染只能即时用作视觉对照，不得保存、登记为资产或写入任何证据文件。人工验收对照运行系统与 Figma 文件，自动化视觉回归使用节点几何与运行态 DOM 的数值断言（`scripts/check-figma-layout.py`）。
- Figma MCP 不可用或读不到真实设计时阻断，不得用截图、手写 HTML 或臆造替代。
- 不再使用 pen.dev、`prototype.pen`、`PAGE-*.html`、`prototype.md`、`manifest.json` 或 `design/design-tokens.json`。
- 无 UI 时：在 `figma-audit.md` 的“设计来源与选择”写入 `- 设计来源状态：N/A` 与 `- 无 UI 理由：<原因>`，再运行 `--strict` 校验；也可使用 `--no-ui --reason "<原因>" --strict` 显式验证。不得用空文件或缺少理由的 N/A 掩盖遗漏。

## 输入

已批准的提案级需求与 AC（proposal/specs/design/user-stories）；项目业务流程、数据对象、RD 矩阵、业务规则（workflows/data-objects/rd-matrix/business-rules）；`docs/product/open-questions.md`（只读，生成时不擅自决策）；`docs/architecture/technology-decisions.md`（总体技术选型，确定目标前端框架/组件库）与 `docs/architecture/frontend-conventions.md` 第 1、9 节（工程与视觉规范）；`docs/architecture/baseline-status.md`；当前 Change 的 `design/baseline-impact.md` 与 `design/baseline-binding.json`；Figma MCP 的实际可访问能力（涉及 UI 时必须）。

## 执行流程

1. **核验输入**：逐项检查文件存在、版本与批准状态；缺失或未批准时停止并报告。
2. **确定目标框架（框架对齐前置条件）**：读取 `docs/architecture/technology-decisions.md` 与 `frontend-conventions.md` 第 1 节，在 `figma-audit.md` 的 `## 设计代码` 记录 `- 目标框架：<Vue 3 + TypeScript + Element Plus / React + ...>`、`- 设计代码扩展名：<.vue / .tsx / .jsx>` 与选型依据（ADR/基线版本）。技术选型为 PENDING、互相冲突或读不到时阻断，不得自行选择。
3. **确定页面范围**：根据已批准 proposal/specs/user-stories 与项目 FLOW/NODE/DO/BR 确定 PAGE 清单；PAGE ID 由本阶段冻结，07–10 不得新增或重命名。
4. **选择设计来源**：默认 Figma MCP AI 自动设计；人工 Figma 设计仅在用户明确选择时使用。把选择、选择人和日期记录到 `figma-audit.md` 的 `## 设计来源与选择`，并写入 `- 设计来源状态：APPROVED`。
5. **生成真实设计**：使用 Figma MCP（`use_figma` 等实际可用工具）按 PAGE 逐页构建可编辑画板；每页绘制后回读真实节点，确认节点非空。
6. **一次性完整导出并框架对齐转码**：先加载官方 `figma-design-to-code` Skill；`get_variable_defs` 读取全文件 token 实际值；`get_metadata` 每 PAGE 读取精确节点 `x/y/w/h`（用于填充断言表）；`get_design_context` 每 PAGE 生成参考实现后，立即按第 2 步目标框架转码并落盘为 `design/figma-code/PAGE-001.vue … PAGE-00N.vue`（React 栈则为 `.tsx`/`.jsx`）。转码必须保留真实文案、字号/字重、间距、圆角、层级与 `data-node-id`，把 Tailwind/内联样式替换为目标 UI 组件库与项目 token（Vue 栈用该端组件库（Web 为 Element Plus，移动端为 uni-app）与 CSS 变量），只做高保真静态页面，不接业务 API。调用 `get_design_context` 时在 `skillNames` 登记 `figma-design-to-code`（资源方式加载时前缀 `resource:`）；返回的渲染仅即时对照，不保存。需要图片/SVG 资产时立即下载到 `design/figma-assets/`，不得保留临时 URL。串行调用，不逐节点轮询，不并行多个 Agent 读取同一文件；受 429/Retry-After 时退避，导出或转码不完整则阻断。
7. **建立契约**：在 `figma-audit.md` 写 token 实际值、文字样式、PAGE → node/尺寸、每 PAGE 区块级规格、目标框架与设计代码说明、断言范围、状态覆盖与决策、资产清单；在 `figma-code/README.md` 写来源 `get_design_context`、目标框架/扩展名、组件与样式/token 替换表、`data-node-id` 对应关系与转码偏差；建立 `figma-layout.csv` 断言子集（每行包含预期 `x/y/w/h`、文本、字号/字重、容差；06 可把 `route`/`dom_selector` 留为 `PENDING`）。需要完整 `get_design_context` 时直接落盘到 `figma-code/`，不另建分散文件。
8. **UI 评审**：设计负责人在真实 Figma 评审稿上完成评审，在 `## UI 评审` 写入 `- UI 评审状态：APPROVED`、`- 评审人：...`、`- 评审证据：workflow/evidence/06-figma-ui-review.md`；证据文件必须真实存在。
9. **门禁**：运行 `python scripts/check-figma-audit.py --change <change-id> --strict --require-framework`，退出码必须为 0；失败时不得进入 07。
10. **无 UI 时**：在 `figma-audit.md` 的“设计来源与选择”写入 `- 设计来源状态：N/A` 与 `- 无 UI 理由：<原因>`，运行 `python scripts/check-figma-audit.py --change <change-id> --strict`；也可使用 `--no-ui --reason "<原因>" --strict` 显式验证。

## 输出

`openspec/changes/<change-id>/design/figma-audit.md`（唯一 UI 契约，单文件），包含：
- `## 设计来源与选择`：来源、选择人/日期、文件版本、PAGE 清单。
- `## 设计输入与风格参考`：需求与 AC、Figma MCP、设计规范第 9 节。
- `## 设计令牌（实际值）`：颜色 hex、间距/圆角/阴影 px、CSS 变量/Element Plus 映射。
- `## 文字样式（实际值）`：字体族、字重、字号、行高、字距。
- `## PAGE 与节点`：PAGE → 真实 node、画板尺寸、状态。
- `## PAGE 关键规格`：每 PAGE 区块级位置/尺寸/布局/padding/gap/边框/圆角/字体；可附录完整 `get_design_context` 快照。
- `## 设计代码`：目标框架与扩展名、选型依据（ADR/基线）、`figma-code/README.md` 来源、转码方式（get_design_context 参考实现 → 目标框架组件/token）、组件与样式替换表、转码偏差，以及 `data-node-id` 与 `figma-layout.csv` 的对应关系。
- `## 断言范围`：列出 `figma-layout.csv` 覆盖的关键区块；未纳入断言的元素由目标框架设计代码与机器断言覆盖；结构性差异写入 `## 差异与待确认`。
- `## 状态覆盖`：每 PAGE default 及适用状态；Figma 无画板的状态写 07 决策/审批。
- `## 资产清单`：仅真实图片/SVG 资产（文件、来源 node、尺寸）；无资产写“无”；不得登记参考截图。
- `## MCP 读取记录`、`## 差异与待确认`、`## UI 评审`。
- `design/figma-code/README.md`：来源 `get_design_context`、目标框架/扩展名、转码方式、组件与样式/token 替换表、转码偏差、`data-node-id` ↔ `figma_node_id` 说明。
- `design/figma-code/PAGE-001.vue … PAGE-00N.vue`（React 栈为 `.tsx`/`.jsx`）：每 PAGE 一个目标框架设计代码，保留真实文案/字号/间距/层级与 `data-node-id`，使用目标组件库与项目 token；08 直接移植为页面骨架，只补业务逻辑。
- `design/figma-layout.csv`：精简断言表（`page_id,route,element_id,figma_node_id,x,y,width,height,dom_selector,assert_geometry,assert_text,tolerance_px,text_content,font_size,font_weight,notes`）；06 可把 `route`/`dom_selector` 留为 `PENDING`，07 必须填满。
- `design/figma-assets/README.md`：仅当存在真实图片/SVG 资产时生成（文件、来源 node、sha256、尺寸）。

不得为每页/每状态拆分子目录，也不得生成分散的 token/contract JSON，不保存参考截图。

## 质量与安全边界

- PAGE ID 稳定唯一；页面集合与 Figma 评审稿一致；每个 PAGE 在 `PAGE 与节点` 与 `PAGE 关键规格` 中闭合。
- token 必须记录实际值；只有变量名/数量不算规格；每 PAGE 至少有 3 个区块级几何/布局行。
- 每个 PAGE 必须有目标框架设计代码（Vue 栈 `figma-code/PAGE-00N.vue`，React 栈 `PAGE-00N.tsx`/`.jsx`），且 `## 设计代码` 必须写明目标框架、扩展名与选型依据；`figma-layout.csv` 必须覆盖每个 PAGE 的关键区块与主操作，几何/文本/字体值来自 Figma；结构性差异写入 `## 差异与待确认`。
- 状态必须有 default；Figma 无画板的状态必须写 07 决策、审批人与依据，不得声称已还原。
- 真实图片/SVG 资产必须实际存在于 `design/figma-assets/` 并由 `README.md` 登记；参考截图不进入资产清单。
- MCP 读取记录必须对应真实成功的 `get_metadata` 与 `get_variable_defs` 调用；工具名或“未执行”不算读取。
- 不得用截图、手写 HTML、臆造链接或空文件替代真实 Figma 设计。
- 页面、元素、事件不得绕过已批准产品/前端/权限约束；冲突时记录约束 ID 并提交例外/BCR，不得自行修改 binding。
- UI 评审未 APPROVED 不得进入 07。

## 与 OpenSpec / Superpowers 的边界

- OpenSpec 保存 proposal、delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 校验。
- 需要澄清交互时可用 Superpowers `brainstorming`；只有确认真实安装且可调用时才声称使用。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查

`python scripts/check-figma-audit.py --change <change-id> --strict --require-framework`；无 UI 时在 `figma-audit.md` 写入 `- 设计来源状态：N/A` 与 `- 无 UI 理由：<原因>` 后运行同一命令，或使用 `--no-ui --reason "<原因>" --strict`。

## 实际工具调用要求

- **Superpowers：** `brainstorming`（若实际可用）；不可用时说明并执行等价澄清步骤。
- **OpenSpec：** 运行 `openspec status --change <id>` 并读取已批准规格；命令必须真实执行并报告退出码/结果。
- **Figma MCP：** 以实际可访问能力为准；必须实际生成/读取真实 Figma 文件、节点、组件和变量；首次调用 `get_design_context` 前必须加载官方 `figma-design-to-code` Skill，并把结果转码为目标框架设计代码；不可用时标记“未执行/阻断”，不得伪造结果。本阶段不使用 pen.dev。
- **状态更新：** 仅在产物落盘且门禁通过后更新 `workflow-state.json`。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="figma-design-review"` 的契约记录。

- **本阶段输入：** 已批准 proposal/specs/design/user-stories；项目业务流程/数据对象/RD 矩阵/业务规则/角色权限/ID 约定（workflows、data-objects、rd-matrix、business-rules、role-permission-matrix、id-conventions）；`docs/product/open-questions.md`（只读）；`docs/architecture/technology-decisions.md`（目标前端框架/组件库）与 frontend-conventions 第 1、9 节；`docs/architecture/baseline-status.md`；`design/baseline-impact.md` 与 `design/baseline-binding.json`；Figma MCP 实际能力（涉及 UI 时必须）。逐项核验存在、版本与批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** `openspec/changes/<change-id>/design/figma-audit.md`（唯一 UI 契约：目标框架/转码说明、token 实际值、文字样式、PAGE 规格、状态决策、设计代码、断言范围、UI 评审）、`design/figma-code/README.md` 与目标框架设计代码 `PAGE-001.vue … PAGE-00N.vue`（React 栈为 `.tsx`/`.jsx`）、`design/figma-layout.csv`（精简断言表：预期几何/文本/字体/选择器；`route`/`dom_selector` 可由 07 填满）；有真实图片/SVG 时附 `design/figma-assets/README.md`，不保存参考截图（无 UI 时 N/A + 理由）。
- **下游交接：** `figma-audit.md`、`figma-code/` 与 `figma-layout.csv` 是 07/08/09/10 的唯一界面输入；07/08 默认离线消费，仅在 Figma 文件版本变化或页面有歧义时按页批量重读（串行、避免限流）。PAGE ID 与页面集合在 06 冻结；`traceability.csv` 由 07 初始化 PAGE → AC 并合并 API/测试映射。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **阻断项解除：** 若 `workflow-state.json` 中本阶段存在 `blocked_items`，`transition` 证据必须增加 `resolved_blockers`（含 `step_id`、`resolution` 与现有证据路径）；其他阶段的阻断项仍需先处理。

## 项目基线约束（只读继承）

- 执行前读取 `docs/architecture/baseline-manifest.json`、`docs/architecture/constraint-registry.json` 与当前 Change 的 `design/baseline-binding.json`。
- 页面、元素、事件不得绕过已批准产品/前端/权限约束；冲突时记录约束 ID 并提交例外/BCR，不得自行修改 binding。
- 通过前执行 `python scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`。
