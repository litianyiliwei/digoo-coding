> 托管块 — 由 `scripts/toolkit-sync.py` 安装与更新；不要编辑 `toolkit:begin` / `toolkit:end` 标记内部。项目专属约定写在块外。

## 流程入口

- 当用户说"下一步/继续/接着做"时，先加载 `workflow-orchestrator` Skill（或 `prompts/00-next-step.md`），依据 `workflow-state.json` 与真实产物判定唯一安全的下一阶段。
- 每阶段开始前读取 `process/STEP-ARTIFACT-CONTRACTS-zh.md` 与 `process/STEP-ARTIFACT-CONTRACTS.json` 中对应 Skill 的契约记录。
- 阶段结束使用 `templates/workflow/step-handoff-report.md` 展示交接报告；产物必须落盘到契约指定路径，不得只在聊天中输出。

## 阶段边界与评审停等（强制）

- **阶段完成 ≠ 可进入下一阶段。** 产物写完、检查通过只代表“可送审”，不代表已批准。未获用户明确批准前，禁止读取或执行下一阶段 Prompt/Skill、禁止创建下一阶段产物、禁止调用下一阶段工具。
- **开始任何阶段前** 必须运行 `python scripts/workflow.py check-entry --step <step-id> [--change-id <id>]`；退出码非 0 时立即停止并报告阻断原因，不得绕过。v2 状态中每个 Change 有独立泳道；05–10 阶段必须传 `--change-id`。
- **启动 Change 必须经过依赖门禁**：运行 `python scripts/workflow.py start-change --change-id <id>`。项目 01–04 未完成、基线未冻结、Change 不在 roadmap 主表或已批准 amendment、或任一 `Dependencies` / `Depends On` 前置未在 10 阶段验收交付（含传递链）时，命令 fail-closed 拒绝，并输出 `ACTIVE@<阶段>` / `NOT_STARTED` / `ABANDONED` / `BROKEN`。只有用户明确指示时才能使用豁免，且必须提供理由与证据；05 入口与 08 入口会再次核对依赖。
- **每个阶段结束流程（顺序不可变）：**
  1. 生成 `workflow/evidence/<step-id>.json`（v2 项目阶段：`workflow/evidence/project/<step-id>.json`；v2 Change 阶段：`workflow/evidence/<change-id>/<step-id>.json`）并运行该阶段全部检查脚本；
  2. 运行 `python scripts/workflow.py request-review --step <step-id> [--change-id <id>] --evidence <证据路径> --summary "<送审摘要>"`，生成固定产物哈希的评审包，并把该泳道冻结为“待评审”（`current_step` 不前进）；
  3. 按 `templates/workflow/step-handoff-report.md` 展示交接报告（产物路径、摘要、检查结果/退出码、待确认项、下一阶段输入）后**立即结束回合**，不得继续。
- **只有用户明确批准待评审阶段（任何无歧义的表述都算；沉默或检查通过不算）后**，才可运行 `python scripts/workflow.py approve --step <step-id> [--change-id <id>] --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>`，再运行 `transition --step <step-id> [--change-id <id>] --evidence <阶段证据>`。不得自行填写 approver/approved_at，不得把“产物完成”“检查通过”或 Agent 自己的判断当作批准。
- **检查在阶段结束时、`request-review` 之前运行。** 评审包会锁定每个已声明阶段产物的 SHA-256。用户若在评审后修改产物，`approve`/`transition` 会因哈希不一致而失败，必须重新评审并生成新的检查结果；下一阶段的 `check-entry` 校验上游交接哈希，而不是重跑上一阶段检查。因此门禁归属于评审边界，而不只是下一阶段入口。
- 默认 `approval_policy` 为 `standard`。risk-based 快车道需用户通过 `python scripts/workflow.py set-approval-policy --policy risk-based --reason "<原因>" --by "<用户>"` 主动开启；低风险阶段（01 初始化、04 路线图、06 Figma）门禁通过后可直接 transition，无需记录审批；高风险阶段仍保持审批要求。不得把该策略理解为整体放弃人工评审。
- **08（实现）与 09（独立验证）同样必须等待用户评审**；09 由独立 Verifier 在独立上下文完成，Builder 不得在同一会话代跑验证并自动进入 10。
- **静态分析门禁**：当 `docs/architecture/quality-gates.json` 存在时，08/09 门禁集合包含静态分析证据（08 为 `openspec/changes/<change-id>/design/evidence/static-analysis.json`，09 为 `static-analysis-independent.json`）；仅在该 gates 文件存在后门禁生效，不存在时无静态门禁。
- **06 为条件阶段**：无 UI 的 Change 必须先在 `design/figma-audit.md` 写 `- Design source status: N/A` 与 `- Reason for no UI: <理由>`，再运行 `python scripts/check-figma-audit.py --change <change-id> --strict --no-ui --reason "<理由>"`，然后运行 `workflow.py skip-stage --step 06-figma-design-review [--change-id <id>] --evidence workflow/evidence/<change-id>/06-figma-design-review-skip.json`；有 UI 的 Change 必须完成完整 Figma 评审，且 evidence 要设置 `approval.required=true`。
- 某一泳道的 `pending_approvals` 非空时，该泳道不得推进；项目泳道的待审批项会阻止所有 Change 泳道。`workflow-state.json` 只能由 `workflow.py` 命令（`upgrade-state`/`start-change`/`request-review`/`approve`/`transition`/`reopen`/`skip-stage`/`reset-state`/`migrate-state`/`abandon-change`）写入，`check-entry` 与 `list-changes` 为只读命令；禁止直接编辑状态文件。
- Claude Code 下由 `.claude/settings.json` 的 PreToolUse hook 拒绝写入当前阶段之后的阶段产物、已完成阶段中非 volatile 的产物、待评审期间当前阶段的声明产物，以及直接编辑 `workflow-state.json`。被拒绝时必须停止并说明，不得绕过（更换写入路径、禁用 hook 或改用其他工具规避均属违规）。Bash 驱动的写入不在该 hook 拦截范围内，属于已记录的信任边界。
- 交接只对已批准的决策/验收产物做哈希。机器管理或生成的文件（`workflow-state.json`、`AGENTS.md`、baseline status/manifest/registry、`BASELINE-INDEX.md`、`toolchain-report.md`）为 volatile：handoff 只验证存在，不校验哈希。契约未声明的额外 evidence 输出仅用于审计，不得使已评审交接失效。

## 模板与产物规则

- 正式产物遵循 `process/TEMPLATE-POLICY-zh.md` 与 `process/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不得删除模板字段；未知项写 `PENDING` 并说明原因与责任人/阻塞条件；不适用项写 `N/A` 并写理由。送审阶段的严格门禁产物中不得残留 `PENDING`/`TODO`/`TBD`：先与用户确认取值，或把问题移入 `docs/product/open-questions.md`。
- `docs/product/open-questions.md` 在阶段内为追加式：新问题须带 owner 与阻塞条件追加；已有问题只能由其 owner/用户答复或关闭。阶段不得替用户裁决未决问题。
- 阶段 02/03/04/05/07/10 开始前先读 `docs/product/BASELINE-BRIEF.md`、`change-sizing.md`、`id-conventions.md`；详细基线按 Change 影响面加载，不整包塞入上下文。基线产物缺失或 `check-requirements.py` 未通过时不得进入下游阶段。
- 项目级基线放 `docs/product/`、`docs/architecture/`、`docs/adr/`；单个功能内容放 `openspec/changes/<change-id>/`。
- 每份 Markdown 正式产物开头注明：Change ID（若适用）、状态、来源基线、关联需求/AC ID、生成日期或版本。
- 阶段 02 必须加载本地方法 Skill `competitor-research`，询问用户是否存在同类产品/竞品/相似系统；存在参考产品时至少调研一个同类产品，并在 `docs/product/reference-research.md` 写入 `## 9. 同类产品偏差确认`；重大偏差必须在评审前取得用户明确确认（确认人+日期），否则 `python scripts/check-reference-research.py --strict` 不通过。
- UI 相关 Change 的界面阶段（06）以 HTML 为主（Figma 可选）：
  - 默认来源：在 `openspec/changes/<change-id>/design/ui-html/` 产出按平台的自包含高保真 HTML 设计稿（每个声明平台每个 PAGE 一个 HTML 文件，外加评审入口 `index.html`、`README.md` 与 `tokens.css`），并写明唯一的 HTML 来源：用户直接提供、AI 按需求生成，或由 Figma-to-HTML 转换。设计负责人在 HTML 评审入口完成 UI 评审。Figma 是 Figma-to-HTML 路径的上游输入，不是单独的评审交付物；HTML 由用户提供或 AI 生成时不得强制依赖 Figma MCP。
  - 目标平台：读取 `design/user-stories.md` 的 `- Target platforms:`（规范值 `web|h5|mini-program|app|android|ios|harmonyos|desktop|pda`）；每个声明平台至少有一个 PAGE；PAGE ID 全局唯一并在 06 冻结。
  - **框架对齐转码（强制）**：按 `docs/architecture/technology-decisions.md` 确定目标框架，并把每个 HTML 页面（或可选 Figma 来源在加载官方 `figma-design-to-code` Skill 后的 `get_design_context` 参考实现）转码为目标框架设计代码：Vue 栈 `.vue`，使用该端组件库（Web 为 Element Plus，移动端为 uni-app）与项目 token；React 栈 `.tsx`/`.jsx`。`design/figma-code/README.md` 记录目标框架、扩展名、替换与偏差；08 只补业务逻辑，不重写样式/布局/文案。
  - 契约：唯一单文件 `design/figma-audit.md`（设计来源/平台选择、token **实际值**、文字样式、每 PAGE 区块规格、设计代码说明、断言范围、状态覆盖与决策、需求覆盖矩阵（每个 AC/US 在每个声明平台 FULL 或 N/A + 理由，每个 PAGE 反向映射，覆盖评审 APPROVED）、资产清单、HTML 渲染量测记录或 MCP 读取记录、UI 评审 APPROVED）；`design/ui-html/`（默认 HTML 来源）；`design/figma-code/`；`design/figma-layout.csv`（每 PAGE 的 `platform`/`viewport` 与几何/文本/字体断言；HTML 模式下 `figma_node_id` 填 HTML `data-node-id`）。真实图片/SVG 资产放 `design/figma-assets/`。**截图不是契约、资产或门禁证据，且全程不保存。**
  - 06 一次性生成；07/08 默认离线消费，仅在来源变化或页面有歧义时按页重读（串行）。07 建 token → CSS/主题映射，填 `route`/`dom_selector`，创建 `design/ui-actions.csv` 把每个功能控件映射到跳转地址+入参、OpenAPI operationId 或用户已确认的本地动作，并定义响应式规则；`check-ui-actions.py --change <change-id> --strict` 必须通过。08 以目标框架设计代码为页面骨架，运行 `check-figma-layout.py`（各页视口取自 CSV）与 `check-design-tokens.py`，并从 JSON 抄录数值化 `## UI fidelity`（仅差异/`UI-DERIVED` PAGE 需人工说明）。09 独立重跑 `layout_checks`；10 逐 PAGE 签收，机器无差异的 PAGE 批量签收，差异/`UI-DERIVED` PAGE 并排核对。缺失 UI 数值证据不得推进阶段。
  - PAGE ID 与按平台页面集合在 06 冻结；未定义的弹窗/状态必须新增设计页面，或以 `UI-DERIVED` 记录规格、审批人与理由。不再使用 pen.dev、`prototype.pen`、`PAGE-*.html` 交接原型、`prototype.md`、`manifest.json`、`design/design-tokens.json` 或分散 token/contract JSON。
- 测试用例矩阵放 `openspec/changes/<change-id>/design/test-cases.csv`，TEST ID 必须回链 AC/PAGE/BLOCK/API/IO，并写入唯一 `traceability.csv`；不得只把测试写在 design.md 叙述里。

## 模块包与 Change 切片（强制）

- 代码归属遵循 `docs/architecture/code-layout.json` 的 `strategy`：`module-packages`（新项目默认；前端 `领域/模块`，后端 `领域/模块/资源`，**一个模块 = 一个有界业务子域**）、`footprint`（只做切片与 diff）或 `none`（模块/切片门禁跳过并标注 `SKIPPED (strategy none)`；缺失布局文件视为 `none`）。布局文件只通过基线变更流程修改。既有领域内新增模块不需要基线变更；新增领域或修改共享契约需要。
- 阶段 04 创建/更新产品级可变注册表 `docs/product/capabilities.csv`（能力进度：属主/附属模块、已交付/剩余切片、活跃 Change）与 `docs/product/modules.csv`（模块归属：路径、共享路径、能力、状态），并填满每条 roadmap 行的 `Primary Capability`、`Owner Module`、`Related Modules`、`Slice Type`、`Slice Coverage`、`Code Target`、`Demo Path`、`Slice Budget`。检查：`python scripts/check-capabilities.py`、`python scripts/check-modules.py`、`python scripts/check-roadmap.py --strict`。
- 阶段 05 使 `proposal.md` 的 `### New Capabilities` / `### Modified Capabilities` 与 roadmap 行一致；每个 AC 写 `- Scenario:` 与 `- Slice position: entry|behavior|result`；写 `## Acceptance Walkthrough`（三种切片位置各至少一个 AC）与 `## Slice Budget`；新增能力或模块时同时更新两份注册表：`docs/product/capabilities.csv`（slug、领域、`owner_module`、`related_modules`、`status`、`active_changes`、`remaining_slices`）与 `docs/product/modules.csv`（slug、领域、前后端路径、`shared_paths`、`capabilities`、`status`）；属主模块的 `capabilities` 必须列出该能力。roadmap 主表外的 Change 必须在 `## Roadmap Amendments` 增加已批准行（理由/申请人/批准人/日期/基线影响）；只有 `BASELINE_CHANGE_REQUIRED` 才走 BCR/ADR。检查：`python scripts/check-requirements.py --change <change-id> --strict`，以及 `python scripts/check-capabilities.py` 与 `python scripts/check-modules.py`。
- 阶段 07 在 `## Design Decisions` 下写 `### Implementation Slice`，字段为 `Primary capability`、`Owner module`、`Related modules`、`Slice type/coverage`、`Code packages`、`Owned paths`、`Integration paths`、`Module card`（可选 `Frozen approvals`、`Out of context`）；owned 路径可以 `/**` 结尾。检查：`python scripts/check-design-sections.py --change <change-id>`。
- 阶段 08 编码前运行 `python scripts/implementation-snapshot.py <change-id>`，再运行 `python scripts/code-context.py <change-id>`；读取上下文清单的 read set，清单外读取必须记为 `CONTEXT_EXPANSION` 并写理由；创建/更新 `<module_path>/MODULE.md` 模块卡；改动保持在切片内（`shared_paths` 需在切片中有 owned 条目，`frozen_paths` 需已批准 BCR）；结束时运行 `python scripts/check-change-footprint.py <change-id>`。
- 阶段 10 按 `## Acceptance Walkthrough` 验收，回写 `docs/product/capabilities.csv` 与 `docs/product/modules.csv`，并运行 `python scripts/check-capabilities.py --completed <change-id>`，适用时运行 `python scripts/check-modules.py --completed <module-slug>`。
- **07→08（切片声明）与 08→09（footprint）是 `workflow.py transition` 硬门禁**；`strategy=none` 时两者均跳过并显式标注，`footprint` 仅要求 owned/integration 路径。实现租约在 07→08 transition 全部门禁通过后获取，并持有到该泳道到达 10、被 abandon，或 ACCEPTED 泳道被 reopen：`none` 策略同一时间只允许一个 Change 持有实现租约；`footprint`/`module-packages` 仅当所有参与泳道都有有效声明且 owned/integration 路径互不重叠时才允许并行实现，否则以 `IMPLEMENTATION_LEASE_HELD` 拒绝，直到持有者到达 10 或被 abandon。

## OpenSpec 约定

- 配置见 `openspec/config.yaml`（schema: spec-driven）；标准 artifact 为 `proposal.md`、`specs/<capability>/spec.md`、`design.md`、`tasks.md`。
- `tasks.md` 必须使用 `- [ ]` / `- [x]` 复选框。
- specs 只写外部可观察行为；类名/框架/实现步骤放 design.md。
- 每个 OpenAPI `operationId` 必须在 `design/api-io-mapping.csv` 映射到至少一个真实 IO，IO 契约写在 `design/io-catalog.csv`。
- 归档（openspec archive）前必须人工批准，不得用 `-y` 绕过。

## 检查脚本

- 包自检：`python scripts/check-package.py`
- 下一阶段建议（只读）：`python scripts/next-step.py`
- 基线文件检查：`bash scripts/check-required-files.sh`
- 各阶段校验命令见 `scripts/README-zh.md`；脚本 fail-closed，不可伪造通过结果。
- 参考调研与 UI 控件检查：`python scripts/check-reference-research.py --strict`（同类产品 + 用户已确认的重大偏差）与 `python scripts/check-ui-actions.py --change <change-id> --strict`（按钮/图标跳转或 API 映射）。
- 本地方法 Skill：`competitor-research`（阶段 02）、`existing-code-impact-analysis`（阶段 07）、`baseline-impact-classification`（阶段 05/07/10）。在要求的阶段加载；其 `methods` 证据由 `python scripts/check-method-evidence.py --step <step-id> --evidence <evidence.json>` 校验。

## 语言与风格

- 仓库文档、Prompt、Skill 与模板以英文为主；流程文档的简体中文译本使用同路径加 `-zh.md`。
- 正式项目产物与 Agent 回复按用户习惯的语言输出；代码、API 字段和标识符遵循仓库已有规范（当前 PENDING，待首个功能实现时确定）。

## Agent 行为边界

- 不自动安装依赖、不提交代码、不改 CI、不归档、不发布，不替业务/设计/架构负责人批准未决规则。
- 不覆盖既有文件；覆盖/修改既有 AGENTS.md 或配置前需用户批准。
- Superpowers 技能名会随版本演进，实施时先确认真实安装与可用性，缺失时如实报告。
- 外部工具（Figma MCP）以实际可访问能力为准，不得把不可读取的链接/字段当作已审查。
