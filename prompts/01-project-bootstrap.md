# Prompt：项目初始化与工具链检查

```text
执行 `@project-bootstrap`。

仓库路径：<repo-path>
项目摘要：<project-summary>
当前 Agent/IDE：<agent-and-ide>

先检查现有 README、目录、构建/CI 文件、Git 状态、OpenSpec CLI 和 Superpowers 实际安装状态。提出最小初始化方案，不覆盖既有配置，不安装/删除/提交任何内容。输出工具状态、已发现约定、缺口、拟创建/修改清单和未执行检查。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@project-bootstrap`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 先检查 Superpowers 是否安装及可用技能目录；若存在 `using-superpowers`，按宿主机制读取。不要在初始化时自动安装或更新工具。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 若存在 `openspec/`，运行 `openspec list --changes`、`openspec list --specs` 与 `openspec version`（若当前 CLI 支持）；未初始化时只报告，不要擅自执行 init。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="project-bootstrap"` 的记录。

- 输入核验：用户提供的项目目标与仓库位置；仓库现有目录/配置/AGENTS.md（若存在）。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：AGENTS.md（仅缺失时创建或经批准修改）；workflow-state.json；docs/architecture/baseline-status.md；工具链检查报告（docs/project/toolchain-report.md）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：仓库约定与工具链报告；workflow-state.json。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。
