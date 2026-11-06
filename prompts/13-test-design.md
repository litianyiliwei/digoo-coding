# Prompt：测试设计

```text
执行 `@test-design`，Change：<change-id>。

AC：<acceptance-criteria>
提案级 US/UC/AC：<stories-and-use-cases>
设计计划：<design-md-and-plan>
API 追踪：<api-traceability>
验收政策：<acceptance-policy>
OpenAPI/前后端设计：<design-paths>
风险：<risk-list>

输出测试矩阵，字段包含 REQ/AC、PAGE/BLOCK、用例 ID、层级、前置条件、数据、步骤、预期、自动化方式和清理方式。先读取提案级 US/UC/AC、design.md、design-plan.md、api-traceability.csv 与项目验收政策，再把 api-traceability 行与测试映射合并进唯一的 `traceability.csv`。覆盖正常、边界、错误、权限、幂等、并发/一致性/超时（适用时）。每条 AC 至少映射一个测试，否则 `N/A + 原因`。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：必须读取 `docs/architecture/test-strategy.md` 并沿用项目测试分层和质量门禁；功能测试用例留在 Change。若需修改全局门禁，先提出基线修订，不得以单功能静默豁免。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@test-design`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按设计复杂度使用 Superpowers `brainstorming` 审视方案；不要将它当成接口/设计模板的替代品。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 先检查 Change 状态：`openspec status --change <id>`；读取已批准 specs/design。若发现需求变化，暂停并回到 OpenSpec 更新规格，不能只改辅助设计文档。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="test-design"` 的记录。

- 输入核验：已批准提案级 US/UC/AC；design.md、design-plan.md、api-traceability.csv；OpenAPI；前后端详细设计；API→IO 映射与 IO 契约；项目级测试策略与 acceptance-policy。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design/test-design.md；openspec/changes/<change-id>/traceability.csv（合并 api-traceability 与测试映射）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：TEST ID、覆盖的 AC/API/IO、测试数据/环境/命令、预期结果。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 基线交互：必须按 `docs/BASELINE-FEATURE-INTERACTION.md` 核验基线读取/变更归属；阶段 05 创建/更新 `design/baseline-impact.md`，后续阶段复核；未经批准不得修改冻结基线。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。


## 机器基线设计门禁（必须执行）

将测试分层、覆盖要求、质量门禁、可观测性等适用约束映射到 test-design/traceability/test matrix，执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。
