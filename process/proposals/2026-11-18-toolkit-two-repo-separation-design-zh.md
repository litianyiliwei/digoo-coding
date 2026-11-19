# 工具包/项目双仓库分离 — 设计

> 状态：草案 v2 — 待用户批准
> 版本说明：按用户 2026-11-18 的决定，v2 取代 v1 的单仓库物理分离：**两个仓库——工具包仓库随时更新，业务项目仓库供团队持续共同开发提交。**
> 日期：2026-11-18
> 基线：提交 `6d6654a` 时的仓库布局
> Language: [English](2026-11-18-toolkit-two-repo-separation-design.md) | 简体中文（本文）

## 1. 意图与原因

目前一个仓库承担两个角色：既是 AI 研发流程工具包的源码，又是产品项目的工作区。工具包改动与项目工作因此共享同一份 git 历史与同一棵目录树：每次工具包升级都要合并进项目分支，混用文件（`AGENTS.md`、`openspec/config.yaml`、`.gitignore`、`.claude/settings.json`）永久冲突；模板与产物甚至同名，模板矩阵还有 15 行直接指向产物路径，导致部分产物根本没有模板。

团队同时需要两种相反的工作方式：工具包必须能由维护者**随时、持续更新**且不干扰任何项目；业务项目仓库必须支持多名开发者的**日常协作提交**且不被工具包的演进拖累。

选定模型为**双仓库**：

- **工具包仓库**（本仓库）：承载 Skills、Prompts、模板、脚本、流程规范与发布标签。维护者随时提交与合并；CI 保护工具包自身。
- **业务项目仓库**（每个项目一个）：承载全部项目产物（基线、OpenSpec Changes、设计证据、状态）与业务代码。团队日常提交；工具包只以**脚本应用并加锁的 vendored 快照**（随附副本）形式进入。

选择 vendoring（在固定路径上复制工具包文件 + `toolkit-lock.json`）而不是 submodule、subtree 或符号链接，是因为在 Windows/macOS 下它同时满足全部硬约束，并保持 Claude Code 的 Skill 发现可用。工具包的 git 历史永远不会进入项目仓库，升级就是普通、可评审的提交。

## 2. 目标

- 工具包仓库的更新永远不要求项目仓库做任何动作；项目按需升级到明确的标签。
- 项目仓库**不含工具包的 git 历史**，也没有混合目录；工具包文件只以加锁、可校验的 vendored 集合存在。
- 项目仓库的 `docs/`（除四个产物子目录外）、`openspec/changes/`、`openspec/specs/` 只放项目产物。
- 所有可复用模板位于工具包仓库的 `templates/`；模板矩阵只引用模板。
- 升级由脚本执行、有版本、可审计，并对多人安全：分支升级 → PR → CI → 合并；所有成员拉取。
- 布局与所有权由两个仓库各自 CI 中的检查脚本强制执行。

## 3. 非目标与反目标

**非目标**

- 不使用 git submodule、git subtree 或符号链接的 Skill 目录（Windows 下脆弱，Claude Code 发现不可靠）。
- 不把工具包打包为 Claude Code 插件。
- 不把 Skill 移出 `.claude/skills/`（Claude Code 只从该处发现项目 Skill；OpenCode 回退 `.agents/skills`）。
- 不用工具包副本替换 OpenSpec CLI 生成文件（`openspec-*` Skills、`opsx` 命令）；它们属于项目仓库、由 CLI 生成。
- 不改写项目仓库的 git 历史或工具包仓库的既有历史。
- 不把 `templates/` 改名（已有数百处引用）。

**反目标**

- 任何迫使项目升级的工具包改动。
- 任何写入项目产物路径的升级操作。
- 静默覆盖开发者本地修改过的 vendored 文件。
- 团队成员需要口头知识才能区分工具包文件与项目文件。
- 任何模板存在第二个事实来源。

## 4. 约束

- Claude Code 的 Skill 发现路径固定为 `.claude/skills/`；因此 vendored 阶段 Skill 必须恰好位于项目仓库的该路径。
- OpenSpec CLI 要求项目仓库中 `openspec/config.yaml` 固定存在。
- 工具包脚本以「仓库根」解析路径（`Path(__file__).parents[1]`）；vendoring 必须保持工具包目录布局相对项目根不变，让 `scripts/`、`prompts/`、`templates/`、`process/`、`.claude/` 路径无需改写即可工作。
- PreToolUse 守卫（`.claude/hooks/stage-boundary-guard.py`）硬编码契约路径；它是 vendored 文件之一，迁移后路径必须指向 `process/`。
- 全仓库有 313 处对 `docs/<流程文档>` 的引用，分布在约 60 个工具包文件中；流程文档迁入 `process/` 需要脚本化改写并由现有测试套件验证。
- `workflow-state.json` 只能由 `scripts/workflow.py` 写入；`atomic_json` 已使用 `O_EXCL` 的 `*.json.lock`。
- Windows 与 macOS 成员共享两个仓库；`.gitattributes` 保持行尾权威。
- 工具包仓库 CI 运行在 GitHub Actions（`bash scripts/ci-check.sh`）；项目仓库收到一个 vendored CI 工作流，以项目模式调用同一入口。

## 5. 备选方案比较

- **A. 逻辑分离（单仓库内所有权清单）。** 成本最低，但工具包与项目仍在同一历史里，「工具包随时更新」与「项目随时提交」持续互相竞争；否决。
- **B. 单仓库物理分离（`process/` 迁移、托管块、原地升级工具）。** 消除了目录混用，但仍偏向以合并方式升级；用户 2026-11-18 选择 C，否决。
- **C. 双仓库 + vendored 工具包快照（已选）。** 工具包仓库用普通 git 操作升级、对项目零影响；每个项目仓库在固定路径接收加锁快照，以显式脚本提交升级。分发机制备选：submodule（可固定版本，但无法服务 `.claude/skills` 发现，Windows/CI 摩擦大）、subtree（把工具包历史写进项目，否决）、vendored 快照 + 锁（已选：可移植、可评审、CI 可校验）。

## 6. 确定的设计

### 6.1 两个仓库的职责

| | 工具包仓库 | 业务项目仓库 |
|---|---|---|
| 承载 | Skills、Prompts、模板、脚本、流程规范、工具文档、发布标签 | 基线、OpenSpec Changes/specs、证据、工作流状态、业务代码、项目设置 |
| 更新方式 | 维护者随时提交/合并；按 `toolkit-vX.Y.Z` 打标签并写变更日志 | 团队持续提交；工具包刷新只通过专门的升级 PR |
| CI | 工具包布局、清单新鲜度、包检查、脚本测试 | 工具包完整性（`toolkit-sync verify`）、布局、包检查、项目检查 |
| 含工具包 git 历史 | 是（它就是来源） | 否 |

### 6.2 工具包仓库布局（本仓库迁移后）

```
.claude/skills/<11 个阶段 Skill>/      阶段 Skill（openspec-* 移除：第三方、属项目侧）
.claude/hooks/stage-boundary-guard.py
.claude/settings.json                  钩子注册
prompts/                               12 个阶段提示词
templates/                             全部可复用模板（P2 补全）
scripts/                               检查器、workflow.py、toolkit-sync.py、gen-manifest.py
process/                               流程文档
│   ├─ PROCESS-MAP.md、STEP-ARTIFACT-CONTRACTS.{md,json}、WORKFLOW-STAGES.json、
│   │   TEMPLATE-POLICY.md、OUTPUT-TEMPLATE-MATRIX.csv、INPUT-OUTPUT-POLICY.md、
│   │   BASELINE-FEATURE-INTERACTION.md、P0-RUNTIME-GOVERNANCE.md、
│   │   QUESTION-COVERAGE-CHECKLIST.md、SUPERPOWERS-MAPPING.md、
│   │   STAGE-IO-OVERVIEW.md（生成物）、TOOLKIT-CHANGELOG.md（发布说明）、
│   │   TOOLKIT-MANIFEST.json（vendored 集合的生成登记表）
│   ├─ examples/                        （从 docs/examples 迁入）
│   └─ proposals/                       工具包设计文档（含本文件）
.github/workflows/ci.yml               工具包 CI
README.md、README-zh.md、LICENSE、.gitattributes、VERSION
AGENTS.md / AGENTS-zh.md               工具包开发约定（简短；不是项目流程规则）
```

本仓库执行的清理：`openspec/`、`workflow/`、`workflow-state.json`、空的 `docs/`、`_trash/` 退出被跟踪的目录树（状态属于项目；`_trash/` 保持 gitignore，可本地删除）。

工具包仓库**不含**项目产物、工作流状态与 OpenSpec CLI 产物。其 AGENTS.md 描述工具包自身如何开发（布局、检查、发布步骤）；项目流程规则以 `templates/workflow/agents-managed.md` 分发，并组合进项目的 AGENTS.md。

### 6.3 项目仓库布局与所有权类别

```
Vendored 工具包（加锁；只能由 toolkit-sync 替换）
├─ .claude/skills/<11 个阶段 Skill>/     （openspec-* Skills 与 opsx 命令为第三方生成）
├─ .claude/hooks/stage-boundary-guard.py
├─ .claude/settings.json                 （仅钩子；项目权限放在 settings.local.json）
├─ prompts/、templates/、scripts/、process/
├─ .github/workflows/toolkit-ci.yml      vendored 工具包 CI 入口

由工具包模板组合（托管块，初始化与升级时生成）
├─ AGENTS.md / AGENTS-zh.md              工具包块 + 项目所有段
├─ openspec/config.yaml                  工具包键块 + 项目 context
└─ .gitignore                            工具包块 + 项目行

项目所有（升级绝不触碰）
├─ docs/product|architecture|adr|project/
├─ openspec/changes/、openspec/specs/
├─ workflow/evidence/、workflow/handoffs/、workflow/state-events.jsonl
├─ workflow-state.json
├─ design/、src/、tests/（业务代码）
├─ toolkit-lock.json                    锁记录（见 6.6）
├─ project-extensions.json              项目自建路径声明
├─ README、LICENSE、.gitattributes、package.json / pyproject.toml / Dockerfile 等、项目 CI 工作流
└─ .claude/settings.local.json          按机器，gitignore
```

OpenSpec CLI 生成文件（`.claude/skills/openspec-*`、`.claude/commands/opsx/*`）属于第三方：toolkit-sync 永不写入或删除它们；项目在锁中记录其存在与 CLI 版本。

### 6.4 Vendored 集合与排除项

Vendored 集合由工具包仓库的 `process/TOOLKIT-MANIFEST.json` 定义：每个工具包托管路径及其 SHA-256 与类别（`toolkit`、`mixed-template`、`generated`）。明确**不** vendored：

- 工具包的 `README.md`、`README-zh.md`、`LICENSE`、`.gitattributes`（项目拥有自己的版本）；
- `.github/workflows/ci.yml`（项目收到的是 `toolkit-ci.yml`）；
- `process/proposals/` 与 `process/examples/`（设计历史与示例留在工具包侧）；
- `VERSION`（版本记录在项目锁里）；
- `.claude/skills/openspec-*` 与 `.claude/commands/` 下的一切（第三方）。

`process/TOOLKIT-CHANGELOG.md` **会**被 vendored，让项目成员能读到从自己的锁版本到最新标签之间的变更。

### 6.5 模板补全与矩阵强制（沿用 v1）

补齐 14 个缺失的产物模板（当前以 `docs/...` 路径登记），并修正 1 条流程文档登记行：

- `templates/product/`：`business-rules.md`、`open-questions.md`、`glossary.md`、`acceptance-policy.md`、`proposal-roadmap.md`。
- `templates/project-baseline/`（或新建 `templates/architecture/`）：`system-context.md`、`technology-decisions.md`、`adr-README.md`、`containers-and-deployment.md`、`data-flows.md`、`logical-erd.md`、`domain-boundaries.md`、`api-conventions.md`、`frontend-conventions.md`、`test-strategy.md`。
- `Input/output context policy` 行引用 `process/INPUT-OUTPUT-POLICY.md`，作为流程参考。

`scripts/check-output-template-matrix.py` 要求产物行的模板路径以 `templates/` 开头；删除现有对 `docs/product|architecture|adr` 路径的放行。流程/工具类行可引用 `process/` 或 `scripts/`；OpenSpec 内置 schema 行保持允许。

### 6.6 版本、清单与锁

**工具包仓库**
- `VERSION` 保存语义化版本；发布打标签 `toolkit-vX.Y.Z`，并在 `process/TOOLKIT-CHANGELOG.md` 中记录（含必要的状态迁移）。
- `scripts/gen-manifest.py --write` 根据当前目录树重新生成 `process/TOOLKIT-MANIFEST.json`；过期时 `--check` 失败。CI 在每次提交上运行 `--check`，因此每次工具包变更都须重新生成清单。

**项目仓库 — `toolkit-lock.json`**（纳入版本管理、项目所有、只由 `toolkit-sync` 写入）：

```
version、source（git URL 或 "local:<path>"）、ref、commit、installed_at、
manifest_sha256、files: {path: sha256},            # 每个 vendored 文件
third_party: {openspec_cli, generated_paths},      # openspec-* Skills、opsx 命令
forks: [有意保留本地的路径]、upgrades: [升级历史]
```

`toolkit-sync verify` 逐文件比对 vendored 文件哈希与锁、检查组合块标记完整、vendored 文件集合与清单一致。工具包仓库自身没有锁；`verify` 以「源模式」运行，改为校验清单。

### 6.7 `toolkit-sync.py`（随工具包分发，在项目仓库运行）

- `init --from <git-url|本地路径> --ref <tag>`：首次安装：写入 vendored 文件，组合 `AGENTS.md` 块、`openspec/config.yaml` 与 `.gitignore`，仅当不存在时脚手架默认 `workflow-state.json`，写入 `toolkit-lock.json`。项目已有锁时拒绝执行（改用 `apply`）。
- `verify [--require-lock]`：vendored 哈希、清单一致性、托管块配对、第三方存在性/版本、锁与版本一致。
- `plan --ref <tag|commit>`：只读：vendored 文件的新增/修改/删除、块变化、本地修改冲突、变更日志声明的状态迁移；同时报告锁定 ref 与目标之间提交的变更。
- `apply --ref <tag|commit>`：前置条件：工作区干净、无 `pending_approvals`、无 `blocked_items`、无其他升级锁。步骤：获取 `toolkit-upgrade.lock`（O_EXCL）→ 备份 `workflow-state.json` 到 `workflow/state-backups/`（gitignore）→ 解析来源（`git fetch --tags <source>`；维护者可用 `--from` 指向本地检出）并校验源清单 → 只替换清单列出的路径 → 删除新清单不再列出且旧锁记录过的路径 → 重新组合托管块 → 重新生成 `process/STAGE-IO-OVERVIEW.md`，存在基线时还包括 `docs/product/BASELINE-INDEX.md` → 执行变更日志声明的迁移命令（如 `workflow.py migrate-state`）→ 运行 `toolkit-sync verify` 与 `bash scripts/ci-check.sh` → 写入新锁 → 在控制台输出 `TOOLKIT-CHANGELOG` 摘要 → 释放锁。
- `repair`：重新组合块、重新生成生成物、从最新备份恢复状态、重新盖章锁文件；幂等。
- 冲突策略：本地修改过的 vendored 文件会中止升级并列出；`--take-upstream` 覆盖；`--keep-local` 在锁中登记分叉（可评审，且应尽快回流工具包）。
- 回滚：升级是一个独立提交；`git revert` 该提交并恢复状态备份即可。

### 6.8 状态、备份与生成物（项目侧）

- `workflow-state.json` 只由 `scripts/workflow.py` 写入（规则不变）；升级流程除声明迁移外绝不改写它。
- 新子命令 `workflow.py recover-state --backup <file>`：恢复备份、补齐默认字段、对照阶段登记表校验，并向 `workflow/state-events.jsonl` 追加恢复事件。
- `workflow/state-backups/` 已 gitignore，按机器本地保存。
- 项目中的工具包生成物：`process/STAGE-IO-OVERVIEW.md`（升级时重新生成），以及 `docs/product/BASELINE-INDEX.md`（经 `workflow.py sync-baseline-index`）。

### 6.9 严格缺失文件策略

`scripts/check-layout.py` 在两个仓库运行：

- 工具包模式：工具包路径存在且与清单一致；不得出现项目产物、状态或 OpenSpec 产物；根目录白名单（工具包文件、`VERSION`、`process/`、`.github/workflows/ci.yml`）。
- 项目模式：`docs/` 只允许 `product|architecture|adr|project`（以及 `project-extensions.json` 中声明的项目自建文档）；`openspec/` 只允许 `config.yaml`、`changes/`、`specs/`；vendored 路径与锁一致；根条目要么匹配内置项目根模式（`package.json`、`pyproject.toml`、`requirements.txt`、`Dockerfile`、compose 文件、`.env.example`、`Makefile`、`.github/workflows/project-ci.yml` 等），要么在 `project-extensions.json` 中声明；托管块标记配对；第三方文件在锁中记录 CLI 版本。

升级工具只替换清单列出的路径，因此其他位置的项目自建文件（例如 `.claude/skills/` 下的额外 Skill）会保留；它们必须在 `project-extensions.json` 中声明才能通过布局检查。

### 6.10 双仓库下的多人协作

1. **工具包仓库**：维护者在分支上工作、向 `main` 提 PR；CI 强制清单新鲜度、包检查、脚本测试与工具包布局。发布打标签并写变更日志。工具包变更永远不需要触碰任何项目仓库。
2. **项目仓库**：团队照常以分支/PR 提交业务工作。工具包文件对成员只读，由 CI 中的 `toolkit-sync verify` 强制（哈希不符即失败并给出指引）。
3. **升级是专门的 PR**：指定的维护者运行 `plan`/`apply`，分支 `toolkit/upgrade-vX.Y.Z`，只提交 vendored 文件、组合块与锁，并发起 PR。CI 运行 `verify` 加项目检查；合并后所有成员拉取。其他人不得执行 `apply`。
4. **同一时间只允许一次升级**：`toolkit-upgrade.lock` 与干净工作区前置条件串行化同一克隆内的升级；PR + CI 阻止分歧的升级未经验证就合并。
5. **每个阶段只有一名驱动者**：`atomic_json` 的锁串行化同机写入；跨机器时同一时间只有一名成员推进某阶段；`workflow-state.json` 并发修改通过从一侧重跑工作流命令解决（绝不手工合并 JSON）；`workflow/state-events.jsonl` 与证据保持审计轨迹。状态备份仅本地保存。
6. **按机器设置保持本地**：项目仓库的 `.claude/settings.local.json` 继续 gitignore。
7. **行尾固定**：各仓库的 `.gitattributes` 各自权威；工具包文件使用 LF。
8. **分叉必须显式**：项目若必须修改 vendored 文件，通过 `toolkit-sync --keep-local` 登记，并把等价改动提交到工具包上游；下次升级即丢弃分叉。

### 6.11 组合文件（托管块）

- `AGENTS.md` / `AGENTS-zh.md`：恰好一个位于 `<!-- toolkit:begin -->` 与 `<!-- toolkit:end -->` 之间的块，从 `templates/workflow/agents-managed.md`（及 `agents-managed-zh.md`）安装。托管块包含 Process Entry、Stage Boundaries and Review Stop-and-Wait、Template and Artifact Rules（含 UI/Figma 规则）、OpenSpec Conventions、Check Scripts、Language and Style、Agent Behavior Boundaries。项目所有内容是状态头、Project Goal，以及后续建立的项目约定（阶段 03 的技术/标识符约定）。阶段 01 的 Prompt/Skill 更新为只写项目所有段。
- `openspec/config.yaml`：标记分隔的工具包键（`schema`、`rules`、`operations`），从 `templates/project-setup/openspec-config.yaml` 组合；项目 `context` 键由组合器保留。
- `.gitignore`：一个从 `templates/project-setup/gitignore-block.txt` 组合的工具包块；项目行写在其后。
- `.claude/settings.json` 原样 vendored（仅钩子）；项目权限放在 `.claude/settings.local.json`。

## 7. 实施阶段与验证

每个阶段结束时，工具包源模式下检查全绿：`python scripts/check-package.py`、`bash scripts/test-scripts.sh`、`bash scripts/ci-check.sh`、`python scripts/check-layout.py --mode toolkit`、`python scripts/gen-manifest.py --check`。

1. **P1 — 工具包清理与流程迁移。** 工具包仓库中移除 `openspec/`、`workflow/`、`workflow-state.json`、`docs/`、`_trash/`（历史保留）；21 个流程文件与 `docs/examples/` 迁入 `process/`；执行脚本化引用改写（313 处）；更新生成器、钩子、检查器与文档。除路径外不改变行为。
2. **P2 — 模板。** 补齐 14 个缺失产物模板与 ADR README；更新矩阵；收紧矩阵校验器。
3. **P3 — 项目初始化模板。** 新增 `templates/workflow/agents-managed{,-zh}.md`、`templates/project-setup/openspec-config.yaml`、`templates/project-setup/gitignore-block.txt`、`templates/workflow/workflow-state.default.json`；把工具包自身 AGENTS.md 改写为工具包开发约定；更新阶段 01 的 Prompt/Skill 以适配组合式 AGENTS.md。
4. **P4 — 同步工具与发布。** 实现 `toolkit-sync.py`（`init/verify/plan/apply/repair`）、`check-layout.py`（双模式）、`gen-manifest.py`、`workflow.py recover-state`；加入 `VERSION`、`process/TOOLKIT-MANIFEST.json`、`process/TOOLKIT-CHANGELOG.md`、vendored `toolkit-ci.yml` 模板、发布标签与来源解析（`git fetch --tags`、`--from`）。
5. **P5 — 演练与接入。** 在临时克隆中创建模拟项目仓库：`init` → 脚手架阶段 01 产物 → 跨两个标签升级 → 注入本人为修改的 vendored 文件（冲突）与状态备份恢复 → 回滚。保留过程记录作为证据。编写 `process/TOOLKIT-UPGRADE.md`（升级与接入指南，含把工具包仓库添加为 `toolkit` 远端，以及如何初始化新的项目仓库）。
6. **P6 — 文档收尾。** 更新 README/AGENTS/process 结构表；修正已知路径漂移（README/AGENTS 写根级 `design/`、契约写 `openspec/changes/<change-id>/design/`，以契约为准）。

第一个真实业务项目仓库在用户重新启动项目时创建；上一次尝试的历史仍保存在被 gitignore 的 `_trash/` 快照中，可有选择地复制进来，或项目从阶段 01 重新开始。

## 8. 风险与缓解

- **引用迁移破坏检查。** 单一脚本化映射表、每阶段全量测试、P1 不改变行为。
- **项目历史中出现 vendored 副本。** 可接受：约 130 个文件的一份副本加刻意的升级提交；替代方案（submodule/subtree）在 Windows 与 Skill 发现上更糟。
- **成员修改 vendored 文件。** CI 中的 `verify` 失败并给出指引；`--keep-local` + 回流的流程有文档。
- **托管块解析错误。** 标记不配对时 `verify` 失败；`repair` 总能重装块。
- **升级期间状态丢失或 schema 漂移。** 升级前备份、`recover-state`、变更日志声明的迁移、以及单提交回退路径。
- **OpenSpec CLI 升级重新生成第三方文件。** 它们不在 vendored 集合内；锁记录 CLI 版本；阶段 01 刷新记录。
- **Windows/macOS 差异。** `.gitattributes`、工具包文件 LF、以及既有的 `O_EXCL` 锁模式。

## 9. 留给实施者

- 托管块的确切标记语法与组合器。
- `TOOLKIT-MANIFEST.json` 与 `toolkit-lock.json` 的 schema。
- `apply` 内部的暂存/回滚细节（拷贝顺序、临时目录、失败处理），以及来源不可达时 `repair` 如何恢复 vendored 文件。
- `process/STAGE-IO-OVERVIEW-zh.md` 是否增加生成支持，或保持人工镜像 + 检查。
- 演练夹具（模拟项目内容、冲突注入、断言）。
- 内置项目根模式清单与 `project-extensions.json` 的 schema。
- `toolkit-ci.yml` 的确切内容与调用 `ci-check.sh` 的方式。

## 10. 批准清单

- 双仓库：工具包仓库（本仓库）随时更新且不含项目产物；每个业务项目一个项目仓库，承载全部产物与业务代码。
- 分发方式为 vendored 快照 + `toolkit-lock.json` + `toolkit-sync`（不用 submodule/subtree/符号链接）；升级经 PR 到明确标签。
- 工具包仓库清理（`openspec/`、`workflow/`、`workflow-state.json`、`docs/`、`_trash/` 退出跟踪；流程文档迁入 `process/`）。
- 模板补全范围（14 个产物模板 + ADR README；1 条流程策略矩阵行改指向）。
- 组合文件：AGENTS 托管块划分（工具包规则 vs 项目状态头/Project Goal/项目约定）、`openspec/config.yaml` 工具包键、`.gitignore` 块、项目权限用 `settings.local.json`。
- `toolkit-sync` 命令集与前置条件（审批挂起时拒绝、工作区干净、同一时间一次升级）。
- 多人规则：工具包仓库走工具包 PR；项目仓库走升级 PR；每个阶段单一驱动者；vendored 路径只读；分叉必须登记并回流。
- P1–P6 分阶段实施，每阶段检查全绿。
</content>
