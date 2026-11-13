# 阶段方法与接口边界流程改造 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 让 02–07 的 OpenSpec/Superpowers 参与从“提示词建议”变成“可审、可门禁的方法证据”，并为 HTTP API、原生桥接、设备、第三方、异步、文件等跨边界接口增加唯一目录与机器检查。

**Architecture:** 复用现有“Skill/Prompt 定方法、scripts 定门禁、contract JSON 定交接”的分层。方法要求在 `STEP-ARTIFACT-CONTRACTS.json` 的 `method_policy` 中集中声明，由 `scripts/method_evidence.py` 校验 evidence 的 `methods` 块；接口边界用新的 `design/interface-catalog.csv` 承载，不改变现有 `api-io-mapping.csv` / `io-catalog.csv` 的 API→IO 语义。

**Tech Stack:** Python 3.11、Markdown、CSV、JSON；现有 `scripts/check-*.py` 与 `scripts/workflow.py`。

**Spec:** 本次会话的审计结论与用户确认的推荐方案（2026-11-13）。

## Global Constraints

- 不直接编辑 `workflow-state.json`；状态只能由 `scripts/workflow.py` 命令管理。
- 不写入当前阶段（02）之后的阶段产物；只改流程工具文件（prompts/skills/scripts/templates/docs 中的流程文档）。
- 所有检查 fail-closed；缺字段、占位符、未批准项不得放行。
- 项目输出语言中文；新增脚本只用标准库，保持 Windows/Linux 兼容。
- 不提交、不推送、不归档、不安装依赖。

## Review Focus

- 旧 Change 的 evidence 没有 `methods` 时，不能因为新门禁而无法重跑；只对 02–10 的新 transition 强制，历史记录不追溯。
- 接口目录不能把“仅 HTTP API”的 Change 误判为缺失；`N/A` 必须在 `design.md` 和 evidence 中都有理由。
- `interface-catalog.csv` 的 `HTTP_API` 行必须与 OpenAPI operationId 双向一致；不能出现目录有、OpenAPI 无的接口。
- 方法证据不能只写“已使用技能”而没有问题/备选/决策；校验器必须要求最小内容。
- 新增输出必须同步 `output_consumption`、`STAGE-IO-OVERVIEW.md` 与 `OUTPUT-TEMPLATE-MATRIX.csv`，否则 `check-package.py` 会失败。

---

### Task 1: 方法证据校验核心

**Files:**
- Create: `scripts/method_evidence.py`
- Modify: `scripts/workflow.py`
- Test: `scripts/test-workflow-runtime.py`

**Interfaces:**
- Produces: `validate_methods(evidence: dict, step_id: str, root: Path) -> list[str]`（返回错误列表，空表示通过）。
- Produces: `scripts/workflow.py check-methods --step <id> --evidence <path>` 子命令。
- Consumes: `docs/STEP-ARTIFACT-CONTRACTS.json` 的 `method_policy`（Task 4 写入；Task 1 先内置最小策略，Task 4 改为读取契约）。

- [x] **Step 1: 写失败测试**：在 `test-workflow-runtime.py` 增加 `test_method_evidence_required_for_stage_03` 与 `test_method_evidence_passes_with_questions_and_alternatives`，构造 stage 03 evidence，分别断言缺少 `methods` 时报错、含 4 个问题/2 个备选/1 个决策且 evidence 文件存在时通过。
- [x] **Step 2: 运行测试确认失败**：`python scripts/test-workflow-runtime.py`。
- [x] **Step 3: 实现**：`method_evidence.py` 定义 `METHOD_POLICY` 与 `validate_methods`；`workflow.py` 导入并在 `parse_evidence` 中对 02–10 调用；新增 `check-methods` 子命令。
- [x] **Step 4: 运行测试确认通过**：`python scripts/test-workflow-runtime.py`。

### Task 2: 方法证据载体与文档

**Files:**
- Modify: `templates/workflow/stage-evidence.schema.json`
- Modify: `templates/workflow/stage-evidence.example.json`
- Modify: `templates/workflow/step-handoff-report.md`
- Modify: `docs/P0-RUNTIME-GOVERNANCE.md`

- [x] **Step 1:** schema 增加 `methods` 数组及字段（skill/mode/summary/questions/alternatives/decisions/open_questions/artifact_section/evidence/reason）。
- [x] **Step 2:** example 增加一条 stage 03 的 methods 示例，路径指向 `docs/architecture/technology-decisions.md#1. 技术选型访谈记录`。
- [x] **Step 3:** handoff 报告增加 `## 4. 方法证据`（技能/模式、问题、备选、决策、未决项、产物落点、证据路径），后续章节顺延。
- [x] **Step 4:** `P0-RUNTIME-GOVERNANCE.md` 增加“方法证据门禁”说明与 `check-methods` 命令。

### Task 3: 参与矩阵与阶段内头脑风暴模式

**Files:**
- Modify: `docs/SUPERPOWERS-MAPPING.md`
- Modify: `docs/PROCESS-MAP.md`

- [x] **Step 1:** 在 `SUPERPOWERS-MAPPING.md` 增加 OpenSpec 参与矩阵：02–10 每阶段 required/allowed/prohibited 命令与技能；明确 `openspec-explore` 只读、`openspec-propose` 禁用、`openspec-update-change` 仅 05/07、`openspec-sync-specs`/`archive` 仅 10 审批后。
- [x] **Step 2:** 增加“阶段内 brainstorming 模式”：使用提问/比较方法，结论写现有阶段产物，不另写 `docs/superpowers/specs/`，阶段评审即批准。
- [x] **Step 3:** `PROCESS-MAP.md` 的阶段 02–07 自动检查列补 `workflow.py check-methods`；07 补 `check-interface-catalog.py`；增加方法矩阵入口链接。

### Task 4: 契约中的方法策略

**Files:**
- Modify: `docs/STEP-ARTIFACT-CONTRACTS.json`
- Modify: `docs/STEP-ARTIFACT-CONTRACTS.md`
- Modify: `scripts/check-step-contracts.py`

- [x] **Step 1:** JSON 顶层增加 `method_policy`，02–10 每阶段列 required skills 与最小问题/备选/决策数；`method_evidence.py` 改为优先读取该契约，缺失时用内置默认值。
- [x] **Step 2:** MD 增加“方法证据政策”章节，与 JSON 对齐。
- [x] **Step 3:** `check-step-contracts.py` 校验 `method_policy` 覆盖 02–10，且每个 required skill 名称出现在对应 Skill 与 Prompt。

### Task 5: 阶段问题清单

**Files:**
- Modify: `.claude/skills/requirements-analysis/SKILL.md`、`prompts/02-requirements-analysis.md`
- Modify: `.claude/skills/project-architecture-baseline/SKILL.md`、`prompts/03-project-architecture-baseline.md`
- Modify: `.claude/skills/feature-requirements/SKILL.md`、`prompts/05-feature-requirements.md`
- Modify: `.claude/skills/detailed-design/SKILL.md`、`prompts/07-detailed-design.md`
- Modify: `.claude/skills/figma-design-review/SKILL.md`、`prompts/06-figma-design-review.md`
- Modify: `.claude/skills/implementation-orchestrator/SKILL.md`、`prompts/08-implementation-orchestrator.md`
- Modify: `.claude/skills/independent-verifier/SKILL.md`、`prompts/09-independent-verification.md`
- Modify: `.claude/skills/acceptance-audit/SKILL.md`、`prompts/10-acceptance-audit.md`

- [x] **Step 1:** 03 增加“平台与集成边界访谈”清单（端形态、跨端方案、uni-app 原生插件/JS Bridge、设备协议、第三方平台、边界类型、每条边界的契约字段）。
- [x] **Step 2:** 05 增加场景完整性清单（平台权限、离线/弱网、推送/深链、多端差异、失败重试、幂等/并发）。
- [x] **Step 3:** 07 增加 `### 接口边界清单` 与 `interface-catalog.csv` 要求；02 增加业务异常清单；06 增加多端状态清单；08/09/10 增加接口测试与验收要求。
- [x] **Step 4:** 每个阶段写清方法证据的 `methods` 块与 `workflow.py check-methods` 命令。

### Task 6: 接口目录模板与检查

**Files:**
- Create: `templates/change-assets/design/interface-catalog.csv`
- Create: `scripts/check-interface-catalog.py`
- Create: `scripts/test-interface-catalog.py`
- Modify: `templates/change-assets/design/test-cases.csv`
- Modify: `scripts/check-test-cases.py`
- Modify: `scripts/check-design-sections.py`
- Modify: `scripts/check-design-assets.sh`
- Modify: `docs/OUTPUT-TEMPLATE-MATRIX.csv`

- [x] **Step 1:** 新增 CSV 模板（interface_id/interface_type/source/target/protocol/operation/input_contract/output_contract/auth/error_semantics/timeout_ms/retry_policy/idempotency/versioning/test_ids/owner/notes）。
- [x] **Step 2:** `check-interface-catalog.py` 校验必填、类型、HTTP operationId 双向一致、TEST/Traceability 关联、`--require-native` 时至少一条 `NATIVE_BRIDGE`。
- [x] **Step 3:** `test-cases.csv` 增加 `interface_ids` 列；`check-test-cases.py` 在目录存在时校验每个接口至少一个 TEST。
- [x] **Step 4:** `check-design-sections.py` 要求 `### 接口边界清单`，非 N/A 时必须引用 `interface-catalog.csv`；`check-design-assets.sh` 在文件存在时运行接口检查。
- [x] **Step 5:** 模板矩阵增加“接口边界清单”行；`test-interface-catalog.py` 覆盖缺失字段、HTTP 不一致、缺 TEST 三类失败。

### Task 7: 07/08/09/10 契约与追踪接线

**Files:**
- Modify: `docs/STEP-ARTIFACT-CONTRACTS.json`（07 output、08/09/10 input、output_consumption、gate）
- Modify: `docs/STEP-ARTIFACT-CONTRACTS.md`
- Modify: `docs/STAGE-IO-OVERVIEW.md`（由脚本生成）
- Modify: `docs/PROCESS-MAP.md`
- Modify: `docs/OUTPUT-TEMPLATE-MATRIX.csv`

- [x] **Step 1:** 07 outputs 增加 `design/interface-catalog.csv`（条件适用）；08/09/10 inputs 增加该文件。
- [x] **Step 2:** `output_consumption` 增加 07 → 08/09/10；07 gate 增加 `check-interface-catalog.py --strict`（有接口时）。
- [x] **Step 3:** 运行 `python scripts/stage-io-report.py --out docs/STAGE-IO-OVERVIEW.md` 重新生成。
- [x] **Step 4:** `check-output-consumption.py`、`check-output-template-matrix.py`、`stage-io-report.py --check` 通过。

### Task 8: 全量回归

- [x] **Step 1:** `python scripts/check-package.py`
- [x] **Step 2:** `python scripts/test-workflow-runtime.py`
- [x] **Step 3:** `python scripts/test-interface-catalog.py`
- [x] **Step 4:** `python scripts/check-step-contracts.py`、`check-output-consumption.py`、`check-output-template-matrix.py`、`stage-io-report.py --check`
- [x] **Step 5:** 检查 `git diff`，确认没有写入 `workflow-state.json` 或 03+ 阶段产物。
