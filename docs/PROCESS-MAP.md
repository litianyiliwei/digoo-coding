# 阶段、Skill、Prompt 与 Script 对照

| 阶段 | Skill ID | Prompt 文件 | 自动检查 |
|---|---|---|---|
| 01 项目初始化与工具链检查 | `project-bootstrap` | `prompts/01-project-bootstrap.md` | `scripts/check-package.py` |
| 02 需求发现与整理 | `requirements-analysis` | `prompts/02-requirements-analysis.md` | `scripts/check-requirements.py --strict`（初稿阶段可不加 --strict） |
| 03 pen.dev 原型评审与需求澄清 | `prototype-audit` | `prompts/03-prototype-audit.md` | `人工评审；原型差异登记后，阶段 11 使用 scripts/check-inventory.py 检查清单结构` |
| 04 项目级产品基线 | `product-baseline` | `prompts/04-product-baseline.md` | `scripts/check-required-files.sh` |
| 05 项目总体架构设计 | `project-architecture-baseline` | `prompts/05-project-architecture-baseline.md` | `scripts/check-required-files.sh` |
| 06 项目级数据与领域基线 | `data-domain-baseline` | `prompts/06-data-domain-baseline.md` | `scripts/check-required-files.sh` |
| 07 项目级接口/前端/测试规范 | `project-contract-baseline` | `prompts/07-project-contract-baseline.md` | `scripts/check-required-files.sh` |
| 08 项目基线审计与冻结 | `baseline-audit` | `prompts/08-baseline-audit.md` | `scripts/check-required-files.sh --strict` |
| 09 提案拆分、依赖排序与路线图 | `proposal-planning` | `prompts/09-proposal-planning.md` | `scripts/check-roadmap.py --strict`（路线图评审前） |
| 10 功能级 OpenSpec Change 与需求细化 | `feature-requirements` | `prompts/10-feature-requirements.md` | `scripts/check-change.sh <change-id>` |
| 11 页面、元素、按钮与交互事件清单 | `page-interaction-inventory` | `prompts/11-page-interaction-inventory.md` | `scripts/check-inventory.py --change <change-id> --strict`（清单完成后） |
| 12 Figma UI 设计与 MCP 审计 | `figma-ui-audit` | `prompts/12-figma-ui-audit.md` | `人工设计评审；前置清单用 scripts/check-inventory.py --strict 验证` |
| 13a 功能详细设计总控 | `feature-design` | `prompts/13a-feature-design.md` | `scripts/check-change.sh <change-id>`；设计完成后 `scripts/check-design-assets.sh <change-id>` |
| 13b OpenAPI 与接口逻辑设计 | `api-contract-design` | `prompts/13b-api-contract-design.md` | `scripts/validate-openapi.sh <openapi-file>`；后续 `check-design-assets.sh` 会验证每个 operationId 都有 IO 映射 |
| 13c 前端详细设计 | `frontend-detail-design` | `prompts/13c-frontend-detail-design.md` | `阶段 13a–13e 全部完成后运行 scripts/check-design-assets.sh <change-id>` |
| 13d 后端详细设计 | `backend-detail-design` | `prompts/13d-backend-detail-design.md` | `阶段 13a–13e 全部完成后运行 scripts/check-design-assets.sh <change-id>` |
| 13e 测试设计 | `test-design` | `prompts/13e-test-design.md` | `scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict` |
| 14 实现、TDD、验证与代码审查 | `implementation-orchestrator` | `prompts/14-implementation-orchestrator.md` | `scripts/test-all.sh <frontend-dir> <backend-dir>`；`scripts/verify-before-completion.sh <change-id> --test-dir <frontend-dir> --test-dir <backend-dir> [--openapi <file>]` |
| 15 人工验收、归档与基线回写 | `acceptance-audit` | `prompts/15-acceptance-audit.md` | `scripts/check-acceptance.py <change-id>` + `scripts/verify-before-completion.sh <change-id> --test-dir <frontend-dir> --test-dir <backend-dir> [--openapi <file>]` |

## 检查策略说明

需求澄清、客户沟通、Figma 视觉与架构合理性不能由通用 Shell 脚本可靠判定；这些阶段有明确交付物和人工评审清单，而不是伪造一个自动化“通过”。


正式产物的模板等级与路径请参照 `docs/TEMPLATE-POLICY.md` 和 `docs/OUTPUT-TEMPLATE-MATRIX.csv`；变更模板目录后运行 `python3 scripts/check-output-template-matrix.py`。后端详细设计的阻断校验必须包含 `scripts/check-api-io-mapping.py`。


## 对话式继续流程

- 在具备仓库访问和工具执行能力的 Agent 中，使用 `prompts/00-next-step.md` 或说“下一步”。
- `workflow-state.json` 只用于定位；AI 必须检查真实文件、审批记录与 OpenSpec CLI 状态。
- 项目基线阶段与功能 Change 阶段不同：需求发现阶段只读取现有 OpenSpec specs；提案获批后才创建 Change。
- 有 pending approval、阻断项、前置产物缺失或 CLI 验证失败时，不能自动前进。


## 强制输入/输出交接

每个阶段的正式输入、正式输出、下游消费关系、审批点与质量门禁，以 `docs/STEP-ARTIFACT-CONTRACTS.md` 和机器可读的 `docs/STEP-ARTIFACT-CONTRACTS.json` 为准。每个 Skill/Prompt 均内嵌对应契约引用。阶段结束必须展示 `templates/workflow/step-handoff-report.md`；未批准产物不得作为下一阶段正式输入。
