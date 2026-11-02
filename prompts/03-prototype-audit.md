# Prompt：pen.dev 原型评审与需求澄清

```text
执行 `@prototype-audit`。

需求基线：<requirements-paths>
pen.dev 链接/导出：<prototype-link-or-export>
客户反馈：<feedback>

按故事和页面检查覆盖、状态、交互与异常路径。输出需求有而原型缺失、原型有而需求未定义、状态/交互缺口和客户问题。若工具/链接不可访问，明确列出未检查部分，不得声称已读取。先给差异清单，不要直接覆盖已确认需求。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@prototype-audit`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按需要使用 Superpowers `brainstorming` 讨论方案；架构决策/产品规则未获批准前不能标为冻结。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 若 OpenSpec 已初始化，读取相关现有 specs/changes 作为约束；此项目基线阶段不擅自创建或归档功能 Change。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="prototype-audit"` 的记录。

- 输入核验：docs/product/* 需求产物；pen.dev 原型链接/导出物（必须实际可访问）；需求疑问与干系人反馈。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：docs/design/prototype-audit.md；docs/product/open-questions.md（更新）；docs/product/requirements-analysis.md（经确认的修订）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：原型评审结论、已确认需求修订、未决问题。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。
