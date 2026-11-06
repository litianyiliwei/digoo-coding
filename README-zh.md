# OpenSpec + Superpowers AI 研发流程工具包

本工具包把 16 个流程阶段（含 10b、13a–13e、14b 子阶段及下一步编排）拆成可独立加载的 Skill、可复制的 Prompt、基线模板和确定性检查脚本。面向 pen.dev + Figma MCP + OpenSpec + Superpowers + OpenCode/兼容 Agent 工作流。

## 包含内容

- `.claude/skills/<skill-id>/SKILL.md`：17 个项目流程 Skill（另有 6 个 OpenSpec 辅助 Skill）。Claude Code 读取 `.claude/skills/`；OpenCode 等其他 Agent 可按其规范迁移或软链到 `.agents/skills/`，检查脚本对两者都兼容。
- `prompts/`：与每个阶段 Skill 一一对应的 Prompt；`prompts/00-next-step.md` 是“下一步”入口。
- `workflow-state.json`：跨阶段状态索引；继续前必须核验真实产物和审批状态。
- `.claude/skills/workflow-orchestrator/SKILL.md`：负责“下一步”判定、前置检查和门禁。
- `scripts/next-step.py`：只读状态文件并打印建议的下一阶段，不会自动修改状态。
- `docs/WORKFLOW-STAGES.json`：状态机唯一阶段 DAG 定义；`scripts/workflow.py` 提供状态、阶段进入守卫、证据门禁、原子状态转换和 SHA-256 handoff。
- `templates/workflow/stage-evidence.schema.json`：每次阶段转换的机器可读证据契约；自动化检查需附真实命令、退出码和日志。
- `independent-verifier` / `prompts/14b-independent-verification.md`：Builder 完成后的独立只读验证，PASS 才能进入人工验收。
- `scripts/check-independent-verification.py`：独立验证报告的结构化门禁。
- `docs/product/`、`docs/architecture/`、`docs/design/`、`docs/adr/`：项目级基线及设计清单模板。
- `openspec/config.yaml`：示例项目上下文和 artifact 规则。**合并前先与已有文件比较，不要直接覆盖已有 OpenSpec 配置。**
- `scripts/`：结构/追踪/OpenAPI/测试/完成前检查，以及无覆盖地初始化 Change 辅助产物模板。
- `docs/SUPERPOWERS-MAPPING.md`：项目阶段与官方 Superpowers 技能的映射。
- `docs/REVIEW-REPORT.md`：本次包的自检报告和已知限制。
- `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv`：定义哪些输出必须有模板、各模板位置和校验门禁。
- `docs/STEP-ARTIFACT-CONTRACTS.md` / `.json`：逐 Skill 定义输入、输出、下游消费关系、审批点和质量门禁；是阶段交接的权威清单。
- `docs/STAGE-IO-OVERVIEW.md`：由上述契约与 DAG 自动生成的逐阶段输入/输出总览；修改契约后执行 `python3 scripts/stage-io-report.py --out docs/STAGE-IO-OVERVIEW.md` 重新生成，`check-package.py` 会检查是否过期。
- `docs/BASELINE-FEATURE-INTERACTION.md`：定义项目基线如何约束功能开发、何时由功能反馈并更新基线。
- `templates/change-assets/design/baseline-impact.md`：每个功能 Change 强制填写的基线适用性/影响清单。
- `templates/project-baseline/baseline-status.md` / `baseline-change-request.md`：人类可读基线状态与修订申请模板。
- `docs/architecture/baseline-manifest.json` / `constraint-registry.json`：机器权威基线 Manifest 与稳定约束注册表；冻结状态由 SHA-256 校验。
- `templates/change-assets/design/baseline-binding.json`：每个 Change 逐条继承 ACTIVE 约束的机器绑定、例外审批、设计/实现证据和 rebase 记录。
- `scripts/baseline-governance.py`：基线治理引擎；由 workflow.py 在阶段门禁中调用。
- `templates/workflow/step-handoff-report.md`：每一步完成后必须展示的交接报告模板。
- `scripts/check-step-contracts.py`：检查每个 Skill/Prompt 都有对应的输入/输出/交接契约。
- `scripts/check-output-template-matrix.py`：检查模板矩阵中登记的模板文件是否真实存在。

## 安装/合并到现有项目

1. 先把 ZIP 解压到临时目录，查看差异；不要直接覆盖项目同名文件。
2. 将 `.claude/skills/`、`prompts/`、`scripts/` 合并到项目根目录。保留已有同名 Skill，先人工比较。
3. 阅读 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv`，据此确定各阶段的模板与质量门禁。把 `docs/` 模板合并进现有文档；不要用模板覆盖真实项目内容。
4. 合并 `openspec/config.yaml` 的 `context`/`rules` 到已有配置；注意 schema 和 rules 需要适配实际业务。
5. 如果尚未初始化 OpenSpec，在项目根目录执行 `openspec init`，工具参数先看 `openspec init --help`。不要用模板包覆盖现有 `openspec/specs/` 或 `openspec/changes/`。
6. 运行（Windows 环境若无 `python3` 命令，请将下述命令中的 `python3` 替换为 `python`；仓库内的 `.sh` 脚本会自动探测两者）：

   ```bash
   python3 scripts/check-package.py
   python3 scripts/next-step.py
   python3 scripts/workflow.py status
   python3 scripts/check-package.py
   bash scripts/check-required-files.sh
   ```

7. 根据实际仓库目录修改测试命令，再在具体 Change 上运行：

   ```bash
   openspec new change <change-id>
   bash scripts/new-change-assets.sh <change-id>
   # 填写 design/baseline-impact.md 并经评审；结构检查：
   python3 scripts/check-baseline-impact.py <change-id>
   # 创建 Change 资产时自动生成 baseline-binding.json（需要已冻结基线）。
   # 阶段 10 需求/绑定门禁：
   python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement
   # 设计/实现/验收门禁由 workflow.py 调用；也可手工执行：
   python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase design
   python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase implementation
   python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase acceptance
   # 使用 prompts/ 和对应 Skill 写完 proposal/specs/design/tasks 后，再运行：
   bash scripts/check-change.sh <change-id>
   bash scripts/check-design-assets.sh <change-id> --strict --lint-api
   bash scripts/validate-openapi.sh openspec/changes/<change-id>/api/openapi.yaml
   bash scripts/test-all.sh <frontend-dir> <backend-dir>
   ```

## 重要设计约定

- 项目级基线存放在 `docs/`；功能级变更用 OpenSpec Change 描述。每个功能 Change 必须先读基线并记录 `design/baseline-impact.md`；实施期间不得直接改冻结基线，批准的跨功能决策才回写项目基线。
- OpenSpec `specs/**/spec.md` 描述可观察行为，不放类名/框架/步骤式实现细节。
- 在当前 `spec-driven` 工作流中标准 artifact 是 `proposal.md`、`specs/<capability>/spec.md`、`design.md` 和 `tasks.md`。其他详细设计文件作为辅助材料放进 Change 目录；文件存在不意味着 OpenSpec 自动验证其内容。
- `tasks.md` 必须使用 `- [ ]` / `- [x]`，否则 OpenSpec 无法正确统计任务进度。
- OpenSpec 归档会更新主规格并将整个 Change 移入 archive；归档前必须检查 delta 是否正确、任务与验收是否完成。
- 当你说“下一步”时，先执行 `@workflow-orchestrator` 或复制 `prompts/00-next-step.md`；此能力要求 Agent 能访问仓库文件、终端与技能。新聊天必须重新读取状态和真实产物，不能只依赖对话记忆。
- Superpowers 技能名会随版本演进。实施时先检查安装版本；本包引用官方技能名 `brainstorming`、`writing-plans`、`test-driven-development`、`systematic-debugging`、`requesting-code-review`、`receiving-code-review`、`verification-before-completion` 等。缺失时必须如实报告。
- 所有外部工具（pen.dev、Figma MCP）都必须以实际可访问能力为准；不能把不可读取的链接/字段当作已经审查。
- 功能页面必须按 PAGE → BLOCK → ELEM/EVT 三层登记：`page-inventory.csv` 说明有哪些页面，`block-inventory.csv` 说明每个页面的功能区块，`interaction-map.csv` 用 `block_id` 说明每个按钮/元素属于哪个区块；由 `scripts/check-inventory.py` 校验层级闭合与归属一致。
- 并非每段 AI 输出都需要模板；正式、可追踪、供下游消费的产物必须按 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 走模板。
- 每个阶段必须按 `docs/STEP-ARTIFACT-CONTRACTS.json` 核验输入并生成输出；结束时展示交接报告。未经审批的草案不得作为下游正式输入。
- 每一个 OpenAPI `operationId` 必须在 `design/api-io-mapping.csv` 显式对应一个或多个 `io_id`，每个 IO ID 必须在 `design/io-catalog.csv` 有完整契约。数据库、文件、HTTP/Feign、Redis、MQ、对象存储和搜索都算具体 I/O。无 IO 的纯计算/健康接口只允许作为有理由和审批人的显式例外；不得为了填表虚构 IO。

### 基线与功能的双向治理

- 功能开始前必须通过 `baseline-manifest.json` 冻结/哈希校验，创建机器可读 `design/baseline-binding.json`；绑定当前注册表全部 ACTIVE 约束。
- 每个 Change 必须同时有 `design/baseline-impact.md`（人类影响分析）和 `design/baseline-binding.json`（机器约束追踪）；两者不能互相替代。
- 约束要逐条给出适用性、设计证据、实现验证；例外必须由责任人审批并限定到当前 Change。
- 实施中不得直接修改冻结基线；发现冲突时暂停受影响任务，提交基线变更请求/ADR。
- 验收时仅回写已批准、已实现、已验证且跨功能复用的决策；OpenSpec 归档与项目基线回写分开判断。

## 建议流程

需求业务梳理（业务流程节点/数据对象/RD 矩阵）→ 项目总体架构设计（含数据流转、领域/公共契约与结束审计冻结）→ 提案拆分 → 提案级需求分析（US/UC/AC）→ AI 通过 pen.dev MCP 生成提案原型并评审 → 页面/区块/交互清单 → Figma 审计 → API/前端/后端/测试设计 → Superpowers TDD → 自动化验证 → 独立验证 → 人工验收 → 归档和基线回写。

## 不要自动做的事情

本包默认不自动安装依赖、不提交代码、不改 CI、不归档、不发布，也不替业务/设计/架构负责人批准未决规则。


## P0 Runtime Governance（新增）

已增加状态机与阶段守卫、SHA-256 交接包、独立 Verifier。完整说明见 `docs/P0-RUNTIME-GOVERNANCE.md`。常用命令：

```bash
python3 scripts/workflow.py status
python3 scripts/workflow.py check-entry --step 01-project-bootstrap
python3 scripts/workflow.py transition --step 01-project-bootstrap --evidence workflow/evidence/01-project-bootstrap.json
python3 scripts/workflow.py handoff-verify --manifest workflow/handoffs/project/01-project-bootstrap--02-requirements-analysis.json
```


### Baseline Governance Engine（增强）

**首次冻结顺序**（不能跳过真实负责人审批）：先完善 `docs/architecture/baseline-manifest.json` 和 `constraint-registry.json`；确认六个基线域的资料与审批证据真实完整，各域设为 `FROZEN`；约束逐条审定，已批准的设为 `ACTIVE`、明确废弃的设为 `RETIRED`，不得留下 DRAFT 规则。然后依次执行：

```bash
python3 scripts/baseline-governance.py refresh-hashes
python3 scripts/baseline-governance.py freeze --approved-by <负责人> --approved-at <ISO日期> --evidence <审批证据路径>
python3 scripts/baseline-governance.py audit --require-frozen
```

Change 资产初始化命令会从当前冻结注册表生成 `design/baseline-binding.json`。`workflow.py check-entry/transition` 会在 05、09 和各功能阶段执行 fail-closed 基线门禁。

基线修改必须先 `open-amendment`；修改后必须升级总体版本和受影响域版本，再刷新哈希并审批关闭修订；总体状态处于 `UNDER_AMENDMENT` 时功能阶段全部阻断。基线文件哈希漂移、漏绑 ACTIVE 约束、未批准例外、缺少设计/实现证据或未完成 rebase 均无法通过门禁。完整规则和限制见 `docs/BASELINE-FEATURE-INTERACTION.md` 第 9 节。
