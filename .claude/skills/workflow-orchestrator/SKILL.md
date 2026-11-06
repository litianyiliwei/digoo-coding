---
name: workflow-orchestrator
description: 当用户说“下一步/继续/接着做”时，根据仓库中的 workflow-state.json、真实产物、审批状态和 OpenSpec 状态决定唯一安全的下一阶段。
---

# 工作流推进器

## 触发条件
用户说“下一步”“继续”“接着做”“继续研发流程”或要求恢复上次流程时使用。

## 必须遵守
1. 先读取 `workflow-state.json`、`docs/PROCESS-MAP.md`、`docs/OUTPUT-TEMPLATE-MATRIX.csv`，再检查当前阶段对应的真实文件。状态文件只是线索，不可代替文件校验。
2. 检查当前 Agent 能发现哪些 Skill。若存在 Superpowers 的 `using-superpowers`，先按宿主 Agent 支持的方式加载它；然后按任务加载相关 Superpowers Skill。不要臆造调用语法或声称执行了未安装的 Skill。
3. 如果 OpenSpec 已初始化，执行 `openspec list --changes`、`openspec list --specs`；对活动 Change 执行 `openspec status --change <id>`。在创建或编辑 OpenSpec artifact 前，按 CLI 实际版本使用 `openspec instructions <artifact> --change <id> --json` 获取指引。
4. 若存在待审批项、阻断项、上一步必需产物缺失、校验失败或关键问题待用户确认，停止自动推进，明确提出需要用户决策的事项。
5. 只推进一个阶段；不得一次性执行多个阶段，不得跳过审批门禁。
6. 按下一阶段 Prompt 和 Skill 执行。Prompt 路径在 `prompts/`，Skill 路径在 `.claude/skills/<skill-id>/SKILL.md`。
7. 调用工具必须真实执行：OpenSpec CLI 用终端命令；Superpowers 按当前 Agent 的技能加载机制读取/调用技能；Figma/pen.dev 只能使用实际可用的 MCP 或已提供导出物。
8. 完成后运行该阶段的检查脚本。只有产物实际存在、质量门禁通过且无需审批时，才把阶段加入 `completed_steps` 并更新 `current_step`。不得伪造测试结果。
9. 如果当前阶段需要客户/产品/架构/设计人工批准，记录到 `pending_approvals`，等待用户明确批准后再继续。
10. 输出：当前状态、检查证据、执行的工具/技能、下一步、阻断项。若只是分析尚未写入文件，不要标记完成。

## OpenSpec 与 Superpowers 分工
- OpenSpec：管理功能 Change 的 proposal/specs/design/tasks、状态、结构校验和归档。
- Superpowers：约束发现/设计/计划/TDD/调试/审查/完成前验证的方法。
- 本工具包的业务阶段 Skill：定义本项目每阶段的输入、输出、模板与门禁。
三者互补，不能用提及名字代替实际加载或命令执行。

## 基线交互提示（强制）

- 选择功能级阶段时，除检查普通输入外，必须读取 `docs/BASELINE-FEATURE-INTERACTION.md` 和当前 `docs/architecture/baseline-status.md`。阶段 10 创建 baseline-impact；阶段 13 复核；阶段 14 不直接修改冻结基线；阶段 15 按审批结果回写。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="workflow-orchestrator"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** workflow-state.json；docs/PROCESS-MAP.md；docs/STEP-ARTIFACT-CONTRACTS.json；docs/OUTPUT-TEMPLATE-MATRIX.csv；真实产物与审批记录；OpenSpec CLI 当前状态（如已初始化）。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** 下一阶段判定报告（对话展示；必要时写入 docs/workflow/next-step-report.md）；workflow-state.json（仅在真实状态变化时更新）。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 所选阶段的 Input Contract 中全部文件。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。


## P0 Runtime Guard (强制)

- 阶段 DAG 读取 `docs/WORKFLOW-STAGES.json`，不得自行推断/改写依赖。
- 执行前运行 `python3 scripts/workflow.py check-entry --step <step-id> [--change-id <id>]`；非 0 退出码表示禁止执行。
- 阶段完成后生成符合 `workflow/evidence/<step-id>.json` 结构的证据，调用 `python3 scripts/workflow.py transition --step <step-id> --evidence <path>`。禁止直接编辑 `completed_steps/current_step`。
- transition 会生成 SHA-256 handoff；下一阶段必须核验全部上游 manifest。文件哈希变化时退回上游重审，不得静默刷新。
- 阶段 14 后必须运行独立 `independent-verifier`，只有 PASS 才进入阶段 15。详情见 `docs/P0-RUNTIME-GOVERNANCE.md`。
