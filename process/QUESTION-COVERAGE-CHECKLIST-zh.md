# 阶段问题覆盖清单（02 / 03 / 05 / 07）

> Language: [English](QUESTION-COVERAGE-CHECKLIST.md) | 简体中文

> 状态：RECOMMENDED（阶段提问辅助；不是硬门禁；证据块可选）
> Change ID：N/A（过程文档）
> 适用范围：02 需求业务分析、03 项目总体架构设计、05 提案级需求分析、07 详细设计/接口/测试设计
> 关联需求/AC：N/A（过程文档）
> 依据：`process/STEP-ARTIFACT-CONTRACTS.md`、`process/STEP-ARTIFACT-CONTRACTS.json`、`prompts/02-requirements-analysis.md`、`prompts/03-project-architecture-baseline.md`、`prompts/05-feature-requirements.md`、`prompts/07-detailed-design.md`，以及 `.claude/skills/` 下的同名 Skill
> 生成日期：2026-11-18

## 1. 用途与用法

本清单把“下游阶段需要什么”转成按阶段的问题列表。它是阶段执行和评审的工作清单，不是机器门禁：阶段自行判断哪些条目适用，不要求逐项记录。

用法：

1. 阶段开始时浏览当前阶段的表格，挑选真正影响本项目/Change 的问题。
2. 用建议问句准备访谈；确实不适用的条目直接跳过，不必生产“不适用”合规行。
3. 答案写入声明的工件章节；未知或未确认项写入 `docs/product/open-questions.md`，并写 owner 和阻塞条件。
4. 阶段结束时检查下游消费问题：**下一阶段能不能在不追问用户的情况下完成它声明的工件？**
5. 如需记录覆盖情况，可以在证据中加入可选的 `question_coverage` 块；它做形状校验，不要求固定条目列表。

当阶段记录 `question_coverage` 时，使用以下状态词表：

| 状态 | 含义 | 必须记录 |
|---|---|---|
| `已答` | 有真实答案 | 答案摘要、来源、落点 |
| `不适用` | 确实不适用 | 原因 |
| `待确认` | 答案未知或未确认 | owner、阻塞条件、开放问题文件 |
| `延后` | 有意推迟 | 原因、批准人、目标阶段/Change |

## 2. 当前覆盖快照

图例：`Q` = 当前 Prompt/Skill 里有明确问询；`F` = 有模板字段或输出，但没有问询或硬校验；`-` = 既无问询也无字段。这张表是诊断快照，不是目标状态。

| ID | 信息主线 | 02 | 03 | 05 | 07 |
|---|---|---|---|---|---|
| T01 | 目标、范围、成功指标 | Q | F | Q | F |
| T02 | 规模与容量 | - | - | - | - |
| T03 | 组织、角色、权限、审批链 | F | F | Q | Q |
| T04 | 流程、异常、补偿 | Q | Q | Q | Q |
| T05 | 数据对象、规则、编码、单位 | Q | Q | F | Q |
| T06 | 数据生命周期、隐私、合规 | F | F | - | F |
| T07 | 外部系统、设备、终端、离线 | F | Q | Q | Q |
| T08 | 报表、打印、导出、追溯凭证 | - | - | - | - |
| T09 | 非功能需求 | F | F | - | F |
| T10 | 迁移、兼容、回滚 | F | F | - | F |
| T11 | 验收、试点、UAT、培训 | F | F | F | F |
| T12 | 运行、发布、监控、运维、灾备 | - | F | - | F |
| T13 | 负责人与 RACI | - | F | - | - |
| T14 | 业务日历、季节、时限 | F | - | - | - |
| T15 | 测试策略、环境、数据、替身 | - | Q | F | Q |
| T16 | 参考产品、能力/模块归属与偏差确认 | Q | F | F | F |
| T17 | 实现切片/模块 footprint 与 UI 控件动作映射 | - | - | - | Q |

最明显的断线是 T02（规模与容量）、T06（数据生命周期与隐私）、T08（报表与打印）、T09（NFR）、T10（迁移）、T11（验收）、T13（负责人/RACI）、T14（业务日历）。这些主线目前没有任何一个阶段从头到尾负责。

## 3. 各阶段清单

### 3.1 02 需求业务分析

| ID | 必须问清 | 建议问句 | 工件落点 | 下游消费者 | 状态 |
|---|---|---|---|---|---|
| 02-T01-01 | 目标、范围、非目标、KPI 基线与目标 | 项目目标是什么，首期范围是什么，明确不做什么，用什么可量化基线和目标定义成功？ | `docs/product/requirements-analysis.md` §1；`BASELINE-BRIEF.md` | 03 系统上下文；04 切片；05 AC；10 验收 | [ ] |
| 02-T02-01 | 规模与量级 | 多少用户和角色、并发多少、多少农场/地块/大棚、多少设备、多少批次/记录、日均和峰值业务量、数据增长和保留年限是多少？ | `requirements-analysis.md` §6 NFR；`data-objects.csv`；`change-sizing.md` | 03 容量/部署；04 切片大小；07 索引/分页；08 压测 | [ ] |
| 02-T03-01 | 组织、角色、权限、审批链 | 组织层级是什么（公司/合作社/基地/农户），谁给谁审批，谁能看谁的数据，是否需要代操作和职责分离？ | `role-permission-matrix.csv`；`business-rules.md`；`rd-matrix.csv` | 03 身份模型；05 权限 AC；06 页面可见性；07 权限设计 | [ ] |
| 02-T04-01 | 流程与节点完整性 | 每个主流程、分支流程、异常流程、补偿流程是否都拆成可执行节点，并包含角色、输入/输出 DO、前置条件、动作、分支和下一节点？ | `workflows.md`；`rd-matrix.csv` | 03 数据流；05 场景；07 错误/补偿设计 | [ ] |
| 02-T04-02 | 人工接管、纠错、回滚权限 | 人工接管、纠错、回滚时谁有权操作，留什么审计，通知谁？ | `workflows.md` 异常节点；`business-rules.md`；`open-questions.md` | 03 审计/控制；05 异常 AC；07 审计/错误设计 | [ ] |
| 02-T05-01 | 业务键、编码、单位、术语 | 地块、批次、品种、农药/肥料等业务键和编号规则是什么，使用什么计量单位、精度、状态字典、同义词或方言？ | `data-objects.csv`；`glossary.md`；`id-conventions.md`；`business-rules.md` | 06 文案/术语；07 数据模型/API | [ ] |
| 02-T06-01 | 数据生命周期、隐私、保留 | 数据从哪里来、归谁所有、保留多久、何时归档/删除/导出、是否有法务保留、哪些字段属于个人或敏感数据？ | `business-rules.md`；`data-objects.csv`；NFR 表；`open-questions.md` | 03 数据治理；05 隐私 AC；07 脱敏/保留 | [ ] |
| 02-T07-01 | 外部系统与第三方清单 | 需要哪些外部系统、监管/追溯平台、天气/地图/支付/短信/微信/ERP/物流服务，目的、数据流向、账号/沙箱、SLA、审批和隐私条款是什么？ | `requirements-analysis.md` §6/§7；`reference-research.md`；`open-questions.md` | 03 第三方清单；05 场景；07 接口目录 | [ ] |
| 02-T07-02 | 现场终端、网络、离线、设备 | 现场使用什么终端（手机/PDA/平板/PC），有没有网络，是否需要离线作业，是否需要扫码/拍照/GPS/称重/打印？ | `workflows.md` 节点输入；`requirements-analysis.md`；NFR 表 | 03 平台；06 交互；07 接口 | [ ] |
| 02-T08-01 | 报表、台账、凭证、导出、打印 | 需要哪些报表、台账、追溯凭证或监管报送，维度、频率、导出格式、打印/签字/二维码要求是什么？ | `requirements-analysis.md`；`workflows.md`；`acceptance-policy.md` | 06 打印布局；07 IO/导出；08/10 验收 | [ ] |
| 02-T09-01 | 量化 NFR 目标 | 性能、可用性、RPO/RTO、离线容忍、安全、隐私、审计保留、可访问性、合规（等保/信创/行业法规）的量化目标是什么？ | `requirements-analysis.md` §6 NFR 表 | 03 约束；05 NFR AC；07 NFR 测试；08/09 验证 | [ ] |
| 02-T10-01 | 旧数据来源、数量、质量、迁移 | 旧数据有哪些（纸/Excel/旧系统）、有多少、有多脏、谁清洗、怎么迁移、双跑多久、旧系统何时停？ | `workflows.md`；`requirements-analysis.md` §7；`open-questions.md` | 03 迁移；04 依赖；07 backfill；08 割接 | [ ] |
| 02-T11-01 | 验收、试点、培训 | 谁验收、用哪些场景/数据、在哪个基地/哪些用户试点、上线后谁培训和谁支持？ | `acceptance-policy.md` | 04 验收方向；05 验证；10 验收 | [ ] |
| 02-T13-01 | 负责人、审批人、RACI | 业务/产品/技术/设计/验收 owner 和审批人是谁，决策 SLA 是什么？ | `decisions.md`；`BASELINE-BRIEF.md`；`open-questions.md` | 所有阶段审批门 | [ ] |
| 02-T14-01 | 业务日历、季节、时限 | 种植/收获/加工/销售窗口、安全间隔期、监管申报截止、节假日和禁期是什么？ | `business-rules.md`；`acceptance-policy.md`；`change-sizing.md` | 04 排序；05 时间窗 AC；07 调度；08 测试数据 | [ ] |
| 02-T15-01 | 测试与验收输入 | 有哪些环境、真实设备、第三方沙箱和样本数据可用于验收和测试？ | `acceptance-policy.md`；`open-questions.md` | 03 测试策略；07 测试设计；08 执行 | [ ] |
| 02-T16-01 | 同类产品与重大偏差 | 有哪些同类/竞品产品，它们的流程/角色/数据对象/规则是什么样的，本项目在哪些关键点偏差过大，每个重大偏差是否已由用户确认（确认人+日期）？ | `docs/product/reference-research.md` §9（同类产品偏差确认）；`open-questions.md` | 03 边界；05 场景；07 设计 | [ ] |

### 3.2 03 项目总体架构设计

| ID | 必须问清 | 建议问句 | 工件落点 | 下游消费者 | 状态 |
|---|---|---|---|---|---|
| 03-T01-01 | 架构目标与 02 对齐 | 哪些业务目标和成功指标必须由架构保持，哪些质量目标必须冻结为基线约束？ | `system-context.md`；`technology-decisions.md`；`constraint-registry.json` | 04 切片；05 基线影响；07 设计约束 | [ ] |
| 03-T02-01 | 容量、HA/DR、RPO/RTO | 预计容量、并发、峰值、增长和保留量是多少，由此得出什么 HA/DR、RPO 和 RTO 目标？ | `containers-and-deployment.md`；`constraint-registry.json`；`test-strategy.md` | 05 NFR AC；07 索引/容量；08 压测；10 运维验收 | [ ] |
| 03-T02-02 | 性能、可用性、SLO | 性能/可用性/SLO 的量化目标是什么，每项如何验证？ | `technology-decisions.md`；`constraint-registry.json`；`test-strategy.md` | 05 AC；07 测试；08/09 验证 | [ ] |
| 03-T03-01 | 身份与授权模型 | 使用哪些认证方式（SSO/AD/LDAP/微信/短信），授权模型是 RBAC 还是 ABAC，是否多租户隔离，账号生命周期、MFA、会话规则是什么？ | `technology-decisions.md`；`api-conventions.md`；`constraint-registry.json` | 05 权限 AC；06 页面可见性；07 权限设计 | [ ] |
| 03-T04-01 | 数据流、事件、补偿 | DF 是否覆盖所有 FLOW/NODE/DO/RD，是否包含同步/异步、事务边界、失败、补偿、顺序、DLQ 和重放语义？ | `data-flows.md`；`api-conventions.md` | 05 场景；07 接口/错误设计；08 实现 | [ ] |
| 03-T05-01 | 领域模型、数据所有权、约定 | 领域边界、实体、生命周期、所有权、逻辑 ERD 是否覆盖所有 DO，命名、ID、审计字段、时间、删除、并发版本和保留约定是否明确？ | `domain-boundaries.md`；`logical-erd.md`；`constraint-registry.json` | 05 DO 引用；07 数据模型/API | [ ] |
| 03-T06-01 | 数据分类、隐私、合规 | 数据分类（公开/内部/敏感/PII）是什么，传输/静态加密、密钥管理、脱敏、保留、删除/导出、法务保留、跨境规则是什么？ | `technology-decisions.md`；`constraint-registry.json`；`api-conventions.md` | 05 隐私 AC；07 脱敏/保留；08/09 审计 | [ ] |
| 03-T07-01 | 平台与集成边界清单 | 客户端形态、跨平台方案、原生插件/JS Bridge、设备/IoT 协议、第三方平台、每个接口边界是否都登记了协议、认证、契约、错误、超时/重试/幂等、版本、测试和 owner？ | `technology-decisions.md`；`api-conventions.md`；`frontend-conventions.md`；`data-flows.md`；`constraint-registry.json` | 05 场景；06 设计；07 接口目录；08 实现 | [ ] |
| 03-T07-02 | 离线、降级、推送、深链 | 离线缓存、同步冲突、权限拒绝/降级、推送/深链、热更新和应用商店合规规则是什么？ | `frontend-conventions.md`；`data-flows.md` | 05 离线 AC；06 交互；07 前端/原生设计 | [ ] |
| 03-T08-01 | 报表、BI、打印、导出、读模型 | 报表/BI/打印/导出/读模型是否在本期，数据来源、刷新频率、权限和导出格式是什么？ | `system-context.md`；`containers-and-deployment.md`；`api-conventions.md`；`data-flows.md` | 05 报表 AC；06 打印布局；07 IO/导出设计 | [ ] |
| 03-T09-01 | NFR 冻结为可验证约束 | 所有 NFR 是否量化为可验证约束，每项是否有 owner、验证方法和证据路径？ | `constraint-registry.json`；`test-strategy.md` | 05 NFR AC；07 NFR 测试；08/09 验证 | [ ] |
| 03-T09-02 | 静态分析采用决策与工具链 | 本项目是否采用静态分析门禁？不采用时记录决策与原因。采用时，每个选定语言选用哪些静态分析工具（lint/format/type/style），版本如何锁定，插件/包清单、配置落点、blocking 严重度与零问题策略是什么，豁免政策（Change 级文件、审批人、过期）是什么？从零仓库能否离线运行（不拉取依赖包）？ | `technology-decisions.md` `## Static Analysis Toolchain`；`test-strategy.md` `## Static Analysis and Quality Gates`；`docs/architecture/quality-gates.json`（采用时）；`constraint-registry.json` `QUALITY-STATIC-001`（采用时 ACTIVE，否则 RETIRED） | 05 适用约束；07 配置/豁免计划；08 门禁；09 独立重跑；10 验收 | [ ] |
| 03-T10-01 | 旧系统迁移与共存 | 旧数据迁移、双跑、割接、停旧和回滚策略是什么，新旧系统边界和共存期是什么？ | `technology-decisions.md`；`containers-and-deployment.md`；`data-flows.md`；`constraint-registry.json` | 04 依赖；05 迁移 AC；07 backfill；08 割接 | [ ] |
| 03-T11-01 | 测试策略与测试输入 | 测试层级、契约/集成/E2E/性能/安全/UAT 策略是什么，谁提供环境、真实设备、第三方沙箱和测试数据？ | `test-strategy.md`；`docs/project/toolchain-report.md` | 05 验证；07 测试设计；08 执行 | [ ] |
| 03-T12-01 | 环境、发布、可观测性、灾备 | dev/test/staging/prod 拓扑、网络分区、域名/证书/VPN、发布/回滚/灰度/开关、DB 迁移策略、日志/指标/追踪/告警/SLO/值班/runbook、备份/灾备是什么？ | `containers-and-deployment.md`；`test-strategy.md`；`constraint-registry.json` | 07 配置/发布；08 实现；10 验收环境 | [ ] |
| 03-T13-01 | 基线 owner 与审批 | 每个基线域（产品/架构/数据/API/前端/测试）的 owner 和 approver 是谁，约束级别、例外流程和审批证据是什么？ | `baseline-manifest.json`；`constraint-registry.json`；`baseline-status.md` | 04/05 基线门禁；07/08/09/10 约束检查 | [ ] |
| 03-T14-01 | 批处理与调度窗口 | 批处理/定时任务/报表生成的窗口和 SLA 是什么，与业务日历和监管截止日有什么关系？ | `containers-and-deployment.md`；`data-flows.md`；`test-strategy.md` | 05 时间窗 AC；07 调度；08 测试数据 | [ ] |

### 3.3 05 提案级需求分析

| ID | 必须问清 | 建议问句 | 工件落点 | 下游消费者 | 状态 |
|---|---|---|---|---|---|
| 05-T01-01 | Change 价值、范围、非目标、成功指标 | 本 Change 交付什么价值，明确不做什么，怎么衡量成功，哪些 AC 阻塞验收、哪些可以延后？ | `proposal.md`；`design/user-stories.md`；`change-sizing.md` | 06 页面范围；07 设计；10 验收 | [ ] |
| 05-T03-01 | 角色、能力、数据范围、降级 | 本 Change 涉及哪些 ROLE/CAP/数据范围，无权限、降级、代操作、脱敏时用户看到什么？ | `design/user-stories.md` AC；`specs/<capability>/spec.md` Scenario；`baseline-impact.md` | 06 页面可见性；07 权限设计；09 验证 | [ ] |
| 05-T04-01 | US 与场景完整性 | 每个用户故事是否包含触发、角色、前置、主/备/异常路径、后置和关联 FLOW/NODE/DO/BR，每条关键路径是否有 Given/When/Then？ | `design/user-stories.md`；`specs/<capability>/spec.md` Scenario | 06 页面；07 测试；09 验证 | [ ] |
| 05-T05-01 | 字段级规则 | 每个字段或数据对象的校验、计算、单位、精度、状态转换、唯一性、重复提交和并发规则是什么？ | `specs/<capability>/spec.md` Scenario；`design/user-stories.md` AC；`business-rules.md` | 07 数据模型/API；08 实现 | [ ] |
| 05-T06-01 | PII 与数据生命周期行为 | 本 Change 涉及哪些 PII/敏感字段，保留、删除、导出和审计的可观察行为是什么？ | `specs/<capability>/spec.md` Scenario；AC；`baseline-impact.md` | 07 脱敏/保留；08/09 审计 | [ ] |
| 05-T07-01 | 多端、离线、第三方失败 | 多平台、设备、离线/弱网、推送/深链、第三方失败/超时/限流/降级、人工兜底的可观察行为是什么？ | `specs/<capability>/spec.md` Scenario；AC | 06 状态；07 接口/错误设计；08 测试 | [ ] |
| 05-T08-01 | 报表、打印、导出、凭证 | 本 Change 是否产出报表、打印、导出或追溯凭证，AC 是什么？ | `specs/<capability>/spec.md` Scenario；AC | 06 打印布局；07 IO/导出；10 验收 | [ ] |
| 05-T09-01 | NFR 转成验收 | 本 Change 承接哪些 NFR，什么阈值、证据、环境和验收方式使每项可验证？ | AC；`baseline-binding.json`；`acceptance-policy.md` | 07 NFR 测试；08/09 验证 | [ ] |
| 05-T10-01 | 迁移、兼容、回滚 | 本 Change 是否涉及旧数据、旧接口、旧页面，迁移正确性、双跑、回滚、向后兼容的 AC 是什么？ | AC；`baseline-impact.md`；`proposal.md` Impact | 07 backfill；08 割接 | [ ] |
| 05-T11-01 | AC 验证与验收输入 | 每条 AC 的验证方式、环境、数据、验收人是什么，谁提供试点用户和验收数据？ | `design/user-stories.md` AC；`acceptance-policy.md`；`traceability.csv` | 07 测试设计；09 验证；10 验收 | [ ] |
| 05-T14-01 | 业务日历 AC | 本 Change 是否受种植/收获/销售窗口、安全间隔期或监管截止日约束，对应的时间窗 AC 是什么？ | AC；`proposal.md`；`change-sizing.md` | 07 调度；08 测试数据 | [ ] |
| 05-T15-01 | 可测试性输入 | 需要哪些测试数据、替身、真实设备和沙箱，每条 AC 是否可观察、可断言？ | `specs/<capability>/spec.md` Scenario；AC；`test-cases.csv`（07） | 07 测试设计；08 执行 | [ ] |
| 05-T13-01 | Change 负责人与开放项 owner | 本 Change 的产品 owner、技术 owner、验收人是谁，每个开放问题由谁关闭？ | `proposal.md`；`decisions.md`；`open-questions.md` | 06/07/08/09/10 审批 | [ ] |
| 05-T16-01 | 能力、归属模块、关联模块与迟到提案修订 | 本 Change 交付哪个能力，由哪个模块拥有，涉及哪些关联/共享模块？两个注册表是否已更新，使归属模块列出该能力、owner/related slug 均存在，且 `partial` 切片声明了 `remaining_slices`？若提案不在路线图主表内，是否有已批准的 `## Roadmap Amendments` 行（理由/提出人/审批人/日期/基线影响）？ | `docs/product/capabilities.csv`；`docs/product/modules.csv`；`docs/product/proposal-roadmap.md` `## Roadmap Amendments` | 07 实现切片；08 footprint；10 注册表回写 | [ ] |

### 3.4 07 详细设计、接口与测试设计

| ID | 必须问清 | 建议问句 | 工件落点 | 下游消费者 | 状态 |
|---|---|---|---|---|---|
| 07-T01-01 | 设计范围、非目标、权衡、缺口 | 本 Change 的设计范围、非目标、关键权衡、设计缺口和准入结论是什么？ | `design.md` `## Design Decisions` | 08 实现；09 验证 | [ ] |
| 07-T04-01 | 现状变更影响 | 涉及哪些文件/类/函数/接口/表/测试/迁移，修改策略、兼容、回滚、风险和验证是什么？ | `design.md` `### Existing Code Change Impact` | 08 实现 | [ ] |
| 07-T05-01 | 数据模型、数据量、索引 | 数据模型是否覆盖所有 DO/AC，预计数据量、增长、索引、分页、归档和分区策略是什么？ | `design.md` `## Backend Detailed Design`；`api/openapi.yaml`；`design/io-catalog.csv` | 08 实现；08 性能测试 | [ ] |
| 07-T06-01 | 隐私实现 | PII/敏感字段在哪些组件、接口、表里分类、脱敏、加密、保留、删除、导出和审计？ | `design.md` `### Shared Concerns`；`design/io-catalog.csv`；`design/test-cases.csv` | 08 实现；09 审计验证 | [ ] |
| 07-T07-01 | 跨边界接口目录 | 所有 HTTP/原生/设备/第三方/IoT/异步/文件边界是否登记了协议、认证、契约、错误、超时/重试/幂等、版本、测试和 owner？ | `design/interface-catalog.csv`；`design.md` `## Interface Design` | 08 实现；09 接口验证 | [ ] |
| 07-T08-01 | 报表、打印、导出、文件存储 | 报表/打印/导出/文件存储落在哪些接口、表、组件，格式、权限、保留和失败路径是什么？ | `design.md` Interface/Backend；`design/io-catalog.csv`；`design/test-cases.csv` | 08 实现；10 验收 | [ ] |
| 07-T09-01 | NFR 测试设计 | 每个 NFR（性能、负载、安全、可访问性、审计）用什么阈值、环境、数据量和证据验证？ | `design.md` `## Test Design`；`design/test-cases.csv` | 08 测试；09 独立验证 | [ ] |
| 07-T10-01 | 数据迁移执行 | 数据迁移的 backfill、转换、校验、对账、双跑、回滚和部署顺序是什么？ | `design.md` `### Data Model and Migration`；`design/test-cases.csv` | 08 割接；09 验证 | [ ] |
| 07-T11-01 | UAT 与验收输入 | UAT/试点场景、验收环境、种子数据、手工验证步骤是什么，谁执行、谁签字？ | `design.md` `### Manual Verification`；验收证据 | 10 验收 | [ ] |
| 07-T12-01 | 配置、密钥、开关、发布 | 配置、密钥、特性开关、环境晋级、发布、回滚和 runbook 怎么处理？ | `design.md` `### Shared Concerns`；基线约束 | 08 发布；10 验收 | [ ] |
| 07-T12-02 | 可观测性与 SLO | 日志、指标、追踪、告警、SLO 和审计日志落在哪里，阈值和 owner 是什么？ | `design.md` `### Shared Concerns`；`design/test-cases.csv` | 08 实现；09/10 证据 | [ ] |
| 07-T15-01 | 测试覆盖与证据 | 测试策略是否覆盖每个 AC/页面/operationId/IO/边界，并包含数据、替身、清理和失败注入？ | `design.md` `## Test Design`；`design/test-cases.csv`；`traceability.csv` | 08 执行；09 验证 | [ ] |
| 07-T15-02 | 离线、同步、多端、设备 | 离线缓存、同步冲突、多端差异、JS Bridge 和设备能力落在哪些组件、事件和接口？ | `design.md` `## Frontend Detailed Design`；`design/interface-catalog.csv`；`design/test-cases.csv` | 08 实现；09 设备验证 | [ ] |
| 07-T15-03 | 静态分析配置与豁免计划 | 采用静态分析时：08 将从已批准规则包复制/固定哪些配置文件到各栈根目录，是否与 `quality-gates.json` 一致（不一致时记录偏差），哪些 blocking 问题需要 Change 级豁免，且审批人与过期时间在 `policy.waiver.max_days` 之内？未采用时记录 `N/A + reason`。 | `design.md` `### Static Analysis`；`design/static-waivers.json`（条件适用） | 08 门禁；09 独立验证；10 验收 | [ ] |
| 07-T16-01 | UI 控件动作映射 | `figma-code/` 与 `figma-audit.md` 中的每个功能按钮/图标/链接/菜单/标签页，是否都有跳转地址+入参或 OpenAPI operationId；两者都没有的本地动作，是否已由用户确认（确认人+日期）？`ui-actions.csv` 是机读清单，`### 事件处理` 解释 handler 行为并按 `element_id` 引用其行、不重复动作映射。 | `design/ui-actions.csv`；`design/figma-code/`；`design/figma-layout.csv`；`design.md` `### Event Handling` | 08 实现；09 验证 | [ ] |
| 07-T13-01 | 设计与执行负责人 | 设计、实现、测试、验收的 owner 是谁，未决决策的截止/阻塞条件是什么？ | `design.md` `### Key Decisions and Trade-offs`；`### Open Decisions` | 08/09/10 审批 | [ ] |
| 07-T03-01 | 权限与审计实现 | 每个页面、接口、IO 的权限、数据范围、脱敏和审计如何实现？ | `api/openapi.yaml`；前端/后端子节；`design/test-cases.csv` | 08 实现；09 验证 | [ ] |
| 07-T17-01 | 实现切片、模块 footprint 与模块卡 | `design.md` 是否含 `### Implementation Slice`，并写明 Primary capability、Owner module、Related modules、Slice type/coverage、Code packages、Owned paths、Integration paths 与 Module card？代码包与拥有路径是否位于归属/关联模块路径下，`shared_paths` 变更是否以拥有条目出现，集成路径是否匹配 `code-layout.json` 且带理由与 task ID，模块卡是否为 create/update（或 `N/A + reason`）？`strategy=none` 时不要求切片；`footprint` 时仅要求 Owned paths 与 Integration paths。 | `design.md` `### Implementation Slice`；`docs/product/capabilities.csv`；`docs/product/modules.csv`；`docs/architecture/code-layout.json`；`<module_path>/MODULE.md` | 08 实现；09 footprint 验证 | [ ] |

## 4. 建议的阶段退出检查

以下是评审辅助，不是机器门禁：

1. 阶段选择处理的条目有答案，或明确标为 `不适用`/`待确认`/`延后`。
2. 每个 `待确认` 项都出现在 `docs/product/open-questions.md`，并有 owner 和阻塞条件。
3. 每个 `已答` 项都指向声明工件里的真实落点。
4. 阶段评审通过“下游消费测试”：下一阶段能不再追问用户缺失事实就完成它声明的工件。
5. 有意推迟的项建议记录为 `延后`，写明批准人和目标阶段；确实不适用的条目无需状态行。

## 5. 证据与交接

- 02/03/05/07 的 `question_coverage` 是可选块。若提供，`python scripts/check-question-coverage.py --step <step-id> --evidence <json>` 会校验每条的状态与字段、拒绝重复 `item_id`，并检查 `landing` / `open_question` 路径存在；不要求固定条目列表，允许额外 item_id，`workflow.py request-review` / `transition` 会自动复核同一个可选块。
- 形状示例（不必覆盖整个清单；`landing` 是一个真实工件路径，可带 `#heading`）：

```json
"question_coverage": [
  {
    "item_id": "02-T02-01",
    "status": "answered",
    "landing": "docs/product/requirements-analysis.md#6. 非功能需求",
    "owner": "产品负责人",
    "date": "2026-11-18"
  },
  {
    "item_id": "02-T11-01",
    "status": "open",
    "owner": "产品负责人",
    "blocking": "试点基地和验收数据未确认",
    "open_question": "docs/product/open-questions.md"
  },
  {
    "item_id": "02-T08-01",
    "status": "n/a",
    "reason": "本期没有报表或打印凭证"
  },
  {
    "item_id": "03-T10-01",
    "status": "deferred",
    "reason": "本期没有旧数据迁移",
    "approver": "技术负责人",
    "target_step": "07-detailed-design"
  },
  {
    "item_id": "CUSTOM-01",
    "status": "answered",
    "landing": "docs/product/open-questions.md#已解决"
  }
]
```

- 不能基于假设或未读文档把项标成 `answered`。没有来源的答案就是 `open`。
- 把清单作为附录或摘要表附在阶段交接报告里是可选的。

## 6. 维护

- 阶段 Prompt、Skill、模板或契约变化时，在同一次变更里更新对应清单行。
- 下游阶段发现缺少输入时，在本清单新增一行并记录来源阶段；不要只在 downstream 工件里修补。
- 本清单是建议，不改变硬门禁；可选的 `question_coverage` 块形状由校验器检查。
