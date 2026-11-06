# 工具包自检报告

## 当前版本检查结果

本次升级已在工具包目录内完成以下检查：

| 检查项 | 结果 |
|---|---|
| Skill / Prompt 配对与 frontmatter | 通过，21 个 Skill / 21 份 Prompt |
| 阶段输入/输出/交接契约 | 通过，21 条阶段记录 |
| 输出模板矩阵 | 通过，46 个登记项，模板路径均存在或为 OpenSpec 内置 artifact |
| 基线治理一致性 | 通过，治理规则、模板、阶段契约、Skill、Prompt、状态文件和模板矩阵均已关联 |
| API → IO 映射回归测试 | 通过 |
| Bash 脚本语法 | 通过 |
| Python 脚本编译 | 通过 |
| 新 Change 辅助模板创建 | 通过；临时 Change 自动生成 `design/baseline-impact.md`，既有文件保留规则不变，测试目录已删除 |
| 基线影响清单检查 | 通过；空白模板的结构检查通过、严格门禁按预期阻断；填充并批准的临时样例严格检查通过 |
| ZIP 完整性 | 打包后执行 `unzip -t` 检查 |

## 本次基线治理升级内容

1. 新增 `docs/BASELINE-FEATURE-INTERACTION.md`，区分基线读取、功能局部变化、开发前基线修订、实施中发现冲突和验收后基线回写。
2. 每个功能 Change 强制创建 `openspec/changes/<change-id>/design/baseline-impact.md`，记录基线域版本、读取文件/章节/ID、约束、复用、冲突、归属分类、审批和 rebase 结论。
3. 新增 `templates/project-baseline/baseline-status.md`，登记产品、架构、数据/领域、公共 API、前端、测试质量等域的版本、状态、审批人和生效日期。
4. 新增 `templates/project-baseline/baseline-change-request.md`，用于需要跨功能推广的基线修订；必要时与 ADR 关联。
5. 更新项目初始化、基线审计、提案拆分、功能需求、API/前端/后端/测试设计、实施和验收的 Skill、Prompt 与阶段契约。
6. `scripts/new-change-assets.sh` 创建 Change 辅助产物时确保生成基线影响清单。
7. 新增 `scripts/check-baseline-governance.py` 和 `scripts/check-baseline-impact.py`，并将治理一致性检查纳入 `scripts/check-package.py`。
8. 明确 OpenSpec archive（更新可观察行为主规格）与项目设计基线回写是两项独立操作。

## 重要规则摘要

- 功能开发前读取基线状态、相关产品规则、系统/模块边界和相关 OpenSpec 主规格；再按功能影响深入读取数据、API、前端、部署、测试等基线。
- 功能专属行为、端点、页面、物理表字段/迁移、内部 IO 和测试留在当前 Change。
- 共享业务规则、系统/模块边界、核心领域模型/数据所有权、公共 API/前端约定和全局质量门禁变化，必须先提出并审批基线修订。
- 实施中不得直接修改冻结基线；发现冲突时暂停受影响任务，走基线变更请求/ADR。批准后更新基线并刷新在途 Change 的基线快照、设计和测试。
- 验收时只回写已批准、已实现、已验证且有跨功能复用价值的决策；列出受影响的在途 Change。

## 未执行的项目级验证

- 本次仅检查工具包自身，没有用户的真实业务仓库和环境，因此未运行真实项目构建、部署、集成测试或业务验收。
- OpenSpec CLI 的 `openspec validate`、`openspec archive` 和用户项目 Schema 语义验证，必须在用户项目安装/初始化 OpenSpec 后执行；本报告不将其标记为通过。
- 架构合理性、需求完整性、基线修订审批和业务验收仍需要相应负责人评审；脚本通过不等于业务批准。


## P0 Runtime Governance Upgrade

- Skill / Prompt：21 / 21（新增 independent-verifier / 14b）。
- 阶段 DAG：`docs/WORKFLOW-STAGES.json`。
- 状态机与阶段守卫：`scripts/workflow.py`。
- SHA-256 交接包：状态转换自动生成，下游入口核验。
- 独立验证：`scripts/check-independent-verification.py` 与两份报告产物。
- 回归测试：`scripts/test-workflow-runtime.py`、`scripts/test-independent-verification.py`。
- 本报告只记录工具包自身测试；实际项目 OpenSpec CLI、构建和业务验收仍需在用户仓库执行。


## Baseline Governance Engine 升级（本版）

本版在既有双向治理文档之上新增可执行治理引擎：

1. `docs/architecture/baseline-manifest.json` 登记总体/域版本、冻结状态、审批和每个权威文件的 SHA-256；`constraint-registry.json` 登记稳定 Constraint ID、等级、适用范围、来源章节、执行器和审批。
2. 新增 `scripts/baseline-governance.py`：冻结审计、初次冻结、打开/关闭基线修订、哈希刷新、Change 绑定初始化/刷新以及 requirement/design/implementation/acceptance 四阶段门禁。
3. 每个 Change 强制生成机器权威 `design/baseline-binding.json`；逐条继承全部 ACTIVE 约束，记录适用性、设计证据、实现验证、Change 级例外和基线 rebase。
4. `workflow.py` 在阶段 08 冻结转换、阶段 09 入口和功能阶段入口/转换调用基线引擎，哈希漂移、未批准约束、漏绑、证据缺失、未决例外或 rebase 缺失均 fail-closed。
5. 新增基线治理回归测试，覆盖冻结哈希漂移、约束漏绑、阶段设计/实现/验收证据、未批准例外、总体/域版本升级和 rebase。
6. 约束指纹覆盖规则全文、来源、执行器、审批元数据；页面/交互与 Figma 审计阶段只读继承需求级绑定。

边界：本引擎验证仓库内记录与文件，不提供企业身份认证/数字签名；必须接入 CI、CODEOWNERS 和受保护分支。工具包自测不等于目标项目真实业务架构、审批或 CI 已验证。
