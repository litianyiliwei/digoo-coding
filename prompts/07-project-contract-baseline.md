# Prompt：项目级接口/前端/测试规范

```text
执行 `@project-contract-baseline`。

架构/技术栈：<architecture-baseline>
鉴权/错误模型：<security-and-errors>
质量目标：<quality-attributes>

定义公共 API、前端工程、错误/分页/幂等/兼容性、测试分层和质量门禁。明确强制/推荐/可例外规则，并标识可自动化检查项。不得设计单个 Change 的具体接口字段。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@project-contract-baseline`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.agents/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按需要使用 Superpowers `brainstorming` 讨论方案；架构决策/产品规则未获批准前不能标为冻结。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 若 OpenSpec 已初始化，读取相关现有 specs/changes 作为约束；此项目基线阶段不擅自创建或归档功能 Change。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="project-contract-baseline"` 的记录。

- 输入核验：已批准架构与数据领域基线；现有前后端工程规范；非功能要求。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：docs/architecture/api-conventions.md；docs/architecture/frontend-conventions.md；docs/architecture/test-strategy.md。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：API 公共约定、前端工程约定、测试策略与质量门禁。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。
