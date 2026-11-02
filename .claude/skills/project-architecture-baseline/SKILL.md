---
name: project-architecture-baseline
description: 项目总体架构设计。定义系统边界、技术选型、部署、数据流、安全与可观测性。
---

# 项目总体架构设计

## 何时使用
当流程进入“项目总体架构设计”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
产品基线、系统约束、部署环境、团队能力、质量属性目标。

## 执行流程
1. 绘制系统上下文、模块/容器、部署和主要信任边界。
2. 对技术选型比较候选、理由、代价、锁定因素和退出策略；重要决策写 ADR。
3. 描述同步请求、异步消息、数据读写、外部系统调用和失败补偿的数据流。
4. 定义鉴权/授权、日志脱敏、指标/追踪、密钥和配置管理策略。
5. 定义模块依赖方向、事务/一致性边界、性能和可靠性目标。
6. 避免提前设计某个 Change 的所有类、方法、Mapper 或 Feign 方法。

## 输出
系统上下文/模块图、技术决策、部署方案、数据流、ADR、风险与待决策项。

## 质量与安全边界
图和文字对同一边界的描述一致；选择有理由；关键非功能需求能被后续验证。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-required-files.sh`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 用于比较架构备选项，并记录权衡，不直接把假设写成决策。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 检查既有 specs、架构文档和 ADR；新增/改变架构决策须记录并等待审批。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="project-architecture-baseline"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准产品基线；现有仓库结构/技术约束；非功能需求。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** docs/architecture/system-context.md；docs/architecture/domain-boundaries.md；docs/architecture/containers-and-deployment.md；docs/architecture/data-flows.md；docs/architecture/technology-decisions.md；docs/adr/README.md。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 系统边界、模块职责、部署拓扑、技术决策、跨模块数据流。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
