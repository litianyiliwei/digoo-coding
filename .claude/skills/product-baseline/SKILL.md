---
name: product-baseline
description: 项目级产品基线。统一跨提案的术语、角色、业务规则与状态机。
---

# 项目级产品基线

## 何时使用
当流程进入“项目级产品基线”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
已确认需求、原型审查结果、角色/权限和业务术语。

## 执行流程
1. 统一术语、角色、权限、业务实体和跨流程状态名。
2. 确定跨提案复用的业务规则、关键状态机、数据归属和审计要求。
3. 将项目级约束与单个提案的细节分开；只把确实是全局的规则放入基线。
4. 每条规则记录 ID、来源、状态、负责人及变更影响。
5. 把冲突转成决策项，不擅自择一。

## 输出
术语表、业务规则基线、角色权限说明、全局状态机和验收政策。

## 质量与安全边界
全局规则可被多个 Change 引用；未确认条目不可标为已批准。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-required-files.sh`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 用于澄清相互冲突的产品规则；没有客户确认的规则标为 PENDING。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 读取相关 specs/changes 作为现有行为约束；不创建功能 Change。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="product-baseline"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已确认需求产物；已批准原型审计与修订记录。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** docs/product/requirements-analysis.md；docs/product/workflows.md；docs/product/use-cases.md；docs/product/user-stories.md；docs/product/business-rules.md；docs/product/glossary.md；docs/product/acceptance-policy.md。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 已批准产品需求基线及稳定 ID。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
