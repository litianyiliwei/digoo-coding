# 每个流程阶段的 Prompt 索引

Prompt 文件位于 `prompts/`，与 `.claude/skills/<skill-id>/SKILL.md` 一一对应；执行前把尖括号占位符替换为当前项目真实值。流程入口是 `prompts/00-next-step.md`。旧版拆分阶段的 Prompt 已归档到 `prompts/legacy/`，不再属于 vibe 流程。

| 阶段 | Prompt | Skill |
|---|---|---|
| 00 下一步编排 | `prompts/00-next-step.md` | `workflow-orchestrator` |
| 01 项目初始化与工具链检查 | `prompts/01-project-bootstrap.md` | `project-bootstrap` |
| 02 需求业务梳理 | `prompts/02-requirements-analysis.md` | `requirements-analysis` |
| 03 项目总体架构设计 | `prompts/03-project-architecture-baseline.md` | `project-architecture-baseline` |
| 04 提案拆分、依赖排序与路线图 | `prompts/04-proposal-planning.md` | `proposal-planning` |
| 05 提案级需求分析 | `prompts/05-feature-requirements.md` | `feature-requirements` |
| 06 原型、页面与交互清单 | `prompts/06-ui-prototype-inventory.md` | `ui-prototype-inventory` |
| 07 详细设计、接口与测试设计 | `prompts/07-detailed-design.md` | `detailed-design` |
| 08 实现、TDD、验证与代码审查 | `prompts/08-implementation-orchestrator.md` | `implementation-orchestrator` |
| 09 独立验证与验收证据 | `prompts/09-independent-verification.md` | `independent-verifier` |
| 10 人工验收、归档与基线回写 | `prompts/10-acceptance-audit.md` | `acceptance-audit` |

输入、输出、审批点与门禁以 `docs/STEP-ARTIFACT-CONTRACTS.json` 为准；阶段总览见 `docs/STAGE-IO-OVERVIEW.md`。
