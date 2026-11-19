# 工具包接入与升级指南

> 语言：[English](TOOLKIT-UPGRADE.md) ｜ 简体中文（本文）

> 适用于以 vendored 方式引入本工具包的**业务项目仓库**。工具包仓库自身遵循 `AGENTS.md`。

## 1. 仓库角色

- **工具包仓库**——本仓库：Skills、Prompts、模板、脚本、流程规范与发布标签。维护者随时更新；项目在主动升级前不受影响。
- **项目仓库**——每个业务项目一个：基线（`docs/`）、OpenSpec Changes、设计证据、工作流状态、业务代码，以及一份 vendored 工具包副本。团队日常在此协作。

项目仓库永不合并工具包的 git 历史；`toolkit-lock.json` 精确记录已安装的工具包版本。

## 2. 创建项目仓库

1. 新建空仓库（例如在 GitHub 上）并在本地克隆。
2. 从标签发布安装工具包：

   ```bash
   python <工具包路径>/scripts/toolkit-sync.py init --from <工具包仓库URL或本地路径> --ref toolkit-v2.0.0 --project .
   ```

   该命令写入 vendored 工具包文件、组合 `AGENTS.md` / `AGENTS-zh.md`、`openspec/config.yaml`、`.gitignore`，在缺失时脚手架 `workflow-state.json`，并写入 `toolkit-lock.json`。
3. 将安装作为单独一次提交，然后照常开始阶段 01（`01-project-bootstrap`）。
4. 可选：把工具包仓库添加为只读远端，便于后续升级：

   ```bash
   git remote add toolkit <工具包仓库URL>
   ```

## 3. 升级项目

升级**在项目仓库内**执行，绝不在工具包仓库执行。

```bash
git fetch toolkit --tags
python scripts/toolkit-sync.py plan --ref toolkit-v2.1.0
python scripts/toolkit-sync.py apply --ref toolkit-v2.1.0
```

- `plan` 为只读：列出新增/修改/删除的 vendored 文件、本地修改冲突、以及需要的状态迁移。
- 工作区不干净、存在 `pending_approvals`/`blocked_items`、或另有升级锁时，`apply` 拒绝执行。它会把 `workflow-state.json` 备份到 `workflow/state-backups/`，只替换清单内路径，刷新托管块，重新生成 `process/STAGE-IO-OVERVIEW.md` 与基线索引，运行布局与 CI 检查，最后更新 `toolkit-lock.json`。
- 把结果放到 `toolkit/upgrade-vX.Y.Z` 分支，发起 PR，等待 CI 通过（`toolkit-sync.py verify`、布局、项目检查），合并后团队拉取。

## 4. 静态分析门禁：启用前保持休眠

静态分析门禁以“显式启用”为前提，因此升级绝不会打断进行中的项目。

- 不新增无条件的必需文件：`scripts/check-required-files.sh --strict` 不要求 `docs/architecture/quality-gates.json`，阶段 03 的契约输出只在升级后该阶段运行（或被重跑）时创建。
- 在 `docs/architecture/quality-gates.json` 存在之前，所有静态门禁保持休眠：条件入口为 `scripts/ci-check.sh`、`scripts/verify-before-completion.sh` 与 08/09 的 `scripts/workflow.py transition`；它们只在文件存在时才运行质量门禁脚本；否则 CI 输出 `SKIP_STATIC_GATES=not-adopted`，各阶段行为与升级前完全一致。
- 既有项目通过下一次阶段 03 基线修订（或显式重跑阶段 03）启用门禁：按语言选择工具，写入并冻结 `quality-gates.json`，在 `technology-decisions.md`/`test-strategy.md` 增加静态分析章节，并登记 `QUALITY-STATIC-001` 约束。此后 07/08/09/10 产出并验证静态证据（`design/evidence/static-analysis.json`、`design/evidence/static-analysis-independent.json`、`design/evidence/static-analysis-logs/`）。
- 不启用静态分析的项目可正常持续升级；工具包检查保持绿色，任何阶段都不要求新产物。
- 现有 `scripts/test-upgrade-rehearsal.py` 只演练 init → upgrade → conflict → repair → rollback；不包含静态门禁夹具，也不演练启用路径。

## 5. 冲突与分叉

本地修改过的 vendored 文件会中止升级并被列出，二选一：

- `--take-upstream`——接受工具包版本（丢弃本地修改）。
- `--keep-local`——保留本地内容，并把该路径登记到 `toolkit-lock.json` 的 `forks` 中。

登记的分叉应尽快回流到工具包；当下一次升级包含对应上游改动时即可丢弃分叉。

## 6. 回滚

每次升级是一个单独提交。回滚步骤：

1. `git revert <升级提交>`（或从上一提交恢复 vendored 路径）。
2. 若执行过迁移，恢复状态备份：`python scripts/workflow.py recover-state --backup workflow/state-backups/<timestamp>.json`。
3. 从被回退的提交恢复上一版 `toolkit-lock.json`。

## 7. 多人协作规则

- 升级由一名指定的维护者以专门 PR 执行；其他成员只拉取合并后的提交。
- vendored 路径对团队成员只读；CI 的 `toolkit-sync.py verify` 对任何哈希不符直接失败。
- 每个工作流阶段只有一名“驱动者”；`workflow-state.json` 只由 `scripts/workflow.py` 写入，并发修改通过重跑工作流命令解决，绝不手工合并 JSON。
- `.claude/settings.local.json` 保持按机器本地、gitignore。

## 8. 第三方文件

`openspec-*` Skills 与 `opsx` 命令由 OpenSpec CLI 在项目仓库中生成。`toolkit-sync.py` 从不写入或删除它们；锁在安装时记录它们的存在与 CLI 版本。OpenSpec CLI 升级后，用 CLI 重新生成这些文件。

## 9. CI 期望

vendored `.github/workflows/toolkit-ci.yml` 运行 `bash scripts/ci-check.sh`；项目模式下依次执行工具包包检查、清单检查、布局检查、`toolkit-sync.py verify --require-lock` 与项目检查。`verify` 失败意味着有 vendored 文件被手工修改；运行 `toolkit-sync.py repair` 或重新应用该发布版本。
