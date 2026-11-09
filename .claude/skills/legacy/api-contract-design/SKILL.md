---
name: api-contract-design
description: OpenAPI 与接口逻辑设计。定义 operationId、请求/响应、错误语义、业务步骤和契约测试。
---

# OpenAPI 与接口逻辑设计

## 何时使用
当流程进入“OpenAPI 与接口逻辑设计”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
规格、事件清单、`design.md` 与 `design/design-plan.md`（统一设计约束/接口范围）、公共 API 约定、鉴权与错误模型。

## 执行流程
1. 每个接口定义稳定 operationId、路径、方法、鉴权、参数、请求体、响应 schema 和错误响应。
2. 描述字段类型、必填、范围、枚举、格式、分页、幂等与并发冲突语义。
3. 在接口逻辑说明中写业务步骤、应用服务/领域调用、事务边界、数据/外部 IO 与失败映射。
4. 用 OpenAPI 3.x 表达契约；业务算法细节放在设计说明，不把说明文字伪装成 schema。
5. 生成正常、边界、校验失败、认证、授权、Not Found、Conflict、依赖失败、重复请求等测试。
6. 对每个 operationId 输出 IO 需求清单，标记需要数据库读写、文件/对象存储、HTTP/Feign、Redis、MQ、搜索等哪类 I/O；这一步只记录“需要什么”，不要提前编造具体 SQL 或 Client 方法。后续后端详细设计必须把每个 operationId 映射到一个或多个具体 IO ID。同时把 operationId → PAGE/EVT/AC 的映射写入 `design/api-traceability.csv`，供 13e 合并进 `traceability.csv`。
7. 若本 Change 不新增/修改任何 API，OpenAPI 文件必须显式设置 `x-api-scope: none`，并说明原因；否则设置 `x-api-scope: defined` 并为每个操作提供 operationId。
8. 运行 Redocly 或项目批准的 OpenAPI lint；禁止未审批地改变契约。

## 输出
`api/openapi.yaml`、`design/api-traceability.csv`、operationId 逻辑表、API IO 需求清单、契约测试矩阵。

## 质量与安全边界
OpenAPI 可解析；响应 schema 与示例一致；每个操作有 operationId、安全配置和错误语义。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/validate-openapi.sh <openapi-file>`；后续运行 `scripts/check-api-io-mapping.py` 校验后端逐接口 IO 映射。；后续运行 `scripts/check-api-io-mapping.py` 校验后端逐接口 IO 映射。


## 实际工具调用要求

- **Superpowers：** `brainstorming` 处理接口契约的备选项和边界争议。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 读取 OpenSpec 已批准规格和 `openspec status --change <id>`；完成后运行 `openspec validate <id> --strict`。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 公共 API 基线约束（强制）

- 生成 OpenAPI 前读取并引用 `docs/architecture/api-conventions.md`，核验认证授权、版本、错误 envelope、分页、幂等、兼容和公共字段约定。
- 单个 operationId / endpoint / schema 属于当前 Change；改变所有 API 应遵循的公共规则才提出公共 API 基线变更。
- 若必须改变公共 API 规则，更新 `design/baseline-impact.md` 并创建基线变更请求/ADR；未批准前不得将偏离约定的契约标记为可实施。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="api-contract-design"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** openspec/changes/<change-id>/design/baseline-impact.md 与当前 docs/architecture/baseline-status.md；已批准功能规格与页面交互清单；openspec/changes/<change-id>/design.md 与 design/design-plan.md（统一设计约束/接口范围）；Figma 交互（适用时）；项目级 API/鉴权/错误码约定。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** openspec/changes/<change-id>/api/openapi.yaml；openspec/changes/<change-id>/design/api-traceability.csv（operationId → PAGE/EVT/AC 映射）。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 唯一 OpenAPI 契约、operationId、请求响应/错误/权限定义、api-traceability.csv。明确指出 13c/13d/13e 消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。


## 机器基线约束（强制）

- API 约束必须逐条映射到 `design/baseline-binding.json` 的 Constraint ID；鉴权、错误模型、幂等、版本兼容等适用规则需有 OpenAPI/设计章节证据。
- 完成本阶段时执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`；不得以 Markdown 影响清单替代机器绑定。
