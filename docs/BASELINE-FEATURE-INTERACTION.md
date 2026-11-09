# 项目基线与功能 Change 的双向治理规则

> 本文件定义项目级基线与功能级 OpenSpec Change 的权责边界，是所有功能开发阶段的强制规则。流程图、Skill、Prompt 与阶段契约不得与本文件冲突。

## 1. 核心原则

1. **基线先约束功能，功能再反馈基线。** 每个功能 Change 在需求细化前必须读取当前有效基线，并形成基线适用性/影响记录。
2. **基线是共享规则，不是功能设计的副本。** 功能 Change 通过文件路径、版本、章节和稳定 ID 引用基线，不复制整份基线。
3. **功能 Change 是单一功能行为的权威变更载体。** 当前功能的行为、页面、端点、局部数据迁移、IO、测试与实现细节留在该 Change。
4. **不因“新增实现”就自动修改基线。** 只有跨功能复用、公共规则改变、系统级约束变化或项目公共模型演进，才提升为基线变更。
5. **基线变更必须显式评审、批准、版本化。** 不得在功能开发中静默改写已冻结基线；未批准的候选决策不能成为其他 Change 的约束。
6. **基线更新不能追溯性地静默改变在途 Change。** 基线版本变化后，在途 Change 必须重新核对适用性并记录是否需要 rebase / 重新评审。

## 2. 项目基线包含哪些权威内容

| 基线域 | 权威文件 | 对功能的约束类型 |
|---|---|---|
| 产品基线 | `docs/product/requirements-analysis.md`、`workflows.md`、`data-objects.csv`、`rd-matrix.csv`、`business-rules.md`、`glossary.md`、`acceptance-policy.md` | 全局业务目标、共享流程与节点、角色/数据对象、RD 矩阵、业务规则、术语、验收口径 |
| 架构基线 | `docs/architecture/system-context.md`、`domain-boundaries.md`、`containers-and-deployment.md`、`data-flows.md`、`technology-decisions.md`、`docs/adr/` | 系统/模块边界、职责与依赖方向、技术选型、部署拓扑、跨模块集成方式 |
| 数据与领域基线 | `docs/architecture/logical-erd.md`、`domain-boundaries.md`、`data-flows.md` | 核心实体及关系、数据所有权、领域不变量、共享事务/一致性原则 |
| 公共 API 基线 | `docs/architecture/api-conventions.md` | 认证授权、错误模型、版本、分页、幂等、兼容与公共响应约定 |
| 前端工程基线 | `docs/architecture/frontend-conventions.md` | 路由、组件/设计系统、状态管理、请求层、错误和可访问性规范 |
| 测试与质量基线 | `docs/architecture/test-strategy.md` | 测试分层、必须执行的质量门禁、测试环境和发布验证要求 |
| 基线治理元数据 | `docs/architecture/baseline-status.md` | 各基线域版本、生效状态、审批人、生效日期、在途修订和豁免 |

OpenSpec `openspec/specs/**` 与上述设计/治理基线互补：OpenSpec 主规格描述系统已经承诺的、可观察的能力行为；项目基线文档描述跨功能复用的业务、架构、数据和工程约束。功能开始时两者都要检查，不能相互替代。

## 3. 功能开发前必须读取什么

### 3.1 固定读取（每个 Change 都做）

- `docs/architecture/baseline-status.md`：核验是否 FROZEN、版本、生效日期、审批人与待处理修订。
- `docs/product/acceptance-policy.md`、`docs/product/glossary.md`：核验验收和术语公共约束。
- 与本 Change 直接关联的产品需求、业务流程、用户故事、业务规则及其稳定 ID。
- `docs/architecture/system-context.md`、`docs/architecture/domain-boundaries.md`：核验涉及的系统、模块、数据所有权和依赖边界。
- `openspec/specs/**` 中与本功能 capability / domain 相关的现行规格；如有依赖 Change，也读取其已归档规格。

### 3.2 按影响读取（命中才深入读取全文/相关章节）

| 影响面 | 必须核验的基线文件 |
|---|---|
| 新增/修改数据、实体、查询、事务 | `logical-erd.md`、`domain-boundaries.md`、`data-flows.md` |
| 新增/修改服务、模块、异步流程、第三方依赖、部署 | `containers-and-deployment.md`、`technology-decisions.md`、相关 ADR、`data-flows.md` |
| 新增/修改 HTTP API、鉴权、对外集成 | `api-conventions.md`、相关 ADR、安全/鉴权约定 |
| 修改页面、路由、组件、状态或视觉系统 | `frontend-conventions.md`、已批准设计系统/组件规范 |
| 修改质量要求、性能、安全、可靠性、可观测性 | `test-strategy.md` 及对应 NFR / ADR / 部署约束 |
| 修改角色、跨功能业务规则、共享流程/术语 | 对应产品基线文件与权限/安全相关架构约定 |

AI 不应无差别把所有文档全文塞入上下文；必须先读取基线状态和目录，再针对本 Change 的影响面读取相关文件/章节，并在基线影响清单中留下证据路径、版本和引用 ID。

## 4. 变更归属判定：留在 Change 还是提升到基线

| 变化类型 | 权威落点 | 是否更新项目基线 | 典型例子 |
|---|---|---|---|
| 当前功能独有的行为、规则、AC、异常场景 | 当前 Change 的 proposal / delta spec | 否 | 订单导出时的字段筛选规则 |
| 当前功能独有的页面、按钮、接口和 API schema | 当前 Change 的页面清单、Figma 审计、OpenAPI | 否 | 新增 `GET /orders/{id}` |
| 当前功能独有的表/字段/索引/迁移和查询 | 当前 Change 的 migration、后端设计、IO 目录 | 通常否 | 仅订单导出任务使用的状态字段 |
| 当前功能独有的类、方法、内部 IO 编排 | 当前 Change 的详细设计和代码 | 否 | 某个功能调用 Redis 的一次性缓存实现 |
| 新的共享业务规则、全局角色/权限语义、跨功能流程或公共术语 | 产品基线（必要时同步 OpenSpec 主规格） | 是，审批后 | 所有订单类操作必须满足统一的审批规则 |
| 新功能成为已批准的产品范围、需要登记新的稳定 US/UC/BR ID | 产品需求/用户故事目录（只登记索引、摘要、状态和 ID）；详细行为/场景/AC 仍以该 Change 的 OpenSpec spec 为准 | 验收批准后更新产品目录；不复制完整功能规格 | 新增“批量导出订单”用户故事 ID；详细导出规则留在 Change spec |
| 系统/模块边界、数据所有权、依赖方向、技术栈、部署拓扑变化 | 架构基线 + ADR | 是，审批后 | 拆分服务、改变模块数据所有权 |
| 共享核心实体、关系、领域不变量或跨模块一致性变化 | 数据与领域基线 | 是，审批后 | 客户实体成为多个上下文共享的主数据 |
| 全局 API 错误格式、认证、幂等、分页/兼容规则变化 | API 公共基线 | 是，审批后 | 全部 API 统一错误 envelope |
| 全局前端组件、路由/状态管理、设计 token 规则变化 | 前端工程基线/设计系统 | 是，审批后 | 全站统一表单校验与错误呈现规范 |
| 全局测试分层、发布门禁、SLO/NFR 阈值变化 | 测试策略/架构基线/ADR | 是，审批后 | 所有服务新增契约测试阻断门禁 |

判定问题：

注意：产品需求基线可以维护项目级 US/UC/BR 目录和稳定 ID；但某个功能的详细行为、Given/When/Then 场景、API schema 和 AC 仍留在对应 OpenSpec Change/归档规格中。新增一条产品故事索引不等于把整个功能设计升级为公共基线。
1. 是否有至少两个功能/模块需要遵守或复用该规则？
2. 是否改变已批准的系统边界、共享实体语义、数据所有权、公共契约或质量门禁？
3. 如果下一个功能没有读取这个决定，会不会产生不一致、重复实现或兼容性风险？

任一项为“是”时，至少创建基线变更候选项并进行评审；如果只是当前功能的局部实现或局部行为，留在 Change。不能仅以“未来可能复用”作为提升基线的充分依据。

## 5. 基线变更的时间点与流程

### A. 功能开发前发现基线缺口/冲突

1. 在功能需求阶段填写 `openspec/changes/<change-id>/design/baseline-impact.md`。
2. 标记为 `BASELINE_CHANGE_REQUIRED`，提出影响域、目标版本、理由、替代方案和受影响 Change。
3. 架构/数据/公共契约等约束若决定了功能设计，必须先走 ADR/基线修订审批，再冻结该 Change 的详细设计。
4. 批准后更新相应基线文档和 `baseline-status.md` 版本；随后重新生成/复核本 Change 的基线影响清单，再继续功能设计。

### B. 功能开发中发现必须改变基线

1. 不允许直接编辑冻结基线，也不允许为了让代码通过而绕过基线。
2. 暂停受影响的任务；不依赖该决策的独立任务只有在负责人确认安全时才可继续。
3. 在当前 Change 的 `baseline-impact.md` 记录新发现，并创建/更新 ADR 或基线修订请求。
4. 批准后更新基线版本；当前 Change 必须重新读取差异、更新设计和任务、重新运行受影响的验证。
5. 若改变外部可观察行为，同时更新当前 Change 的 OpenSpec delta spec；若影响公共能力/既有承诺，还要评估主规格变更和兼容迁移。

### C. 功能验收与归档时回写基线

1. 只回写已批准、已实现、已验证且确实具有项目级复用价值的变化。
2. 功能特有的 API、页面、物理表结构、IO 和测试案例留在归档 Change，不复制到全局基线。
3. 对需要同步的产品需求目录、逻辑 ERD、公共约定、ADR 或架构说明，更新基线文档和版本记录；不得将未批准的实现事实自动提升为规范。
4. 更新基线状态、审批人、生效日期、修订摘要和关联 Change ID；运行基线一致性审计。
5. 归档 OpenSpec Change 后，在途 Change 对新基线版本执行影响复核，不得静默假定自动兼容。

## 6. 基线版本与在途 Change 的绑定

- `docs/architecture/baseline-status.md` 是基线状态索引；至少记录产品、架构、数据/领域、公共 API、前端工程、测试策略各域版本及冻结/审批信息。
- 每个 Change 的 `design/baseline-impact.md` 必须记录开始时采用的基线域版本（baseline snapshot），并引用具体文件、章节/ID。
- 基线状态发生变化时，比较 Change 记录的版本与当前版本；只复核受影响域，但必须留下 `NO_IMPACT` 或 `REBASE_REQUIRED` 结论和依据。
- 已冻结基线采用增量版本更新：普通文字澄清可按项目规则做补丁版本；公共约束/模型变化至少升级次版本；系统边界/重大技术策略变化升级主版本。若团队采用其他版本策略，必须在 `baseline-status.md` 明确。
- `workflow-state.json` 只记录索引、待审批和阻断，不取代基线文档、ADR 或审批证据。

## 7. 功能 Change 的强制基线影响清单

每个 Change 必须创建 `design/baseline-impact.md`（按 `templates/change-assets/design/baseline-impact.md`）：

- 当前基线版本和各域状态；
- 固定读取项与按影响读取项的核验结果；
- 约束 ID / 文件 / 章节 / 版本 / 适用性 / 对当前功能的设计影响；
- 复用的现有模块、领域实体、API 公共约定、前端组件和测试策略；
- 与基线冲突、缺口和假设；
- 归属分类：`CHANGE_ONLY`、`BASELINE_CHANGE_REQUIRED`、`BASELINE_UPDATE_AFTER_ACCEPTANCE`、`N/A`；
- 需创建/更新的 ADR、基线修订请求、审批人、状态；
- 在途 Change 的 rebase 结论；
- 结论：`COMPATIBLE`、`BLOCKED_PENDING_BASELINE_CHANGE` 或 `APPROVED_BASELINE_AMENDMENT`。

这个文件从阶段 03 开始建立，在 06–07 设计时复核，在阶段 08 实现时仅追加发现，不擅自修改基线，在阶段 10 验收时完成回写核验。

## 8. 角色和审批责任

| 决策范围 | 必要审批角色 |
|---|---|
| 产品规则、角色、流程、术语、验收政策 | 产品负责人/业务负责人 |
| 系统边界、模块依赖、技术选型、部署拓扑、ADR | 架构负责人/技术负责人 |
| 核心实体、数据所有权、共享数据不变量 | 数据负责人 + 架构负责人 |
| 公共 API、前端公共规范、质量门禁 | 对应技术负责人；影响跨团队时由架构负责人批准 |
| 单个功能行为和 AC | 产品负责人；技术实现由对应技术负责人评审 |

AI 可以分析、提出候选修改和生成文档，不可代替负责人批准，不可自行宣布基线已冻结或升级。


## 9. 机器可执行的基线治理引擎（强制）

本项目不再以 `baseline-status.md` 中的文字状态作为唯一判断依据。以下文件构成机器权威来源：

- `docs/architecture/baseline-manifest.json`：总体/域版本、状态、审批、生效 revision、每个基线文件的 SHA-256。
- `docs/architecture/constraint-registry.json`：稳定 Constraint ID、约束等级、适用范围、规则正文、来源章节、执行方式、负责人和审批状态。
- `openspec/changes/<change-id>/design/baseline-binding.json`：当前 Change 对全部 ACTIVE 约束的逐条绑定、基线快照、设计证据、实现验证证据、例外审批和 rebase 结论。
- `scripts/baseline-governance.py`：上述数据的唯一检查入口；`workflow.py` 在阶段进入/转换时调用它。

### 9.1 冻结条件

项目总体架构设计阶段 03 的结束审计只有在以下条件全部满足时才允许转换：

1. Manifest `status=FROZEN`，且六个必需域均为 `FROZEN`。
2. 每个域具备语义版本、owner、approver、approved_at、effective_revision。
3. 每份权威基线文件都存在且 SHA-256 与 Manifest 一致；约束注册表自身也有 SHA-256。
4. 约束 ID 唯一、等级合法、来源文件属于对应域且来源章节真实存在。
5. 不允许 DRAFT 约束混入冻结基线；ACTIVE 约束必须有 owner、approved_by、approved_at。
6. 总体审批必须有 approver、approved_at 和仓库内 evidence 文件。
7. 阶段 03 的 Evidence 必须将 Manifest 和 Constraint Registry 作为输出交接。

### 9.2 约束注册表规则

每条约束至少包含：`id`、`domain`、`revision`、`status`、`level`、`scope`、`title`、`rule`、`rationale`、`source.file`、`source.section`、`enforcement`、`owner` 和审批字段。等级使用 `MUST`、`SHOULD`、`MAY`、`PROHIBITED`；状态使用 `DRAFT`、`ACTIVE`、`RETIRED`。

- MUST / PROHIBITED 是硬约束；除已批准的 Change 级例外外不得偏离。例外对象必须为空或状态完整的 `APPROVED`，被拒绝/待批的例外不能与 `COMPLIANT` 决策并存。
- SHOULD 是强建议；若不遵守，必须给出理由和评审结论。
- MAY 表示允许采用，不意味着必须采用。
- 只有 ACTIVE 约束进入 Change 机器绑定；DRAFT 规则不能假装成有效基线。冻结注册表至少包含一条 ACTIVE 约束，所有 DRAFT 规则必须在冻结前转为 ACTIVE 或 RETIRED。
- `AUTOMATED` / `HYBRID` 必须引用仓库内真实存在的 validator；`MANUAL` / `HYBRID` 必须要求人工证据。没有可执行校验器时不得伪称自动化。
- 约束修改/停用/新增属于基线修订，不能仅编辑 Change 绑定文件。

### 9.3 Change 绑定与分阶段门禁

创建 Change 辅助资产时运行：

```bash
python3 scripts/baseline-governance.py init-binding --change-id <change-id>
```

生成的 `baseline-binding.json` 必须覆盖当前注册表全部 ACTIVE 约束，禁止删除约束行。每条约束必须选择 `APPLICABLE` 或 `NOT_APPLICABLE`；N/A 必须写明理由。适用约束在设计阶段必须为 `COMPLIANT` 或 `EXCEPTION_APPROVED`，并关联真实设计证据文件。

实现阶段每条适用约束必须有 `implementation_verification.status=PASS` 和真实证据文件；确实只影响设计、不影响运行实现的约束，仍须显式写 `NOT_APPLICABLE` 和理由。`PENDING`、`NOT_RUN`、`SKIPPED` 不能视为通过。验收阶段还必须单独填写 `acceptance_verification`，以独立验收/复核证据再次确认约束遵守情况，不得直接复制实现阶段 PASS；N/A 同样必须说明理由。

例外必须记录唯一 exception_id、偏离原因、范围、批准人、批准时间和仓库内审批证据。Change 级例外仅允许该 Change 在获批范围内偏离；它不修改、不降低项目基线，也不自动授权其他 Change。

工作流门禁映射：

| 阶段 | 机器检查 | 目的 |
|---|---|---|
| 08 基线冻结 | `audit --require-frozen` | 校验 Manifest、约束目录、哈希与审批 |
| 04 提案规划 | `audit --require-frozen` | 确保项目基线仍有效 |
| 10 需求细化 | `check-change --phase requirement` | 约束覆盖完整、适用性已判定、基线绑定已审批 |
| 11–12 | `check-change --phase requirement` | 防止早期需求绑定被删改或基线漂移 |
| 09 转出及 10–13 | `check-change --phase design` | 每条约束有设计结论和证据，例外已审批 |
| 14 / 15 | `check-change --phase implementation` | 适用约束有实现验证证据 |
| 15 | `check-change --phase acceptance` | 所有约束完成最终验证 |

### 9.4 基线演进和在途 Change rebase

冻结后发现需要修改基线时，**必须先**运行：

```bash
python3 scripts/baseline-governance.py open-amendment \
  --request-id BCR-<id> --domains architecture,data_domain --opened-by <reviewer>
```

该命令把总体状态改为 `UNDER_AMENDMENT` 并标记指定域，所有功能级入口立即 fail-closed。修改文档/约束后，必须同时升级总体 `overall_version` 和每个受影响域的语义版本，再运行 `refresh-hashes`；然后执行 `close-amendment --request-id <BCR-ID> --approved-by <负责人> --approved-at <日期> --effective-revision <git:commit或snapshot:sha256> --evidence <审批证据文件>`。命令会检查受影响域版本确实升级、哈希正确和证据存在，再恢复 FROZEN。完成后重新执行 `audit --require-frozen`。在此期间不允许功能开发继续消费正在修改的基线。

在途 Change 的每个受影响域必须填写 `rebase_reviews`：当前 version、当前 fingerprint、结论、reviewer、reviewed_at、仓库内证据。每次总体版本变化还必须填写 `rebase_reviews.overall`，对总体升级给出独立影响结论。`NO_IMPACT` 可以保留原快照，但每个阶段都会重新校验该结论仍对应当前 fingerprint/version；需要改变设计/实现的，必须对总体和受影响域完成 rebase 并标记 `REBASE_COMPLETED`，再运行 `refresh-binding`。Refresh 会重置变化域的约束判断并撤销旧绑定审批，必须重新评审。

### 9.5 约束与安全边界

脚本验证的是仓库内 JSON、文件哈希、审批记录结构和证据存在性；不具备企业身份认证、电子签名或不可抵赖能力。必须把 `baseline-governance.py audit --require-frozen` 和适用 Change phase gate 接入 CI，并对基线文件/Manifest/Registry 设置 Git CODEOWNERS、受保护分支和必需审批。否则有权限直接修改脚本、状态 JSON 或绕过 CI 的 Agent/用户仍可能规避门禁。
