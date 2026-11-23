# 阶段、Skill、Prompt 与 Script 对照

> 语言：简体中文 ｜ [English](PROCESS-MAP.md)

| 阶段 | Skill ID | Prompt 文件 | 自动检查 |
|---|---|---|---|
| 01 项目初始化与工具链检查 | `project-bootstrap` | `prompts/01-project-bootstrap.md` | `scripts/check-package.py` + 按选定/现有语言探测静态分析工具并记录到 `docs/project/toolchain-report.md`（`Static Analysis Toolchain` 表与“静态分析配置存在性”说明；不安装任何工具） |
| 02 需求业务梳理 | `requirements-analysis` | `prompts/02-requirements-analysis.md` | `scripts/check-requirements.py --strict`（流程节点、数据对象、RD 矩阵结构）+ `python scripts/check-reference-research.py --strict`（参考产品与互联网调研：≥3 个问题、≥3 条来源、≥2 条对比；存在参考产品时至少 1 个同类产品、≥2 条同类产品偏差行，重大偏差须有用户明确确认） |
| 03 项目总体架构设计 | `project-architecture-baseline` | `prompts/03-project-architecture-baseline.md` | `scripts/check-required-files.sh --strict` + `python scripts/check-quality-gates.py --root . --strict`（采用时：quality-gates.json 结构与选型，阶段 03 不要求栈目录已物化；文件不存在时报告 NOT_ADOPTED 并通过） + `python scripts/check-architecture-baseline.py --strict`（现有系统二开约束/第三方接口依赖清单/LEGACY-*/EXT-*） + 技术选型访谈记录 + 阶段结束审计 `baseline-governance.py freeze` / `audit --require-frozen`（采用时同时作为门禁文件的批准） + `docs/architecture/code-layout.json` 的结构、策略枚举与路径合法性在 04/05 首次消费时由 `check-capabilities.py` / `check-modules.py` / `check-roadmap.py` 校验（格式错误的布局 fail-closed） |
| 04 提案拆分、依赖排序与路线图 | `proposal-planning` | `prompts/04-proposal-planning.md` | `baseline-governance.py audit --require-frozen` + `scripts/check-roadmap.py --strict`（模块列对照注册表校验） + `scripts/check-capabilities.py` + `scripts/check-modules.py` |
| 05 提案级需求分析 | `feature-requirements` | `prompts/05-feature-requirements.md` | `scripts/check-requirements.py --change <change-id> --strict`（UC 可选）+ `baseline-governance.py check-change --phase requirement` + `scripts/check-baseline-impact.py <change-id>` + `scripts/check-capabilities.py` + `scripts/check-modules.py` + 写入 `## Roadmap Amendments` 行时 `scripts/check-roadmap.py --strict` |
| 06 Figma 设计与评审（Figma-only） | `figma-design-review` | `prompts/06-figma-design-review.md` | `scripts/check-figma-audit.py --change <change-id> --strict --require-framework`（目标框架/转码说明 + 单文件 token 实际值 + 每 PAGE 区块规格 + figma-code/ 目标框架设计代码 + figma-layout.csv 断言映射 + 断言范围理由 + 状态决策 + UI 评审 APPROVED） |
| 07 详细设计、接口与测试设计 | `detailed-design` | `prompts/07-detailed-design.md` | 涉及 UI 时读取 `figma-audit.md` 的 token 实际值、每 PAGE 规格、状态决策与 `figma-assets/`；默认离线消费，仅在版本变化/歧义时按页重读并避免限流；`openspec instructions design --change <change-id> --json` + `scripts/check-change.sh <change-id>` + `scripts/check-design-assets.sh <change-id> --strict --lint-api` + `scripts/check-design-sections.py --change <change-id>` + `scripts/check-test-cases.py --change <change-id> --strict` + `scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict` + 有 API 时 `scripts/check-api-traceability.py --change <change-id>` + `openspec validate <change-id> --strict` + `baseline-governance.py check-change --phase design` + 有跨边界接口时 `scripts/check-interface-catalog.py --change <change-id> --strict` + 涉及 UI 时 `scripts/check-ui-actions.py --change <change-id> --strict`（每个功能按钮/图标/链接/菜单/标签页映射到跳转地址+入参或 OpenAPI operationId，否则须用户确认本地动作） + `scripts/check-design-sections.py --change <change-id> --slice-only` + `scripts/check-change-footprint.py <change-id> --declaration-only`（07→08 `### Implementation Slice` 硬门禁；`workflow.py transition` 自动运行 slice-only 检查） |
| 08 实现、TDD、验证与代码审查 | `implementation-orchestrator` | `prompts/08-implementation-orchestrator.md` | `baseline-governance.py check-change --phase implementation` + `scripts/test-all.sh` + `verify-before-completion.sh` + `docs/architecture/quality-gates.json` 存在时的静态分析：`python scripts/check-quality-gates.py --root . --strict --require-materialized` + `python scripts/run-quality-gates.py <change-id> --output openspec/changes/<change-id>/design/evidence/static-analysis.json --identity <builder>` + `python scripts/check-static-analysis.py --change <change-id> --strict` + `scripts/check-figma-layout.py` + `scripts/check-design-tokens.py` + `scripts/check-code-review.py --change <change-id> --strict`（UI Change 直接移植目标框架设计代码，## UI fidelity 数值取自 figma-layout-check.json，仅差异/UI-DERIVED PAGE 需人工说明；启用门禁时 ## Static analysis 行从 static-analysis.json 复制） + `python scripts/implementation-snapshot.py <change-id>`（入口快照） + `python scripts/code-context.py <change-id>`（检索清单） + `python scripts/check-change-footprint.py <change-id>`（写入 implementation-diff.json；08→09 硬门禁在 transition 时运行 `--verify`） |
| 09 独立验证与验收证据 | `independent-verifier` | `prompts/09-independent-verification.md` | `openspec status --change <change-id>` + `openspec validate <change-id> --strict` + `scripts/check-independent-verification.py --report <report> --evidence <json>`（UI Change 校验 layout_checks 逐 PAGE 断言元素数/最大偏差/容差/缺失元素/判定与独立重跑记录）；`docs/architecture/quality-gates.json` 存在时：`python scripts/run-quality-gates.py <change-id> --independent --identity <verifier> --builder-identity <08 builder> --output openspec/changes/<change-id>/design/evidence/static-analysis-independent.json` + `python scripts/check-static-analysis.py --change <change-id> --expect-independent`；PASS 后才进入阶段 10 + `scripts/check-change-footprint.py <change-id> --verify`（08→09 硬门禁：对照 `implementation-base.json` 重算工作区差异，与 `implementation-diff.json` 比较排序后的 changed-path 集合与 `diff_sha256`，并重跑切片分类） |
| 10 人工验收、归档与基线回写 | `acceptance-audit` | `prompts/10-acceptance-audit.md` | `baseline-governance.py check-change --phase acceptance` + `scripts/check-acceptance.py <change-id>` + `verify-before-completion.sh`（`docs/architecture/quality-gates.json` 存在时默认运行静态门禁；`--skip-static` 不属于完整验证） + `## Static analysis` 静态证据核对（非 PASS、门禁漂移或豁免过期/无效时阻断验收） + `python scripts/check-capabilities.py --completed <change-id>` + `python scripts/check-modules.py --completed <module-slug>`（Change 完成某个模块时） |

## 方法与证据门禁

- 02–10 的阶段 evidence 必须包含 `methods` 块；`python scripts/check-method-evidence.py --step <step-id> --evidence <evidence.json>` 可单独校验，`workflow.py transition` 会自动调用同一逻辑。
- 02/03/05/07 的逐阶段问题清单（`process/QUESTION-COVERAGE-CHECKLIST-zh.md`）是建议提问指引，不是逐项硬门禁。阶段证据可选包含 `question_coverage` 块；若提供，`scripts/check-question-coverage.py` 会做形状校验，`workflow.py request-review` / `transition` 自动复核同一个可选块。待确认问题必须写入 `docs/product/open-questions.md`，写明 owner 与阻塞条件。
- 02/03/04/05/07 的 `brainstorming` 必须记录到 evidence 的 `methods` 块，结论落入阶段产物；不设问题/备选/决策的最少数量。缺少方法记录、证据路径或落点章节时不得推进。
- 03 必须沟通“新系统 / 基于现有系统二开 / 混合、代码地址、第三方接口”：二开时实际读取代码并写入 `technology-decisions.md` 的“现有系统二开约束”与 `constraint-registry.json` 的 `LEGACY-*`；第三方接口写入“第三方接口依赖清单”、EXTERNAL 数据流与 API 约定。
- 07 必须沟通“修改现有功能代码 / 新功能开发、代码地址、第三方接口”：修改现有功能时实际读取代码并写入 `design.md` 的 `### 现有代码变更影响`；第三方接口写入 `interface-catalog.csv` 的 `THIRD_PARTY_API` 行与 test/fakes 证据。
- 07 存在 HTTP API、原生桥接、设备、第三方、异步或文件边界时，必须生成 `design/interface-catalog.csv` 并运行 `check-interface-catalog.py --change <change-id> --strict`；仅 HTTP API 的 Change 也要在目录中登记 `HTTP_API` 行。
- OpenSpec/Superpowers 的逐阶段允许/禁止范围见 `process/SUPERPOWERS-MAPPING.md` 的“OpenSpec 参与矩阵”与“阶段内方法模式”。

## 模块包与切片门禁

- `docs/architecture/code-layout.json` 的 `strategy` 选择 `module-packages`（新项目默认）、`footprint` 或 `none`；缺少布局文件按 `none` 处理，格式错误则 fail-closed。
- 07→08：07 的 `workflow.py transition` 运行 `scripts/check-design-sections.py --change <change-id> --slice-only`；`design.md` 的 `### Implementation Slice` 必须声明主能力、归属/关联模块、切片类型/覆盖、代码包、拥有/集成路径与模块卡动作。
- 08→09：08 的 `workflow.py transition` 运行 `scripts/check-change-footprint.py <change-id> --verify`；落地差异必须位于声明的 footprint 内，且与对照 `implementation-base.json` 重算的 `implementation-diff.json` 一致。
- `strategy=none` 时两次 transition 都打印 `FOOTPRINT_GATE=SKIPPED (strategy none)` 并继续；`check-capabilities.py`、`check-modules.py` 与 `check-roadmap.py` 同样跳过注册表规则。

## 上下文预算

- 契约 `inputs` 是完整审计/溯源集；默认读取以 `input_policy.stage_profiles.lean` 为准（建议值：每阶段约 8 个读取组、约 16000 字符）。
- 读序：`BASELINE-BRIEF` → 当前 Change 产物 → 按命中 ID 定向读行/章节 → 完整基线/架构/ADR/完整 specs 仅在必要时按需读并记录原因。
- 运行 `python scripts/agent-context.py --stage <id> --change <change-id>` 获取精简包；`--full` 仅用于交接审计。超出建议值时只报警告并继续。
- 输出采用引用式输出，不复制输入全文；`output_policy.summary_budgets` 是建议行数，`check-output-context.py` 默认只报警告。完整规则见 `process/INPUT-OUTPUT-POLICY.md`。

## 检查策略说明

> 说明：项目级与提案级都不产出 `use-cases` 文件。项目级用 FLOW/NODE 表达业务流程；提案级用例场景统一写在 delta spec 的 Scenario，US/AC 保留在 `design/user-stories.md`。

需求澄清、客户沟通、Figma 视觉与架构合理性不能由通用 Shell 脚本可靠判定；这些阶段有明确交付物和人工评审清单，而不是伪造一个自动化“通过”。

正式产物的模板等级与路径请参照 `process/TEMPLATE-POLICY-zh.md` 和 `process/OUTPUT-TEMPLATE-MATRIX.csv`；变更模板目录后运行 `python3 scripts/check-output-template-matrix.py`。详细设计合并到 `design.md` 五节，API→IO 映射仅在存在 API 时强制。

## 项目基线与功能 Change 的交互

- 阶段 04：按每个候选 Change 初步读取冻结基线，识别适用域、约束复用和潜在修订；在路线图中体现。
- 阶段 05：强制创建 `openspec/changes/<change-id>/design/baseline-impact.md`，记录基线版本、文件/章节/ID、适用约束、复用项、冲突及分类。
- 阶段 06–07：按设计域重新核验基线版本；基线变化必须得出 `NO_IMPACT` 或 `REBASE_REQUIRED`。
- 阶段 08：遵循已批准基线；实现发现冲突时暂停受影响任务、提交 BCR/ADR，不得直接编辑冻结基线。
- 阶段 10：只回写已批准、已实现、已验证且可跨功能复用的决策；功能特有细节保留在归档 Change。
- 完整规则：`process/BASELINE-FEATURE-INTERACTION-zh.md`；Change 记录模板：`templates/change-assets/design/baseline-impact.md`。

## 对话式继续流程

- 在具备仓库访问和工具执行能力的 Agent 中，使用 `prompts/00-next-step.md` 或说“下一步”。
- `workflow-state.json` 只用于定位；AI 必须检查真实文件、审批记录与 OpenSpec CLI 状态。
- 项目基线阶段与功能 Change 阶段不同：需求业务梳理阶段只读取现有 OpenSpec specs；提案获批后才创建 Change。
- 有 pending approval、阻断项、前置产物缺失或 CLI 验证失败时，不能自动前进。

## 强制输入/输出交接

每个阶段的正式输入、正式输出、下游消费关系、审批点与质量门禁，以 `process/STEP-ARTIFACT-CONTRACTS-zh.md` 和机器可读的 `process/STEP-ARTIFACT-CONTRACTS.json` 为准。每个 Skill/Prompt 均内嵌对应契约引用。阶段结束必须展示 `templates/workflow/step-handoff-report.md`；未批准产物不得作为下一阶段正式输入。

涉及 UI 时，阶段 06 的唯一 UI 契约是单文件 `design/figma-audit.md`（目标框架/转码说明、token 实际值、文字样式、每 PAGE 区块规格、状态决策、设计代码、断言范围、UI 评审 APPROVED）与 `design/figma-code/`（06 按总体技术选型转码的目标框架设计代码：Vue 栈 `.vue` + Element Plus，React 栈 `.tsx`/`.jsx`）、`design/figma-layout.csv`（运行态断言映射）；07/08 默认离线消费，仅在 Figma 文件版本变化或页面有歧义时按页批量重读（串行、避免限流）。07 以设计代码为基线填写 `### PAGE→BLOCK→组件映射`（只登记业务化适配与 `UI-DEVIATION`），填满 `route`/`dom_selector`，创建 `design/ui-actions.csv` 将每个功能按钮/图标/链接/菜单/标签页映射到跳转地址+入参或 OpenAPI operationId（本地动作须用户确认），`### 事件处理` 写 handler 行为并按 `element_id` 引用 CSV 行、不重复动作映射，并定义响应式规则；08 直接移植设计代码、只补业务逻辑，运行 `check-figma-layout.py` 与 `check-design-tokens.py`，`code-review.md` 的 `## UI fidelity` 数值直接取自 `figma-layout-check.json`；09 在 `layout_checks` 独立重跑核验，人工抽查仅限差异/`UI-DERIVED`/未断言 PAGE（缺失/超差/未批准差异不得 PASS）；10 无差异 PAGE 按机器证据批量签收，差异/`UI-DERIVED` PAGE 并排核对后在 `## UI acceptance` 签收。**全流程不保存截图。** Figma 评审稿是视觉/组件/变量最终权威，PAGE ID 由 06 冻结。不再使用 pen.dev、prototype.pen、PAGE-*.html、prototype.md、manifest.json、design-tokens.json、page-inventory/block-inventory/interaction-map/design-spec/figma-handoff。

## P0 Runtime Governance

- 阶段 DAG 以 `process/WORKFLOW-STAGES.json` 为准；状态转换只能通过 `scripts/workflow.py transition`。
- 每次成功转换生成 SHA-256 handoff manifest；下游入口自动核验上游交接文件未漂移；被后续阶段声明为输出的产物标记为 `mutable_by_design`，只核验存在性。
- 阶段 08 实施后必须经过阶段 09 独立只读验证，PASS 后才进入阶段 10。
- 返工使用 `workflow.py reopen --step <id> --reason <原因>`；当前 Change 验收后使用 `workflow.py next-change --change-id <id>` 开始下一个 Change。
- 详细命令、Evidence JSON 和限制见 `process/P0-RUNTIME-GOVERNANCE-zh.md`。

## Baseline Governance Engine 门禁

- 项目基线冻结：`baseline-governance.py freeze` / `audit --require-frozen`；脚本核对各域状态、审批证据、约束来源和 SHA-256。
- 项目基线修订：`open-amendment` 先将总体状态切换为 UNDER_AMENDMENT；修订期间所有 Change 阶段阻断；`close-amendment` 只有在受影响域版本升级、哈希刷新和审批证据齐全后才重新冻结。
- Change 绑定：阶段 05 自动创建 `baseline-binding.json`，按 manifest `governance_profile` 建立约束记录（`standard` 全部 ACTIVE，`lite` 仅 `critical: true`）；阶段 06–07 由设计证据门禁，阶段 08/09 由实现证据门禁，阶段 10 由验收门禁。
- 完整使用规则见 `process/BASELINE-FEATURE-INTERACTION-zh.md` 第 9 节；自动化检查并不等同于审批身份认证，仍须使用受保护分支/CI/CODEOWNERS。
