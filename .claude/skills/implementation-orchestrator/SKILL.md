---
name: implementation-orchestrator
description: 实现、TDD、验证与代码审查。使用已安装的 Superpowers 工作流实施小任务并以真实测试结果验收。
---

# 实现、TDD、验证与代码审查

## 何时使用
当流程进入“实现、TDD、验证与代码审查”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
审批通过的 OpenSpec artifacts、详细设计、tasks、仓库规范、可用 Superpowers。

## 执行流程
1. 先读取 `openspec instructions apply --change <id>` 和项目开发说明；核对 Superpowers 实际安装的技能。
2. 根据复杂度按需执行 Superpowers 的 `brainstorming`、`using-git-worktrees`、`writing-plans`、`subagent-driven-development` 或 `executing-plans`。
3. 对行为变化使用 `test-driven-development` 的 RED-GREEN-REFACTOR：先写失败测试并观察失败，再做最小实现。
4. 按小任务实现并更新 OpenSpec tasks 复选框；每个任务运行相关测试。
5. 失败时使用 `systematic-debugging`，优先定位根因，不进行无证据的随机修改。
6. 阶段性使用 `requesting-code-review`；收到评论后按 `receiving-code-review` 核实并处理。
7. 结束前使用 `verification-before-completion`，运行真实测试/构建/契约检查，并报告命令、退出码和未执行项。
8. 不要声称使用了未安装的 Superpowers 技能；不要擅改 specs/OpenAPI。如规格确需变化，暂停并更新 Change。

## 输出
代码变更、测试、更新后的 tasks、代码审查报告和验证证据。

## 质量与安全边界
不以代码生成代替测试；不把未运行的检查报告为通过；禁止未审批的契约/需求变更。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/test-all.sh <project-dir>; scripts/verify-before-completion.sh`


## 实际工具调用要求

- **Superpowers：** 检查并按宿主机制加载 `using-superpowers`、`writing-plans`、`test-driven-development`；故障时 `systematic-debugging`；审查用 `requesting-code-review`/`receiving-code-review`；完成前 `verification-before-completion`。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 先执行 `openspec instructions apply --change <id> --json` 和 `openspec status --change <id>`；完成后 `openspec validate <id> --strict`，不擅改规格。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="implementation-orchestrator"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准 tasks.md/design.md；前后端详细设计、OpenAPI、IO 契约；test-design.md 与 traceability.csv；项目级工程规范/测试策略。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** 实际源代码/迁移/配置；自动化测试代码与运行结果；openspec/changes/<change-id>/design/evidence/code-review.md；实现/验证证据。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 代码差异、测试报告、审查结论、未解决问题。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
