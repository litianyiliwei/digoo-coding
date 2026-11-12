# AGENTS.md — 智慧农业项目仓库约定

> 状态：APPROVED（2026-10-30 由 project-bootstrap 阶段创建，2026-10-30 经用户确认；仓库尚无源代码，技术栈相关约定为 PENDING，待架构阶段补充）
> 下游消费：所有阶段的 Agent（Claude/OpenCode 等）；需求发现（阶段 02）起必须遵守本文件的流程入口与模板政策。

## 项目目标

智慧农业项目。当前仓库仅包含 AI 研发流程工具包（Skills、Prompts、模板、检查脚本），尚无业务源代码。

## 流程入口

- 当用户说"下一步/继续/接着做"时，先加载 `workflow-orchestrator` Skill（或 `prompts/00-next-step.md`），依据 `workflow-state.json` 与真实产物判定唯一安全的下一阶段。
- 每阶段开始前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中对应 Skill 的契约记录。
- 阶段结束使用 `templates/workflow/step-handoff-report.md` 展示交接报告；产物必须落盘到契约指定路径，不得只在聊天中输出。

## 模板与产物规则

- 正式产物遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不得删除模板字段；未知项写 `PENDING` 并说明原因与责任人/阻塞条件；不适用项写 `N/A` 并写理由。
- 阶段 02/03/04/05/07/10 开始前先读 `docs/product/BASELINE-BRIEF.md`、`change-sizing.md`、`id-conventions.md`；详细基线按 Change 影响面加载，不整包塞入上下文。基线产物缺失或 `check-requirements.py` 未通过时不得进入下游阶段。
- 项目级基线放 `docs/product/`、`docs/architecture/`、`docs/adr/`；单个功能内容放 `openspec/changes/<change-id>/`。
- 每份 Markdown 正式产物开头注明：Change ID（若适用）、状态、来源基线、关联需求/AC ID、生成日期或版本。
- UI 相关 Change 的界面阶段（06）为 Figma-only：
  - 以已批准的提案需求/AC、产品流程、`docs/architecture/frontend-conventions.md` 第 9 节与 `docs/architecture/technology-decisions.md`（总体技术选型）为输入，通过 Figma MCP AI 生成真实 Figma 设计；用户必须在真实 Figma 评审稿上完成 UI 评审。
  - **框架对齐转码（强制）**：06 必须在调用 `get_design_context` 前加载官方 `figma-design-to-code` Skill，并先按总体技术选型确定目标框架；返回的参考实现必须转码为目标框架设计代码：技术选型为 Vue 时输出 Vue SFC（`.vue`，使用该端组件库（Web 为 Element Plus，移动端为 uni-app）与项目 token），为 React 时输出 React（`.tsx`/`.jsx`，使用项目组件库与 token）。`figma-code/README.md` 必须记录目标框架、扩展名、组件/样式/token 替换与偏差；禁止把 React/Tailwind 原始参考实现直接当作交付代码，08 只在此基础上补业务逻辑，不重写样式/布局/文案。
  - 设计完成后必须通过 Figma MCP 实际读取真实文件/节点/组件/变量，并把 token **实际值**（颜色 hex、字号/行高、间距/圆角/阴影）、文字样式、每 PAGE 区块规格、状态覆盖与决策、设计代码（含目标框架与转码说明）、断言范围、MCP 读取记录、UI 评审 APPROVED 落盘到唯一单文件 `design/figma-audit.md`；同时导出 `design/figma-code/`（目标框架设计代码）与 `design/figma-layout.csv`（运行态断言映射）。**截图不是契约、资产或门禁证据**：`get_design_context` 返回的渲染只能即时用作视觉对照，不得保存、登记或入库；真实图片/SVG 资产放 `design/figma-assets/`，由 README 登记文件/来源 node/sha256/尺寸，无资产写“无”。Figma MCP 不可用或读不到真实设计时阶段阻断；不得用截图或臆造替代。
  - 06 一次性完整导出；07/08 默认离线消费 `figma-audit.md`、`figma-code/` 与 `figma-layout.csv`，仅在 Figma 文件版本变化或页面有歧义时按页批量重读（串行、避免限流）。07 必须在 design.md 建 token → CSS 变量/Element Plus 主题/字体映射，填满 `figma-layout.csv` 的 `route`/`dom_selector` 并定义 `### 响应式与视口规则`；08 必须直接以目标框架设计代码为页面骨架（只补业务逻辑/路由/API/状态），落地全局 token 层与字体，运行 `check-figma-layout.py`（Figma 节点几何 vs 1440×900 运行态 DOM，元素缺失/超差即 FAIL）与 `check-design-tokens.py`，生成 `design/evidence/figma-layout-check.json`。**UI 验证以机器证据为主**：`code-review.md` 的 `## UI fidelity` 逐 PAGE 数值直接从 JSON 抄录，只有存在差异/`UI-DERIVED` 的 PAGE 才需要人工说明与审批人；09 在 `independent-verification.json` 的 `layout_checks` 独立重跑并核验（缺失、超差或未批准差异不得 PASS），人工抽查仅限差异/`UI-DERIVED` PAGE；10 在 `acceptance.md` 的 `## UI acceptance` 逐 PAGE 签收，无差异且机器 PASS 的 PAGE 可按机器证据批量签收，仅差异/`UI-DERIVED` PAGE 需并排核对。**全流程不保存截图；截图不是 UI 证据。** 缺失这些 UI 数值证据不得推进对应阶段或归档。
  - PAGE ID 与页面集合在 06 冻结；不得新增或重命名 PAGE。Figma 未定义的弹窗/抽屉/状态必须新增 Figma 画板，或以 `UI-DERIVED` 记录视觉规格、审批人与理由。
  - 不再使用 pen.dev、`prototype.pen`、`PAGE-*.html`、`prototype.md`、`manifest.json`、`design/design-tokens.json` 或分散的 token/contract JSON。
- 测试用例矩阵放 `design/test-cases.csv`，TEST ID 必须回链 AC/PAGE/BLOCK/API/IO，并写入唯一 `traceability.csv`；不得只把测试写在 design.md 叙述里。

## OpenSpec 约定

- 配置见 `openspec/config.yaml`（schema: spec-driven）；标准 artifact 为 `proposal.md`、`specs/<capability>/spec.md`、`design.md`、`tasks.md`。
- `tasks.md` 必须使用 `- [ ]` / `- [x]` 复选框。
- specs 只写外部可观察行为；类名/框架/实现步骤放 design.md。
- 每个 OpenAPI `operationId` 必须在 `design/api-io-mapping.csv` 映射到至少一个真实 IO，IO 契约写在 `design/io-catalog.csv`。
- 归档（openspec archive）前必须人工批准，不得用 `-y` 绕过。

## 检查脚本

- 包自检：`python3 scripts/check-package.py`
- 下一阶段建议（只读）：`python3 scripts/next-step.py`
- 基线文件检查：`bash scripts/check-required-files.sh`
- 各阶段校验命令见 `scripts/README.md`；脚本 fail-closed，不可伪造通过结果。

## 语言与风格

- 项目输出语言默认中文；代码、API 字段和标识符遵循仓库已有规范（当前 PENDING，待首个功能实现时确定）。

## Agent 行为边界

- 不自动安装依赖、不提交代码、不改 CI、不归档、不发布，不替业务/设计/架构负责人批准未决规则。
- 不覆盖既有文件；覆盖/修改既有 AGENTS.md 或配置前需用户批准。
- Superpowers 技能名会随版本演进，实施时先确认真实安装与可用性，缺失时如实报告。
- 外部工具（pen.dev、Figma MCP）以实际可访问能力为准，不得把不可读取的链接/字段当作已审查。
