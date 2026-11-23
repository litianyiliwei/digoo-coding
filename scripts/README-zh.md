# 脚本

> 语言：简体中文 ｜ [English](README.md)

大多数脚本会根据自身位置解析项目根目录；`validate-openapi.sh` 的文件参数可以是绝对路径，也可以是相对于当前目录/项目根目录的路径。复制后，请把脚本放到项目根目录的 `scripts/` 文件夹下。检查脚本在匹配产物章节名/状态标记时同时接受英文规范名与中文对照名，因此产物可跟随用户语言，而模板保持英文优先。项目状态类命令（`workflow.py`、`next-step.py`、`baseline-governance.py` 与项目检查）在引入本工具包的业务项目仓库中运行；工具包仓库自身不携带任何项目状态。

阶段 Skill 与阶段 Prompt 一一配对。本地方法 Skill（例如 `competitor-research`、`existing-code-impact-analysis`、`baseline-impact-classification`）在阶段内调用、不配阶段 Prompt；`check-package.py` 校验每个方法 Skill 都被 `method_policy` 引用，`check-method-evidence.py` 校验其阶段证据。

| 脚本 | 用途 | 通过意味着 | 不意味着 |
|---|---|---|---|
| `check-output-template-matrix.py` | 校验已登记的 L1/L2 模板路径是否存在 | 模板登记引用的是真实文件 | 模板内容完整且正确 |
| `agent-context.py --stage <id> [--change <change-id>] [--full]` | 打印精简的默认读取集（`input_policy.stage_profiles`）、按需清单，以及（带 `--full` 时）完整的审计输入。精简集超出建议值时只报警告并继续 | 精简包与建议预算可见 | Agent 确实读取了每个必需文件 |
| `stage-io-report.py [--check\|--out <path>]` | 生成/校验派生的阶段输入/输出概览，包括精简/按需画像 | 概览与权威契约一致 | 每个阶段的真实上下文都很小 |
| `gen-manifest.py --write\|--check` | 生成/校验 `process/TOOLKIT-MANIFEST.json`（vendored 集合与哈希） | 清单与工具包目录树一致 | 发布已打标签 |
| `check-layout.py --mode toolkit\|project\|auto` | 强制工作树所有权（工具包路径 vs 项目路径、托管块） | 目录布局符合双仓库模型 | 项目内容正确 |
| `toolkit-sync.py init\|verify\|plan\|apply\|repair` | 在项目仓库内安装/升级 vendored 工具包；校验哈希、托管块与第三方文件 | 项目锁定版本与工具包发布一致，且只改动了工具包路径 | 项目业务工作正确 |
| `check-api-io-mapping.py <openapi> <mapping.csv> <catalog.csv> [--strict]` | 每个 OpenAPI operationId 映射到一个或多个具体 IO ID；严格模式下 catalog 契约完整；有意无 API 的变更必须声明 `x-api-scope: none` | 设计具有正确的业务行为或安全的事务语义 |
| `test-api-io-mapping.sh` | 临时正向/负向夹具验证 API→IO 检查器行为，包括显式无 API 范围 | 基本检查器回归能被捕获 | 真实项目 API/IO 设计正确 |
| `check-acceptance.py <id>` | 验收结果、证据、评审人和 AC 行；UI Change 还需要逐 PAGE 的真实系统入口 + Figma 节点 + `figma-layout-check.json` PASS | 证据表没有待填字段并包含已接受的 AC 行；UI 验收针对运行中的系统和 Figma 文件签署（不含截图） | 业务验收确实合理 |
| `check-package.py` | Skill/Prompt 配对、frontmatter 与语法检查 | 包结构一致 | 内容/逻辑正确 |
| `check-output-consumption.py` | 正向：每个文件输出都有登记的消费者；反向：每个对更早输出的输入引用都已登记 | 输出/消费者映射双向闭合 | 下游语义正确 |
| `check-requirements.py [--strict]` | 声明的 workflow/story/AC/business-rule ID 与重复项 | 必需 ID 存在且声明唯一 | 语义完整性已被证明 |
| `check-roadmap.py [--strict]` | 按 `code-layout.json` 策略校验 `docs/product/proposal-roadmap.md`：`none` 仅校验旧版 ID/重复；`footprint` 校验 `Code Target` 位于布局 roots 下；`module-packages` 校验模块列（Primary Capability/Owner Module/Related Modules/Slice Type/Slice Coverage/Code Target/Demo Path/Slice Budget）并与 `capabilities.csv`/`modules.csv` 对照、校验已批准的 `## Roadmap Amendments` 行以及每个 Change/`active_changes` 引用均已登记 | 路线图结构一致且与注册表关联 | 优先级/业务价值正确 |
| `check-capabilities.py [--completed <change-id>]` | `module-packages` 下校验能力进度注册表 `docs/product/capabilities.csv`：恰好十列、每个能力唯一 owner、合法状态/域、owner 与 related slug 已登记于 `modules.csv`、`partial` 切片有 `remaining_slices`；`--completed` 要求 Change 在 `delivered_slices` 中且不在 `active_changes` | 注册表与模块、域和路线图结构一致 | 业务优先级/完成判断正确 |
| `check-modules.py [--completed <module-slug>]` | `module-packages` 下校验模块归属注册表 `docs/product/modules.csv`：恰好九列、路径唯一且以 `code-layout.json` root 开头、`shared_paths` 位于模块内、能力归属/托管一致、ACTIVE/DELIVERED 模块存在 `<path>/MODULE.md` 模块卡；`--completed` 要求 DELIVERED 且无活跃能力 | 模块注册表与模块卡结构一致 | 模块边界在架构上正确 |
| `check-change-footprint.py <change-id> [--declaration-only\|--verify]` | `--declaration-only`（07）对照 `modules.csv`/`capabilities.csv`/`code-layout.json` 校验 `### Implementation Slice`；差异模式（08）写入 `design/evidence/implementation-diff.json` 并要求每个变更路径位于拥有/集成路径内（执行 shared/frozen 规则）；`--verify`（09）对照 `implementation-base.json` 重算差异并比较路径集合与 `diff_sha256`；`strategy=none` 以显式标记跳过 | 切片声明有效，落地差异与声明 footprint 及存储证据一致 | 实现行为正确性 |
| `implementation-snapshot.py <change-id> [--force --reason <text>]` | 阶段 08 入口快照：`git rev-parse HEAD`、经共享排除规则后的逐文件 SHA-256 与指纹，写入 `design/evidence/implementation-base.json`；仅可通过 `--force` 加非空理由覆盖 | footprint 差异的基线存在且由脚本生成 | 工作区干净或快照已评审 |
| `code-context.py <change-id>` | 阶段 08 检索闭包：读取切片与注册表并写入 `design/context-manifest.json`（`read_set`/`not_needed`/`missing`）；不是门禁；`strategy=none` 时跳过且不写文件 | 必需读取集与缺失输入可见 | 实现者确实读取了每个文件 |
| `check-required-files.sh [--strict]` | 基线文件存在性与占位符警告 | 必需基线文件存在；严格模式拒绝占位符 | 需求/架构合理 |
| `new-change-assets.sh <id>` | 在不覆盖文件的前提下为既有 Change 添加补充设计/证据模板 | 自定义资产骨架存在 | OpenSpec 产物已创建/有效 |
| `check-design-assets.sh <id> [--strict] [--lint-api]` | `design.md` 五个章节、追踪矩阵、条件性 OpenAPI/API→IO/catalog，以及 UI 变更的 Figma 审计 + `figma-code/`/`figma-layout.csv`/`ui-actions.csv` | 统一设计资产存在且 API→IO/Figma 几何/UI 动作引用一致 | 设计质量与运行时行为正确 |
| `check-change.sh <id> [--no-openspec]` | Change 结构/tasks/specs 与 OpenSpec 校验 | Change 结构校验通过 | AC/业务完整性已被证明 |
| ~~`check-inventory.py --change <id> [--strict]` or `--change <id> --no-ui --reason "..." --strict`~~ | 已于 2026-11-19 移除：历史 Change 的遗留 page/block/event CSV 检查器不再需要；移至 `_trash/2026-11-19/scripts/` 以留档 | N/A | N/A |
| ~~`check-stage06a.py --change <id>`~~ | 随 Figma-only 阶段 06 重写而移除；移至 `_trash/2026-11-11/scripts/legacy/` 以留档 | N/A | N/A |
| ~~`build-figma-source.py --change <id>`~~ | 随 Figma-only 阶段 06 重写而移除；移至 `_trash/2026-11-11/scripts/legacy/` 以留档 | N/A | N/A |
| ~~`scripts/legacy/build-figma-handoff.py`~~ | 已被 `design/figma-audit.md` + `figma-code/` + `figma-layout.csv` 取代；移至 `_trash/2026-11-19/scripts/legacy/` 以留档 | N/A | N/A |
| `check-design-sections.py --change <id> [--slice-only]` | 完整模式：`design.md` 五个统一章节及必需子章节，包括 `### 响应式与视口规则` / `### 页面几何与保真断言`；UI Change 必须具有填写了 `route`/`dom_selector` 的 `figma-layout.csv` 与 `ui-actions.csv`，前端章节必须引用 `check-ui-actions.py`。`--slice-only` 仅校验 `## Design Decisions` 与 `### Implementation Slice`（07→08 硬门禁），跳过其余章节与所有 UI 检查 | 详细设计不只是标题外壳，运行时断言/UI 动作映射可执行，模块切片声明有效 | 字段语义正确 |
| `check-interface-catalog.py --change <id> [--strict] [--require-native]` | 跨边界接口目录：必需字段、HTTP_API ↔ OpenAPI operationId 双射、每接口 TEST 与追踪行；`--require-native` 要求存在 `NATIVE_BRIDGE` 行 | 接口清单结构闭合且测试/追踪已链接 | 契约与运行时行为正确 |
| `check-method-evidence.py --step <id> --evidence <json>` | 根据契约 `method_policy` 校验阶段证据的 `methods` 块：必需方法技能、mode、真实证据路径，以及要求的产物落点章节（`<path>#<heading>`）。不强制问题/备选/决策数量，也不做主题关键词匹配 | 方法参与已记录并引用真实产物 | 问题是否明智或决策是否正确 |
| `check-question-coverage.py --step <id> --evidence <json>` | 校验可选的阶段证据 `question_coverage` 块：每条状态与必需字段、重复 item_id、真实 `landing`/`open_question` 路径。清单只是建议，不要求固定条目列表，允许未知 item_id | 记录的问题已落到真实工件或明确分类 | 答案是否正确；方法证据仍独立 |
| `test-question-coverage.py` | 问题覆盖检查器的正向/负向夹具 | 检查器回归能被捕获 | 真实项目答案正确 |
| `test-interface-catalog.py` | 接口目录检查器的正向/负向夹具 | 检查器回归能被捕获 | 真实项目接口正确 |
| `test-quality-gates.py` / `test-static-analysis.py` / `test-code-review-static.py` | 质量门禁结构、静态分析运行器/检查器与代码审查静态行的正向/负向夹具 | 检查器回归能被捕获 | 真实项目规则与证据正确 |
| `check-reference-research.py --strict` | 阶段 02 参考研究：研究问题、存在参考产品时至少一个同类产品、带 URL/日期的真实来源、对比、结论/影响映射，以及 `## 9. 同类产品偏差确认`；重大偏差须用户确认（确认人+日期） | 研究记录结构完整且重大偏差已有用户确认 | 研究结论正确 |
| `check-ui-actions.py --change <id> [--strict]` | 阶段 07 UI 动作映射：`design/ui-actions.csv` 是 `design.md` `### 事件处理` 的机读投影；每个功能按钮/图标/链接/菜单/标签页都必须有 `navigate` 跳转地址+`route_params`、`api` 且 operationId 存在于 `api/openapi.yaml`，或用户已确认（确认人+日期）的 `local-only` 动作；交叉检查 `figma-layout.csv` 与 `figma-code/` 是否漏项，无 UI 时以 N/A 通过 | 所有功能控件均已登记并完成动作映射；未确认的本地动作失败并须提交用户确认 | 控件的运行时行为正确 |
| `test-ui-actions.py` | UI 动作检查器的正/负向回归用例 | 已覆盖检查器回归 | 真实 UI 动作正确 |
| `test-capabilities.py` / `test-modules.py` / `test-change-footprint.py` / `test-code-context.py` / `test-implementation-snapshot.py` / `test-gate-common.py` / `test-roadmap.py` / `test-design-sections.py` | 能力/模块注册表、切片/footprint、上下文清单、入口快照、共享 `gate_common.py` 解析器与路线图/设计门禁的正向/负向夹具 | 检查器回归能被捕获 | 真实模块边界与实现正确 |
| `check-architecture-baseline.py --strict` | 阶段 03 既有系统与第三方基线：`现有系统二开约束` 记录代码访问，`第三方接口依赖清单` 与 `第三方接口与集成约定` 存在，第三方数据流存在，且 `LEGACY-*`/`EXT-*` 约束已登记 | 既有系统/第三方访谈结果写入架构基线并登记 | 约束本身在技术上正确 |
| `test-architecture-baseline.py` | 架构基线检查器的正向/负向夹具 | 检查器回归能被捕获 | 真实架构内容正确 |
| `check-output-context.py --stage <id> [--change <change-id>]` | 按 `output_policy.summary_budgets` 的建议行/字符预算检查既有 summary/evidence 文件；默认只报警告，`--strict` 才作为失败 | 摘要输出保持简洁并引用上游而非复制 | 输出内容语义正确 |
| `test-output-context.py` | 输出预算检查器的正向/负向夹具 | 检查器回归能被捕获 | 真实阶段输出简洁 |
| `test-agent-context.py` | 精简包建议值的正向/负向夹具 | 检查器回归能被捕获 | 真实阶段上下文符合建议值 |
| `check-api-traceability.py --change <id> [--strict]` | 每个 OpenAPI operationId 在 traceability.csv 中链接到 PAGE/EVT/AC | API 到 UI/AC 的追踪已闭合 | API 行为正确 |
| `check-test-cases.py --change <id> [--strict]` | TEST ID 唯一性、必需字段、AC/page/operationId/IO 覆盖（PAGE 来自 figma-audit.md；BLOCK 可选），以及 traceability.csv 中链接的 TEST ID | 测试用例矩阵结构完整 | 测试断言确实通过 |
| `check-figma-audit.py --change <id> [--strict] [--require-framework]` / `--no-ui --reason "..." --strict` | UI Change 必须具有 `design/figma-audit.md`，包含真实 Figma 链接/节点、实际的 `get_metadata`/`get_variable_defs` 记录、目标框架 + `figma-design-to-code` 使用（配合 `--require-framework`）、`figma-code/` 目标框架设计代码（Vue 为 `.vue`，React 为 `.tsx`/`.jsx`）、`figma-layout.csv`（断言映射）、每个可见 TEXT 已断言或说明理由，以及 `- UI 评审状态：APPROVED` | Figma 设计确实已生成/读取、框架对齐、完整清点并评审；参考截图不被接受 | Figma 视觉质量正确 |
| `check-figma-layout.py --change <id> --base-url <url> --viewport 1440x900 [--out <json>] [--storage-state <file>]` | 参数化视觉回归：使用 Playwright 测量运行中 DOM 的每个已映射元素，并将其 x/y/w/h/text/font 与 Figma 节点几何比较；写入 `design/evidence/figma-layout-check.json` | 几何/文本/字体断言全部在容差内通过且无已映射元素缺失 | Figma 设计本身正确；未映射元素不在覆盖范围内 |
| `check-design-tokens.py --change <id> --tokens <token.css>` | 将 Figma token 实际值（颜色/px）与项目 CSS 自定义属性进行精确静态比较 | token 层与 Figma 实际值一致 | 布局/间距结构正确（由 `check-figma-layout.py` 覆盖） |
| `check-traceability.py --file <csv> [--strict]` | 追踪 CSV 列、重复链接与状态 | 追踪边结构合理 | 所有语义覆盖都存在 |
| `validate-openapi.sh <file>` | Redocly OpenAPI lint | Linter 接受该契约 | 业务语义正确 |
| `test-all.sh <dir>...` | 运行检测到的测试入口（仅测试；lint 与静态分析由 `run-quality-gates.py` 运行） | 所有请求的检测到的测试命令均已通过 | 除非另行执行，否则 lint/build/E2E/静态分析未运行 |
| `verify-before-completion.sh <id> ...` | 运行严格 OpenSpec、diff 及可选 API/测试检查；`docs/architecture/quality-gates.json` 存在时还运行静态门禁运行器与检查器（显式 `--skip-static` 不属于完整验证） | 配置的检查已成功运行（启用时包含静态门禁） | 人工验收/发布批准完成 |
| `check-code-review.py --change <id> [--strict]` | 阶段 08 `design/evidence/code-review.md` 必须具有真实头字段、已批准的结论、findings/status、没有未解决的 TODO/PENDING 标记；UI Change 还需要数值化 `## UI fidelity` 和 PASS 的 `figma-layout-check.json`；启用质量门禁时还需从 `static-analysis.json` 复制的 `## Static analysis` 表（含字面 `exit 0` 行与豁免审批人） | 代码审查证据结构完整且 UI 几何与静态结果经机器校验 | 审查发现技术上正确 |
| `check-quality-gates.py --root <项目根> [--strict] [--require-materialized]` | 校验 `docs/architecture/quality-gates.json`：schema/policy 完整性、blocking 栈/工具、安全的仓库相对根路径、栈相对配置、离线安全命令；`--strict` 交叉核对 `technology-decisions.md`；`--require-materialized` 要求栈根与配置文件存在且 SHA-256 可读。文件不存在时报告 `QUALITY_GATES_NOT_ADOPTED` 并退出 0；带 `--require-materialized`（已采用模式）则视为缺失错误 | 门禁选型与结构有效；技术选型提及每个栈语言 | 选定规则在技术上正确或已获批准；冻结批准仍属基线治理 |
| `run-quality-gates.py <change-id> --output <证据路径> [--root <项目根>] [--identity <名称>] [--builder-identity <名称>] [--independent] [--stack <id>] [--source-revision <rev>]` | 读取冻结门禁与 Change 级豁免文件，探测每个工具但绝不安装，在栈根目录按超时运行每个 blocking 命令，在 `design/evidence/static-analysis-logs/` 下按工具捕获日志（文件名取自净化后的栈根目录），并原子写入 `design/evidence/static-analysis.json` | 结论为 PASS，每个 blocking 栈/工具一条干净结果且有真实日志；`--independent` 记录不同的 verifier 与 builder 身份 | 项目代码质量在选定规则之外是否正确；工具缺失为 BLOCKED，绝不跳过 |
| `check-static-analysis.py --change <change-id> [--root <项目根>] [--evidence <路径>] [--expect-independent] [--strict]` | 对照当前门禁文件与 Change 级豁免校验静态证据：门禁哈希漂移、每个 blocking 栈/工具一条结果、全部退出码 0、日志在仓库内且存在、栈相对配置哈希、豁免有效（`policy.waiver.allowed`、审批人、过期在 `policy.waiver.max_days` 内）、结论 PASS；`--expect-independent` 要求身份不同 | 静态证据可机器校验，且与冻结门禁和豁免一致 | 内联抑制标记是否合理（由 09 人工审计）或工具规则本身是否正确 |

当脚本无法运行必需检查时，它们会有意地 fail-closed。如果仓库不使用 Bash/WSL/macOS/Linux，请针对 Windows PowerShell 进行适配。

| `workflow.py status` | 展示工作流状态 | 状态 JSON 可读取且阶段 ID 合法 | 业务产物真实完成 |
| `workflow.py check-entry --step <id>` | 阶段进入守卫，核验依赖/审批/阻断/上游 SHA-256 handoff | 阶段满足进入条件 | 当前阶段产物质量正确 |
| `workflow.py check-methods --step <id> --evidence <json>` | 校验 evidence 的 `methods` 块（02–10）；`transition` 也会自动调用 | 方法证据已记录且引用真实产物 | 问题质量与决策正确性 |
| `workflow.py check-coverage --step <id> --evidence <json>` | 校验可选的 evidence `question_coverage` 块；`request-review` 和 `transition` 也会自动调用 | 记录的问题已落点或明确分类 | 答案质量与决策正确性 |
| `workflow.py request-review --step <id> --summary <text>` | 阶段完成后登记待评审：写入 pending_approvals 且 current_step 不前进；next-step/check-entry 随即阻断 | 送审状态已记录 | 产物质量正确 |
| `workflow.py approve --step <id> --approver <name> --approved-at <date> --evidence <file>` | 记录用户明确批准，写入 approvals_history 并清除该阶段待评审 | 用户审批已登记 | 审批身份由脚本认证 |
| `workflow.py set-approval-policy --policy <standard\|risk-based> --reason <text> [--by <name>]` | 设置状态级 `approval_policy`；`risk-based` 让低风险阶段 01/04/06 快车道通过，高风险阶段仍需审批。存在待评审项时拒绝，并记录 `approval_policy_history` | 策略变更已记录，待评审项不受影响 | 用户确实授权了策略 |
| `workflow.py transition --step <id> --evidence <json>` | 校验契约声明的全部文件型输出、门禁、审批，生成下游 handoff 并原子推进状态；人工审批阶段必须有 approvals_history 记录 | 阶段证据通过且状态推进成功 | 人工审批身份由脚本认证 |
| `workflow.py reopen --step <id> --reason <text>` | 返工回退：移除目标阶段及其下游依赖闭包，清理相关审批/阻断，current_step 回到目标阶段 | 回退完成并记录 reopen_history | 不校验返工后产物质量 |
| `workflow.py next-change --change-id <id>` | 当前 Change 验收后归档 05–10，切换 active_change_id 并从 05 开始下一个 Change | 上一个 Change 已完成验收且无阻断 | 不支持并发 Change 调度 |
| `workflow.py sync-baseline-index` | 从 baseline-manifest.json 同步 workflow-state.json 的基线版本/状态索引 | 状态索引与机器权威 Manifest 一致 | 不冻结或修改基线本身 |
| `workflow.py handoff-verify --manifest <json>` | 校验交接包文件 SHA-256 | 交接文件未变化 | 文件语义正确 |
| `check-independent-verification.py` | 校验独立验证报告与结构化证据；UI Change 需要逐 PAGE 的 `layout_checks`（已断言元素、最大偏差/容差、缺失元素）以及独立运行 `check-figma-layout.py` | AC/tests/revision/read-only/findings 满足 PASS 规则；UI 几何已被独立重新测量 | 无法证明 Verifier Agent 身份确实独立 |
| `workflow.py handoff-create --from-step <id> --to-step <id> --evidence <json>` | 从原阶段已批准 evidence 恢复丢失的交接 manifest；必须提供 `--evidence`，不再接受 `--file` | 重新校验原始输出/门禁/审批并重建哈希 | 不可绕过原阶段失败门禁；09 必须保留独立验证 checker 证据 |

| `baseline-governance.py audit [--require-frozen]` | 校验机器 Manifest、域状态、文件/注册表 SHA-256、约束 ID/来源/审批；`--require-frozen` 用于功能阶段 | 基线元数据与文件完整性通过 | 不等于企业身份认证；需配合 CI/受保护分支 |
| `baseline-governance.py init-binding --change-id <id>` | 从冻结基线生成 Change 约束绑定：`standard` 覆盖全部 ACTIVE，`lite` 只覆盖 `critical: true` | 初始绑定按 manifest 模式完整生成 | 适用性、设计结论、证据和审批仍需人/Agent填写 |
| `baseline-governance.py check-change --change-id <id> --phase <requirement\|design\|implementation\|acceptance>` | 按阶段检查基线快照、约束覆盖、例外审批、设计和实现证据、rebase 结论 | 当前阶段无基线治理阻断 | 不证明业务判断正确；证据语义仍需独立审查 |
| `baseline-governance.py open-amendment --request-id <id> --domains <csv>` | 冻结前置修订状态，阻断功能门禁 | 修订窗口已打开 | 不负责自动审批或自动升级版本 |
| `baseline-governance.py refresh-hashes` | 在 DRAFT/UNDER_AMENDMENT 状态刷新基线文件与约束目录哈希 | 哈希登记已更新 | FROZEN 状态下拒绝执行 |
| `baseline-governance.py refresh-binding --change-id <id>` | 完成 REBASE_COMPLETED 审核后刷新 Change 快照，重置变更域判定并撤销旧绑定审批 | Change 进入重新评审 | 不会替代人工重新批准 |
