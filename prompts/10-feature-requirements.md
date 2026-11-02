# Prompt：功能级 OpenSpec Change 与需求细化

```text
执行 `@feature-requirements`，Change：<change-id>。

业务目标：<goal>
关联 US/AC/BR：<ids>
pen.dev：<prototype-link-or-export>

先查 `openspec status --change <change-id>`、`openspec list --specs` 并读取相关规格全文。按当前 OpenSpec schema 完成 proposal、spec delta、design、tasks。spec 仅写外部可观察行为；每个 Requirement 含至少一个 Scenario；tasks 使用 `- [ ]` 复选框。列出原型改动、基线影响和审批问题。完成后运行 `openspec validate <change-id> --strict`，不得开始编码直到评审批准。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@feature-requirements`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 使用 Superpowers `brainstorming` 检查方案与需求边界；不在本阶段编码。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 必须使用 OpenSpec CLI：`openspec status --change <id>`、`openspec list --specs`、按需 `openspec instructions <artifact> --change <id> --json`，完成后 `openspec validate <id> --strict`。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="feature-requirements"` 的记录。

- 输入核验：已批准路线图/当前 Change 范围；项目级产品/架构/数据/公共契约基线；关联 US/AC/BR/FLOW/UC；现有 OpenSpec specs。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/proposal.md；openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）；openspec/changes/<change-id>/tasks.md（初步任务）；openspec/changes/<change-id>/design.md（有设计决策时）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：已批准 Change proposal/specs、范围边界、验收标准、需求追踪 ID。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。
