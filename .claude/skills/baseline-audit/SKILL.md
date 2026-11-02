---
name: baseline-audit
description: 项目基线审计与冻结。检查跨文档矛盾、未决事项和审批状态。
---

# 项目基线审计与冻结

## 何时使用
当流程进入“项目基线审计与冻结”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
产品、架构、数据/领域、公共契约和测试基线文档。

## 执行流程
1. 检查要求的基线文件是否存在以及是否仍含占位符。
2. 交叉检查术语、权限、系统边界、核心领域、API 错误模型和测试策略的一致性。
3. 按阻断/高/中/低风险列出矛盾、缺失和未决事项。
4. 形成有版本、日期、审批人、适用范围的基线状态记录。
5. 只有关键决策确认后才建议冻结；不要把空白当作默认同意。

## 输出
基线审计报告、待审批事项、批准版本和冻结/未冻结状态。

## 质量与安全边界
审批状态有负责人/证据；存在阻断项时不得建议冻结。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-required-files.sh --strict`


## 实际工具调用要求

- **Superpowers：** 必要时使用 `brainstorming` 组织冲突决策；对可核验的完整性采用检查脚本。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 若 CLI 可用，执行 `openspec list --specs` 和 `openspec list --changes`，核对基线与现有规格的关系。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="baseline-audit"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 产品基线；架构基线；数据/领域基线；公共契约/测试基线；未决问题清单。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** templates/project-baseline/baseline-audit-report.md 的项目实例（建议 docs/project/baseline-audit-report.md）；docs/architecture/baseline-status.md。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 冻结的项目基线版本、缺口/豁免、审批记录。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
