# 项目 · AI 研发流程工具包

> 语言：简体中文 ｜ 主文档：[README.md](README.md)

本仓库是一套面向 **OpenSpec + Superpowers + Figma MCP** 的 AI 研发流程工具包的源代码仓库：把项目研发拆成 10 个带审批与门禁的阶段，每个阶段由可独立加载的 Skill、Prompt、模板和确定性检查脚本组成。业务项目位于独立仓库，通过 vendored 方式引入本工具包的发布版本；本仓库不包含项目产物、工作流状态或业务代码。

## 当前仓库状态

工具包仓库通过以下命令校验：

```bash
bash scripts/ci-check.sh               # 仓库全量 CI 检查（包自检、回归、清单、布局）
python scripts/check-layout.py --mode toolkit  # 更严格的工具包专用布局检查
```

项目工作流命令（`scripts/workflow.py`、`scripts/next-step.py`、`openspec list`）与工作流状态（`workflow-state.json`）位于各业务项目仓库，不在本仓库。在项目仓库中继续研发时，对 Agent 说“下一步 / 继续 / 接着做”，它会加载 `workflow-orchestrator` Skill，依据项目的 `workflow-state.json` 与真实产物判定唯一安全的下一阶段。

## 阶段总览

下表主要产物均在业务项目仓库中生成；路径相对于该项目仓库。

| 阶段 | Skill | Prompt | 主要产物 |
|---|---|---|---|
| 01 项目初始化与工具链检查 | `project-bootstrap` | `prompts/01-project-bootstrap.md` | `AGENTS.md`、`workflow-state.json`、`docs/architecture/baseline-status.md`、`docs/project/toolchain-report.md` |
| 02 需求业务梳理 | `requirements-analysis` | `prompts/02-requirements-analysis.md` | `docs/product/` 需求、流程节点表、数据对象、RD 矩阵、业务规则、术语、验收政策 |
| 03 项目总体架构设计 | `project-architecture-baseline` | `prompts/03-project-architecture-baseline.md` | `docs/architecture/` 基线、ADR、基线 Manifest 与约束注册表（冻结） |
| 04 提案拆分与路线图 | `proposal-planning` | `prompts/04-proposal-planning.md` | `docs/product/proposal-roadmap.md` |
| 05 提案级需求分析 | `feature-requirements` | `prompts/05-feature-requirements.md` | `openspec/changes/<change-id>/` 的 proposal、specs、design、tasks、user-stories、基线影响/绑定 |
| 06 Figma 设计与评审（Figma-only） | `figma-design-review` | `prompts/06-figma-design-review.md` | `openspec/changes/<change-id>/design/figma-audit.md`、`.../figma-code/`、`.../figma-layout.csv` |
| 07 详细设计 | `detailed-design` | `prompts/07-detailed-design.md` | `openspec/changes/<change-id>/design.md` 五节、`.../design/test-cases.csv`、OpenAPI、API→IO 映射、`.../traceability.csv` |
| 08 实现与代码审查 | `implementation-orchestrator` | `prompts/08-implementation-orchestrator.md` | 源代码、测试、`.../design/evidence/code-review.md`、`figma-layout-check.json` |
| 09 独立验证 | `independent-verifier` | `prompts/09-independent-verification.md` | `.../design/evidence/independent-verification-report.md` 与 `.json` |
| 10 人工验收与归档 | `acceptance-audit` | `prompts/10-acceptance-audit.md` | `.../design/evidence/acceptance.md`、验收记录、OpenSpec archive、基线回写 |

阶段 DAG 的唯一权威定义在 `process/WORKFLOW-STAGES.json`；每个阶段的输入/输出/交接契约在 `process/STEP-ARTIFACT-CONTRACTS.md` 与 `.json`。

## 目录结构

| 路径 | 作用 |
|---|---|
| `.claude/skills/` | 11 个项目流程 Skill（10 个阶段 + `workflow-orchestrator`）；OpenSpec 辅助 Skill 由 OpenSpec CLI 在项目仓库中生成 |
| `prompts/` | 与 Skill 一一对应的阶段 Prompt；`prompts/00-next-step.md` 是入口 |
| `scripts/` | 结构、追踪、OpenAPI、测试、基线治理、工作流状态机等检查与工具脚本 |
| `templates/` | 项目基线、Change 辅助产物、工作流证据与交接报告模板 |
| `process/` | 流程规范（`PROCESS-MAP.md`、`TEMPLATE-POLICY.md`、`BASELINE-FEATURE-INTERACTION.md`、阶段契约、模板矩阵）与工具包设计文档 |
| `VERSION`、`process/TOOLKIT-MANIFEST.json` | 发布版本与 vendored 集合的生成登记表（路径、哈希、安装目标） |
| `AGENTS-zh.md` | 工具包开发约定的简体中文译本；英文主文件为 `AGENTS.md` |

业务项目仓库还包含 `docs/product|architecture|adr|project`、`openspec/`、`design/`、`workflow/`、`workflow-state.json` 与业务代码；工具包仓库从不存放这些内容。

## 快速开始

Windows 环境若无 `python3` 命令，请使用 `python`；`.sh` 脚本会自动探测。

```bash
bash scripts/ci-check.sh               # 仓库全量 CI 检查（包自检、回归、清单、布局）
python scripts/check-layout.py --mode toolkit  # 更严格的工具包专用布局检查
```

阶段门禁（`check-entry --step <id>`、`workflow.py request-review`、`approve`、`transition`）在业务项目仓库中运行：进入某阶段前先运行 `check-entry`（非 0 退出码表示禁止执行）；完成后运行检查、生成证据并执行 `request-review`，结束回合等待用户明确批准待评审阶段（任何无歧义的表述都算），再运行 `approve` 与 `transition`。

## 核心规则

以下规则适用于业务项目仓库内的工作；工具包仓库自身只遵循 [AGENTS.md](AGENTS.md) 中的布局、检查与发布规则。

## 核心规则

1. **产物落盘**：每阶段产物写入契约指定路径，不得只在聊天中输出；结束时按 `templates/workflow/step-handoff-report.md` 展示交接报告。
2. **状态纪律**：`workflow-state.json` 只记录门禁通过且审批完成的阶段；草案不得记为完成。
3. **模板治理**：正式产物遵循 `process/TEMPLATE-POLICY.md` 与 `process/OUTPUT-TEMPLATE-MATRIX.csv`；未知项写 `PENDING` 并说明责任人与阻塞条件，不适用项写 `N/A` 及理由，不得删除模板字段。
4. **基线优先**：功能 Change 开始前必须读取冻结基线并生成 `design/baseline-impact.md` 与 `design/baseline-binding.json`；实施期间不得直接修改冻结基线。
5. **UI 证据**：阶段 06 为 Figma-only。`openspec/changes/<change-id>/design/figma-audit.md`、`.../figma-code/`、`.../figma-layout.csv` 是唯一界面输入；08/09 运行 `check-figma-layout.py`、`check-design-tokens.py` 做数值断言。全流程不使用截图作为证据。
6. **OpenSpec**：标准 artifact 为 `proposal.md`、`specs/<capability>/spec.md`、`design.md`、`tasks.md`；`tasks.md` 必须使用 `- [ ]` / `- [x]`；归档前必须人工批准。
7. **Agent 边界**：不自动安装依赖、不提交代码、不改 CI、不归档、不发布，不替业务/设计/架构负责人批准未决规则。

## 进一步阅读

> 流程文档中英文同步维护，每份文档顶部提供语言切换；英文为主文档并沿用正式文件名，中文译本为同路径加 `-zh.md`；`scripts/README-zh.md` 为脚本说明的中文版。

- [AGENTS-zh.md](AGENTS-zh.md) — 仓库约定与流程入口
- [process/PROCESS-MAP-zh.md](process/PROCESS-MAP-zh.md) — 阶段与产物全景
- [process/STAGE-IO-OVERVIEW-zh.md](process/STAGE-IO-OVERVIEW-zh.md) — 逐阶段输入/输出总览（由契约自动生成）
- [process/P0-RUNTIME-GOVERNANCE-zh.md](process/P0-RUNTIME-GOVERNANCE-zh.md) — 状态机、门禁、交接包与独立验证
- [process/BASELINE-FEATURE-INTERACTION-zh.md](process/BASELINE-FEATURE-INTERACTION-zh.md) — 项目基线与功能 Change 的双向治理
- [process/TEMPLATE-POLICY-zh.md](process/TEMPLATE-POLICY-zh.md) — 输出模板治理规范
- [process/STEP-ARTIFACT-CONTRACTS-zh.md](process/STEP-ARTIFACT-CONTRACTS-zh.md) — 阶段交接契约（权威清单）
- [process/TOOLKIT-UPGRADE-zh.md](process/TOOLKIT-UPGRADE-zh.md) — 工具包接入项目仓库与升级指南
- [process/TOOLKIT-CHANGELOG.md](process/TOOLKIT-CHANGELOG.md) — 发布说明
- [process/QUESTION-COVERAGE-CHECKLIST-zh.md](process/QUESTION-COVERAGE-CHECKLIST-zh.md) — 02/03/05/07 的建议提问清单（可选证据块，不是硬门禁）
- [scripts/README-zh.md](scripts/README-zh.md) — 检查脚本说明

> 说明：本文件是 [README.md](README.md) 的简体中文版本，两者同步维护；如有差异以 `README.md` 为准。

## 许可证

Copyright (c) 2026 litianyiliwei。本项目基于 [MIT 许可证](LICENSE) 授权。
