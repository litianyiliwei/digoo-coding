# Prompt：提案原型生成与评审

```text
执行 `@prototype-generation`，Change：<change-id>。

提案需求：<proposal-and-user-stories-paths>
项目业务流程/RD 矩阵：<product-paths>
目标页面范围：<pages-scope，可留空表示按 UC/US 推导>

按已批准的提案级 UC/US/AC 与项目 FLOW/NODE/DO 逐页绘制：先在 openspec/changes/<change-id>/design/prototype-build.md 登记 PAGE ID，再用 pen.dev MCP 逐页绘制，并在每页绘制后用 get_app_state 核验真实渲染。页面按功能区块组织，映射表逐行登记 PAGE ID → UC/US/FLOW/BR ID。绘制完成后执行阶段结束评审：逐页核对状态与交互，把原型与需求的差异、决策和待确认项写入 openspec/changes/<change-id>/design/prototype-audit.md。若 MCP 不可用或调用失败，在构建记录中如实登记 blocked；不得声称已生成，不得伪造链接或页面。先给页面清单与映射表，不要直接跳到视觉细节。完成后运行 `python scripts/check-prototype-build.py --change <change-id> --strict`。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：本阶段为提案级，必须填写真实 Change ID。
- 加载 Skill：在支持 Agent Skill 的环境中使用 `@prototype-generation`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按需要使用 Superpowers `brainstorming` 讨论页面方案；先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 读取相关已批准 proposal/specs 作为约束；本阶段不创建或归档功能 Change。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行。
- **pen.dev MCP（pencil 工具）：** 先 `read_skill` 加载画布设计指引，再 `get_app_state` 核验当前状态，用 `execute` 绘制页面；每次调用结果如实登记到构建记录。MCP 不可用时在构建记录中标记 blocked 并停止，不得伪造链接或页面。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/MCP 工具、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="prototype-generation"` 的记录。

- 输入核验：已批准的提案级 proposal/specs/design/user-stories/use-cases；docs/product/open-questions.md（只读）；pen.dev MCP 实际可访问能力；当前 Change 的 baseline-binding.json。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design/prototype-build.md；openspec/changes/<change-id>/design/prototype-audit.md；pen.dev 原型页面（链接登记到构建记录）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：已批准原型链接/导出物、PAGE→UC/US/FLOW/BR 映射、原型评审结论与需求澄清。在报告中明确阶段 11 如何消费这些文件。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。

## 阶段结束审计（必须执行）

- 逐页核对原型状态与交互：默认、加载、空数据、成功、失败、无权限、禁用、边界值、重复提交；返回/取消/关闭/刷新/未保存提示/导航/表单校验。
- 逐条核对提案级 UC/US 的入口、操作和结果路径是否都有页面覆盖；缺页面/缺元素/多出业务行为必须登记为差异。
- 差异、决策、负责人、日期和原型版本写入 `design/prototype-audit.md`；未决问题转入 open-questions，不擅自决策。
- 运行 `python scripts/check-prototype-build.py --change <change-id> --strict`，退出码必须为 0；审计结论写入交接报告。
