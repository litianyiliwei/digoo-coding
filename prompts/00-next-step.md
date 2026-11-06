# Prompt：继续研发流程 / 下一步

```text
执行 `@workflow-orchestrator`。我的指令是“下一步”。

先读取 `workflow-state.json`、`docs/PROCESS-MAP.md`、`docs/OUTPUT-TEMPLATE-MATRIX.csv`，核验当前阶段产物与审批状态，不要只相信状态文件。

技能调用要求：如果当前 Agent 已安装/可发现 Superpowers，先按该 Agent 的真实机制加载 `using-superpowers`，再加载本阶段适用的具体技能。需求业务梳理优先使用 `brainstorming`；计划使用 `writing-plans`；实施使用 `test-driven-development`；故障用 `systematic-debugging`；审查用 `requesting-code-review`/`receiving-code-review`；完成前用 `verification-before-completion`。先检查技能是否存在；缺失时明确报告并执行等价流程，不能谎称已调用。

OpenSpec 要求：若仓库已初始化 OpenSpec，执行 `openspec list --changes` 和 `openspec list --specs`；如有活动 Change，执行 `openspec status --change <change-id>`。创建/更新 artifact 前读取 `openspec instructions <artifact> --change <change-id> --json`。只有在提案规划/提案级需求分析阶段才创建或修改 Change；不要在需求业务梳理阶段提前创建 Change。需要时执行 `openspec validate <change-id> --strict`，不得未经人工批准自动归档。

选择唯一的下一阶段；功能级阶段还必须读取 `docs/BASELINE-FEATURE-INTERACTION.md` 与 `docs/architecture/baseline-status.md`，核对当前 Change 的 `design/baseline-impact.md`。阶段 05 必须建立该清单，阶段 09–13 复核，阶段 14 不直接修改冻结基线，阶段 16 仅回写已批准的公共决策。读取 `prompts/<next-prompt>` 和 `.claude/skills/<skill-id>/SKILL.md`，核验前置产物，按模板执行并运行阶段检查脚本。若有待审批、缺失输入或检查失败，暂停并提出具体问题。完成后生成 `workflow/evidence/<step-id>.json` 证据，并执行 `python scripts/workflow.py transition --step <step-id> --evidence workflow/evidence/<step-id>.json` 完成状态更新；禁止直接编辑 `workflow-state.json` 的 `completed_steps`/`current_step`，状态只能由 transition 写入。

不要一次跨越多个阶段，不要自动提交、发布、覆盖已有文件或绕过门禁。最终报告当前阶段、已实际调用的技能/命令、产物路径、检查结果和下一步。
```

## 使用前提
- 在能够读取当前项目仓库并调用终端/Skill 的 Agent 中使用。
- 如果只是普通聊天且没有仓库访问权限，先上传状态文件与相关产物，或手动复制对应阶段 Prompt；不能假装读取本地文件或执行 CLI。
- `workflow-state.json` 只是状态索引，真实文件、OpenSpec 状态和审批记录优先。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="workflow-orchestrator"` 的记录。

- 输入核验：workflow-state.json；docs/PROCESS-MAP.md；docs/STEP-ARTIFACT-CONTRACTS.json；docs/OUTPUT-TEMPLATE-MATRIX.csv；真实产物与审批记录；OpenSpec CLI 当前状态（如已初始化）。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：下一阶段判定报告（对话展示；不强制落盘）；workflow-state.json（仅在真实状态变化时更新）。状态文件由 `workflow.py transition` 写入，不要手工落盘阶段产物。
- 下一步输入：所选阶段的 Input Contract 中全部文件。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后，通过 `workflow.py transition` 更新 `workflow-state.json`；不得自动跨越审批点，不得直接编辑状态文件。


## P0 Runtime Guard (强制)

- 阶段 DAG 读取 `docs/WORKFLOW-STAGES.json`，不得自行推断/改写依赖。
- 执行前运行 `python3 scripts/workflow.py check-entry --step <step-id> [--change-id <id>]`；非 0 退出码表示禁止执行。
- 阶段完成后生成符合 `workflow/evidence/<step-id>.json` 结构的证据，调用 `python3 scripts/workflow.py transition --step <step-id> --evidence <path>`。禁止直接编辑 `completed_steps/current_step`。
- transition 会生成 SHA-256 handoff；下一阶段必须核验全部上游 manifest。文件哈希变化时退回上游重审，不得静默刷新。
- 阶段 14 后必须运行独立 `independent-verifier`，只有 PASS 才进入阶段 16。详情见 `docs/P0-RUNTIME-GOVERNANCE.md`。
