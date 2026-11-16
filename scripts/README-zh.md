# 脚本

> 语言：简体中文 ｜ [English](README.md)

大多数脚本会根据自身位置解析项目根目录；`validate-openapi.sh` 的文件参数可以是绝对路径，也可以是相对于当前目录/项目根目录的路径。复制后，请把脚本放到项目根目录的 `scripts/` 文件夹下。检查脚本在匹配产物章节名/状态标记时同时接受英文规范名与中文对照名，因此产物可跟随用户语言，而模板保持英文优先。

| 脚本 | 用途 | 通过意味着 | 不意味着 |
|---|---|---|---|
| `check-output-template-matrix.py` | 校验已登记的 L1/L2 模板路径是否存在 | 模板登记引用的是真实文件 | 模板内容完整且正确 |
| `agent-context.py --stage <id> [--change <change-id>] [--full]` | 打印精简的默认读取集（`input_policy.stage_profiles`）、按需清单，以及（带 `--full` 时）完整的审计输入 | 默认上下文保持在声明的读取组预算内 | Agent 确实读取了每个必需文件 |
| `stage-io-report.py [--check\|--out <path>]` | 生成/校验派生的阶段输入/输出概览，包括精简/按需画像 | 概览与权威契约一致 | 每个阶段的真实上下文都很小 |
| `check-api-io-mapping.py <openapi> <mapping.csv> <catalog.csv> [--strict]` | 每个 OpenAPI operationId 映射到一个或多个具体 IO ID；严格模式下 catalog 契约完整；有意无 API 的变更必须声明 `x-api-scope: none` | 设计具有正确的业务行为或安全的事务语义 |
| `test-api-io-mapping.sh` | 临时正向/负向夹具验证 API→IO 检查器行为，包括显式无 API 范围 | 基本检查器回归能被捕获 | 真实项目 API/IO 设计正确 |
| `check-acceptance.py <id>` | 验收结果、证据、评审人和 AC 行；UI Change 还需要逐 PAGE 的真实系统入口 + Figma 节点 + `figma-layout-check.json` PASS | 证据表没有待填字段并包含已接受的 AC 行；UI 验收针对运行中的系统和 Figma 文件签署（不含截图） | 业务验收确实合理 |
| `check-package.py` | Skill/Prompt 配对、frontmatter 与语法检查 | 包结构一致 | 内容/逻辑正确 |
| `check-output-consumption.py` | 正向：每个文件输出都有登记的消费者；反向：每个对更早输出的输入引用都已登记 | 输出/消费者映射双向闭合 | 下游语义正确 |
| `check-requirements.py [--strict]` | 声明的 workflow/story/AC/business-rule ID 与重复项 | 必需 ID 存在且声明唯一 | 语义完整性已被证明 |
| `check-roadmap.py [--strict]` | 路线图表格 ID 与重复项 | 提案计划结构一致 | 优先级/业务价值正确 |
| `check-required-files.sh [--strict]` | 基线文件存在性与占位符警告 | 必需基线文件存在；严格模式拒绝占位符 | 需求/架构合理 |
| `new-change-assets.sh <id>` | 在不覆盖文件的前提下为既有 Change 添加补充设计/证据模板 | 自定义资产骨架存在 | OpenSpec 产物已创建/有效 |
| `check-design-assets.sh <id> [--strict] [--lint-api]` | `design.md` 五个章节、追踪矩阵、条件性 OpenAPI/API→IO/catalog，以及 UI 变更的 Figma 审计 + `figma-code/`/`figma-layout.csv` | 统一设计资产存在且 API→IO/Figma 几何引用一致 | 设计质量与运行时行为正确 |
| `check-change.sh <id> [--no-openspec]` | Change 结构/tasks/specs 与 OpenSpec 校验 | Change 结构校验通过 | AC/业务完整性已被证明 |
| `check-inventory.py --change <id> [--strict]` or `--change <id> --no-ui --reason "..." --strict` | 历史 Change 的遗留 page/block/event CSV 检查器；不再属于阶段 06 | 遗留清单链接结构合理 | UI/交互行为正确 |
| ~~`check-stage06a.py --change <id>`~~ | 随 Figma-only 阶段 06 重写而移除；移至 `_trash/2026-11-11/scripts/legacy/` 以留档 | N/A | N/A |
| ~~`build-figma-source.py --change <id>`~~ | 随 Figma-only 阶段 06 重写而移除；移至 `_trash/2026-11-11/scripts/legacy/` 以留档 | N/A | N/A |
| `check-design-sections.py --change <id>` | `design.md` 五个统一章节及必需子章节，包括 `### 响应式与视口规则` / `### 页面几何与保真断言`；UI Change 必须具有填写了 `route`/`dom_selector` 的 `figma-layout.csv` | 详细设计不只是标题外壳，且运行时断言映射可执行 | 字段语义正确 |
| `check-interface-catalog.py --change <id> [--strict] [--require-native]` | 跨边界接口目录：必需字段、HTTP_API ↔ OpenAPI operationId 双射、每接口 TEST 与追踪行；`--require-native` 要求存在 `NATIVE_BRIDGE` 行 | 接口清单结构闭合且测试/追踪已链接 | 契约与运行时行为正确 |
| `check-method-evidence.py --step <id> --evidence <json>` | 根据契约 `method_policy` 校验阶段证据的 `methods` 块：skill/mode/questions/alternatives/decisions/artifact section/evidence | 方法参与已记录并引用真实产物 | 问题是否明智或决策是否正确 |
| `test-interface-catalog.py` | 接口目录检查器的正向/负向夹具 | 检查器回归能被捕获 | 真实项目接口正确 |
| `check-reference-research.py --strict` | 阶段 02 参考研究：研究问题、参考产品、带 URL/日期的真实来源、对比、结论/影响映射 | 研究记录结构完整 | 研究结论正确 |
| `check-architecture-baseline.py --strict` | 阶段 03 既有系统与第三方基线：`现有系统二开约束` 记录代码访问，`第三方接口依赖清单` 与 `第三方接口与集成约定` 存在，第三方数据流存在，且 `LEGACY-*`/`EXT-*` 约束已登记 | 既有系统/第三方访谈结果写入架构基线并登记 | 约束本身在技术上正确 |
| `test-architecture-baseline.py` | 架构基线检查器的正向/负向夹具 | 检查器回归能被捕获 | 真实架构内容正确 |
| `check-output-context.py --stage <id> [--change <change-id>]` | 对既有 summary/evidence 文件强制执行 `output_policy.summary_budgets` 的行/字符限制 | 摘要输出保持简洁并引用上游而非复制 | 输出内容语义正确 |
| `test-output-context.py` | 输出预算检查器的正向/负向夹具 | 检查器回归能被捕获 | 真实阶段输出简洁 |
| `test-agent-context.py` | 精简包预算的正向/负向夹具 | 检查器回归能被捕获 | 真实阶段上下文很小 |
| `check-api-traceability.py --change <id> [--strict]` | 每个 OpenAPI operationId 在 traceability.csv 中链接到 PAGE/EVT/AC | API 到 UI/AC 的追踪已闭合 | API 行为正确 |
| `check-test-cases.py --change <id> [--strict]` | TEST ID 唯一性、必需字段、AC/page/operationId/IO 覆盖（PAGE 来自 figma-audit.md；BLOCK 可选），以及 traceability.csv 中链接的 TEST ID | 测试用例矩阵结构完整 | 测试断言确实通过 |
| `check-figma-audit.py --change <id> [--strict] [--require-framework]` / `--no-ui --reason "..." --strict` | UI Change 必须具有 `design/figma-audit.md`，包含真实 Figma 链接/节点、实际的 `get_metadata`/`get_variable_defs` 记录、目标框架 + `figma-design-to-code` 使用（配合 `--require-framework`）、`figma-code/` 目标框架设计代码（Vue 为 `.vue`，React 为 `.tsx`/`.jsx`）、`figma-layout.csv`（断言映射）、每个可见 TEXT 已断言或说明理由，以及 `- UI 评审状态：APPROVED` | Figma 设计确实已生成/读取、框架对齐、完整清点并评审；参考截图不被接受 | Figma 视觉质量正确 |
| `check-figma-layout.py --change <id> --base-url <url> --viewport 1440x900 [--out <json>] [--storage-state <file>]` | 参数化视觉回归：使用 Playwright 测量运行中 DOM 的每个已映射元素，并将其 x/y/w/h/text/font 与 Figma 节点几何比较；写入 `design/evidence/figma-layout-check.json` | 几何/文本/字体断言全部在容差内通过且无已映射元素缺失 | Figma 设计本身正确；未映射元素不在覆盖范围内 |
| `check-design-tokens.py --change <id> --tokens <token.css>` | 将 Figma token 实际值（颜色/px）与项目 CSS 自定义属性进行精确静态比较 | token 层与 Figma 实际值一致 | 布局/间距结构正确（由 `check-figma-layout.py` 覆盖） |
| `check-traceability.py --file <csv> [--strict]` | 追踪 CSV 列、重复链接与状态 | 追踪边结构合理 | 所有语义覆盖都存在 |
| `validate-openapi.sh <file>` | Redocly OpenAPI lint | Linter 接受该契约 | 业务语义正确 |
| `test-all.sh <dir>...` | 运行检测到的测试入口 | 所有请求的检测到的测试命令均已通过 | 除非包含在命令中，否则 lint/build/E2E 未运行 |
| `verify-before-completion.sh <id> ...` | 运行严格 OpenSpec、diff 及可选 API/测试检查 | 配置的检查已成功运行 | 人工验收/发布批准完成 |
| `check-code-review.py --change <id> [--strict]` | 阶段 08 `design/evidence/code-review.md` 必须具有真实头字段、已批准的结论、findings/status、没有未解决的 TODO/PENDING 标记；UI Change 还需要数值化 `## UI fidelity` 和 PASS 的 `figma-layout-check.json` | 代码审查证据结构完整且 UI 几何经机器校验 | 审查发现技术上正确 |

当脚本无法运行必需检查时，它们会有意地 fail-closed。如果仓库不使用 Bash/WSL/macOS/Linux，请针对 Windows PowerShell 进行适配。

| `workflow.py status` | 展示工作流状态 | 状态 JSON 可读取且阶段 ID 合法 | 业务产物真实完成 |
| `workflow.py check-entry --step <id>` | 阶段进入守卫，核验依赖/审批/阻断/上游 SHA-256 handoff | 阶段满足进入条件 | 当前阶段产物质量正确 |
| `workflow.py check-methods --step <id> --evidence <json>` | 校验 evidence 的 `methods` 块（02–10）；`transition` 也会自动调用 | 方法证据已记录且引用真实产物 | 问题质量与决策正确性 |
| `workflow.py request-review --step <id> --summary <text>` | 阶段完成后登记待评审：写入 pending_approvals 且 current_step 不前进；next-step/check-entry 随即阻断 | 送审状态已记录 | 产物质量正确 |
| `workflow.py approve --step <id> --approver <name> --approved-at <date> --evidence <file>` | 记录用户明确批准，写入 approvals_history 并清除该阶段待评审 | 用户审批已登记 | 审批身份由脚本认证 |
| `workflow.py transition --step <id> --evidence <json>` | 校验契约声明的全部文件型输出、门禁、审批，生成下游 handoff 并原子推进状态；人工审批阶段必须有 approvals_history 记录 | 阶段证据通过且状态推进成功 | 人工审批身份由脚本认证 |
| `workflow.py reopen --step <id> --reason <text>` | 返工回退：移除目标阶段及其下游依赖闭包，清理相关审批/阻断，current_step 回到目标阶段 | 回退完成并记录 reopen_history | 不校验返工后产物质量 |
| `workflow.py next-change --change-id <id>` | 当前 Change 验收后归档 05–10，切换 active_change_id 并从 05 开始下一个 Change | 上一个 Change 已完成验收且无阻断 | 不支持并发 Change 调度 |
| `workflow.py sync-baseline-index` | 从 baseline-manifest.json 同步 workflow-state.json 的基线版本/状态索引 | 状态索引与机器权威 Manifest 一致 | 不冻结或修改基线本身 |
| `workflow.py handoff-verify --manifest <json>` | 校验交接包文件 SHA-256 | 交接文件未变化 | 文件语义正确 |
| `check-independent-verification.py` | 校验独立验证报告与结构化证据；UI Change 需要逐 PAGE 的 `layout_checks`（已断言元素、最大偏差/容差、缺失元素）以及独立运行 `check-figma-layout.py` | AC/tests/revision/read-only/findings 满足 PASS 规则；UI 几何已被独立重新测量 | 无法证明 Verifier Agent 身份确实独立 |
| `workflow.py handoff-create --from-step <id> --to-step <id> --evidence <json>` | 从原阶段已批准 evidence 恢复丢失的交接 manifest | 重新校验原始输出/门禁/审批并重建哈希 | 不可绕过原阶段失败门禁；15 必须保留独立验证 checker 证据 |

| `baseline-governance.py audit [--require-frozen]` | 校验机器 Manifest、域状态、文件/注册表 SHA-256、约束 ID/来源/审批；`--require-frozen` 用于功能阶段 | 基线元数据与文件完整性通过 | 不等于企业身份认证；需配合 CI/受保护分支 |
| `baseline-governance.py init-binding --change-id <id>` | 从冻结基线生成 Change 约束绑定，覆盖当前全部 ACTIVE Constraint ID | 初始绑定完整生成 | 适用性、设计结论、证据和审批仍需人/Agent填写 |
| `baseline-governance.py check-change --change-id <id> --phase <requirement\|design\|implementation\|acceptance>` | 按阶段检查基线快照、约束覆盖、例外审批、设计和实现证据、rebase 结论 | 当前阶段无基线治理阻断 | 不证明业务判断正确；证据语义仍需独立审查 |
| `baseline-governance.py open-amendment --request-id <id> --domains <csv>` | 冻结前置修订状态，阻断功能门禁 | 修订窗口已打开 | 不负责自动审批或自动升级版本 |
| `baseline-governance.py refresh-hashes` | 在 DRAFT/UNDER_AMENDMENT 状态刷新基线文件与约束目录哈希 | 哈希登记已更新 | FROZEN 状态下拒绝执行 |
| `baseline-governance.py refresh-binding --change-id <id>` | 完成 REBASE_COMPLETED 审核后刷新 Change 快照，重置变更域判定并撤销旧绑定审批 | Change 进入重新评审 | 不会替代人工重新批准 |
