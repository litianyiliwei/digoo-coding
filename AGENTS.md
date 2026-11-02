# AGENTS.md — 智慧农业项目仓库约定

> 状态：APPROVED（2026-10-30 由 project-bootstrap 阶段创建，2026-10-30 经用户确认；仓库尚无源代码，技术栈相关约定为 PENDING，待架构阶段补充）
> 下游消费：所有阶段的 Agent（Claude/OpenCode 等）；需求发现（阶段 02）起必须遵守本文件的流程入口与模板政策。

## 项目目标

智慧农业项目。当前仓库仅包含 AI 研发流程工具包（Skills、Prompts、模板、检查脚本），尚无业务源代码。

## 流程入口

- 当用户说"下一步/继续/接着做"时，先加载 `workflow-orchestrator` Skill（或 `prompts/00-next-step.md`），依据 `workflow-state.json` 与真实产物判定唯一安全的下一阶段。
- 每阶段开始前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中对应 Skill 的契约记录。
- 阶段结束使用 `templates/workflow/step-handoff-report.md` 展示交接报告；产物必须落盘到契约指定路径，不得只在聊天中输出。

## 模板与产物规则

- 正式产物遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不得删除模板字段；未知项写 `PENDING` 并说明原因与责任人/阻塞条件；不适用项写 `N/A` 并写理由。
- 项目级基线放 `docs/product/`、`docs/architecture/`、`docs/adr/`；单个功能内容放 `openspec/changes/<change-id>/`。
- 每份 Markdown 正式产物开头注明：Change ID（若适用）、状态、来源基线、关联需求/AC ID、生成日期或版本。

## OpenSpec 约定

- 配置见 `openspec/config.yaml`（schema: spec-driven）；标准 artifact 为 `proposal.md`、`specs/<capability>/spec.md`、`design.md`、`tasks.md`。
- `tasks.md` 必须使用 `- [ ]` / `- [x]` 复选框。
- specs 只写外部可观察行为；类名/框架/实现步骤放 design.md。
- 每个 OpenAPI `operationId` 必须在 `design/api-io-mapping.csv` 映射到至少一个真实 IO，IO 契约写在 `design/io-catalog.csv`。
- 归档（openspec archive）前必须人工批准，不得用 `-y` 绕过。

## 检查脚本

- 包自检：`python3 scripts/check-package.py`
- 下一阶段建议（只读）：`python3 scripts/next-step.py`
- 基线文件检查：`bash scripts/check-required-files.sh`
- 各阶段校验命令见 `scripts/README.md`；脚本 fail-closed，不可伪造通过结果。

## 语言与风格

- 项目输出语言默认中文；代码、API 字段和标识符遵循仓库已有规范（当前 PENDING，待首个功能实现时确定）。

## Agent 行为边界

- 不自动安装依赖、不提交代码、不改 CI、不归档、不发布，不替业务/设计/架构负责人批准未决规则。
- 不覆盖既有文件；覆盖/修改既有 AGENTS.md 或配置前需用户批准。
- Superpowers 技能名会随版本演进，实施时先确认真实安装与可用性，缺失时如实报告。
- 外部工具（pen.dev、Figma MCP）以实际可访问能力为准，不得把不可读取的链接/字段当作已审查。
