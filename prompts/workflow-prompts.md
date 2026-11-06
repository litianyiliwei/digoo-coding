# 每个流程阶段的 Prompt 索引

Prompt 文件位于 `prompts/`，与 `.claude/skills/<skill-id>/SKILL.md` 一一对应；执行前把尖括号占位符替换为当前项目真实值。流程入口是 `prompts/00-next-step.md`。

| 阶段 | Prompt | Skill |
|---|---|---|
| 00 下一步编排 | `prompts/00-next-step.md` | `workflow-orchestrator` |
| 01 项目初始化与工具链检查 | `prompts/01-project-bootstrap.md` | `project-bootstrap` |
| 02 需求业务梳理 | `prompts/02-requirements-analysis.md` | `requirements-analysis` |
| 03 项目总体架构设计 | `prompts/03-project-architecture-baseline.md` | `project-architecture-baseline` |
| 04 提案拆分、依赖排序与路线图 | `prompts/04-proposal-planning.md` | `proposal-planning` |
| 05 提案级需求分析 | `prompts/05-feature-requirements.md` | `feature-requirements` |
| 06 提案原型生成与评审 | `prompts/06-prototype-generation.md` | `prototype-generation` |
| 07 页面、功能区块、元素与交互事件清单 | `prompts/07-page-interaction-inventory.md` | `page-interaction-inventory` |
| 08 Figma UI 设计与 MCP 审计 | `prompts/08-figma-ui-audit.md` | `figma-ui-audit` |
| 09 功能详细设计总控 | `prompts/09-feature-design.md` | `feature-design` |
| 10 OpenAPI 与接口逻辑设计 | `prompts/10-api-contract-design.md` | `api-contract-design` |
| 11 前端详细设计 | `prompts/11-frontend-detail-design.md` | `frontend-detail-design` |
| 12 后端详细设计 | `prompts/12-backend-detail-design.md` | `backend-detail-design` |
| 13 测试设计与追踪矩阵 | `prompts/13-test-design.md` | `test-design` |
| 14 实现、TDD、验证与代码审查 | `prompts/14-implementation-orchestrator.md` | `implementation-orchestrator` |
| 15 独立验证与验收证据 | `prompts/15-independent-verification.md` | `independent-verifier` |
| 16 人工验收、归档与基线回写 | `prompts/16-acceptance-audit.md` | `acceptance-audit` |

输入、输出、审批点与门禁以 `docs/STEP-ARTIFACT-CONTRACTS.json` 为准；阶段总览见 `docs/STAGE-IO-OVERVIEW.md`。
