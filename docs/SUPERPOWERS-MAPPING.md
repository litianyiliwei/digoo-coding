# Superpowers 技能映射

本项目 Skill 负责业务阶段；Superpowers 负责编码方法与协作流程。两者不是一套需要相互替换的技能。

| 本项目阶段 | 对应 Superpowers 技能（如安装版本中存在） | 用法 |
|---|---|---|
| 对话启动/技能发现 | `using-superpowers` | 若已安装且 Agent 可发现，先读取其规则，再选择任务相关技能；按宿主 Agent 的真实调用方式执行 |
| 需求发现/方案讨论 | `brainstorming` | 先与用户澄清目标、用户、痛点、范围、成功标准和未决问题；不应未经澄清就一次性生成完整方案；需求规格最终落入项目基线/OpenSpec |
| 计划实施 | `using-git-worktrees`、`writing-plans` | 在获批方案后准备隔离工作区并拆成小任务 |
| 编码实施 | `test-driven-development` | RED → GREEN → REFACTOR，验证先行 |
| 任务执行 | `subagent-driven-development` 或 `executing-plans` | 按当前环境支持的模式执行并设置检查点 |
| 故障处理 | `systematic-debugging` | 复现、定位根因、验证修复，不做随机修改 |
| 代码审查 | `requesting-code-review`、`receiving-code-review` | 根据规格/计划检查并核实审查反馈 |
| 完成前验证 | `verification-before-completion` | 用真实命令和结果证明功能已修复/实现 |
| 分支结束 | `finishing-a-development-branch` | 在所有验证通过后讨论合并/PR/清理，不能自动发布 |

技能名称和触发规则可能随 Superpowers 版本及 Agent 适配有所变化。实施前先检查当前安装内容；若缺少技能，应明确报告并执行等价的显式流程，不要声称调用了不存在的技能。


## 必须执行而非只提及

- 每个阶段 Prompt 必须先加载对应的项目 Skill，并检查适用的 Superpowers 技能是否实际可用。
- 需求发现阶段明确使用 `brainstorming`；它通常发生在正式 OpenSpec Change 之前，因此先读取已有 specs，不要提前创建 Change。
- OpenSpec 相关阶段必须运行真实 CLI：用 `openspec list/status/instructions/validate` 读取状态和规则；只有用户批准且门禁通过后才 archive。
- 若 Agent 没有仓库/终端/Skill 访问能力，必须请求用户提供文件或说明无法执行，不能模拟工具结果。
