# Prompt：功能详细设计总控

```text
执行 `@feature-design`，Change：<change-id>。

规格：<spec-paths>
页面/事件清单：<inventory-paths>
Figma 审计：<figma-audit>
项目基线：<baseline-paths>

先生成 `openspec/changes/<change-id>/design/design-plan.md`（设计范围、任务分解、接口范围草案、设计缺口/决策、准入结论），再生成详细设计目录和依赖顺序：API 契约 → 前端设计 → 后端设计 → 测试设计。确保设计项均关联 REQ/AC/PAGE/EVT 或写明 N/A 原因。后端设计必须将每个 OpenAPI operationId 映射到一个或多个具体 IO ID，并登记在 `design/api-io-mapping.csv`；所有 IO ID 必须在 `design/io-catalog.csv` 有输入/输出、数据库/Client 操作、事务/一致性、超时、重试、错误处理及测试 ID。运行 `scripts/check-design-assets.sh <change-id> --strict --lint-api` 验证后再进入实现。识别跨基线影响，不要让前后端各自发明字段。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：重新核验 `design/baseline-impact.md` 与当前 `baseline-status.md`。任何基线版本变化都要写明 `NO_IMPACT` 或 `REBASE_REQUIRED`；违反基线的方案必须先走 ADR/基线修订审批，批准后才能冻结详细设计。完成复核后运行 `python3 scripts/check-baseline-impact.py <change-id> --strict`。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@feature-design`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按设计复杂度使用 Superpowers `brainstorming` 审视方案；不要将它当成接口/设计模板的替代品。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 先检查 Change 状态：`openspec status --change <id>`；读取已批准 specs/design。若发现需求变化，暂停并回到 OpenSpec 更新规格，不能只改辅助设计文档。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="feature-design"` 的记录。

- 输入核验：已批准 proposal/specs；页面/交互清单与 Figma 审计（适用时）；项目级架构/数据/公共契约基线。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design.md；openspec/changes/<change-id>/design/design-plan.md（任务分解/缺口/准入结论）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：统一设计约束、接口范围、前后端/测试设计任务与缺口。在报告中明确 10–13 如何读取 design.md 与 design-plan.md。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 基线交互：必须按 `docs/BASELINE-FEATURE-INTERACTION.md` 核验基线读取/变更归属；阶段 05 创建/更新 `design/baseline-impact.md`，后续阶段复核；未经批准不得修改冻结基线。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。


## 机器基线设计门禁（必须执行）

详细设计必须逐条处理 `design/baseline-binding.json`：适用约束须为 COMPLIANT 或 EXCEPTION_APPROVED，并关联真实设计证据；N/A 必须有理由；例外必须有批准人/日期/证据。阶段 09 转出时执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。
