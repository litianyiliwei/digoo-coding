# 项目基线状态与版本登记

- 项目名称：智慧农业项目
- 总体基线版本：`v1.0.2`
- 总体状态：FROZEN
- 最近生效日期：2026-11-11
- 产品负责人：用户（welly，代行业务负责人）
- 架构负责人：用户（welly，代行架构负责人）
- 技术负责人：用户（welly，代行技术负责人）
- 基线仓库版本/Commit：工作区（未提交变更除外）

> **机器权威来源：** `docs/architecture/baseline-manifest.json`。本 Markdown 仅供人审阅；版本、冻结状态、审批和哈希以 JSON Manifest 为准。
> **约束权威来源：** `docs/architecture/constraint-registry.json`。所有适用的 MUST / SHOULD / MAY / PROHIBITED 规则必须有稳定 Constraint ID。
> 禁止只修改本文件来宣称冻结或升级；必须同时通过 `scripts/baseline-governance.py audit`。

## 1. 各基线域版本

| 基线域 | 权威文件 | 版本 | 状态 | 审批人 | 生效日期 | 最近关联 ADR |
|---|---|---|---|---|---|---|
| 产品 | `docs/product/requirements-analysis.md`、`workflows.md`、`data-objects.csv`、`rd-matrix.csv`、`business-rules.md`、`glossary.md`、`acceptance-policy.md` | v1.0.2 | FROZEN | 用户（welly，代行） | 2026-11-11 | N/A |
| 架构 | `docs/architecture/system-context.md`、`domain-boundaries.md`、`containers-and-deployment.md`、`data-flows.md`、`technology-decisions.md`、`docs/adr/README.md` | v1.0.0 | FROZEN | 用户（welly，代行） | 2026-11-10 | ADR-001~014 |
| 数据与领域 | `docs/architecture/logical-erd.md`、`domain-boundaries.md`、`data-flows.md` | v1.0.0 | FROZEN | 用户（welly，代行） | 2026-11-10 | ADR-003/010 |
| 公共 API | `docs/architecture/api-conventions.md` | v1.0.0 | FROZEN | 用户（welly，代行） | 2026-11-10 | ADR-006 |
| 前端工程 | `docs/architecture/frontend-conventions.md` | v1.0.2 | FROZEN | 用户（welly，代行） | 2026-11-11 | ADR-002 |
| 测试与质量 | `docs/architecture/test-strategy.md` | v1.0.0 | FROZEN | 用户（welly，代行） | 2026-11-10 | ADR-007 |

> 当前 22 条约束均为 ACTIVE；机器权威以 `constraint-registry.json` 与 `baseline-manifest.json` 为准。

## 1.1 服务清单

| 服务 | 领域 | 一期状态 | 说明 |
|---|---|---|---|
| `platform-service` | DOM-001、DOM-009 | 启用 | 身份、RBAC、审计、通知、系统配置 |
| `mes-service` | DOM-002~005、DOM-007、DOM-008 | 启用 | 农业 MES 主服务：计划、任务、作业、库存、批次、溯源、监管 |
| `iot-service` | DOM-006 | 启用 | 设备、遥测、预警、控制、适配层 |
| `gis-service` | DOM-010 | 启用 | 地块几何、图层、GeoJSON、PostGIS |
| `ecommerce-service` | DOM-011 | 远期预留，默认不部署 | 商品、订单、支付、售后；启用前需产品基线修订 |

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

## 4. 当前待处理的基线修订

| 修订 ID | 影响域 | 提出来源 Change | 变更摘要 | 状态 | 负责人/审批人 | 生效版本 |
|---|---|---|---|---|---|---|
| N/A | N/A | N/A | 初次冻结，无修订 | N/A | 产品/架构/技术负责人 | v1.0.0 |
| BCR-2026-11-11-FRONTEND-06 | 前端工程、产品 | 流程修复（阶段 06 收敛） | 修正冻结后漂移；明确设计令牌以 Figma MCP 读取结果为准，不再维护 design-tokens.json；acceptance-policy 同步 06 产物定义 | CLOSED | 用户（welly，代行架构/技术负责人） | v1.0.1 |
| BCR-2026-11-11-FIGMA-ONLY | 前端工程、产品 | 流程调整（阶段 06 改为 Figma-only） | 移除 06a/pen.dev/PAGE HTML 引用；06 唯一 UI 产物改为 figma-audit.md；验收设计证据同步 | CLOSED | 用户（welly，代行架构/技术负责人） | v1.0.2 |

## 5. 冻结批准记录

| 基线版本 | 审批范围 | 审批人 | 日期 | 证据/会议记录 |
|---|---|---|---|---|
| v1.0.0 | 产品、架构、数据与领域、公共 API、前端工程、测试与质量 | 用户（welly，代行业务/架构/技术负责人） | 2026-11-10 | `workflow/evidence/03-architecture-baseline-approval.md` |
| v1.0.1 | 前端工程、产品（阶段 06 规则收敛与冻结漂移修正） | 用户（welly，代行架构/技术负责人） | 2026-11-11 | `workflow/evidence/baseline-amendment-2026-11-11-frontend.md` |
| v1.0.2 | 前端工程、产品（阶段 06 改为 Figma-only） | 用户（welly，代行架构/技术负责人） | 2026-11-11 | `workflow/evidence/baseline-amendment-2026-11-11-figma-only.md` |

## 6. 机器登记操作

- DRAFT 阶段完成文档内容后，运行 `python3 scripts/baseline-governance.py refresh-hashes`。
- 人工确认每个域的负责人、审批人、批准日期、生效 revision、审批证据和版本；将所有适用约束从 DRAFT 审批为 ACTIVE。
- 将各域状态设置为 FROZEN 并填好域审批字段，随后执行 `python3 scripts/baseline-governance.py freeze --approved-by <负责人> --approved-at <日期> --evidence <审批证据文件>`。
- 冻结后禁止直接编辑基线文件。先执行 `open-amendment`；修订、升级版本、重新计算哈希、审批后执行 `close-amendment`，才能恢复功能级门禁。
