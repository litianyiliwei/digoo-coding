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

   该命令写入 vendored 工具包文件、组合 `AGENTS.md` / `AGENTS-zh.md`、`openspec/config.yaml`、`.gitignore`，在缺失时脚手架 `workflow-state.json`，并写入 `toolkit-lock.json`。安装后按“项目自有路径”小节声明项目自有路径。
3. 将安装作为单独一次提交，然后照常开始阶段 01（`01-project-bootstrap`）。
4. 可选：把工具包仓库添加为只读远端，便于后续升级：

   ```bash
   git remote add toolkit <工具包仓库URL>
   ```

### 项目自有路径（project-extensions.json）

安装后，把项目特有的顶层路径声明在仓库根的 `project-extensions.json`，并随项目内容一起提交：

```json
{
  "root": ["backend", "frontend", "infra", ".vscode"],
  "paths": ["docs/api"]
}
```

- `root`：项目自有的额外顶层目录或文件（服务根、monorepo 包、编辑器配置等）。
- `paths`：`docs/` 下的路径；`docs/` 后的第一级子目录会被放开（例如 `docs/api` 允许 `docs/api/` 目录）。
- 项目模式布局检查接受 vendored 工具包路径、内置项目根条目与上述声明；未声明条目会让检查失败，报错信息会给出需要添加的声明片段。
- 被 Git 忽略的本地产物无需声明：检查按仓库跟踪内容判断，会跳过未跟踪且被 Git 忽略的路径（`node_modules/`、`.venv/`、`dist/`）；不在 Git 工作树内时回退为扫描工作区。

## 3. 升级项目

升级**在项目仓库内**执行，绝不在工具包仓库执行。

```bash
git fetch toolkit --tags
python scripts/toolkit-sync.py plan --ref toolkit-v2.1.0
python scripts/toolkit-sync.py apply --ref toolkit-v2.1.0
```

- `plan` 为只读：列出新增/修改/删除的 vendored 文件、本地修改冲突、以及需要的状态迁移。
- 工作区不干净、存在 `pending_approvals`/`blocked_items`、或另有升级锁时，`apply` 拒绝执行。在写入任何文件前，它会先用目标发布版本的项目布局规则检查当前仓库；失败时以退出码 2 中止且不改动工作区（按“项目自有路径”小节修正声明）。随后它把 `workflow-state.json` 备份到 `workflow/state-backups/`，只替换清单内路径，刷新托管块，重新生成 `process/STAGE-IO-OVERVIEW.md` 与基线索引，用安装后的版本运行布局与 CI 检查，最后更新 `toolkit-lock.json`。
- 把结果放到 `toolkit/upgrade-vX.Y.Z` 分支，发起 PR，等待 CI 通过（`toolkit-sync.py verify`、布局、项目检查），合并后团队拉取。

### v2 工作流状态升级（多 Change 泳道）

发布 v2 多泳道状态的工具包，需要在每个项目执行一次状态转换：

```bash
python scripts/workflow.py upgrade-state --reason "adopt multi-lane workflow"
```

- 命令幂等，先把 v1 状态备份到 `workflow/evidence/state-v2-backup-<时间戳>.json`，把项目阶段 01–04 移入 `project` 泳道，把活动 Change 的 05–10 移入 `changes[<change-id>]`。
- 未执行前，`start-change`、`list-changes` 与 v2 泳道解析返回 `UPGRADE_REQUIRED`；原有 v1 命令行为不变。
- 转换后，用 `start-change --change-id <id>` 启动提案（触发 roadmap 依赖门禁），用 `list-changes` 查看泳道，05–10 阶段传 `--change-id`。`next-change` 保留为兼容别名。转换后写入的证据与 handoff 使用 `workflow/evidence/<change-id>/` 与 `workflow/handoffs/<change-id>/`；旧的平铺证据保留在磁盘供审计。

## 4. 静态分析门禁：启用前保持休眠

静态分析门禁以“显式启用”为前提，因此升级绝不会打断进行中的项目。

- 不新增无条件的必需文件：`scripts/check-required-files.sh --strict` 不要求 `docs/architecture/quality-gates.json`，阶段 03 的契约输出只在升级后该阶段运行（或被重跑）时创建。
- 在 `docs/architecture/quality-gates.json` 存在之前，所有静态门禁保持休眠：条件入口为 `scripts/ci-check.sh`、`scripts/verify-before-completion.sh` 与 08/09 的 `scripts/workflow.py transition`；它们只在文件存在时才运行质量门禁脚本；否则 CI 输出 `SKIP_STATIC_GATES=not-adopted`，各阶段行为与升级前完全一致。
- 既有项目通过下一次阶段 03 基线修订（或显式重跑阶段 03）启用门禁：按语言选择工具，写入并冻结 `quality-gates.json`，在 `technology-decisions.md`/`test-strategy.md` 增加静态分析章节，并登记 `QUALITY-STATIC-001` 约束。此后 07/08/09/10 产出并验证静态证据（`design/evidence/static-analysis.json`、`design/evidence/static-analysis-independent.json`、`design/evidence/static-analysis-logs/`）。
- 不启用静态分析的项目可正常持续升级；工具包检查保持绿色，任何阶段都不要求新产物。
- 现有 `scripts/test-upgrade-rehearsal.py` 只演练 init → upgrade → conflict → repair → rollback；不包含静态门禁夹具，也不演练启用路径。

## 5. 模块包：新项目默认

模块模型由 `docs/architecture/code-layout.json` 的策略驱动；新项目默认 `module-packages`。

- **新项目**：阶段 03 记录 `code-layout.json`，`strategy: module-packages`，并填写 roots、`package_pattern`、`integration_paths`、`frozen_paths`、`module_card` 与 `dependency_rules`；阶段 04 创建 `docs/product/capabilities.csv`、`docs/product/modules.csv` 与模块化路线图列。此后 07 的 `### Implementation Slice` 与 08 的 footprint 检查为硬转换门禁。
- **既有项目**升级后按项目选择：
  - `none`：不提供 `code-layout.json`（或写 `strategy: none`）；切片/footprint 门禁打印 `FOOTPRINT_GATE=SKIPPED (strategy none)`，注册表规则跳过。无需新增产物。
  - `footprint`：新增 `code-layout.json`，`strategy: footprint`，填写 roots/包模式与集成/冻结路径；路线图行需 `Code Target`；不要求注册表与模块卡。
  - `module-packages`：另需新增 `capabilities.csv`/`modules.csv`（在阶段 04 或显式重跑阶段 04 时），补充模块化路线图列，并在 `<module_path>/MODULE.md` 维护模块卡。
- **采用布局与注册表**：通过下一次阶段 03 基线修订或显式重跑阶段 03 采用；布局随架构基线冻结。`capabilities.csv` 与 `modules.csv` 是可变的项目级注册表，不是冻结基线文件：阶段 05 更新、阶段 10 回写；它们有意不列入 `baseline-manifest.json`，变更无需基线修订。
- 升级不会因缺少模块文件而失败：所有模块门禁以 `code-layout.json` 存在且声明有效策略为前提；布局无效时 fail-closed，而不是静默跳过。

## 6. HTML 优先的 UI 设计（未发布）

- **无需迁移 workflow-state。** 阶段 ID `06-figma-design-review` 与 Skill 名称保持不变，现有 `workflow-state.json` 继续可用。
- **新 Change：** 阶段 05 必须在 `proposal.md` 声明 `Target Platforms`，并在 `design/user-stories.md` 写入 `- Target platforms:`（规范值 `web|h5|mini-program|app|android|ios|harmonyos|desktop|pda`）；阶段 06 默认产出 `design/ui-html/`，并写明 HTML 来源（用户直接提供、AI 按需求生成，或 Figma-to-HTML 转换）。运行 `bash scripts/new-change-assets.sh <change-id>` 生成新的 `ui-html` 模板及更新后的 `figma-audit.md`/`figma-layout.csv`。
- **既有项目产物：** 在下一次阶段 04/05 门禁前，为 `docs/product/requirements-analysis.md` 增加 `## 10. Target Platforms and Client Forms`，并为路线图增加 `Target Platforms` 列；进行中的 Change 必须在下一阶段门禁前补齐平台声明与新的 UI 契约；已完成 Change 不重写。
- **旧版 UI Change：** `check-figma-audit.py` 仍接受直接 Figma 来源；不带 `--require-framework` 时旧 Change 可继续通过既有契约。新 Change 应使用 HTML 优先契约并带 `--require-framework`。
- **实现证据：** UI 验收/代码审查/独立验证表现在接受 HTML `data-node-id` 或 Figma node id 作为设计来源引用；`check-figma-layout.py` 从 `figma-layout.csv` 读取各 PAGE 视口，旧表回退到 `--viewport`。

## 7. 冲突与分叉

本地修改过的 vendored 文件会中止升级并被列出，二选一：

- `--take-upstream`——接受工具包版本（丢弃本地修改）。
- `--keep-local`——保留本地内容，并把该路径登记到 `toolkit-lock.json` 的 `forks` 中。

登记的分叉应尽快回流到工具包；当下一次升级包含对应上游改动时即可丢弃分叉。

## 8. 回滚

每次升级是一个单独提交。回滚步骤：

1. `git revert <升级提交>`（或从上一提交恢复 vendored 路径）。
2. 若执行过迁移，恢复状态备份：`python scripts/workflow.py recover-state --backup workflow/state-backups/<timestamp>.json`。
3. 从被回退的提交恢复上一版 `toolkit-lock.json`。

## 9. 多人协作规则

- 升级由一名指定的维护者以专门 PR 执行；其他成员只拉取合并后的提交。
- vendored 路径对团队成员只读；CI 的 `toolkit-sync.py verify` 对任何哈希不符直接失败。
- 每个工作流阶段只有一名“驱动者”；`workflow-state.json` 只由 `scripts/workflow.py` 写入，并发修改通过重跑工作流命令解决，绝不手工合并 JSON。
- `.claude/settings.local.json` 保持按机器本地、gitignore。

## 10. 第三方文件

`openspec-*` Skills 与 `opsx` 命令由 OpenSpec CLI 在项目仓库中生成。`toolkit-sync.py` 从不写入或删除它们；锁在安装时记录它们的存在与 CLI 版本。OpenSpec CLI 升级后，用 CLI 重新生成这些文件。

## 11. CI 期望

vendored `.github/workflows/toolkit-ci.yml` 运行 `bash scripts/ci-check.sh`；项目模式下依次执行工具包包检查、清单检查、布局检查、`toolkit-sync.py verify --require-lock` 与项目检查。布局检查按 Git 跟踪内容判断，未跟踪且被 Git 忽略的路径会被跳过，因此本地存在的依赖/构建目录（或 CI 在检查前安装的依赖）不会让它失败。`verify` 失败意味着有 vendored 文件被手工修改；运行 `toolkit-sync.py repair` 或重新应用该发布版本。
