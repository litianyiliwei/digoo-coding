# 技术选型决策

- Change ID：N/A（项目级架构基线）
- 状态：DRAFT v1.0（2026-11-10 服务化架构修订；待基线审批）
- 来源基线：产品基线 v0.6-DRAFT、技术选型访谈（2026-11-10）、用户 2026-11-10 架构指令、工具链报告
- 关联需求/AC：NFR-001~004、FLOW-001~008、BR-003/BR-005/BR-006
- 确认人/日期：用户（welly，代行业务/技术负责人）/ 2026-11-10
- 生成日期/版本：2026-11-10 / v1.0.0

## 1. 技术选型访谈记录

> 阶段 03 前置门禁：以下选型由用户逐项确认；候选方案与权衡一并记录。未确认项不得写成已批准决策。

| 选型项 | 用户偏好/约束 | 候选方案 | 推荐与理由 | 最终选择 | 确认人/日期 | 状态 |
|---|---|---|---|---|---|---|
| 应用架构 | 用户要求主服务类似 MES，并明确 IoT、GIS、电商服务 | 模块化单体、服务化、混合 | 主 MES 管理农业生产；IoT/GIS/电商按边界独立，避免设备、空间与交易逻辑污染 MES | `platform-service` + `mes-service` + `iot-service` + `gis-service` + `ecommerce-service`（远期） | 用户 2026-11-10 | APPROVED |
| 后端语言/框架 | 用户选择 JDK 25 + Spring Boot 4 | Spring Boot 4、NestJS、FastAPI、Go | Spring 生态成熟，RBAC、事务、调度、审计完整；团队 Java 熟悉 | JDK 25 + Spring Boot 4 + MyBatis + Spring Security | 用户 2026-11-10 | APPROVED |
| 前端框架/UI 组件库 | 用户选择 Vue 3 + Element Plus + uni-app | Vue + Element Plus、React + Ant Design、Vue + TDesign | 与 RA-008 的 Web 后台 + uniApp 移动端一致；Element Plus 后台组件覆盖度高 | Vue 3 + TypeScript + Element Plus + uni-app | 用户 2026-11-10 | APPROVED |
| 数据库与存储 | 用户选择 PostgreSQL 16 + Redis 7 | PostgreSQL、MySQL、openGauss/达梦 | PostgreSQL 复杂查询、JSON、PostGIS 空间扩展与事务能力强；Redis 做缓存与限流 | PostgreSQL 16 + PostGIS 3 + Redis 7 | 用户 2026-11-10 | APPROVED |
| 缓存/消息/任务调度 | 用户选择 Spring Scheduler，不引入 MQ | Spring Scheduler、Quartz、RabbitMQ、Kafka | 一期 <100 并发，单机调度足够；跨服务异步用 Outbox 补偿，避免 MQ 运维成本 | Redis 缓存 + Spring Scheduler + 事务性 Outbox | 用户 2026-11-10 | APPROVED |
| 部署与运行环境 | 用户选择 Docker Compose + 单台云服务器 | Docker Compose、Kubernetes、物理机、信创云 | 一期规模小，单机 Compose 成本低；多服务仍可单机运行，后续可平滑迁移 K8s | Docker Compose + 单台云服务器 + Nginx | 用户 2026-11-10 | APPROVED |
| 认证与权限 | 用户选择 JWT + RBAC + Spring Security | JWT、Session、Sa-Token、Keycloak | 无状态、适合多服务与多端；RBAC 对应 ROLE-001~006；platform-service 统一签发 | JWT + RBAC + Spring Security | 用户 2026-11-10 | APPROVED |
| GIS 服务 | 用户要求增加 GIS 服务，显示地块地理信息 | PostGIS + gis-service、GeoServer、外部地图服务 | PostGIS 与现有 PostgreSQL 同栈；gis-service 输出 GeoJSON，避免额外 GeoServer 运维；GeoServer 可按 OGC 需求后加 | PostGIS 3 + `gis-service`（Spring Boot）+ GeoJSON；前端 MapLibre/Leaflet | 用户 2026-11-10 | APPROVED |
| 电商服务 | 用户要求增加电商服务，支持后期电商功能 | 一期实现、远期预留、独立仓库 | 一期不改变 Q-004 范围；先定义服务边界与只读契约，远期启用前做产品基线修订 | `ecommerce-service` 远期预留，默认不部署 | 用户 2026-11-10 | DEFERRED |
| 构建/测试/CI | 用户选择 Maven + JUnit5 + GitHub Actions | Maven/Gradle、JUnit/Testcontainers、GitHub/GitLab/Jenkins | Maven 稳定；Testcontainers 保证真实 PostgreSQL/PostGIS/Redis；GitHub Actions 托管成本低 | Maven + JUnit 5 + Testcontainers + Vitest + Playwright + GitHub Actions | 用户 2026-11-10 | APPROVED |
| 既有系统集成 | 用户选择无旧系统，预留设备适配层 | MQTT、Modbus、厂商云 API、暂不预留 | 一期模拟数据；IoT 服务隔离协议变化，真实设备后续接入 | 无旧系统；`iot-service` 预留 MQTT/Modbus/厂商云 API 适配 | 用户 2026-11-10 | APPROVED |
| 许可/成本/团队/运维 | 用户选择全开源、Java 团队、自运维 | 全开源、商业许可、信创、托管云 | 无许可费用；团队 Java 熟悉；多服务单机自运维成本可控 | 全开源组件；Java 团队；自运维 | 用户 2026-11-10 | APPROVED |

## 2. 决策表

| 决策 ID | 领域 | 候选方案 | 评价维度 | 选择与理由 | 代价/退出策略 | 用户确认 | 状态/审批 |
|---|---|---|---|---|---|---|---|
| ADR-001 | 后端 | Spring Boot 4、NestJS、FastAPI、Go | 团队、稳定性、事务、安全 | JDK 25 + Spring Boot 4 + MyBatis + Spring Security；企业级 RBAC 与事务完整 | Spring Boot 4 较新，需在阶段 08 首次构建前验证 MyBatis/Spring Security 兼容；必要时回退 Spring Boot 3.5 LTS | 用户 2026-11-10 | APPROVED |
| ADR-002 | 前端 | Vue + Element Plus、React + Ant Design、Vue + TDesign | 组件覆盖、多端、团队 | Vue 3 + TypeScript + Element Plus + uni-app；符合 RA-008 | 需统一 Web 与移动端设计令牌；uni-app 平台差异在阶段 07 细化 | 用户 2026-11-10 | APPROVED |
| ADR-003 | 数据库 | PostgreSQL、MySQL、openGauss/达梦 | 查询能力、扩展、运维 | PostgreSQL 16 + PostGIS 3；复杂查询、空间扩展与事务能力强 | 需团队熟悉 PostgreSQL/PostGIS 运维；空间索引与备份策略在部署阶段落地 | 用户 2026-11-10 | APPROVED |
| ADR-004 | 缓存/调度 | Redis + Spring Scheduler、RabbitMQ、Kafka | 复杂度、容量、可靠性 | Redis 7 + Spring Scheduler；一期规模无需 MQ | 跨服务异步用 Outbox；后续设备量增大再引入 MQ | 用户 2026-11-10 | APPROVED |
| ADR-005 | 部署 | Docker Compose、Kubernetes、物理机、信创云 | 成本、弹性、运维 | Docker Compose + 单台云服务器 + Nginx；多服务单机运行 | 单点故障；通过备份与快速重建缓解，后续可迁 K8s | 用户 2026-11-10 | APPROVED |
| ADR-006 | 认证 | JWT、Session、Sa-Token、Keycloak | 多端、无状态、生态 | JWT + RBAC + Spring Security；platform-service 签发 | JWT 撤销需黑名单或短 TTL；敏感操作二次校验 | 用户 2026-11-10 | APPROVED |
| ADR-007 | 构建/CI | Maven/Gradle、JUnit/Testcontainers、GitHub/GitLab/Jenkins | 稳定性、真实依赖、托管成本 | Maven + JUnit 5 + Testcontainers + Vitest + Playwright + GitHub Actions | GitHub Actions 依赖网络；关键门禁本地可复跑 | 用户 2026-11-10 | APPROVED |
| ADR-008 | 集成 | MQTT、Modbus、厂商云 API、暂不预留 | 协议隔离、后续扩展 | 无旧系统；`iot-service` 预留设备适配层，模拟数据起步 | 适配层增加抽象成本；真实设备接入前需协议验证 | 用户 2026-11-10 | APPROVED |
| ADR-009 | 许可/运维 | 全开源、商业许可、信创、托管云 | 成本、合规、运维 | 全开源 + Java 团队 + 自运维 | 无商业支持；关键组件需锁定版本与升级窗口 | 用户 2026-11-10 | APPROVED |
| ADR-010 | 应用架构 | 模块化单体、服务化、混合 | 复杂度、事务、部署、边界 | 服务化：platform + mes + iot + gis；ecommerce 远期预留；主服务为农业 MES | 多服务运维与分布式一致性成本上升；用 Outbox、契约测试、健康检查缓解 | 用户 2026-11-10 | APPROVED |
| ADR-011 | 附件存储 | 本地卷、MinIO/S3、数据库大字段 | 成本、扩展、备份 | 一期本地卷 + 存储接口；预留 S3/MinIO 适配 | 单机卷容量有限；后续按附件量切换 | 随基线审批 | PROPOSED |
| ADR-012 | 数据库迁移 | Flyway、Liquibase、手工 SQL | 可重复、回滚、团队 | Flyway Community + expand/contract；按服务 schema 迁移 | 迁移只前进不回滚；需在预发演练 | 随基线审批 | PROPOSED |
| ADR-013 | GIS 数据策略 | 示意层、真实测绘、外部地图服务 | 成本、精度、合规 | 一期支持手工绘制/导入 GeoJSON；真实测绘坐标与底图来源由 Q-014 决策 | 地图精度有限；不影响 MES 核心生产与溯源 | 未决（Q-014） | DEFERRED |
| ADR-014 | 可观测性 | 结构化日志 + Actuator、Prometheus/Grafana、APM | 成本、排障 | 一期 JSON 日志 + Actuator + traceId；Prometheus/Grafana 后续可选 | 缺少指标可视化；后续按运维需要增强 | 随基线审批 | PROPOSED |
| ADR-015 | GIS 服务 | PostGIS + gis-service、GeoServer、外部地图服务 | 运维、标准、扩展 | PostGIS 3 + `gis-service`（Spring Boot）+ GeoJSON；前端 MapLibre/Leaflet；GeoServer 按 OGC 需求后加 | 自研 GIS API 需维护空间查询与图层契约；OGC WMS/WFS 需求出现时增加 GeoServer | 随基线审批 | PROPOSED |
| ADR-016 | 电商服务 | 一期实现、远期预留、独立仓库 | 范围、合规、运维 | `ecommerce-service` 远期预留，默认不部署；只消费 MES 溯源只读数据 | 启用前需产品基线修订（Q-004 重评）、支付/隐私合规与独立 schema | 用户 2026-11-10 | DEFERRED |
| ADR-017 | 服务间认证 | 服务 JWT、mTLS、共享密钥 | 安全、运维、复杂度 | 用户 JWT + 服务 JWT；platform-service 签发，其他服务公钥校验；服务间不透传用户令牌 | 需管理服务密钥与轮换；mTLS 作为后续增强 | 随基线审批 | PROPOSED |

## 3. 选型风险与验证点

| 风险 ID | 风险 | 影响 | 验证/缓解 | 负责人 | 到期 |
|---|---|---|---|---|---|
| TECH-RISK-001 | Spring Boot 4 与 MyBatis、Spring Security 的 starter 兼容性需实测 | 首次构建失败或 API 不兼容 | 阶段 08 首个任务前做最小构建验证；必要时回退 Spring Boot 3.5 LTS 并走基线修订 | 技术负责人 | 阶段 08 开始前 |
| TECH-RISK-002 | JDK 25 与部分构建插件/静态分析工具兼容性 | 构建或扫描失败 | CI 固定 JDK 25，验证 Maven 插件与 Testcontainers | 技术负责人 | 阶段 08 开始前 |
| TECH-RISK-003 | 多服务单机部署增加运维与启动复杂度 | 发布/排障成本上升 | Docker Compose healthcheck、启动顺序、统一日志与 traceId；阶段 10 前演练 | 技术负责人 | 阶段 10 前 |
| TECH-RISK-004 | 跨服务一致性依赖 Outbox 与重试 | 事件丢失或重复 | Outbox 表、幂等消费者、失败告警；契约测试覆盖 | 技术负责人 | 阶段 08 前 |
| TECH-RISK-005 | GIS 图层性能与 PostGIS 空间索引 | 大地块/大范围查询超时 | 空间索引、简化几何、要素上限、分页；压测 | 技术负责人 | 阶段 08/09 |
| TECH-RISK-006 | 电商服务启用涉及支付、隐私与合规 | 合规风险与返工 | 启动前产品基线修订、支付安全评估、隐私影响评估 | 用户/技术负责人 | 电商启用前 |
| TECH-RISK-007 | 本地附件卷容量与备份 | 附件丢失或磁盘满 | 容量监控、每日备份、预留 S3 适配 | 技术负责人 | 阶段 10 前 |

## 4. 未决项

- Q-014：GIS 真实测绘坐标、坐标系统与底图来源未决；本基线承诺 GIS 服务与 GeoJSON 展示，不承诺法定测绘精度。
- Q-017：一期成功指标未定义；不影响技术选型，但影响阶段 04 路线图优先级与阶段 10 验收口径。
- Q-004（远期）：电商服务启用前必须重评“一期不含销售/商城”的范围决定，并新增电商 DO 与产品基线。
- 上述未决项登记在 `docs/product/open-questions.md`，不得在本基线中自行关闭。

## 5. 状态与审批

- 当前状态：DRAFT v1.0；ADR-001~010 已由用户确认，ADR-011/012/014/015/017 随基线审批，ADR-013/016 为 DEFERRED。
- 冻结后技术选型或服务拆分变化必须走基线修订流程，并在 ADR 中记录原因、代价与退出策略。
