# 基线常驻简报（Agent 入口）

- Change ID：N/A（项目级）
- 状态：DRAFT（阶段 02 新契约产物已生成，待产品负责人批准）
- 来源基线：需求 v0.5（APPROVED 2026-11-05）、原型评审记录（2026-11-05）、阶段 02 节点级重跑（2026-11-09）
- 关联需求/AC：FLOW/NODE/DO/BR/TERM/DEC/ASM ID
- 生成日期/版本：2026-11-09 / 产品基线 v0.6-DRAFT

> 本文件是阶段 02–05 的常驻上下文入口，控制在一页以内。详细内容按“读取顺序”按需加载，不把整包基线塞入上下文。

## 1. 目标与非目标

- 产品目标：以农业生产管理为主线，实现生产计划、任务派工、作业留痕、批次质检与溯源；环境监测与设备控制作为支撑能力（RA-011）。
- 业务范围：种植、畜牧、水产全覆盖（Q-006），含政府监管端（Q-001）。
- 明确不做：销售/商城、土地认养、消费者反馈互动（Q-004）；消费者扫码溯源查询保留。
- 成功标准：PENDING（见 [open-questions.md](open-questions.md) Q-017；需用户定义环境数据上线率、农事记录覆盖率、扫码查询次数等指标）。

## 2. 角色与权限

| 角色 ID | 角色 | 核心能力 | 数据范围 | 访问级别 |
|---|---|---|---|---|
| ROLE-001 | 系统管理员 | 用户、角色、权限、审计 | 全系统 | READ_WRITE |
| ROLE-002 | 农场管理员 | 计划、任务、审核、溯源、预警配置、设备 | 本农场 | READ_WRITE |
| ROLE-003 | 作业人员（种植员/养殖员） | 任务执行、作业记录、环境查看 | 本人任务与授权地块 | READ_WRITE |
| ROLE-004 | 采购员 | 农资采购入库、库存台账 | 本农场农资 | READ_WRITE |
| ROLE-005 | 消费者 | 扫码查询溯源信息 | 批次公开信息 | READ |
| ROLE-006 | 政府监管人员 | 辖区汇总看板、只读下钻 | 辖区汇总 | READ |

完整矩阵见 [role-permission-matrix.csv](role-permission-matrix.csv)；权限语义以 BR-005 为准。

## 3. 核心数据对象与不变量

`data-objects.csv` 已登记 28 个业务数据对象；核心对象包括地块、品种、生产计划、农事模板、农事任务、作业记录、农资与库存、生产批次、检测报告、溯源码、用户与角色、审计日志、监管汇总。以下为已确认的业务不变量：

| 不变量 | 来源 |
|---|---|
| 生产批次是溯源核心单元，必须可关联计划、地块/塘口、投入品、作业与质检记录 | BR-009 |
| 一批次一码，溯源码全局唯一、不可重复生成 | BR-001 |
| 未上传检测报告的批次不得生成溯源码 | BR-002 |
| 农资消耗必须关联地块/批次并扣减库存 | BR-007 |
| 农事任务必须有可追溯来源（计划/模板/临时任务） | BR-008 |
| 设备远程控制指令必须记录操作人、时间、指令与结果，不可删除 | BR-003 |
| 预警阈值修改必须留痕 | BR-004 |
| 用户只能访问职责范围内的功能与数据 | BR-005 |
| 传感器历史、作业记录与扫码数据保留 2 年 | BR-006 |

## 4. 硬规则（MUST / PROHIBITED 摘要）

| BR ID | 规则摘要 | 等级 |
|---|---|---|
| BR-001 | 一批次一码，全局唯一 | MUST |
| BR-002 | 溯源前必须有检测报告 | MUST |
| BR-003 | 设备控制指令可审计不可删除 | MUST |
| BR-004 | 预警阈值配置留痕 | MUST |
| BR-005 | RBAC + 职责范围内数据访问 | MUST |
| BR-006 | 数据保留 2 年 | MUST |
| BR-007 | 农资使用关联地块/批次并扣减库存 | MUST |
| BR-008 | 农事任务来源可追溯 | MUST |
| BR-009 | 批次可正向/反向追溯 | MUST |

完整规则、例外与执行方式见 [business-rules.md](business-rules.md)。

## 5. 核心术语

| TERM ID | 术语 | 一句话定义 |
|---|---|---|
| TERM-001 | 地块 | 种植或养殖的空间单元总称 |
| TERM-007 | 茬口 | 种植生产周期 |
| TERM-009 | 生产计划 | 品种+地块+周期+目标产量的计划单元 |
| TERM-010 | 农事模板 | 按品种与生长阶段组织的标准作业与投入品清单 |
| TERM-011 | 农事任务 | 派发给责任人的作业单 |
| TERM-012 | 作业记录 | 作业执行后提交的事实记录 |
| TERM-013 | 生产批次 | 采收/出栏形成的溯源核心单元 |
| TERM-014 | 溯源码 | 批次对应的唯一编码 |
| TERM-016 | 农资 | 肥料、农药、饲料、耗材等投入品 |
| TERM-017 | 预警 | 环境指标超阈值产生的通知记录 |

完整术语与禁用词见 [glossary.md](glossary.md)。

## 6. Change 切片与完成定义

- 一个 Change 只做一个可独立验收的业务能力；优先纵向切片。
- 禁止在同一 Change 内顺手改公共契约/共享模型；需要时先走基线变更。
- 完成定义（DoD）见 [change-sizing.md](change-sizing.md)；所有 Change 必须逐项核对。

## 7. 阻塞问题与阶段 02 缺口

| 类型 | ID | 内容 | 阻塞范围 | 负责人/到期 |
|---|---|---|---|---|
| 基线缺口 | 已关闭 | `workflows.md` 已补齐 78 个 NODE，`data-objects.csv` 28 个 DO，`rd-matrix.csv` 185 条 RD；`check-requirements.py --strict` 通过 | N/A | 阶段 02 产物负责人 |
| Q | Q-017 | 一期成功指标未定义 | 阶段 04 路线图 | 用户 |
| Q | Q-014 | GIS 地块几何数据源与图层范围 | 阶段 03 前 | 用户/技术负责人 |
| Q | Q-015 | 采购员/系统管理员角色外壳变体 | 阶段 06 前 | 用户 |
| Q | Q-016 | 原型缺口 D-01~D-12 补齐阶段 | 阶段 06 前 | 用户/设计负责人 |
| ASM | ASM-001 | 传统农业管理依赖人工经验与纸质记录 | 业务目标验证 | 用户 |
| ASM | ASM-003 | GIS 示意地图不要求真实坐标 | 阶段 03 | 用户/技术负责人 |

完整清单见 [open-questions.md](open-questions.md)、[assumptions.md](assumptions.md)。

## 8. 读取顺序与上下文预算

1. 本简报（≤1 页）。
2. [role-permission-matrix.csv](role-permission-matrix.csv) 与 [id-conventions.md](id-conventions.md)。
3. 本 Change 命中的 FLOW 节点表与相关 RD 行。
4. [decisions.md](decisions.md)、[assumptions.md](assumptions.md)、[open-questions.md](open-questions.md)。
5. 仅在需要时读取 `workflows.md` 全文、`data-objects.csv` 全量、[lessons.md](lessons.md)。
6. 架构/数据/公共契约基线按 [BASELINE-FEATURE-INTERACTION.md](../BASELINE-FEATURE-INTERACTION.md) 的影响面读取。

## 9. 基线状态与版本

- 产品基线版本：v0.6-DRAFT（需求 v0.5 已批准；阶段 02 新契约产物已生成，待批准）
- 冻结状态：DRAFT
- 索引：[BASELINE-INDEX.md](BASELINE-INDEX.md)（由 `scripts/gen-baseline-index.py` 生成）
- 变更方式：只通过基线修订流程；功能 Change 不直接改本文件
