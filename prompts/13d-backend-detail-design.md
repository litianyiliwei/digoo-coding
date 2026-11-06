# Prompt：后端详细设计

```text
执行 `@backend-detail-design`，Change：<change-id>。

输入：
- OpenSpec 规格/验收标准：<spec-paths>
- OpenAPI：<change-dir>/api/openapi.yaml
- 页面/事件清单：<change-dir>/design/page-inventory.csv、interaction-map.csv
- 项目架构/领域/数据基线：<baseline-paths>

必须按 `templates/change-assets/design/backend-design.md` 输出，并维护两个机器可检查文件：
1. `design/api-io-mapping.csv`：OpenAPI 的每一个 operationId 至少对应一个 IO ID；如果一个接口触发多个 IO/数据库请求，每次请求分别列一行并写明调用顺序、事务/一致性范围、失败处理和测试 ID。
2. `design/io-catalog.csv`：每个 IO ID 明确类型、资源/Client、具体 Mapper/SQL/文件操作/HTTP/Feign/Redis/MQ 操作、输入输出契约、事务/一致性、超时、重试、幂等、错误映射、日志/指标/追踪和测试 ID。

每个数据库操作需要具体到表/字段、Mapper 方法或 SQL、过滤/排序/分页、索引/约束、事务与并发控制；每个非数据库 IO 需要具体到接口签名、输入输出、超时、重试、幂等/投递语义、补偿和错误处理。

输出 operationId → Controller → Application Service → Domain → IO ID 的调用链。禁止只写“访问数据库”“调用 Feign”这类不可验证描述。必须说明每个 API 在每一步执行哪些 IO、失败后如何处理，以及相应测试。项目级已有能力优先复用；涉及基线变更先列审批事项。

对确实不产生 I/O 的纯计算/健康 API，不要省略映射：使用 NO_IO_EXCEPTION，并填写 no_io_reason、approved_by；严格校验要求有明确审批。不要为了填表而虚构一次无意义的数据库访问。

生成完成后运行：
`python3 scripts/check-api-io-mapping.py <change-dir>/api/openapi.yaml <change-dir>/design/api-io-mapping.csv <change-dir>/design/io-catalog.csv`
并在设计全部完成后运行：
`bash scripts/check-design-assets.sh <change-id> --strict --lint-api`
如未实际运行，不得声称通过。未知内容标为 PENDING，说明负责人和阻塞条件，不要猜测。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：必须读取 system-context、domain-boundaries、logical-erd、data-flows、technology-decisions、相关 ADR 和 api-conventions。功能物理表/字段/迁移及 IO 留在 Change；共享实体语义、数据所有权、领域不变量、模块边界或公共集成策略变化须提出基线修订。
```

## 执行前变量

- `<change-id>`：OpenSpec Change ID。
- `<change-dir>`：`openspec/changes/<change-id>` 的实际路径。
- `<spec-paths>`、`<baseline-paths>`：填真实文件路径。
- 按 Agent 环境加载 `backend-detail-design` Skill；若 Agent 不支持 `@skill` 语法，直接读取对应 `SKILL.md`。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按设计复杂度使用 Superpowers `brainstorming` 审视方案；不要将它当成接口/设计模板的替代品。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 先检查 Change 状态：`openspec status --change <id>`；读取已批准 specs/design。若发现需求变化，暂停并回到 OpenSpec 更新规格，不能只改辅助设计文档。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="backend-detail-design"` 的记录。

- 输入核验：已批准 OpenAPI；功能规格与 AC；项目级架构/领域/数据模型/公共 Client 规范。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design/backend-design.md；openspec/changes/<change-id>/design/api-io-mapping.csv；openspec/changes/<change-id>/design/io-catalog.csv。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：API→IO 映射、每个 IO 契约、事务/幂等/超时/重试/错误映射、测试 ID。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 基线交互：必须按 `docs/BASELINE-FEATURE-INTERACTION.md` 核验基线读取/变更归属；阶段 10 创建/更新 `design/baseline-impact.md`，后续阶段复核；未经批准不得修改冻结基线。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。


## 机器基线设计门禁（必须执行）

将模块边界、数据所有权、事务、领域模型、公共 Client 和数据流约束映射到 backend-design、IO catalog、API→IO mapping 或 OpenAPI，执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。
