---
name: project-contract-baseline
description: 项目级接口/前端/测试规范。建立跨功能 API、前端工程与测试策略的公共约定。
---

# 项目级接口/前端/测试规范

## 何时使用
当流程进入“项目级接口/前端/测试规范”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
架构基线、技术栈决定、鉴权方式、接口与质量属性要求。

## 执行流程
1. 约定 API 版本、operationId、认证授权、错误模型、分页、幂等和兼容策略。
2. 约定前端目录、路由、API 调用层、状态管理、表单与错误展示原则。
3. 约定测试层级、契约测试、集成测试、E2E、测试数据与环境策略。
4. 定义安全扫描、代码规范、日志隐私、可访问性和性能门禁。
5. 清晰标记强制规则、推荐规则和可申请例外的规则。

## 输出
API 约定、前端约定、测试策略、质量门禁列表。

## 质量与安全边界
规则可用于审查或脚本检查；不重复定义所有功能级 operation schema。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-required-files.sh`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 用于讨论公共契约的取舍；将最终约定写入基线文档。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 读取现有 API/specs 与工程约定；公共契约变更必须经评审。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="project-contract-baseline"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准架构与数据领域基线；现有前后端工程规范；非功能要求。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** docs/architecture/api-conventions.md；docs/architecture/frontend-conventions.md；docs/architecture/test-strategy.md。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** API 公共约定、前端工程约定、测试策略与质量门禁。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
