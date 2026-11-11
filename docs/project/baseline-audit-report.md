# 项目基线审计报告

- 审计日期/版本：2026-11-10 / v1.0.0（初次冻结候选，服务化架构修订）
- 审计范围：`docs/product/`、`docs/architecture/`、`docs/adr/`
- 审计人：架构阶段（AI 辅助审计，待责任人复核）
- 建议状态：FROZEN（已批准，v1.0.0；存在非阻断风险，见第 3 节）

## 1. 本次修订范围（2026-11-10）

| 用户指令 | 架构落点 |
|---|---|
| 增加 GIS 服务，显示地块地理信息 | `gis-service`、PostGIS 3、ENT-029 地块几何、DF-011、ADR-015 |
| 明确主服务类似 MES，管理农业生产 | `mes-service` 定位为农业 MES；计划/任务/作业/库存/批次/溯源主链路 |
| 明确 IoT 服务 | `iot-service` 独立拥有设备、遥测、阈值、预警、控制；DF-001/006 |
| 增加电商服务，支持后期电商 | `ecommerce-service` 远期预留，默认不部署；ADR-016；不改变一期范围 |

## 2. 必需产物清单

| 产物 | 路径 | 完整性 | 交叉一致性 | 结论/证据 |
|---|---|---|---|---|
| 需求业务梳理 | `docs/product/requirements-analysis.md`、`workflows.md`、`data-objects.csv`、`rd-matrix.csv`、`business-rules.md`、`glossary.md`、`acceptance-policy.md` | 已生成；8 FLOW、78 NODE、28 DO、185 RD | 节点↔RD↔DO↔BR 引用闭合；`check-requirements.py --strict` 退出码 0 | 通过 |
| 系统架构与数据流转 | `docs/architecture/system-context.md`、`domain-boundaries.md`、`containers-and-deployment.md`、`data-flows.md`、`logical-erd.md`、`technology-decisions.md` | 已生成；5 个服务、9+2 个领域、29 个实体、12 条数据流 | 边界↔数据流↔ERD↔DO 一致；服务间只走 API/事件 | 通过 |
| 公共契约与 ADR | `docs/architecture/api-conventions.md`、`frontend-conventions.md`、`test-strategy.md`、`docs/adr/README.md` | 已生成；ADR-001~017 | 契约↔架构↔测试策略一致；服务路由与服务间 JWT 已定义 | 通过 |
| 机器基线 | `docs/architecture/baseline-manifest.json`、`constraint-registry.json` | 已生成；22 条约束候选 | 六个域文件清单齐全；约束有 ID、来源、等级与执行方式 | 通过 |
| 基线状态镜像 | `docs/architecture/baseline-status.md` | 已生成；含 5 个服务清单 | 与 Manifest 版本域一致；人工可读 | 通过 |

## 3. 问题与风险

| ID | 严重级 | 问题/矛盾 | 影响的文档/规则 | 建议动作 | 负责人 | 阻断冻结 |
|---|---|---|---|---|---|---|
| TECH-RISK-001 | HIGH | Spring Boot 4 与 MyBatis、Spring Security 的 starter 兼容性尚未实测 | ADR-001、DEPLOY-TECH-001 | 阶段 08 首个任务前做最小构建验证；不兼容时回退 Spring Boot 3.5 LTS 并走基线修订 | 技术负责人 | No |
| TECH-RISK-002 | MEDIUM | JDK 25 与部分 Maven 插件/静态分析工具兼容性未验证 | ADR-001、ADR-007 | CI 固定 JDK 25，验证插件与 Testcontainers | 技术负责人 | No |
| SERVICE-RISK-001 | MEDIUM | 多服务单机部署增加启动、发布与排障复杂度 | containers-and-deployment、ADR-010 | Docker Compose healthcheck、启动顺序、统一日志/traceId；阶段 10 前演练 | 技术负责人 | No |
| SERVICE-RISK-002 | MEDIUM | 跨服务一致性依赖 Outbox 与重试 | data-flows、SERVICE-BOUNDARY-001 | Outbox 表、幂等消费者、失败告警、契约测试 | 技术负责人 | No |
| GIS-RISK-001 | MEDIUM | GIS 图层性能与空间索引未实测 | ADR-015、DF-011 | 空间索引、简化几何、要素上限、压测；阶段 08/09 验证 | 技术负责人 | No |
| BASELINE-GAP-001 | MEDIUM | GIS 真实测绘坐标、坐标系统与底图来源未决（Q-014） | logical-erd、frontend-conventions、ADR-013 | 一期支持手工/导入 GeoJSON；Q-014 决策后按基线修订补充 | 用户/技术负责人 | No |
| BASELINE-GAP-002 | MEDIUM | 一期成功指标未定义（Q-017） | requirements-analysis、acceptance-policy | 阶段 04 路线图前由用户定义 3 个可量化指标 | 用户 | No |
| ECOM-RISK-001 | MEDIUM | 电商服务远期启用涉及支付、隐私与合规 | ADR-016、ECOMMERCE-FUTURE-001 | 启用前产品基线修订、支付安全评估、隐私影响评估 | 用户/技术负责人 | No |
| BASELINE-GAP-003 | LOW | 单机 Docker Compose 存在单点故障 | containers-and-deployment、ADR-005 | 每日备份、镜像不可变 tag、快速重建演练 | 技术负责人 | No |
| BASELINE-GAP-004 | LOW | 附件一期使用本地卷，容量与扩展受限 | ADR-011、DF-010 | 容量监控、每日备份、预留 S3 适配 | 技术负责人 | No |

## 4. 冻结结论

- 可以冻结的基线范围：产品基线核心文件、服务化架构边界与部署、数据流与逻辑 ERD、GIS/IoT 服务边界、公共 API/前端/测试契约、22 条约束注册表。
- 不允许功能提案擅自决定的事项：服务拆分与数据所有权、技术栈主版本、公共 API 错误/认证/幂等契约、IoT/GIS 数据边界、电商启用条件、测试与验收门禁、数据保留与审计规则。
- 必须在功能 Change 中细化的事项：具体 API 字段与 operationId、物理表与迁移、页面组件树与状态、GIS 图层字段与底图配置、测试用例与失败注入、电商远期实体（启用后）。
- 非阻断未决项：Q-014 GIS、Q-017 成功指标、电商启用条件；按各自阶段处理，不阻塞本次架构基线冻结。
- 批准人/日期：用户（welly，代行业务/架构/技术负责人） / 2026-11-10。
- 下次审查触发条件：服务拆分或数据所有权变化、技术栈主版本变化、公共契约破坏性变更、GIS/IoT 边界变化、电商启用、首次生产发布前。

## 5. 审计命令与证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `bash scripts/check-required-files.sh --strict` | 退出码 0 | 基线必需文件存在且无占位符 |
| `python scripts/check-requirements.py --strict` | 退出码 0 | FLOW=8、NODE=78、DO=28、RD=185、BR=9 |
| `python scripts/baseline-governance.py audit` | BASELINE_VALID | DRAFT 基线结构有效；22 条约束待批准为 ACTIVE |
| `python scripts/check-package.py` | 退出码 0 | 流程包结构与契约一致 |
| `python scripts/gen-baseline-index.py --check` | 退出码 0 | 产品基线索引最新 |

> 本报告不替代人工评审。冻结前由产品/架构/技术负责人逐项复核本报告、Manifest、Constraint Registry 与审批证据。
