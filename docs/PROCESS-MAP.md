# 阶段、Skill、Prompt 与 Script 对照

| 阶段 | Skill ID | Prompt 文件 | 自动检查 |
|---|---|---|---|
| 01 项目初始化与工具链检查 | `project-bootstrap` | `prompts/01-project-bootstrap.md` | `scripts/check-package.py` |
| 02 需求业务梳理 | `requirements-analysis` | `prompts/02-requirements-analysis.md` | `scripts/check-requirements.py --strict`（流程节点、数据对象、RD 矩阵结构；初稿阶段可不加 --strict） |
| 03 项目总体架构设计 | `project-architecture-baseline` | `prompts/03-project-architecture-baseline.md` | `scripts/check-required-files.sh --strict` + 技术选型访谈记录与用户确认 + 阶段结束审计 `baseline-governance.py freeze` / `audit --require-frozen` |
| 04 提案拆分、依赖排序与路线图 | `proposal-planning` | `prompts/04-proposal-planning.md` | `baseline-governance.py audit --require-frozen` + `scripts/check-roadmap.py --strict` |
| 05 提案级需求分析 | `feature-requirements` | `prompts/05-feature-requirements.md` | `scripts/check-requirements.py --change <change-id> --strict` + `baseline-governance.py check-change --phase requirement` + `scripts/check-baseline-impact.py <change-id>` |
| 06 提案原型生成与评审 | `prototype-generation` | `prompts/06-prototype-generation.md` | `scripts/check-prototype-build.py --change <change-id> --strict`（构建记录 + 页面映射 + 原型评审；MCP 不可用时如实阻断） |
| 07 页面、功能区块、元素与交互事件清单 | `page-interaction-inventory` | `prompts/07-page-interaction-inventory.md` | `scripts/check-inventory.py --change <change-id> --strict`（页面→区块→元素/事件归属闭合） |
| 08 Figma UI 设计与 MCP 审计 | `figma-ui-audit` | `prompts/08-figma-ui-audit.md` | `人工设计评审；前置清单用 scripts/check-inventory.py --strict 验证` |
| 09 功能详细设计总控 | `feature-design` | `prompts/09-feature-design.md` | `baseline-governance.py check-change --phase design` + `scripts/check-baseline-impact.py <change-id> --strict` |
| 10 OpenAPI 与接口逻辑设计 | `api-contract-design` | `prompts/10-api-contract-design.md` | `scripts/validate-openapi.sh <openapi-file>` + 有 API 时 `scripts/check-traceability.py --file <change>/design/api-traceability.csv --strict`；`x-api-scope: none` 时记录 N/A；后续 `check-design-assets.sh` 会验证每个 operationId 都有 IO 映射 |
| 11 前端详细设计 | `frontend-detail-design` | `prompts/11-frontend-detail-design.md` | `阶段 09–13 全部完成后运行 scripts/check-design-assets.sh <change-id>` |
| 12 后端详细设计 | `backend-detail-design` | `prompts/12-backend-detail-design.md` | `阶段 09–13 全部完成后运行 scripts/check-design-assets.sh <change-id>` |
| 13 测试设计 | `test-design` | `prompts/13-test-design.md` | `scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict` |
| 14 实现、TDD、验证与代码审查 | `implementation-orchestrator` | `prompts/14-implementation-orchestrator.md` | `baseline-governance.py check-change --phase implementation` + `scripts/test-all.sh` + `verify-before-completion.sh` |
| 15 独立验证与验收证据 | `independent-verifier` | `prompts/15-independent-verification.md` | `scripts/check-independent-verification.py --report <report> --evidence <json>`；PASS 后才进入阶段 16 |
| 16 人工验收、归档与基线回写 | `acceptance-audit` | `prompts/16-acceptance-audit.md` | `baseline-governance.py check-change --phase acceptance` + `scripts/check-acceptance.py <change-id>` + `verify-before-completion.sh` |

## 检查策略说明

需求澄清、客户沟通、Figma 视觉与架构合理性不能由通用 Shell 脚本可靠判定；这些阶段有明确交付物和人工评审清单，而不是伪造一个自动化“通过”。


正式产物的模板等级与路径请参照 `docs/TEMPLATE-POLICY.md` 和 `docs/OUTPUT-TEMPLATE-MATRIX.csv`；变更模板目录后运行 `python3 scripts/check-output-template-matrix.py`。后端详细设计的阻断校验必须包含 `scripts/check-api-io-mapping.py`。



## 项目基线与功能 Change 的交互

- 阶段 04：按每个候选 Change 初步读取冻结基线，识别适用域、约束复用和潜在修订；在路线图中体现。
- 阶段 05：强制创建 `openspec/changes/<change-id>/design/baseline-impact.md`，记录基线版本、文件/章节/ID、适用约束、复用项、冲突及分类。
- 阶段 09–13：按设计域重新核验基线版本；基线变化必须得出 `NO_IMPACT` 或 `REBASE_REQUIRED`。
- 阶段 14：遵循已批准基线；实现发现冲突时暂停受影响任务、提交 BCR/ADR，不得直接编辑冻结基线。
- 阶段 16：只回写已批准、已实现、已验证且可跨功能复用的决策；功能特有细节保留在归档 Change。
- 完整规则：`docs/BASELINE-FEATURE-INTERACTION.md`；Change 记录模板：`templates/change-assets/design/baseline-impact.md`。

## 对话式继续流程

- 在具备仓库访问和工具执行能力的 Agent 中，使用 `prompts/00-next-step.md` 或说“下一步”。
- `workflow-state.json` 只用于定位；AI 必须检查真实文件、审批记录与 OpenSpec CLI 状态。
- 项目基线阶段与功能 Change 阶段不同：需求业务梳理阶段只读取现有 OpenSpec specs；提案获批后才创建 Change。
- 有 pending approval、阻断项、前置产物缺失或 CLI 验证失败时，不能自动前进。


## 强制输入/输出交接

每个阶段的正式输入、正式输出、下游消费关系、审批点与质量门禁，以 `docs/STEP-ARTIFACT-CONTRACTS.md` 和机器可读的 `docs/STEP-ARTIFACT-CONTRACTS.json` 为准。每个 Skill/Prompt 均内嵌对应契约引用。阶段结束必须展示 `templates/workflow/step-handoff-report.md`；未批准产物不得作为下一阶段正式输入。


## P0 Runtime Governance (added)

- 阶段 DAG 以 `docs/WORKFLOW-STAGES.json` 为准；状态转换只能通过 `scripts/workflow.py transition`。
- 每次成功转换生成 SHA-256 handoff manifest；下游入口自动核验上游交接文件未漂移。
- 阶段 14 实施后新增 `15-independent-verification`，独立只读验证通过后才进入阶段 16。
- 详细命令、Evidence JSON 和限制见 `docs/P0-RUNTIME-GOVERNANCE.md`。


## Baseline Governance Engine 门禁

- 项目基线冻结：`baseline-governance.py freeze` / `audit --require-frozen`；脚本核对各域状态、审批证据、约束来源和 SHA-256。
- 项目基线修订：`open-amendment` 先将总体状态切换为 UNDER_AMENDMENT；修订期间所有 Change 阶段阻断；`close-amendment` 只有在受影响域版本升级、哈希刷新和审批证据齐全后才重新冻结。
- Change 绑定：阶段 05 自动创建 `baseline-binding.json`，对全部 ACTIVE Constraint ID 建立逐条记录；阶段 09 转出及 10–13 由设计证据门禁，阶段 14/15 由实现证据门禁，阶段 16 由验收门禁。
- 完整使用规则见 `docs/BASELINE-FEATURE-INTERACTION.md` 第 9 节；自动化检查并不等同于审批身份认证，仍须使用受保护分支/CI/CODEOWNERS。
