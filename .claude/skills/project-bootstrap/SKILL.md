---
name: project-bootstrap
description: 项目初始化与工具链检查。初始化仓库上下文与工具状态；不覆盖用户文件。
---

# 项目初始化与工具链检查

## 何时使用
当流程进入“项目初始化与工具链检查”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
仓库路径、项目摘要、当前工具和 IDE/Agent 环境。

## 执行流程
1. 读取 README、目录结构、构建配置、CI、Git 状态和既有 OpenSpec 配置。
2. 执行非破坏性工具探测；读取 `openspec --version`、`openspec init --help` 或相关帮助，不凭记忆猜参数。
3. 检查当前 Agent 是否能发现 `.claude/skills/<name>/SKILL.md`，并确认 Superpowers 已安装及其真实技能名。
4. 对缺失文件提出最小补充方案；任何覆盖、安装、删除、提交和 CI 修改均需用户明确授权。

## 输出
工具状态表、现有目录/规则摘要、冲突与缺口清单、最小初始化计划；初始化 `docs/architecture/baseline-status.md` 时以 `templates/project-baseline/baseline-status.md` 为模板，不得仅写一个未版本化的 TODO 状态。

## 质量与安全边界
不覆盖已有文件；不把“找不到命令”写成“已安装”；所有未执行检查明确标记。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- Figma MCP 的输入必须基于实际可访问的链接、节点和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-package.py`


## 实际工具调用要求

- **Superpowers：** `using-superpowers`（若存在）并检查当前 Agent 可用的 Superpowers 技能；不要自动安装或覆盖工具。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 若存在 `openspec/`，真实运行 `openspec version`、`openspec list --changes`、`openspec list --specs`；未初始化时只报告，未经用户批准不运行 init。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="project-bootstrap"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 用户提供的项目目标与仓库位置；仓库现有目录/配置/AGENTS.md（若存在）。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** AGENTS.md（仅缺失时创建或经批准修改）；workflow-state.json；docs/architecture/baseline-status.md（依据 `templates/project-baseline/baseline-status.md` 建立域版本登记）；工具链检查报告（docs/project/toolchain-report.md）。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 仓库约定与工具链报告；workflow-state.json。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
