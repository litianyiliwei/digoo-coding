# 输出模板治理规范

> 语言：简体中文 ｜ [English](TEMPLATE-POLICY.md)

## 1. 原则

不是所有 AI 回复都需要单独模板。需要模板的是可保存、可评审、被下游消费、可自动检查或作为决策/验收证据的正式产物。临时讨论与推理过程不作为正式产物；一旦形成决策，必须回写对应的规格、ADR、设计或验收文档。

| 等级 | 定义 | 约束 | 示例 |
|---|---|---|---|
| L1 强制模板 | 结构稳定、下游依赖、需要追踪或机器检查 | 必填字段/列固定；缺失阻断；版本控制 | 用户故事/AC、OpenSpec proposal/spec/design/tasks、UI 设计契约（HTML 优先）/HTML 设计稿/设计代码/布局断言、OpenAPI、API→IO 映射、统一详细设计（design.md）、测试设计、追踪矩阵、验收记录 |
| L2 推荐模板 | 需要一致结构，但存在分析弹性 | 固定章节；允许按项目删减并注明 N/A 理由 | 需求分析、基线审计、架构基线、技术选型、数据流、领域边界、UI 设计契约（HTML 优先）、提案排序、风险分析 |
| L3 自由表达 | 临时讨论、探索、调试、方案头脑风暴 | 不要求套模板；正式决策需回写 | 临时聊天、错误排查过程、备选方案讨论 |

## 2. 模板、Skill、Prompt、Script 的分工

- 模板：规定交付物的结构、字段、表格和格式。
- Skill：规定分析顺序、工作方法、不能做什么和质量标准。
- Prompt：绑定本次输入、输出路径、范围、基线和执行命令。
- Script：验证字段、ID、关联关系、OpenAPI operationId、API→IO 覆盖、任务复选框和证据状态等可机械判断的规则。
- 人工评审：判断业务真实性、设计质量、风险是否可接受、客户是否同意。自动检查通过不等于业务正确。

## 3. 输出文件位置规则

1. 项目级、跨 Change 稳定复用的内容放在 `docs/product/`、`docs/architecture/`、`docs/adr/`。
2. 单个功能/提案的内容放在 `openspec/changes/<change-id>/`；不要把功能级页面清单和 IO 映射混放到全局文档中。
3. OpenSpec 的核心文件由 OpenSpec schema 生成：`proposal.md`、`specs/**/spec.md`、`design.md`、`tasks.md`。不要另建一套同名“真相来源”。
4. 辅助产物从 `templates/change-assets/` 拷贝，由 `scripts/new-change-assets.sh <change-id>` 无覆盖创建。
5. CSV 用于清单和机器校验；Markdown 用于解释、决策与评审；OpenAPI 使用 YAML/JSON；示意图使用 Mermaid 并保留源文本。
6. 不适用的字段不允许留空：填 `N/A` 并写原因。尚未决策的内容应填 `PENDING` 并标负责人/截止条件；严格门禁时不得有未决项。

## 4. 哪些输出必须模板化

L1 强制模板包含（仅在矩阵中的适用条件成立时强制；不适用必须留下有原因的 N/A 记录）：
- 需求：业务流程（节点表）、业务数据对象目录、RD 矩阵、提案级用户故事/验收标准、业务规则和未决问题。
- OpenSpec：proposal、delta specs、design、tasks。
- 设计：HTML 优先的 UI 设计产物（默认 `design/ui-html/`：README、评审入口 `index.html`、tokens、每个声明平台每个 PAGE 一个自包含 HTML；用户选择时可用可选 Figma 来源）与共享的单文件 `design/figma-audit.md`（设计来源/平台选择、token 实际值、文字样式、每 PAGE 区块规格、设计代码、断言范围、状态覆盖与决策、资产清单、HTML 渲染量测或 MCP 读取记录、UI 评审 APPROVED）；`design/figma-code/`：从 HTML 页面（或可选 Figma）转码的目标框架设计代码；`design/figma-layout.csv`：含平台/视口的运行态断言映射；`design/ui-actions.csv`：功能按钮/图标/链接/菜单/标签页动作映射（跳转地址+入参、API operationId，或用户已确认的本地动作）；`design/figma-assets/README.md`：仅真实图片/SVG 资产清单；**不使用截图**；涉及 UI 时必填，07/08 默认离线消费，仅在来源变化/歧义时按页重读
- 质量门禁（项目在 03 采用静态分析时）：`docs/architecture/quality-gates.json`（机器可读的静态分析栈根目录、工具命令、配置路径、严重度与豁免政策；校验器 `scripts/check-quality-gates.py --strict`；批准来自冻结的 test_quality 基线域）与条件适用的 `templates/change-assets/design/static-waivers.example.json` Change 级豁免结构（文件+规则范围、审批人、过期时间；由 `scripts/check-static-analysis.py` 按 `policy.waiver.allowed` 与 `policy.waiver.max_days` 强制；绝不放入冻结门禁文件）。未采用时记录 `N/A + reason`，并让门禁文件不进入基线。
- 验证：自动化检查结果、代码审查记录、人工验收矩阵、归档清单。

L2 推荐模板包含：系统上下文、技术选型/ADR、部署与模块边界、数据流、逻辑 ERD、领域边界、API 约定、前端规范、测试策略、提案路线图（含可机检的 `Dependencies` 依赖图）和基线审计报告。

L3 自由表达包括工具包随附的 `templates/static-analysis/` 规则包：在 03 选定、08 复制/固定到项目中的 lint/format/type/style 起始配置。它们只是默认值、不是规范；从不在工具包内执行，执行时以冻结的 `quality-gates.json` 为准。

## 5. 项目基线与功能 Change 的交互

- 每个功能 Change 必须使用 `templates/change-assets/design/baseline-impact.md` 记录当前基线版本、适用约束、复用项、冲突、归属分类和审批状态。
- 仅跨功能共享规则、系统/模块边界、核心领域模型、公共 API/前端规范或全局质量门禁变化才提出基线修订；单功能 API、页面、字段迁移、IO 和测试保留在 Change。
- 基线修订使用 `templates/project-baseline/baseline-change-request.md`，获批后更新 `templates/project-baseline/baseline-status.md` 对应项目实例及正式基线文档。
- 具体边界、时点和审批规则以 `process/BASELINE-FEATURE-INTERACTION-zh.md` 为准。

## 6. AI 生成规则

每份 Markdown 正式产物开头必须注明：Change ID（若适用）、状态、来源基线、关联需求/AC ID、生成日期或版本；CSV 通过列字段表达状态/来源，OpenAPI 通过 `info` 与约定扩展字段表达元数据。输出前先读取对应模板；不得自创同义字段替代模板字段，不得自行删除无法填写的字段；未知内容写 `PENDING + 原因 + 责任人/阻塞条件`。生成后运行矩阵中指定的校验器，并报告实际命令与真实结果。
