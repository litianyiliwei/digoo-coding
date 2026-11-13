# Scripts

Most scripts resolve the project root from their own location; file arguments to `validate-openapi.sh` may be absolute or relative to the current directory/project root. After copying, place scripts under the project root `scripts/` folder.

| Script | Purpose | Success means | Does not mean |
|---|---|---|---|
| `check-output-template-matrix.py` | Validates that registered L1/L2 template paths exist | Template registry references real files | Template content is complete/correct |
| `agent-context.py --stage <id> [--change <change-id>] [--full]` | Prints the lean default read set (`input_policy.stage_profiles`), the on-demand list, and (with `--full`) the full audit inputs | Default context stays within the declared read-group budget | The agent actually reads every required file |
| `stage-io-report.py [--check\|--out <path>]` | Generates/verifies the derived stage input/output overview, including lean/on-demand profiles | Overview matches the authoritative contracts | Each stage's real context is small |
| `check-api-io-mapping.py <openapi> <mapping.csv> <catalog.csv> [--strict]` | Every OpenAPI operationId maps to one or more concrete IO IDs; catalog contracts are complete in strict mode; intentional no-API change must declare `x-api-scope: none` | Design has correct business behavior or safe transaction semantics |
| `test-api-io-mapping.sh` | Temporary positive/negative fixtures verify API→IO checker behavior, including explicit no-API scope | Basic checker regressions are caught | Real project API/IO design is correct |
| `check-acceptance.py <id>` | Acceptance result, evidence, reviewer and AC rows; UI Changes also require per-PAGE live system entry + Figma node + `figma-layout-check.json` PASS | Evidence sheet has no pending fields and includes accepted AC rows; UI acceptance is signed against the running system and Figma file (no screenshots) | Business acceptance is actually justified |
| `check-package.py` | Skill/Prompt pairing, frontmatter and syntax checks | Package structure is consistent | Content/logic is correct |
| `check-output-consumption.py` | Forward: each file output has a registered consumer; reverse: each input reference to an earlier output is registered | Output/consumer map is bidirectionally closed | Downstream semantics are correct |
| `check-requirements.py [--strict]` | Declared workflow/story/AC/business-rule IDs and duplicates | Required IDs exist and declarations are unique | Semantic completeness is proven |
| `check-roadmap.py [--strict]` | Roadmap table IDs and duplicates | Proposal plan structurally consistent | Priority/business value are correct |
| `check-required-files.sh [--strict]` | Baseline file presence and placeholder warnings | Required baseline files exist; strict rejects placeholders | Requirements/architecture are sound |
| `new-change-assets.sh <id>` | Add supplemental design/evidence templates to an existing Change without overwriting files | Custom asset skeletons exist | OpenSpec artifacts are created/valid |
| `check-design-assets.sh <id> [--strict] [--lint-api]` | `design.md` five sections, traceability, conditional OpenAPI/API→IO/catalog, and Figma audit + `figma-code/`/`figma-layout.csv` for UI changes | Unified design assets exist and API→IO/Figma geometry references are consistent | Design quality and runtime behavior are correct |
| `check-change.sh <id> [--no-openspec]` | Change structure/tasks/specs and OpenSpec validation | Change structure validates | AC/business completeness is proven |
| `check-inventory.py --change <id> [--strict]` or `--change <id> --no-ui --reason "..." --strict` | Legacy page/block/event CSV checker for historical Changes; no longer part of stage 06 | Legacy inventory links are structurally sound | UI/interaction behavior is correct |
| ~~`check-stage06a.py --change <id>`~~ | Removed with the Figma-only stage 06 rewrite; moved to `_trash/2026-11-11/scripts/legacy/` for history | N/A | N/A |
| ~~`build-figma-source.py --change <id>`~~ | Removed with the Figma-only stage 06 rewrite; moved to `_trash/2026-11-11/scripts/legacy/` for history | N/A | N/A |
| `check-design-sections.py --change <id>` | `design.md` five unified sections and required subsections, including `### 响应式与视口规则` / `### 页面几何与保真断言`; UI Changes must have `figma-layout.csv` with filled `route`/`dom_selector` | Detailed design is not just a heading shell and the runtime assertion mapping is actionable | Field semantics are correct |
| `check-interface-catalog.py --change <id> [--strict] [--require-native]` | Cross-boundary interface catalog: required fields, HTTP_API ↔ OpenAPI operationId bijection, per-interface TEST and traceability rows; `--require-native` demands a `NATIVE_BRIDGE` row | Interface inventory is structurally closed and test/trace linked | Contracts and runtime behavior are correct |
| `check-method-evidence.py --step <id> --evidence <json>` | Validates the stage evidence `methods` block against the contract `method_policy`: skill/mode/questions/alternatives/decisions/artifact section/evidence | Method participation is recorded and references real artifacts | The questions were wise or the decisions correct |
| `test-interface-catalog.py` | Positive/negative fixtures for the interface catalog checker | Checker regressions are caught | Real project interfaces are correct |
| `check-reference-research.py --strict` | Stage 02 reference research: research questions, reference products, real sources with URLs/dates, comparisons, conclusions/impact mapping | Research record is structurally complete | The research conclusions are correct |
| `check-architecture-baseline.py --strict` | Stage 03 existing-system and third-party baseline: `现有系统二开约束` records code access, `第三方接口依赖清单` and `第三方接口与集成约定` exist, third-party data flows are present, and `LEGACY-*`/`EXT-*` constraints are registered | Existing-system/third-party interview results are written into the architecture baseline and registry | The constraints themselves are technically correct |
| `test-architecture-baseline.py` | Positive/negative fixtures for the architecture baseline checker | Checker regressions are caught | Real architecture content is correct |
| `check-output-context.py --stage <id> [--change <change-id>]` | Enforces `output_policy.summary_budgets` line/char limits for existing summary/evidence files | Summary outputs stay concise and reference upstream instead of copying | Output content is semantically correct |
| `test-output-context.py` | Positive/negative fixtures for the output budget checker | Checker regressions are caught | Real stage outputs are concise |
| `test-agent-context.py` | Positive/negative fixtures for the lean-bundle budget | Checker regressions are caught | Real stage context is small |
| `check-api-traceability.py --change <id> [--strict]` | Every OpenAPI operationId links to PAGE/EVT/AC in traceability.csv | API-to-UI/AC trace is closed | API behavior is correct |
| `check-test-cases.py --change <id> [--strict]` | TEST ID uniqueness, required fields, AC/page/operationId/IO coverage (PAGE from figma-audit.md; BLOCK optional), and TEST IDs linked in traceability.csv | Test-case matrix is structurally complete | Test assertions actually pass |
| `check-figma-audit.py --change <id> [--strict] [--require-framework]` / `--no-ui --reason "..." --strict` | UI Changes must have `design/figma-audit.md` with real Figma link/node, actual `get_metadata`/`get_variable_defs` records, target framework + `figma-design-to-code` usage (with `--require-framework`), `figma-code/` target-framework design code (`.vue` for Vue, `.tsx`/`.jsx` for React), `figma-layout.csv` (assertion mapping), every visible TEXT asserted or justified, and `- UI 评审状态：APPROVED` | Figma design was actually generated/read, framework-aligned, fully inventoried and reviewed; reference screenshots are not accepted | Figma visual quality is correct |
| `check-figma-layout.py --change <id> --base-url <url> --viewport 1440x900 [--out <json>] [--storage-state <file>]` | Parameterized visual regression: measure every mapped element in the running DOM with Playwright and compare its x/y/w/h/text/font with Figma node geometry; writes `design/evidence/figma-layout-check.json` | Geometry/text/font assertions all pass within tolerance and no mapped element is missing | Figma design itself is correct; unmapped elements are not covered |
| `check-design-tokens.py --change <id> --tokens <token.css>` | Exact static comparison of Figma token actual values (colors/px) with the project CSS custom properties | Token layer matches Figma actual values | Layout/spacing structure is correct (covered by `check-figma-layout.py`) |
| `check-traceability.py --file <csv> [--strict]` | Traceability CSV columns, duplicate links and states | Trace edges are structurally sound | All semantic coverage exists |
| `validate-openapi.sh <file>` | Redocly OpenAPI lint | Linter accepts the contract | Business semantics are correct |
| `test-all.sh <dir>...` | Run detected test entrypoints | All requested detected test commands passed | Lint/build/E2E ran unless included in command |
| `verify-before-completion.sh <id> ...` | Run strict OpenSpec, diff and optional API/tests checks | Configured checks ran successfully | Human acceptance/release approval complete |
| `check-code-review.py --change <id> [--strict]` | Stage 08 `design/evidence/code-review.md` must have real header fields, an approved conclusion, findings/status, no unresolved TODO/PENDING markers; UI Changes also need numeric `## UI fidelity` and a PASS `figma-layout-check.json` | Code review evidence is structurally complete and machine-checked for UI geometry | Review findings are technically correct |

The scripts are intentionally fail-closed when they cannot run a required check. Adapt for Windows PowerShell if the repository does not use Bash/WSL/macOS/Linux.

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
| `check-independent-verification.py` | Verifies independent verification report and structured evidence; UI Changes require per-PAGE `layout_checks` (asserted elements, max delta/tolerance, missing elements) and an independent `check-figma-layout.py` run | AC/tests/revision/read-only/findings satisfy PASS rules; UI geometry was independently re-measured | Cannot prove the Verifier Agent identity is truly independent |
| `workflow.py handoff-create --from-step <id> --to-step <id> --evidence <json>` | 从原阶段已批准 evidence 恢复丢失的交接 manifest | 重新校验原始输出/门禁/审批并重建哈希 | 不可绕过原阶段失败门禁；15 必须保留独立验证 checker 证据 |

| `baseline-governance.py audit [--require-frozen]` | 校验机器 Manifest、域状态、文件/注册表 SHA-256、约束 ID/来源/审批；`--require-frozen` 用于功能阶段 | 基线元数据与文件完整性通过 | 不等于企业身份认证；需配合 CI/受保护分支 |
| `baseline-governance.py init-binding --change-id <id>` | 从冻结基线生成 Change 约束绑定，覆盖当前全部 ACTIVE Constraint ID | 初始绑定完整生成 | 适用性、设计结论、证据和审批仍需人/Agent填写 |
| `baseline-governance.py check-change --change-id <id> --phase <requirement\|design\|implementation\|acceptance>` | 按阶段检查基线快照、约束覆盖、例外审批、设计和实现证据、rebase 结论 | 当前阶段无基线治理阻断 | 不证明业务判断正确；证据语义仍需独立审查 |
| `baseline-governance.py open-amendment --request-id <id> --domains <csv>` | 冻结前置修订状态，阻断功能门禁 | 修订窗口已打开 | 不负责自动审批或自动升级版本 |
| `baseline-governance.py refresh-hashes` | 在 DRAFT/UNDER_AMENDMENT 状态刷新基线文件与约束目录哈希 | 哈希登记已更新 | FROZEN 状态下拒绝执行 |
| `baseline-governance.py refresh-binding --change-id <id>` | 完成 REBASE_COMPLETED 审核后刷新 Change 快照，重置变更域判定并撤销旧绑定审批 | Change 进入重新评审 | 不会替代人工重新批准 |
