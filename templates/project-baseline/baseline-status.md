# 项目基线状态与版本登记

- 项目名称：
- 总体基线版本：`v0.1.0`
- 总体状态：DRAFT / FROZEN / UNDER_AMENDMENT
- 最近生效日期：
- 产品负责人：
- 架构负责人：
- 技术负责人：
- 基线仓库版本/Commit：

## 1. 各基线域版本

| 基线域 | 权威文件 | 版本 | 状态 | 审批人 | 生效日期 | 最近关联 Change / ADR |
|---|---|---|---|---|---|---|
| 产品 | `docs/product/*` | v0.1.0 | DRAFT / FROZEN | | | |
| 架构 | `docs/architecture/system-context.md`、`domain-boundaries.md`、`containers-and-deployment.md`、`data-flows.md`、`technology-decisions.md`、`docs/adr/*` | v0.1.0 | DRAFT / FROZEN | | | |
| 数据与领域 | `docs/architecture/logical-erd.md`、`domain-boundaries.md`、`data-flows.md` | v0.1.0 | DRAFT / FROZEN | | | |
| 公共 API | `docs/architecture/api-conventions.md` | v0.1.0 | DRAFT / FROZEN | | | |
| 前端工程 | `docs/architecture/frontend-conventions.md` | v0.1.0 | DRAFT / FROZEN | | | |
| 测试与质量 | `docs/architecture/test-strategy.md` | v0.1.0 | DRAFT / FROZEN | | | |

## 2. 生效规则

- 状态为 `FROZEN` 的域是功能开发必须遵循的规范；功能 Change 必须记录实际引用的域版本。
- `DRAFT` 域可以作为参考，但不能冒充已批准约束；影响该域的功能设计必须标记风险并取得负责人批准。
- `UNDER_AMENDMENT` 表示存在基线修订；在审批生效前仍以旧版本为准，待修订规则不能提前作为强制要求。
- 任何正式变更都必须记录修订版本、变更理由、审批人、生效日期、关联 ADR/Change 和受影响的在途 Change。

## 3. 版本策略

默认使用语义版本：
- PATCH：不改变规范语义的澄清、错字、引用修正。
- MINOR：新增兼容的共享规则、实体/公共约定或质量要求。
- MAJOR：改变系统边界、数据所有权、公共契约或可能导致既有功能不兼容的约束。

项目可采用其他策略，但必须在此明确并保持一致。

## 4. 当前待处理的基线修订

| 修订 ID | 影响域 | 提出来源 Change | 变更摘要 | 状态 | 负责人/审批人 | 生效版本 |
|---|---|---|---|---|---|---|
| | | | | PENDING / APPROVED / REJECTED / IMPLEMENTED | | |

## 5. 冻结批准记录

| 基线版本 | 审批范围 | 审批人 | 日期 | 证据/会议记录 |
|---|---|---|---|---|
| | | | | |
