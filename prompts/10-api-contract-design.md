# Prompt：OpenAPI 与接口逻辑设计

```text
执行 `@api-contract-design`，Change：<change-id>。

需求规格：<spec-paths>
事件清单：<interaction-map>
详细设计：<design-md-and-plan>
公共 API 规范：<api-conventions>

按模板生成 OpenAPI 3.x 文件、稳定 operationId、权限、请求/响应 schema、错误响应和示例。逐个 operationId 输出 API IO 需求清单，标明所需的数据库读/写、文件/对象存储、HTTP/Feign、Redis、MQ、搜索等 I/O 类别；不要在本阶段虚构具体 SQL 或 Client 方法。后续后端详细设计必须将每个 operationId 映射到一个或多个具体 IO ID。同时生成 `design/api-traceability.csv`，登记 operationId → PAGE/EVT/AC 映射，供 13e 合并进 traceability.csv。为成功、边界、校验、认证、授权、404、冲突、依赖失败和幂等生成测试用例。运行 `scripts/validate-openapi.sh <file>`；有 API 时运行 `scripts/check-traceability.py --file openspec/changes/<change-id>/design/api-traceability.csv --strict`，`x-api-scope: none` 时在 design.md 记录 N/A + 理由。未知字段列为 PENDING + 原因，不可猜测。
如果本 Change 不新增/修改 API，必须设置 `x-api-scope: none` 并说明原因；否则设置 `x-api-scope: defined` 并提供 operationId。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：必须遵循 `docs/architecture/api-conventions.md`。单个 API 属于 Change；改变全局错误模型、鉴权、版本、分页、幂等或兼容规则时提出 API 基线修订，不得局部静默偏离。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@api-contract-design`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按设计复杂度使用 Superpowers `brainstorming` 审视方案；不要将它当成接口/设计模板的替代品。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 先检查 Change 状态：`openspec status --change <id>`；读取已批准 specs/design。若发现需求变化，暂停并回到 OpenSpec 更新规格，不能只改辅助设计文档。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="api-contract-design"` 的记录。

- 输入核验：已批准功能规格与页面交互清单；Figma 交互（适用时）；项目级 API/鉴权/错误码约定。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/api/openapi.yaml；openspec/changes/<change-id>/design/api-traceability.csv（operationId → PAGE/EVT/AC）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：唯一 OpenAPI 契约、operationId、请求响应/错误/权限定义、api-traceability.csv。在报告中明确 13c/13d/13e 如何消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 基线交互：必须按 `docs/BASELINE-FEATURE-INTERACTION.md` 核验基线读取/变更归属；阶段 05 创建/更新 `design/baseline-impact.md`，后续阶段复核；未经批准不得修改冻结基线。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。


## 机器基线设计门禁（必须执行）

将 API/鉴权/错误/版本/幂等等适用 Constraint ID 映射到 OpenAPI 或设计证据。执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`；不允许只在 Markdown 里声明兼容。
