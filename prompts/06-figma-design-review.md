# Prompt：Figma 设计与评审（Figma-only）

```text
执行 `@figma-design-review`，Change：<change-id>。

提案需求与 AC：<proposal-and-user-stories-paths>
项目业务流程/RD 矩阵：<product-paths>
前端规范：<frontend-conventions>（视觉规范取第 9 节）
技术选型：<technology-decisions>（目标前端框架/组件库，06 转码必须按此执行）
基线绑定：openspec/changes/<change-id>/design/baseline-binding.json
Figma MCP：<figma-file-link-or-file-key>（必须实际可访问）

先读已批准的 proposal/specs/user-stories 与项目 FLOW/NODE/DO/BR，确定本 Change 的页面范围。

阶段 06 为 Figma-only，不再经过 pen.dev 原型或 PAGE HTML 交接：
- 唯一 UI 契约是 `openspec/changes/<change-id>/design/figma-audit.md`：**单文件**记录 Figma 文件/版本、目标框架/转码说明、PAGE 清单、token **实际值**（颜色 hex、字号/行高、间距/圆角/阴影）、文字样式、每 PAGE 区块级规格、状态覆盖与决策、设计代码、断言范围、MCP 读取记录、差异与待确认、UI 评审 APPROVED。
- 机器契约是 `openspec/changes/<change-id>/design/figma-code/`（每 PAGE 一个**目标框架对齐**的设计代码：Vue 栈为 `PAGE-00N.vue` + 该端组件库（Web 为 Element Plus，移动端为 uni-app 组件库），React 栈为 `PAGE-00N.tsx`/`.jsx`；含真实文案/字号/间距/层级/`data-node-id`）与 `figma-layout.csv`（精简断言表：`page_id,route,element_id,figma_node_id,x,y,width,height,dom_selector,assert_geometry,assert_text,tolerance_px,text_content,font_size,font_weight,notes`）。06 建立断言子集，`route`/`dom_selector` 可由 07 填满。
- **框架对齐转码（强制）**：首次调用 `get_design_context` 前先加载官方 `figma-design-to-code` Skill，并按总体技术选型把参考实现转码为目标框架代码；不得把 React/Tailwind 原始参考实现直接作为交付代码。`figma-code/README.md` 记录目标框架、扩展名、组件/样式/token 替换与偏差；08 直接移植，只补业务逻辑。
- **不使用截图**：`get_design_context` 返回的渲染仅即时用作视觉对照，不得保存、登记或写入证据；不导出 `PAGE-*.default.png`，不保存实现截图；自动化视觉回归用 `scripts/check-figma-layout.py` 比较 Figma 节点几何与运行态 DOM，token 用 `scripts/check-design-tokens.py` 精确比对。无差异 PAGE 的后续 UI 验证以机器证据为主。
- 图片/SVG 资产统一放 `openspec/changes/<change-id>/design/figma-assets/`，并生成 `README.md` 清单（文件名、来源 node、sha256、尺寸）；无资产写“无”。
- 不维护 `design/design-tokens.json`；token 实际值写入 `figma-audit.md` 的“设计令牌（实际值）”表。
- 无 UI 时：在 `figma-audit.md` 的“设计来源与选择”写入 `- 设计来源状态：N/A` 与 `- 无 UI 理由：<原因>`，再运行 `--strict` 校验；也可使用 `--no-ui --reason "<原因>" --strict` 显式验证。不得用空文件或缺少理由的 N/A 掩盖遗漏。

执行步骤：
1. 先要求用户选择设计来源（默认 Figma MCP AI 自动设计；人工 Figma 设计仅在用户明确选择时），并在 figma-audit.md 的“设计来源与选择”记录；设计来源状态必须为 APPROVED。
2. **确定目标框架**：读取 `docs/architecture/technology-decisions.md` 与 `frontend-conventions.md` 第 1 节，在 figma-audit.md 的 `## 设计代码` 写入 `- 目标框架：<Vue 3 + TypeScript + Element Plus / React + ...>`、`- 设计代码扩展名：<.vue / .tsx / .jsx>` 与选型依据；选型 PENDING/冲突/读不到时阻断，不得自行选择。
3. **一次性完整导出并框架对齐转码**：先加载官方 `figma-design-to-code` Skill（调用 `get_design_context` 时在 `skillNames` 登记，资源方式加载时前缀 `resource:`）；使用 Figma MCP 从已批准需求生成/确认真实 Figma 设计后，按 PAGE 逐页读取；`get_variable_defs` 至少覆盖全文件 token 实际值，`get_metadata` 每 PAGE 读取精确 `x/y/w/h`（用于断言表），`get_design_context` 每 PAGE 生成参考实现后立即转码为目标框架并落盘为 `figma-code/PAGE-001.vue … PAGE-00N.vue`（React 栈为 `.tsx`/`.jsx`）；保留真实文案/字号/间距/圆角/层级与 `data-node-id`，替换为目标组件库与项目 token，只做静态高保真页面，不接业务 API。返回的渲染仅即时对照，不保存。有图片/SVG 资产时立即下载到 `figma-assets/`。不得逐节点轮询，不得并行多个 Agent 读取同一文件。
4. 在 figma-audit.md 建立 PAGE → node 映射、每 PAGE 区块级实际规格、状态覆盖与差异/待确认；建立 `figma-layout.csv` 断言子集，断言范围必须在 `## 断言范围` 说明；设计代码中的文字/结构以目标框架代码为准。状态没有 Figma 画板时必须写明 07 设计决策、审批人和依据，不能声称已还原。
5. 用户必须在真实 Figma 评审稿上完成 UI 评审，并在 `## UI 评审` 写入 `- UI 评审状态：APPROVED`、`- 评审人：...`、`- 评审证据：workflow/evidence/06-figma-ui-review.md`（文件必须真实存在）。
6. MCP 不可用或读不到真实设计时阻断，不得用截图、手写 HTML 或臆造替代。PAGE ID 由 06 冻结，07–10 不得新增或重命名 PAGE。
7. 完成后运行 `python scripts/check-figma-audit.py --change <change-id> --strict --require-framework`，退出码必须为 0。缺少目标框架、节点 CSV、断言映射、token 实际值、可见 TEXT 覆盖或 UI 评审时失败。

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
- **Figma MCP：** 使用 `use_figma`、`get_metadata`、`get_variable_defs`、`get_design_context` 等实际可用工具生成/读取 Figma 文件、节点、组件和变量；首次调用 `get_design_context` 前必须加载官方 `figma-design-to-code` Skill；本阶段**一次性完整导出并转码**（token 实际值、每 PAGE 区块规格、目标框架设计代码 `figma-code/PAGE-00N.vue`（React 栈为 `.tsx`）、`figma-layout.csv` 断言表、真实图片/SVG 资产），资产立即下载到 `figma-assets/`；串行调用、按页批量，不逐节点轮询或并行多个 Agent，避免限流。返回的渲染仅即时对照，不保存；MCP 不可用或读不到真实设计时阻断，不得伪造或用截图替代。本阶段不使用 pen.dev。
- **状态与门禁：** 仅在产物写入指定路径且脚本检查通过后更新 `workflow-state.json`；遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用工具、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="figma-design-review"` 的记录。

- 输入核验：已批准 proposal/specs/design/user-stories；项目业务流程/数据对象/RD 矩阵/业务规则/角色权限/ID 约定（workflows、data-objects、rd-matrix、business-rules、role-permission-matrix、id-conventions）；`docs/product/open-questions.md`（只读）；`docs/architecture/technology-decisions.md`（目标前端框架/组件库）与 frontend-conventions 第 1、9 节；`docs/architecture/baseline-status.md`；`design/baseline-impact.md` 与 `design/baseline-binding.json`；Figma MCP 实际可访问能力（涉及 UI 时必须）。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：`openspec/changes/<change-id>/design/figma-audit.md`（唯一 UI 契约：Figma 文件/版本 + 目标框架/转码说明 + token 实际值 + 文字样式 + PAGE 与 node + 每 PAGE 区块规格 + 设计代码 + 断言范围 + 状态覆盖/决策 + UI 评审 APPROVED；无 UI 时 N/A + 理由）、`design/figma-code/README.md` 与目标框架设计代码 `PAGE-001.vue … PAGE-00N.vue`（React 栈为 `.tsx`/`.jsx`）、`design/figma-layout.csv`（精简断言表，`route`/`dom_selector` 可由 07 填满）；有真实图片/SVG 时附 `design/figma-assets/README.md`。不再输出参考截图、`prototype.pen`、`PAGE-*.html`、`prototype.md`、`manifest.json`、`design-tokens.json`、分散的 token/contract JSON 或 06 初始化的 `traceability.csv`。
- 下一步输入：`design/figma-audit.md`、`design/figma-code/` 与 `design/figma-layout.csv` 是 07/08/09/10 的唯一界面输入；07/08 默认离线消费，仅在 Figma 文件版本变化或页面有歧义时重新读取 Figma；不得要求每个阶段全量实时读取。PAGE ID 与页面集合在 06 冻结；`traceability.csv` 由 07 初始化 PAGE → AC 并合并 API/测试映射。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- **阶段边界（强制）：** 阶段完成 ≠ 可进入下一阶段。产物写完、检查通过后运行 `python scripts/workflow.py request-review --step 06-figma-design-review --summary "<送审摘要>"`（流程冻结为待评审），按交接模板展示报告后**立即结束回合**；用户明确回复“评审通过 06-figma-design-review”前，禁止读取/执行下一阶段 Prompt/Skill、禁止创建下一阶段产物。批准后运行 `python scripts/workflow.py approve --step 06-figma-design-review --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>`，再执行 `transition`。不得自行填写 approver/approved_at，不得把产物完成或自检通过当作批准。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。
- 若 `workflow-state.json` 中本阶段存在 `blocked_items`，`transition` 证据必须增加 `resolved_blockers`（含 `step_id`、`resolution` 与现有证据路径），否则 `transition` 仍会被阻断。

## 阶段结束审计（必须执行）

- `figma-audit.md` 必须包含 `## 设计来源与选择`、`## 设计输入与风格参考`、`## 设计令牌（实际值）`、`## 文字样式（实际值）`、`## PAGE 与节点`、`## PAGE 关键规格`、`## 设计代码`、`## 断言范围`、`## 状态覆盖`、`## 资产清单`、`## MCP 读取记录`、`## 差异与待确认`、`## UI 评审`。
- token 必须记录**实际值**（颜色 hex、字号/行高、间距/圆角/阴影），只有变量名或“共 N 个变量”不算通过；每 PAGE 必须有真实 node、画板尺寸、至少 3 个区块级几何/布局规格。
- 每个 PAGE 必须有目标框架设计代码（Vue 栈 `figma-code/PAGE-00N.vue`，React 栈 `PAGE-00N.tsx`/`.jsx`），且 `## 设计代码` 必须写明目标框架、扩展名与选型依据；`figma-layout.csv` 必须覆盖每个 PAGE 的关键区块与主操作，几何/文本/字体值来自 Figma；结构性差异写入 `## 差异与待确认`。
- 每个 PAGE 必须有 default 状态；Figma 无画板的状态必须写 07 决策、审批人和依据，不得声称已还原。
- 真实图片/SVG 资产必须存在于 `design/figma-assets/` 并由 `README.md` 登记；**不得登记或保存参考截图**。
- MCP 读取记录必须包含实际成功的 `get_metadata` 与 `get_variable_defs` 调用；不得只登记工具名或“未执行”。
- UI 评审必须由设计负责人在真实 Figma 评审稿上完成，并写入 `- UI 评审状态：APPROVED`、评审人与存在的评审证据文件。
- 运行 `python scripts/check-figma-audit.py --change <change-id> --strict --require-framework`，退出码必须为 0；审计结论写入交接报告。
