# AGENTS.md — 工具包仓库约定

> 语言：简体中文 ｜ [English](AGENTS.md)

> 状态：APPROVED（2026-11-18 采用双仓库模型；本仓库为工具包源代码仓库；项目流程约定以 `templates/workflow/agents-managed.md` 分发，由 `scripts/toolkit-sync.py` 安装进项目仓库）

## 仓库角色

- 本仓库是 AI 研发流程**工具包源码**。业务项目位于独立仓库，通过 vendored 方式引入本工具包的发布版本，并在项目仓库中运行阶段流程。
- 只放工具包内容：`.claude/skills/<stage>/`、`.claude/hooks/`、`.claude/settings.json`、`prompts/`、`templates/`、`scripts/`、`process/`、`README*.md`、`LICENSE`、`.gitattributes`、`VERSION`。
- 绝不把项目产物加入本仓库：`docs/product|architecture|adr|project`、`openspec/`、`design/`、`workflow/`、`workflow-state.json`、`toolkit-lock.json` 或业务代码。`_trash/` 是 gitignore 的本地历史（已完成的计划、移除的脚本、任务草稿），不纳入跟踪。
- 项目流程规则（阶段门禁、模板政策、UI 规则、OpenSpec 约定）不属于本文件的范围；其权威托管块为 `templates/workflow/agents-managed.md`（中文为 `agents-managed-zh.md`）。

## 布局与所有权

- `process/` 存放流程规范与登记表；项目运行路径不会出现在这里。
- `process/proposals/` 只存放仍在进行中的工作计划。计划对应的工作落地后，把其设计文档、实施计划和演练证据移到 `_trash/<YYYY-MM-DD>/process/proposals/`；已完成的计划文档属本地历史，不再作为受跟踪的工具包内容。`.superpowers/sdd/` 下已完成的任务草稿按同样方式归档（`_trash/<YYYY-MM-DD>/superpowers-sdd/`）。
- 安装进项目仓库的 vendored 集合由 `process/TOOLKIT-MANIFEST.json` 声明（生成物，禁止手改）。
- OpenSpec CLI 生成的第三方文件（`openspec-*` Skills、`opsx` 命令）属于项目仓库，不属于本工具包。

## 检查

任何评审前运行以下全部命令；结果 fail-closed，不得伪造：

```bash
bash scripts/ci-check.sh
python scripts/check-layout.py --mode toolkit
```

`ci-check.sh` 已包含包自检、脚本回归测试、清单校验与 `auto` 模式的布局检查；单独运行的 `--mode toolkit` 检查更严格，不可省略。

## 生成文件

- `process/STAGE-IO-OVERVIEW.md` 与 `process/TOOLKIT-MANIFEST.json` 为生成物。用其脚本重新生成（`stage-io-report.py --out ...`、`gen-manifest.py --write`），禁止手改。
- `VERSION` 只在发布时递增，并同时打 `toolkit-vX.Y.Z` 标签、写 `process/TOOLKIT-CHANGELOG.md` 条目。

## 发布流程

1. 上述检查全绿；2. 重新生成生成物；3. 更新 `VERSION` 与变更日志；4. 由用户提交并打标签。Agent 从不提交、打标签或发布。
项目在自己的仓库内用 `scripts/toolkit-sync.py` 升级到指定标签。

## 项目仓库规则

- 阶段流程在业务项目仓库中运行。接入与升级步骤见 `process/TOOLKIT-UPGRADE.md`。
- 项目的 `AGENTS.md` 包含 `<!-- toolkit:begin -->` 与 `<!-- toolkit:end -->` 之间的托管块，以及项目所有内容（状态头、Project Goal、项目约定）。在项目中工作的 Agent 绝不能编辑托管块内部。

## Agent 行为边界

- 不自动安装依赖、不提交代码、不在已批准的工具包变更之外改动 CI、不归档、不发布。
- 不替业务/设计/架构负责人批准未决规则。
- 不编辑生成物；绝不把项目产物复制进本仓库。
- 外部工具（Figma MCP、OpenSpec CLI、Superpowers）以实际可访问能力为准；不可读取的链接/字段不视为已审查。
