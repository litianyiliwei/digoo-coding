# Superpowers 技能映射

本项目 Skill 负责业务阶段；Superpowers 负责编码方法与协作流程。两者不是一套需要相互替换的技能。

| 本项目阶段 | 对应 Superpowers 技能（如安装版本中存在） | 用法 |
|---|---|---|
| 对话启动/技能发现 | `using-superpowers` | 若已安装且 Agent 可发现，先读取其规则，再选择任务相关技能；按宿主 Agent 的真实调用方式执行 |
| 需求业务梳理/方案讨论 | `brainstorming` | 先与用户澄清目标、用户、痛点、范围、成功标准和未决问题；不应未经澄清就一次性生成完整方案；需求规格最终落入项目基线/OpenSpec |
| 参考产品/互联网调研 | `internet-research` | 用 WebSearch/WebFetch 或宿主等价联网工具记录研究问题、来源、对比、结论与影响映射；无联网能力时标记 BLOCKED，不得用记忆替代 |
| 计划实施 | `using-git-worktrees`、`writing-plans` | 在获批方案后准备隔离工作区并拆成小任务 |
| 编码实施 | `test-driven-development` | RED → GREEN → REFACTOR，验证先行 |
| 任务执行 | `subagent-driven-development` 或 `executing-plans` | 按当前环境支持的模式执行并设置检查点 |
| 故障处理 | `systematic-debugging` | 复现、定位根因、验证修复，不做随机修改 |
| 代码审查 | `requesting-code-review`、`receiving-code-review` | 根据规格/计划检查并核实审查反馈 |
| 完成前验证 | `verification-before-completion` | 用真实命令和结果证明功能已修复/实现 |
| 07 详细设计 | `brainstorming`、`writing-plans` | 用 `brainstorming` 比较数据模型、接口形态、状态流转与测试策略的取舍；用 `writing-plans` 把已批准 spec/AC 拆成设计任务与测试计划；必须记录方法证据 |
| 09 独立验证 | `verification-before-completion`、`systematic-debugging`（只读） | 用 `verification-before-completion` 要求真实命令/退出码/测试结果；用 `systematic-debugging` 复现失败、定位根因但不修复代码；不得用 code review 技能替代独立验证 |
| 分支结束 | `finishing-a-development-branch` | 在所有验证通过后讨论合并/PR/清理，不能自动发布 |

技能名称和触发规则可能随 Superpowers 版本及 Agent 适配有所变化。实施前先检查当前安装内容；若缺少技能，应明确报告并执行等价的显式流程，不要声称调用了不存在的技能。

## OpenSpec 参与矩阵

OpenSpec 在本项目中既是“规格与校验系统”，也是可用的“探索/修订方法”。但它的 `propose` 会一次性生成 proposal/specs/design/tasks，和本项目 05/06/07 的分阶段门禁冲突，因此必须区分允许与禁止。

| 阶段 | 必须执行（真实命令） | 允许（有边界） | 禁止 |
|---|---|---|---|
| 02 需求业务梳理 | `openspec list --specs` 并读取相关规格 | `openspec-explore` 只读思考（不得创建 Change、不得写代码） | `openspec new change`、`openspec-propose` |
| 03 总体架构 | `openspec list --specs`、`openspec list --changes` | `openspec-explore` 只读比较架构/边界 | `openspec new change`、`openspec-propose` |
| 04 提案拆分 | `openspec list --specs`、`openspec list --changes` | `openspec-explore` 只读；批准后逐个 `openspec new change` | 审批前 `openspec new change`、`openspec-propose` |
| 05 提案需求 | `openspec status --change`、`openspec list --specs`、`openspec instructions <artifact> --change --json`、`openspec validate --strict` | `openspec-explore`（当前 Change 范围内）；`openspec-update-change`（需求修订，需重新评审） | `openspec-propose`；跳过 05 直接创建 Change 产物 |
| 06 Figma | `openspec status --change`、读取已批准 specs | `openspec-explore` 只读澄清交互 | `openspec-propose`、`openspec-update-change`（需求变化须回 05） |
| 07 详细设计 | `openspec status --change`、`openspec instructions design --json`、`openspec validate --strict` | `openspec-explore`（设计歧义时）；`openspec-update-change`（仅设计决策一致性，需重新评审） | `openspec-propose`；用 design 反向覆盖已批准行为 |
| 08 实现 | `openspec instructions apply --json`、`openspec status --change`、`openspec validate --strict` | 读取 tasks/specs/design；不得改规格 | `openspec-propose`、`openspec-update-change`（规格冲突须暂停回 05/07） |
| 09 独立验证 | `openspec status --change`、`openspec validate --strict` | 只读规格/设计/tasks | `openspec-propose`、`openspec-update-change`、`openspec-sync-specs` |
| 10 验收归档 | `openspec validate --strict`；用户批准后 `openspec archive` | `openspec-sync-specs`（如需先同步主规格） | `openspec archive -y`、未批准归档、`openspec-propose` |

## 阶段内方法模式（stage-scoped brainstorming）

Superpowers `brainstorming` 的完整流程要求写独立设计文档并单独获批；本项目的阶段门禁要求产物落在 `design.md` / `technology-decisions.md` 等既有载体，并由阶段评审批准。两者直接叠加会产生编外文档和第二套审批。因此本项目默认使用 **stage-scoped** 模式：

1. 加载 `using-superpowers` 与 `brainstorming`，实际使用其“先澄清、再比较备选、记录取舍”的方法。
2. 把澄清问题、备选、决策与未决项写入阶段已有产物（`technology-decisions.md` 的访谈记录、`design.md` 的 `### 关键决策与权衡`、`open-questions.md` 等），不另写 `docs/superpowers/specs/` 设计文档。
3. 阶段 `request-review` + 用户明确批准就是该方法产物的批准；不增加第二套批准。
4. 只有用户明确要求“独立 Superpowers 设计文档”时，才执行完整 `brainstorming` 流程；此时必须在交接报告中说明编外文档路径，并确保阶段产物仍为权威。
5. 技能确实不可用时使用 `mode=equivalent`，记录 `reason` 与等价步骤；不得把“可用”当作“已使用”。

## 阶段沟通清单（强制）

### 03 项目总体架构

- 系统来源：新系统、基于现有系统二开、还是混合；不得默认。
- 若二开：要求代码地址（仓库/本地路径/分支/commit），实际探索代码结构、技术栈、模块边界、API/数据模型、构建/测试/发布命令、既有规范与技术债；写入 `technology-decisions.md` 的“现有系统二开约束”，并转换为 `constraint-registry.json` 的 `LEGACY-*` 约束；代码不可访问时 BLOCKED。
- 第三方接口：列出提供方、用途、协议、鉴权、SLA/配额、沙箱/测试账号、审批、数据共享/隐私、错误/超时、责任人；写入“第三方接口依赖清单”、`data-flows.md` 的 EXTERNAL 数据流、`api-conventions.md` 的“第三方接口与集成约定”；无则 NONE + 理由。

### 07 详细设计

- 变更类型：修改现有功能代码，还是新功能开发；不得默认。
- 若修改现有功能代码：要求代码地址（仓库/路径/分支/commit），实际探索文件/类/函数/数据结构/测试/迁移；写入 `design.md` 的 `### 现有代码变更影响`（文件/类/函数/接口/表/测试、修改策略、兼容性、迁移/回滚、风险、验证方式）；代码不可访问时 BLOCKED。
- 第三方接口：与 03 清单核对；每个第三方接口在 `interface-catalog.csv` 建 `THIRD_PARTY_API` 行，记录 provider/协议/鉴权/输入输出/错误/超时重试幂等/SLA/配额/沙箱/数据共享隐私/test_ids/owner；测试在 `test-cases.csv` 的 `interface_ids`/`fakes_env` 覆盖沙箱、模拟器或人工验证。

## 方法证据

02–10 的阶段 evidence 必须包含 `methods` 块，记录 skill/mode/questions/alternatives/decisions/open_questions/artifact_section/evidence。策略见 `docs/STEP-ARTIFACT-CONTRACTS.json` 的 `method_policy`；单独校验命令：

```bash
python scripts/check-method-evidence.py --step <step-id> --evidence <evidence.json>
```

`workflow.py transition` 会自动调用同一校验；交接报告第 4 节必须展示关键问题、备选、决策、未决项与产物落点。没有 `methods` 或内容不足时，阶段不得推进。



## 必须执行而非只提及

- 每个阶段 Prompt 必须先加载对应的项目 Skill，并检查适用的 Superpowers 技能是否实际可用。
- 详细设计必须实际使用 `brainstorming` 与 `writing-plans`，并记录方法证据；独立验证必须使用 `verification-before-completion`，独立运行 OpenSpec `status`/`validate`，不能用 code review 技能替代独立验证。
- 需求业务梳理阶段明确使用 `brainstorming` 与 `internet-research`；它通常发生在正式 OpenSpec Change 之前，因此先读取已有 specs，不要提前创建 Change。调研结果写入 `docs/product/reference-research.md`。
- OpenSpec 相关阶段必须运行真实 CLI：用 `openspec list/status/instructions/validate` 读取状态和规则；只有用户批准且门禁通过后才 archive。
- 若 Agent 没有仓库/终端/Skill 访问能力，必须请求用户提供文件或说明无法执行，不能模拟工具结果。
