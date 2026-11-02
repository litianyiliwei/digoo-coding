# Prompt：需求发现与整理

```text
先按当前 Agent 的实际机制检查并加载 Superpowers 的 `using-superpowers`（若已安装），再加载本项目 Skill `requirements-analysis`。本阶段必须使用 Superpowers `brainstorming`（若可用）进行需求发现：先逐步澄清目标、用户、问题、范围、约束与成功标准；信息不足时先提问，不要一轮直接臆造完整需求。

需求材料：<paste-or-file-paths>
业务/行业背景：<context>
关键干系人：<stakeholders>

如果 OpenSpec 已初始化，先运行 `openspec list --specs` 并阅读与需求相关的现有规格（必要时用 `openspec show <spec-name> --type spec`）；此阶段只读取既有规格，不创建功能 Change。等需求确认并进入阶段 9/10 后，再由 OpenSpec 管理 proposal/specs/design/tasks。

在 brainstorming 澄清结束并得到足够输入后，生成业务流程、功能用例、用户故事、业务规则、非功能要求、Given/When/Then 验收标准和需求追踪矩阵。所有内容标注“已确认/待确认/假设/冲突”，每个 ID 稳定唯一。不要臆测未知业务规则，不提前决定数据库表和类。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@requirements-analysis`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 需求发现必须优先使用 Superpowers `brainstorming`；先澄清、后产出。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 只读取既有规格：`openspec list --specs`，必要时 `openspec show <spec-name> --type spec`；不要在需求发现阶段创建 Change。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="requirements-analysis"` 的记录。

- 输入核验：访谈/业务材料/旧系统资料；项目目标、用户、角色、约束；既有 docs/product/*（若存在）；既有 OpenSpec specs（只读）。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：docs/product/requirements-analysis.md；docs/product/workflows.md；docs/product/use-cases.md；docs/product/user-stories.md；docs/product/business-rules.md；docs/product/open-questions.md。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：需求分析报告、流程、用例、故事、规则、未决问题。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。
