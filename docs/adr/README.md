# Architecture Decision Records

- Change ID：N/A（项目级架构基线）
- 状态：DRAFT v1.0（2026-11-10 服务化架构修订；待基线审批）
- 来源基线：`docs/architecture/technology-decisions.md`
- 生成日期/版本：2026-11-10 / v1.0.0

本仓库采用单文件 ADR 索引：决策正文统一记录在 `docs/architecture/technology-decisions.md`，按 ADR ID 索引。若某决策需要独立评审或长期演进，可从本索引拆分为单独 ADR 文件。

| ADR ID | 决策 | 状态 | 日期 | 备注 |
|---|---|---|---|---|
| ADR-001 | JDK 25 + Spring Boot 4 + MyBatis + Spring Security | APPROVED | 2026-11-10 | 用户确认；阶段 08 首次构建前验证兼容性 |
| ADR-002 | Vue 3 + TypeScript + Element Plus + uni-app | APPROVED | 2026-11-10 | 用户确认；与 RA-008 一致 |
| ADR-003 | PostgreSQL 16 + PostGIS 3 + Redis 7 | APPROVED | 2026-11-10 | 用户确认；GIS 空间扩展 |
| ADR-004 | Spring Scheduler + 事务性 Outbox，暂不引入 MQ | APPROVED | 2026-11-10 | 用户确认；后续按设备量引入 MQ |
| ADR-005 | Docker Compose + 单台云服务器 + Nginx | APPROVED | 2026-11-10 | 用户确认；多服务单机运行 |
| ADR-006 | JWT + RBAC + Spring Security | APPROVED | 2026-11-10 | 用户确认；platform-service 签发 |
| ADR-007 | Maven + JUnit 5 + Testcontainers + Vitest + Playwright + GitHub Actions | APPROVED | 2026-11-10 | 用户确认 |
| ADR-008 | 无旧系统；`iot-service` 预留 MQTT/Modbus/厂商云 API 适配 | APPROVED | 2026-11-10 | 用户确认；一期模拟数据 |
| ADR-009 | 全开源组件；Java 团队；自运维 | APPROVED | 2026-11-10 | 用户确认 |
| ADR-010 | 服务化架构：platform + mes + iot + gis，电商远期预留 | APPROVED | 2026-11-10 | 用户要求主 MES/IoT/GIS/电商服务 |
| ADR-011 | 附件一期本地卷，预留 S3/MinIO 适配 | PROPOSED | 2026-11-10 | 随基线冻结批准 |
| ADR-012 | Flyway Community + expand/contract 迁移，按服务 schema | PROPOSED | 2026-11-10 | 随基线冻结批准 |
| ADR-013 | GIS 一期支持手工/导入 GeoJSON；真实测绘由 Q-014 决策 | DEFERRED | 2026-11-10 | 依赖 Q-014 |
| ADR-014 | JSON 日志 + Actuator + traceId；Prometheus/Grafana 后续 | PROPOSED | 2026-11-10 | 随基线冻结批准 |
| ADR-015 | GIS 服务：PostGIS 3 + gis-service + GeoJSON；前端 MapLibre/Leaflet | PROPOSED | 2026-11-10 | 服务已由用户确认；技术实现随基线审批 |
| ADR-016 | 电商服务远期预留，默认不部署；启用前需产品基线修订 | DEFERRED | 2026-11-10 | 用户要求预留；不改变一期范围 |
| ADR-017 | 服务间认证：用户 JWT + 服务 JWT；platform-service 签发，其他服务公钥校验 | PROPOSED | 2026-11-10 | 随基线冻结批准 |

## 决策状态说明

- APPROVED：已由用户/技术负责人确认，随基线冻结生效。
- PROPOSED：架构阶段提出，随基线审批一并批准。
- DEFERRED：依赖未决问题或远期范围，暂不作为强制约束。
- 任何状态变化必须通过基线修订流程并记录修订原因、影响与生效版本。
