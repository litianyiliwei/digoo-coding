# 工具包自检报告

## 本次静态检查

本轮增补后的实际校验结果：
- `python3 scripts/check-output-template-matrix.py`：通过（35 个输出登记项，模板路径均存在/为 OpenSpec 内置产物）。
- `python3 scripts/check-package.py`：通过（20 个阶段 Skill、20 份阶段 Prompt、模板矩阵、Bash/Python 语法和 API→IO 回归测试）。
- `bash scripts/test-api-io-mapping.sh`：通过；正向多 IO、缺失映射负向、显式无 API 变更三类场景均符合预期。
- 临时 Change 集成测试：`check-design-assets.sh --strict` 成功核验 `operationId → IO ID → IO catalog`，`check-inventory.py --no-ui --reason ... --strict` 成功核验明确的无 UI 例外；测试用 Change 已删除。
- `openspec/config.yaml` 与 OpenAPI 模板 YAML 可解析。当前环境仍未检测到 OpenSpec CLI，未声称运行 `openspec validate`。

- 已执行 Skill/Prompt 配对检查，19 个目录名与 frontmatter `name` 一致。
- 已执行全部 Shell 脚本 `bash -n` 语法检查和 Python 脚本编译检查。
- 已解析 `openspec/config.yaml` 的 YAML 结构。
- 已用临时 Change 验证 Change 结构检查、辅助模板创建和二次运行不覆盖既有文件。
- 已验证严格模式会阻断仍有占位符的设计/基线/路线图/验收证据，并验证不存在的测试目录与 OpenAPI 文件均不会被误报为通过。
- 用临时 npm fixture 验证测试脚本对成功与失败退出码的处理；用临时 Change 验证结构检查及辅助文件创建时不覆盖已有内容。

- 计划 Skill：19 个（阶段 1—15，阶段 13 拆成 5 个 Skill）。
- 辅助脚本：已覆盖包结构、输出模板矩阵、需求 ID、基线文件、Change、路标、页面/事件清单、追踪矩阵、OpenAPI、API→IO 映射、测试、验收证据和完成前检查；新 Change 模板脚本不会覆盖已有附件。
- Prompt：19 份，与 Skill ID 一一对应。
- Skill front matter：必须包含 `name` 和 `description`，且 `name` 必须与目录名相同。
- Script：逐一执行 Bash 语法检查；Python 脚本做编译/基本执行测试。
- ZIP：解包后再次检查文件存在性、计数和压缩包完整性。

## 已修正的问题

1. OpenSpec 当前 `spec-driven` Change 需使用正确的 `specs/<capability>/spec.md` Delta Spec 路径。
2. `tasks.md` 必须用 Markdown checkbox；纯 bullet 不会被 OpenSpec 正确计入任务。
3. Superpowers 的代码审查技能使用 `requesting-code-review`，而不是臆造的 `code-review`。
4. 测试脚本发现不到可识别的项目或测试入口时必须非零退出，不得假报成功。
5. 工作区检查覆盖 staged 与 unstaged diff，且不自动提交或归档。
6. Skill/Prompt 配对有独立脚本校验。
7. 后端设计新增 `api-io-mapping.csv` 与 `io-catalog.csv`；检查器会核对全部 OpenAPI operationId、一个到多个 IO ID、IO 目录契约及无 API Change 的显式声明。
8. 新增输出模板治理规则和模板矩阵，并由 `check-output-template-matrix.py` 检查矩阵中登记的模板路径。

## 仍需按具体项目适配

- `test-all.sh` 当前支持常见 npm/pnpm/yarn/bun、Maven、Gradle、pytest、Go 测试入口；单体仓库的多模块目录、专用测试命令需要在调用时显式传目录或修改脚本。
- OpenAPI lint 默认尝试本机 Redocly CLI，其次通过 npx 获取；CI 建议锁定工具版本并使用项目已安装依赖。
- 追踪 CSV 只校验结构/唯一 ID/引用闭合，不能自动判断业务需求是否正确或覆盖完整。
- 视觉一致性、需求合理性、架构决策与客户验收仍需人审。
- 当前环境未提供用户的实际产品代码仓库；未执行项目级测试/构建。临时 Change 使用 `--no-openspec` 仅验证脚本自身的结构检查逻辑，不代表 OpenSpec CLI 语义验证通过。当前执行环境未检测到 OpenSpec CLI，因此实际 `openspec validate`、归档和 schema 语义校验未执行；需要在用户项目安装/初始化后的环境中运行。
- 本环境未检测到 ShellCheck（如未安装），故只运行了 Bash 语法检查，未声称通过 ShellCheck。

## 官方参考（用于按实际版本核对）

- OpenSpec CLI：https://openspec.dev/docs/cli
- OpenSpec spec-driven schema：https://openspec.dev/docs/schemas/spec-driven
- OpenSpec project config：https://openspec.dev/docs/configuration/config-yaml
- OpenCode Agent Skills：https://docs.opencode.ai/docs/skills/
- Superpowers 官方仓库：https://github.com/obra/superpowers


## 追加复核（workflow continuation）

- 新增 `workflow-orchestrator` 与 `prompts/00-next-step.md`，支持仓库可访问的 Agent 根据 `workflow-state.json` 判断下一阶段。
- 新增 `scripts/next-step.py`，只读状态并输出下一 Prompt/Skill，不自动修改状态。
- 需求发现阶段明确要求优先使用可用的 Superpowers `brainstorming`；OpenSpec 只读取已有规格，不提前创建 Change。
- 每个阶段 Prompt 与 Skill 都补充真实工具调用协议：检查技能是否存在、使用宿主机制加载、真实执行 OpenSpec CLI、报告未执行项。
- 20 个 Skill / 20 个 Prompt 的配对由 `scripts/check-package.py` 检查。


## 交付物交接升级（2026-10-30）

- 新增 `docs/STEP-ARTIFACT-CONTRACTS.json` 与 `.md`：为 20 个 Skill 定义输入、输出、下游消费文件、审批点和门禁。
- 所有 20 个 Skill 与 20 个 Prompt 均加入强制输入/输出/交接条款。
- 新增 `templates/workflow/step-handoff-report.md`，要求每步展示实际读取、生成文件、摘要、追踪关系、检查结果、阻断项和下一步输入。
- 新增 `scripts/check-step-contracts.py` 并纳入 `check-package.py`；`scripts/next-step.py` 现在也会打印所选阶段的输入、输出和下一阶段消费内容。
- 新增工具链检查报告模板并登记到输出模板矩阵。
- 本次验证：`python3 scripts/check-package.py` 通过；该检查包含 20 Skill/20 Prompt 配对、交接契约完整性、模板矩阵、Bash/Python 语法和 API→IO 回归测试。
- 限制：本次仅对工具包本身进行静态/脚本检查；没有在用户的真实项目仓库执行 OpenSpec CLI、构建、部署或业务验收。

## 环境适配修复（2026-10-30，Windows + .claude/skills）

在本机实际运行检查脚本后修复了打包环境与安装环境的错位：

1. Skill 目录解析：`check-package.py`、`check-step-contracts.py`、`next-step.py` 原硬编码 `.agents/skills/`，实际技能安装在 `.claude/skills/`。现改为优先 `.claude/skills/`、回退 `.agents/skills/`，并同步修正所有 Prompt/手册中的路径引用。
2. Prompt 计数：`prompts/workflow-prompts.md` 是汇总文档，不再计入 20 份阶段 Prompt。
3. OpenSpec 包装器 Skill（`openspec-apply-change` 等 6 个）改为与 `.claude/commands/opsx/<command>.md` 显式配对，不再误报缺 Prompt。
4. Python 兼容：`test-api-io-mapping.sh`、`check-design-assets.sh`、`test-all.sh` 由硬编码 `python3` 改为 `python3`/`python` 自动回退（Windows 常见仅装 `python`）。
5. 手册目录树中 `docs/design/` 的 page-inventory/interaction-map 后缀修正为 `.csv`；补建 `docs/project/` 目录（阶段 01/08 契约输出路径）。

本次实际验证结果：
- `python scripts/check-package.py`：通过（26 个 Skill，其中 20 个阶段 Skill；20 份阶段 Prompt；交接契约、模板矩阵、Bash/Python 语法、API→IO 回归测试均通过）。
- `python scripts/next-step.py`：通过，正确输出 `NEXT_STEP=01-project-bootstrap` 及契约信息。
- `bash scripts/check-required-files.sh`：通过（存在基线占位符时仅 WARN，不阻断）。
- `bash scripts/check-required-files.sh --strict`：按预期失败（基线尚未填写，占位符仍在；阶段 08 前应保持此状态）。
- 限制：本机未检测到 OpenSpec CLI，`openspec validate` 等仍未执行。
