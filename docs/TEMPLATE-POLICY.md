# 输出模板治理规范

## 1. 原则

不是所有 AI 回复都需要单独模板。需要模板的是可保存、可评审、被下游消费、可自动检查或作为决策/验收证据的正式产物。临时讨论与推理过程不作为正式产物；一旦形成决策，必须回写对应的规格、ADR、设计或验收文档。

| 等级 | 定义 | 约束 | 示例 |
|---|---|---|---|
| L1 强制模板 | 结构稳定、下游依赖、需要追踪或机器检查 | 必填字段/列固定；缺失阻断；版本控制 | 用户故事/AC、OpenSpec proposal/spec/design/tasks、页面/事件清单、OpenAPI、API→IO 映射、统一详细设计（design.md）、测试设计、追踪矩阵、验收记录 |
| L2 推荐模板 | 需要一致结构，但存在分析弹性 | 固定章节；允许按项目删减并注明 N/A 理由 | 需求分析、原型审计、架构基线、技术选型、数据流、领域边界、Figma 审计、提案排序、风险分析 |
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
- 设计：Figma 设计与评审产物（单文件 `design/figma-audit.md`：token 实际值、文字样式、每 PAGE 区块规格、设计代码、断言范围、状态覆盖与决策、资产清单、MCP 读取记录、UI 评审 APPROVED；`design/figma-code/`：设计代码（get_design_context 落盘）；`design/figma-layout.csv`：运行态断言映射；`design/figma-assets/README.md`：仅真实图片/SVG 资产清单；**不使用截图**；涉及 UI 时必填，07/08 默认离线消费，仅在版本变化/歧义时按页重读）、OpenAPI、统一详细设计（design.md 五节）、测试用例矩阵（test-cases.csv）、API→IO 映射、IO 目录、需求追踪矩阵。
- 验证：自动化检查结果、代码审查记录、人工验收矩阵、归档清单。

L2 推荐模板包含：系统上下文、技术选型/ADR、部署与模块边界、数据流、逻辑 ERD、领域边界、API 约定、前端规范、测试策略、提案路线图和基线审计报告。

## 5. 项目基线与功能 Change 的交互

- 每个功能 Change 必须使用 `templates/change-assets/design/baseline-impact.md` 记录当前基线版本、适用约束、复用项、冲突、归属分类和审批状态。
- 仅跨功能共享规则、系统/模块边界、核心领域模型、公共 API/前端规范或全局质量门禁变化才提出基线修订；单功能 API、页面、字段迁移、IO 和测试保留在 Change。
- 基线修订使用 `templates/project-baseline/baseline-change-request.md`，获批后更新 `templates/project-baseline/baseline-status.md` 对应项目实例及正式基线文档。
- 具体边界、时点和审批规则以 `docs/BASELINE-FEATURE-INTERACTION.md` 为准。

## 6. AI 生成规则

每份 Markdown 正式产物开头必须注明：Change ID（若适用）、状态、来源基线、关联需求/AC ID、生成日期或版本；CSV 通过列字段表达状态/来源，OpenAPI 通过 `info` 与约定扩展字段表达元数据。输出前先读取对应模板；不得自创同义字段替代模板字段，不得自行删除无法填写的字段；未知内容写 `PENDING + 原因 + 责任人/阻塞条件`。生成后运行矩阵中指定的校验器，并报告实际命令与真实结果。
