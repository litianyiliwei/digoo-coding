---
name: backend-detail-design
description: 后端详细设计。定义接口调用链、领域类/方法、DDL、Mapper、File I/O、Feign、Redis、MQ Client。
---

# 后端详细设计

## 何时使用
当流程进入“后端详细设计”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
规格、OpenAPI、接口逻辑、领域/数据/架构基线。

## 执行流程
1. 按 operationId 梳理 Controller → Application Service → Domain → Repository/Client 的调用链和依赖方向。
2. 设计本 Change 新增/修改的领域类、实体/值对象和方法，写清职责、参数、返回、不变量和异常。
3. 仅设计本 Change 所需的物理表/字段/索引/约束/迁移；共享模型变化走基线审批。
4. **逐个 operationId 建立 API→I/O 映射。每个业务 API 必须至少映射 1 个具体 IO ID；如果一个接口涉及多个数据库/磁盘/HTTP/Feign/Redis/MQ/对象存储/搜索请求，逐个列出并标注执行顺序。**
5. 将映射写入 `design/api-io-mapping.csv`，把每一个具体 I/O 操作登记在 `design/io-catalog.csv`；禁止只写“调用数据库/外部服务”，必须给出唯一 IO ID、资源、方法/SQL、入参/出参、事务/一致性、超时、重试、幂等、异常映射、可观测性和测试 ID。
6. 对每个 Mapper/SQL 说明读写表、字段、筛选、排序/分页、索引、事务、锁/乐观并发和异常。
7. 对 File I/O、Feign/HTTP、Redis、MQ 等 Client 给出接口签名、输入输出、超时、重试、幂等、熔断/死信（适用时）、错误映射和可观测性。
8. 定义事务边界；谨慎避免在长数据库事务内执行远程 IO。数据库与 MQ/远程 HTTP 的原子性不得凭空假设，必要时设计 outbox、幂等、补偿或一致性策略。
9. 测试设计必须覆盖每个 operationId 和每个 IO ID 的成功路径、关键失败路径及副作用断言。
10. 对确实不产生 I/O 的纯计算/健康接口，使用 `NO_IO_EXCEPTION`，填写原因并记录审批人；不得默默漏掉映射。

## 输出
`design/backend-design.md`、`design/api-io-mapping.csv`、`design/io-catalog.csv`、调用链、领域方法表、DDL/迁移、Mapper 与 IO Client 契约。

## 质量与安全边界
项目已有公共 Client 优先复用；事务与重试策略明确；避免把业务逻辑塞入 Controller/Mapper。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`阶段 13a–13e 全部设计产物完成后运行 scripts/check-design-assets.sh <change-id> --strict`；该检查会逐个核对 OpenAPI operationId 是否均映射到一个或多个 IO ID。


## 实际工具调用要求

- **Superpowers：** `brainstorming` 用于讨论领域/事务/IO 设计取舍；按模板逐接口映射 IO。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 读取 Change 状态、规格和 OpenAPI；若实现设计改变外部行为，先修改 OpenSpec 规格。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 架构、数据与 IO 基线约束（强制）

- 详细设计前读取 `system-context.md`、`domain-boundaries.md`、`logical-erd.md`、`data-flows.md`、`technology-decisions.md` 和相关 ADR；凡涉及 API 时同时遵守 `api-conventions.md`。
- 具体表/字段/索引/迁移、单功能事务编排、Feign/HTTP、Redis、MQ、文件/对象存储等 IO 契约留在当前 Change 的后端设计和 IO 目录。
- 只有共享实体语义/关系/数据所有权/领域不变量、模块边界、跨模块集成策略或全局 IO 约定变化才提出数据/架构基线修订。
- 基线约束与功能实现冲突时，不得通过局部代码绕过；在 `design/baseline-impact.md` 记录并走审批。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="backend-detail-design"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** openspec/changes/<change-id>/design/baseline-impact.md 与当前 docs/architecture/baseline-status.md；已批准 OpenAPI；功能规格与 AC；项目级架构/领域/数据模型/公共 Client 规范。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** openspec/changes/<change-id>/design/backend-design.md；openspec/changes/<change-id>/design/api-io-mapping.csv；openspec/changes/<change-id>/design/io-catalog.csv。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** API→IO 映射、每个 IO 契约、事务/幂等/超时/重试/错误映射、测试 ID。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。


## 机器基线约束（强制）

- 模块边界、数据所有权、共享实体、事务一致性、公共 Client、API 和可观测性规则必须逐条核验 `baseline-binding.json`；设计证据需定位到 backend-design、IO catalog、API→IO mapping 或 OpenAPI。
- 完成本阶段时执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。
