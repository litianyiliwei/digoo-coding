# OpenSpec + Superpowers AI 研发流程工具包

本工具包把 15 个流程阶段拆成可独立加载的 Skill、可复制的 Prompt、基线模板和确定性检查脚本。面向 pen.dev + Figma MCP + OpenSpec + Superpowers + claude/兼容 Agent 工作流。

## 包含内容

- `.claude/skills/<skill-id>/SKILL.md`：20 个项目流程 Skill。
- `prompts/`：与每个阶段 Skill 一一对应的 Prompt；`prompts/00-next-step.md` 是“下一步”入口。
- `workflow-state.json`：跨阶段状态索引；继续前必须核验真实产物和审批状态。
- `.claude/skills/workflow-orchestrator/SKILL.md`：负责“下一步”判定、前置检查和门禁。
- `scripts/next-step.py`：只读状态文件并打印建议的下一阶段，不会自动修改状态。
- `docs/product/`、`docs/architecture/`、`docs/design/`、`docs/adr/`：项目级基线及设计清单模板。
- `openspec/config.yaml`：示例项目上下文和 artifact 规则。**合并前先与已有文件比较，不要直接覆盖已有 OpenSpec 配置。**
- `scripts/`：结构/追踪/OpenAPI/测试/完成前检查，以及无覆盖地初始化 Change 辅助产物模板。
- `docs/SUPERPOWERS-MAPPING.md`：项目阶段与官方 Superpowers 技能的映射。
- `docs/REVIEW-REPORT.md`：本次包的自检报告和已知限制。
- `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv`：定义哪些输出必须有模板、各模板位置和校验门禁。
- `scripts/check-output-template-matrix.py`：检查模板矩阵中登记的模板文件是否真实存在。

## 安装/合并到现有项目

1. 先把 ZIP 解压到临时目录，查看差异；不要直接覆盖项目同名文件。
2. 将 `.claude/skills/`、`prompts/`、`scripts/` 合并到项目根目录。保留已有同名 Skill，先人工比较。
3. 阅读 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv`，据此确定各阶段的模板与质量门禁。把 `docs/` 模板合并进现有文档；不要用模板覆盖真实项目内容。
4. 合并 `openspec/config.yaml` 的 `context`/`rules` 到已有配置；注意 schema 和 rules 需要适配实际业务。
5. 如果尚未初始化 OpenSpec，在项目根目录执行 `openspec init`，工具参数先看 `openspec init --help`。不要用模板包覆盖现有 `openspec/specs/` 或 `openspec/changes/`。
6. 运行：

   ```bash
   python3 scripts/check-package.py
   python3 scripts/next-step.py
   bash scripts/check-required-files.sh
   ```

7. 根据实际仓库目录修改测试命令，再在具体 Change 上运行：

   ```bash
   openspec new change <change-id>
   bash scripts/new-change-assets.sh <change-id>
   # 使用 prompts/ 和对应 Skill 写完 proposal/specs/design/tasks 后，再运行：
   bash scripts/check-change.sh <change-id>
   bash scripts/check-design-assets.sh <change-id> --strict --lint-api
   bash scripts/validate-openapi.sh openspec/changes/<change-id>/api/openapi.yaml
   bash scripts/test-all.sh <frontend-dir> <backend-dir>
   ```

## 重要设计约定

- 项目级基线存放在 `docs/`；功能级变更用 OpenSpec Change 描述。
- OpenSpec `specs/**/spec.md` 描述可观察行为，不放类名/框架/步骤式实现细节。
- 在当前 `spec-driven` 工作流中标准 artifact 是 `proposal.md`、`specs/<capability>/spec.md`、`design.md` 和 `tasks.md`。其他详细设计文件作为辅助材料放进 Change 目录；文件存在不意味着 OpenSpec 自动验证其内容。
- `tasks.md` 必须使用 `- [ ]` / `- [x]`，否则 OpenSpec 无法正确统计任务进度。
- OpenSpec 归档会更新主规格并将整个 Change 移入 archive；归档前必须检查 delta 是否正确、任务与验收是否完成。
- 当你说“下一步”时，先执行 `@workflow-orchestrator` 或复制 `prompts/00-next-step.md`；此能力要求 Agent 能访问仓库文件、终端与技能。新聊天必须重新读取状态和真实产物，不能只依赖对话记忆。
- Superpowers 技能名会随版本演进。实施时先检查安装版本；本包引用官方技能名 `brainstorming`、`writing-plans`、`test-driven-development`、`systematic-debugging`、`requesting-code-review`、`receiving-code-review`、`verification-before-completion` 等。缺失时必须如实报告。
- 所有外部工具（pen.dev、Figma MCP）都必须以实际可访问能力为准；不能把不可读取的链接/字段当作已经审查。
- 并非每段 AI 输出都需要模板；正式、可追踪、供下游消费的产物必须按 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 走模板。
- 每一个 OpenAPI `operationId` 必须在 `design/api-io-mapping.csv` 显式对应一个或多个 `io_id`，每个 IO ID 必须在 `design/io-catalog.csv` 有完整契约。数据库、文件、HTTP/Feign、Redis、MQ、对象存储和搜索都算具体 I/O。无 IO 的纯计算/健康接口只允许作为有理由和审批人的显式例外；不得为了填表虚构 IO。

## 建议流程

需求 → 原型差异与确认 → 产品基线 → 总体架构/领域/公共契约 → 基线审计 → Change 排序 → OpenSpec 规格 → 页面/事件清单 → Figma 审计 → API/前端/后端/测试设计 → Superpowers TDD → 自动化验证 → 人工验收 → 归档和基线回写。

## 不要自动做的事情

本包默认不自动安装依赖、不提交代码、不改 CI、不归档、不发布，也不替业务/设计/架构负责人批准未决规则。
