# Prompt：实现、TDD、验证与代码审查

```text
执行 `@implementation-orchestrator`，Change：<change-id>。

先读取 `openspec instructions apply --change <change-id>`、设计文档与 tasks。检查 Superpowers 当前可用技能。按复杂度使用 `brainstorming`、`using-git-worktrees`、`writing-plans`、`subagent-driven-development`/`executing-plans`；实施遵循 `test-driven-development`，调试使用 `systematic-debugging`，审查使用 `requesting-code-review` / `receiving-code-review`，完成前使用 `verification-before-completion`。

一次完成一个可验证小任务：先写测试并观察预期失败，再实现最小代码、复测、重构、更新 tasks。不得擅改规格/OpenAPI；规格冲突先暂停并更新 Change。最终报告真实执行命令、退出码、测试/构建结果和未执行项，未执行不能写通过。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：实施前复核 `design/baseline-impact.md` 和当前基线版本。若实现中发现冲突/缺口，暂停受影响任务、提交基线修订请求/ADR；不得直接编辑冻结基线。基线获批更新后，刷新 Change 的基线快照、设计和测试；实施前运行 `python3 scripts/check-baseline-impact.py <change-id> --strict`。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@implementation-orchestrator`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 必须检查并按宿主机制加载可用的 `using-superpowers`、`writing-plans`、`test-driven-development`、必要时 `systematic-debugging`、`requesting-code-review`/`receiving-code-review`、`verification-before-completion`。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 先运行 `openspec instructions apply --change <id> --json` 和 `openspec status --change <id>`；按批准 tasks 实施，完成后 `openspec validate <id> --strict`。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="implementation-orchestrator"` 的记录。

- 输入核验：已批准 tasks.md/design.md；设计五节、OpenAPI、IO 契约；design.md（含测试设计节）、design/test-cases.csv 与 traceability.csv；项目级工程规范/测试策略；涉及 UI 时 Figma 设计（`design/figma-audit.md`、`design/design-spec.json`，按 Figma 实际设计实现）。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：实际源代码/迁移/配置；自动化测试代码与运行结果；openspec/changes/<change-id>/design/evidence/code-review.md；实现/验证证据。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：代码差异、测试报告、审查结论、未解决问题。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。


## 独立验证交接（新增强制要求）

Builder 完成后不直接进入人工验收。必须交接给独立 Skill `@independent-verifier`（阶段 `09-independent-verification`），使用独立 Agent/上下文只读验证代码、规格、AC、IO 契约并重新执行测试。Builder 不得自行生成 PASS 结论替代 Verifier。


## 机器基线实现门禁（必须执行）

编码前先通过 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。实现后为每条适用约束补充 PASS、验证方法和真实证据文件；阶段 08 转出前执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase implementation`。
