# 项目 · AI 研发流程工具包

> 语言：简体中文 ｜ 主文档：[README.md](README.md)

本仓库是一套面向 **OpenSpec + Superpowers + Figma MCP** 的 AI 研发流程工具包：把项目研发拆成 10 个带审批与门禁的阶段，每个阶段由可独立加载的 Skill、Prompt、模板和确定性检查脚本组成。业务代码尚未开始实现，仓库当前处于初始化状态。

## 当前仓库状态

| 项 | 值 |
|---|---|
| 工作流状态 | 阶段 `01-project-bootstrap` 已完成，下一步 `02-requirements-analysis`（需求业务梳理） |
| 活动 Change | 无 |
| 待审批 / 阻断项 | 无 |
| 项目基线 | `v0.1.0` DRAFT，六个基线域均未冻结 |
| OpenSpec | 无活动 Change、无主规格（`openspec/changes/`、`openspec/specs/` 为空骨架） |
| 业务源代码 | 无 |

继续研发时，对 Agent 说“下一步 / 继续 / 接着做”，它会先加载 `workflow-orchestrator` Skill，依据 `workflow-state.json` 与真实产物判定唯一安全的下一阶段。

## 阶段总览

| 阶段 | Skill | Prompt | 主要产物 |
|---|---|---|---|
| 01 项目初始化与工具链检查 | `project-bootstrap` | `prompts/01-project-bootstrap.md` | `AGENTS.md`、`workflow-state.json`、`docs/architecture/baseline-status.md`、`docs/project/toolchain-report.md` |
| 02 需求业务梳理 | `requirements-analysis` | `prompts/02-requirements-analysis.md` | `docs/product/` 需求、流程节点表、数据对象、RD 矩阵、业务规则、术语、验收政策 |
| 03 项目总体架构设计 | `project-architecture-baseline` | `prompts/03-project-architecture-baseline.md` | `docs/architecture/` 基线、ADR、基线 Manifest 与约束注册表（冻结） |
| 04 提案拆分与路线图 | `proposal-planning` | `prompts/04-proposal-planning.md` | `docs/product/proposal-roadmap.md` |
| 05 提案级需求分析 | `feature-requirements` | `prompts/05-feature-requirements.md` | `openspec/changes/<change-id>/` 的 proposal、specs、design、tasks、user-stories、基线影响/绑定 |
| 06 Figma 设计与评审（Figma-only） | `figma-design-review` | `prompts/06-figma-design-review.md` | `design/figma-audit.md`、`design/figma-code/`、`design/figma-layout.csv` |
| 07 详细设计 | `detailed-design` | `prompts/07-detailed-design.md` | `design.md` 五节、`design/test-cases.csv`、OpenAPI、API→IO 映射、`traceability.csv` |
| 08 实现与代码审查 | `implementation-orchestrator` | `prompts/08-implementation-orchestrator.md` | 源代码、测试、`design/evidence/code-review.md`、`figma-layout-check.json` |
| 09 独立验证 | `independent-verifier` | `prompts/09-independent-verification.md` | `design/evidence/independent-verification-report.md` 与 `.json` |
| 10 人工验收与归档 | `acceptance-audit` | `prompts/10-acceptance-audit.md` | `design/evidence/acceptance.md`、验收记录、OpenSpec archive、基线回写 |

阶段 DAG 的唯一权威定义在 `docs/WORKFLOW-STAGES.json`；每个阶段的输入/输出/交接契约在 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `.json`。

## 目录结构

| 路径 | 作用 |
|---|---|
| `.claude/skills/` | 11 个项目流程 Skill（10 个阶段 + `workflow-orchestrator`）与 6 个 OpenSpec 辅助 Skill，共 17 个 |
| `prompts/` | 与 Skill 一一对应的阶段 Prompt；`prompts/00-next-step.md` 是入口 |
| `scripts/` | 结构、追踪、OpenAPI、测试、基线治理、工作流状态机等检查与工具脚本 |
| `templates/` | 项目基线、Change 辅助产物、工作流证据与交接报告模板 |
| `docs/` | 流程规范（`PROCESS-MAP.md`、`TEMPLATE-POLICY.md`、`BASELINE-FEATURE-INTERACTION.md` 等）与项目级基线骨架 |
| `openspec/` | OpenSpec 配置与 Change/规格目录（当前为空骨架） |
| `workflow/` | 阶段证据 `evidence/` 与 SHA-256 交接包 `handoffs/` |
| `workflow-state.json` | 跨阶段状态索引；只通过 `scripts/workflow.py transition` 推进，禁止手改 |
| `AGENTS.md` | 仓库级 Agent 约定（流程入口、模板政策、Agent 行为边界） |

## 快速开始

Windows 环境若无 `python3` 命令，请使用 `python`；`.sh` 脚本会自动探测。

```bash
python scripts/next-step.py            # 只读：打印下一阶段
python scripts/workflow.py status      # 工作流状态摘要
python scripts/workflow.py check-entry --step 02-requirements-analysis
python scripts/check-package.py        # 工具包自检
bash scripts/check-required-files.sh   # 基线文件存在性（非 strict）
```

进入某阶段前先运行 `check-entry --step <id>`（非 0 退出码表示禁止执行）；完成后按脚本提示生成证据并执行 `workflow.py transition`。

## 核心规则

1. **产物落盘**：每阶段产物写入契约指定路径，不得只在聊天中输出；结束时按 `templates/workflow/step-handoff-report.md` 展示交接报告。
2. **状态纪律**：`workflow-state.json` 只记录门禁通过且审批完成的阶段；草案不得记为完成。
3. **模板治理**：正式产物遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv`；未知项写 `PENDING` 并说明责任人与阻塞条件，不适用项写 `N/A` 及理由，不得删除模板字段。
4. **基线优先**：功能 Change 开始前必须读取冻结基线并生成 `design/baseline-impact.md` 与 `design/baseline-binding.json`；实施期间不得直接修改冻结基线。
5. **UI 证据**：阶段 06 为 Figma-only。`design/figma-audit.md`、`figma-code/`、`figma-layout.csv` 是唯一界面输入；08/09 运行 `check-figma-layout.py`、`check-design-tokens.py` 做数值断言。全流程不使用截图作为证据。
6. **OpenSpec**：标准 artifact 为 `proposal.md`、`specs/<capability>/spec.md`、`design.md`、`tasks.md`；`tasks.md` 必须使用 `- [ ]` / `- [x]`；归档前必须人工批准。
7. **Agent 边界**：不自动安装依赖、不提交代码、不改 CI、不归档、不发布，不替业务/设计/架构负责人批准未决规则。

## 进一步阅读

- [AGENTS.md](AGENTS.md) — 仓库约定与流程入口
- [docs/PROCESS-MAP.md](docs/PROCESS-MAP.md) — 阶段与产物全景
- [docs/STAGE-IO-OVERVIEW.md](docs/STAGE-IO-OVERVIEW.md) — 逐阶段输入/输出总览（由契约自动生成）
- [docs/P0-RUNTIME-GOVERNANCE.md](docs/P0-RUNTIME-GOVERNANCE.md) — 状态机、门禁、交接包与独立验证
- [docs/BASELINE-FEATURE-INTERACTION.md](docs/BASELINE-FEATURE-INTERACTION.md) — 项目基线与功能 Change 的双向治理
- [docs/TEMPLATE-POLICY.md](docs/TEMPLATE-POLICY.md) — 输出模板治理规范
- [docs/STEP-ARTIFACT-CONTRACTS.md](docs/STEP-ARTIFACT-CONTRACTS.md) — 阶段交接契约（权威清单）
- [scripts/README.md](scripts/README.md) — 检查脚本说明

> 说明：本文件是 [README.md](README.md) 的简体中文版本，两者同步维护；如有差异以 `README.md` 为准。
