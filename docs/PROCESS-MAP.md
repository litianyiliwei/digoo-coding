# 阶段、Skill、Prompt 与 Script 对照

| 阶段 | Skill ID | Prompt 文件 | 自动检查 |
|---|---|---|---|
| 01 项目初始化与工具链检查 | `project-bootstrap` | `prompts/01-project-bootstrap.md` | `scripts/check-package.py` |
| 02 需求业务梳理 | `requirements-analysis` | `prompts/02-requirements-analysis.md` | `scripts/check-requirements.py --strict`（流程节点、数据对象、RD 矩阵结构）+ `python scripts/check-reference-research.py --strict`（参考产品与互联网调研：≥3 个问题、≥3 条来源、≥2 条对比） |
| 03 项目总体架构设计 | `project-architecture-baseline` | `prompts/03-project-architecture-baseline.md` | `scripts/check-required-files.sh --strict` + `python scripts/check-architecture-baseline.py --strict`（现有系统二开约束/第三方接口依赖清单/LEGACY-*/EXT-*） + 技术选型访谈记录 + 阶段结束审计 `baseline-governance.py freeze` / `audit --require-frozen` |
| 04 提案拆分、依赖排序与路线图 | `proposal-planning` | `prompts/04-proposal-planning.md` | `baseline-governance.py audit --require-frozen` + `scripts/check-roadmap.py --strict` |
| 05 提案级需求分析 | `feature-requirements` | `prompts/05-feature-requirements.md` | `scripts/check-requirements.py --change <change-id> --strict`（UC 可选）+ `baseline-governance.py check-change --phase requirement` + `scripts/check-baseline-impact.py <change-id>` |
| 06 Figma 设计与评审（Figma-only） | `figma-design-review` | `prompts/06-figma-design-review.md` | `scripts/check-figma-audit.py --change <change-id> --strict --require-framework`（目标框架/转码说明 + 单文件 token 实际值 + 每 PAGE 区块规格 + figma-code/ 目标框架设计代码 + figma-layout.csv 断言映射 + 断言范围理由 + 状态决策 + UI 评审 APPROVED） |
| 07 详细设计、接口与测试设计 | `detailed-design` | `prompts/07-detailed-design.md` | 涉及 UI 时读取 `figma-audit.md` 的 token 实际值、每 PAGE 规格、状态决策与 `figma-assets/`；默认离线消费，仅在版本变化/歧义时按页重读并避免限流；`openspec instructions design --change <change-id> --json` + `scripts/check-change.sh <change-id>` + `scripts/check-design-assets.sh <change-id> --strict --lint-api` + `scripts/check-design-sections.py --change <change-id>` + `scripts/check-test-cases.py --change <change-id> --strict` + `scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict` + 有 API 时 `scripts/check-api-traceability.py --change <change-id>` + `openspec validate <change-id> --strict` + `baseline-governance.py check-change --phase design` + 有跨边界接口时 `scripts/check-interface-catalog.py --change <change-id> --strict` |
| 08 实现、TDD、验证与代码审查 | `implementation-orchestrator` | `prompts/08-implementation-orchestrator.md` | `baseline-governance.py check-change --phase implementation` + `scripts/test-all.sh` + `verify-before-completion.sh` + `scripts/check-figma-layout.py` + `scripts/check-design-tokens.py` + `scripts/check-code-review.py --change <change-id> --strict`（UI Change 直接移植目标框架设计代码，## UI fidelity 数值取自 figma-layout-check.json，仅差异/UI-DERIVED PAGE 需人工说明） |
| 09 独立验证与验收证据 | `independent-verifier` | `prompts/09-independent-verification.md` | `openspec status --change <change-id>` + `openspec validate <change-id> --strict` + `scripts/check-independent-verification.py --report <report> --evidence <json>`（UI Change 校验 layout_checks 逐 PAGE 断言元素数/最大偏差/容差/缺失元素/判定与独立重跑记录）；PASS 后才进入阶段 10 |
| 10 人工验收、归档与基线回写 | `acceptance-audit` | `prompts/10-acceptance-audit.md` | `baseline-governance.py check-change --phase acceptance` + `scripts/check-acceptance.py <change-id>` + `verify-before-completion.sh` |

## 方法与证据门禁

- 02–10 的阶段 evidence 必须包含 `methods` 块；`python scripts/check-method-evidence.py --step <step-id> --evidence <evidence.json>` 可单独校验，`workflow.py transition` 会自动调用同一逻辑。
- 02/03/04/05/07 的 `brainstorming` 至少记录问题/备选/决策；03/07 至少 4 个问题与 2 个备选。未记录不得推进。
- 03 必须沟通“新系统 / 基于现有系统二开 / 混合、代码地址、第三方接口”：二开时实际读取代码并写入 `technology-decisions.md` 的“现有系统二开约束”与 `constraint-registry.json` 的 `LEGACY-*`；第三方接口写入“第三方接口依赖清单”、EXTERNAL 数据流与 API 约定。
- 07 必须沟通“修改现有功能代码 / 新功能开发、代码地址、第三方接口”：修改现有功能时实际读取代码并写入 `design.md` 的 `### 现有代码变更影响`；第三方接口写入 `interface-catalog.csv` 的 `THIRD_PARTY_API` 行与 test/fakes 证据。
- 07 存在 HTTP API、原生桥接、设备、第三方、异步或文件边界时，必须生成 `design/interface-catalog.csv` 并运行 `check-interface-catalog.py --change <change-id> --strict`；仅 HTTP API 的 Change 也要在目录中登记 `HTTP_API` 行。
- OpenSpec/Superpowers 的逐阶段允许/禁止范围见 `docs/SUPERPOWERS-MAPPING.md` 的“OpenSpec 参与矩阵”与“阶段内方法模式”。

## 检查策略说明

> 说明：项目级与提案级都不产出 `use-cases` 文件。项目级用 FLOW/NODE 表达业务流程；提案级用例场景统一写在 delta spec 的 Scenario，US/AC 保留在 `design/user-stories.md`。

需求澄清、客户沟通、Figma 视觉与架构合理性不能由通用 Shell 脚本可靠判定；这些阶段有明确交付物和人工评审清单，而不是伪造一个自动化“通过”。

正式产物的模板等级与路径请参照 `docs/TEMPLATE-POLICY.md` 和 `docs/OUTPUT-TEMPLATE-MATRIX.csv`；变更模板目录后运行 `python3 scripts/check-output-template-matrix.py`。详细设计合并到 `design.md` 五节，API→IO 映射仅在存在 API 时强制。

## 项目基线与功能 Change 的交互

- 阶段 04：按每个候选 Change 初步读取冻结基线，识别适用域、约束复用和潜在修订；在路线图中体现。
- 阶段 05：强制创建 `openspec/changes/<change-id>/design/baseline-impact.md`，记录基线版本、文件/章节/ID、适用约束、复用项、冲突及分类。
- 阶段 06–07：按设计域重新核验基线版本；基线变化必须得出 `NO_IMPACT` 或 `REBASE_REQUIRED`。
- 阶段 08：遵循已批准基线；实现发现冲突时暂停受影响任务、提交 BCR/ADR，不得直接编辑冻结基线。
- 阶段 10：只回写已批准、已实现、已验证且可跨功能复用的决策；功能特有细节保留在归档 Change。
- 完整规则：`docs/BASELINE-FEATURE-INTERACTION.md`；Change 记录模板：`templates/change-assets/design/baseline-impact.md`。

## 对话式继续流程

- 在具备仓库访问和工具执行能力的 Agent 中，使用 `prompts/00-next-step.md` 或说“下一步”。
- `workflow-state.json` 只用于定位；AI 必须检查真实文件、审批记录与 OpenSpec CLI 状态。
- 项目基线阶段与功能 Change 阶段不同：需求业务梳理阶段只读取现有 OpenSpec specs；提案获批后才创建 Change。
- 有 pending approval、阻断项、前置产物缺失或 CLI 验证失败时，不能自动前进。

## 强制输入/输出交接

每个阶段的正式输入、正式输出、下游消费关系、审批点与质量门禁，以 `docs/STEP-ARTIFACT-CONTRACTS.md` 和机器可读的 `docs/STEP-ARTIFACT-CONTRACTS.json` 为准。每个 Skill/Prompt 均内嵌对应契约引用。阶段结束必须展示 `templates/workflow/step-handoff-report.md`；未批准产物不得作为下一阶段正式输入。

涉及 UI 时，阶段 06 的唯一 UI 契约是单文件 `design/figma-audit.md`（目标框架/转码说明、token 实际值、文字样式、每 PAGE 区块规格、状态决策、设计代码、断言范围、UI 评审 APPROVED）与 `design/figma-code/`（06 按总体技术选型转码的目标框架设计代码：Vue 栈 `.vue` + Element Plus，React 栈 `.tsx`/`.jsx`）、`design/figma-layout.csv`（运行态断言映射）；07/08 默认离线消费，仅在 Figma 文件版本变化或页面有歧义时按页批量重读（串行、避免限流）。07 以设计代码为基线填写 `### PAGE→BLOCK→组件映射`（只登记业务化适配与 `UI-DEVIATION`），填满 `route`/`dom_selector` 并定义响应式规则；08 直接移植设计代码、只补业务逻辑，运行 `check-figma-layout.py` 与 `check-design-tokens.py`，`code-review.md` 的 `## UI fidelity` 数值直接取自 `figma-layout-check.json`；09 在 `layout_checks` 独立重跑核验，人工抽查仅限差异/`UI-DERIVED`/未断言 PAGE（缺失/超差/未批准差异不得 PASS）；10 无差异 PAGE 按机器证据批量签收，差异/`UI-DERIVED` PAGE 并排核对后在 `## UI acceptance` 签收。**全流程不保存截图。** Figma 评审稿是视觉/组件/变量最终权威，PAGE ID 由 06 冻结。不再使用 pen.dev、prototype.pen、PAGE-*.html、prototype.md、manifest.json、design-tokens.json、page-inventory/block-inventory/interaction-map/design-spec/figma-handoff。

## P0 Runtime Governance

- 阶段 DAG 以 `docs/WORKFLOW-STAGES.json` 为准；状态转换只能通过 `scripts/workflow.py transition`。
- 每次成功转换生成 SHA-256 handoff manifest；下游入口自动核验上游交接文件未漂移；被后续阶段声明为输出的产物标记为 `mutable_by_design`，只核验存在性。
- 阶段 08 实施后必须经过阶段 09 独立只读验证，PASS 后才进入阶段 10。
- 返工使用 `workflow.py reopen --step <id> --reason <原因>`；当前 Change 验收后使用 `workflow.py next-change --change-id <id>` 开始下一个 Change。
- 详细命令、Evidence JSON 和限制见 `docs/P0-RUNTIME-GOVERNANCE.md`。

## Baseline Governance Engine 门禁

- 项目基线冻结：`baseline-governance.py freeze` / `audit --require-frozen`；脚本核对各域状态、审批证据、约束来源和 SHA-256。
- 项目基线修订：`open-amendment` 先将总体状态切换为 UNDER_AMENDMENT；修订期间所有 Change 阶段阻断；`close-amendment` 只有在受影响域版本升级、哈希刷新和审批证据齐全后才重新冻结。
- Change 绑定：阶段 05 自动创建 `baseline-binding.json`，对全部 ACTIVE Constraint ID 建立逐条记录；阶段 06–07 由设计证据门禁，阶段 08/09 由实现证据门禁，阶段 10 由验收门禁。
- 完整使用规则见 `docs/BASELINE-FEATURE-INTERACTION.md` 第 9 节；自动化检查并不等同于审批身份认证，仍须使用受保护分支/CI/CODEOWNERS。
