# OpenSpec + Superpowers AI 研发流程落地手册

版本：1.0\
适用：pen.dev + Figma MCP + OpenSpec + Superpowers + 前后端仓库\
原则：项目级基线先行、功能级 Change
交付、人工审批设门禁、脚本做确定性校验。

------------------------------------------------------------------------

## 1. 总体优化建议

原流程方向正确，但建议调整为 15
个阶段，并增加变更影响分析、自动化质量门禁和归档复盘。

1.  项目初始化与工具链检查
2.  需求发现与整理：业务流程、用例、用户故事、约束、验收标准
3.  pen.dev 原型评审：用页面流程检查需求遗漏，再与客户确认
4.  项目级产品基线：术语、角色权限、业务规则、非功能需求
5.  项目总体架构设计：前后端技术选型、部署、数据流、系统边界
6.  项目级数据与领域基线：逻辑 ERD、领域边界、公共领域概念、事务边界
7.  项目级接口/前端/测试规范：公共契约、错误码、鉴权、测试策略
8.  基线审计与冻结：输出可供各功能提案复用的基线
9.  提案拆分、依赖排序与路线图
10. 功能级 OpenSpec Change：需求细化、原型更新、验收标准、影响分析
11. 页面/元素/事件清单：从确认后的提案需求和 pen.dev 导出
12. Figma UI 设计与 MCP 审计：视觉稿与页面元素映射
13. 功能级详细设计：OpenAPI、前端设计、后端设计、测试用例
14. 实现与验证：前端、后端按 TDD 实施，集成测试与代码审查
15. 人工验收、归档与基线回写

### 关键调整

-   把原第 3
    步拆成"总体架构""数据/领域基线""公共契约与测试规范"，避免项目级和功能级设计混在一起。
-   提案应按可独立验收的业务能力切分，而不是按前端、后端或数据库切分。
-   OpenSpec 的 `proposal/specs/design/tasks`
    用于描述一次功能变更；项目级长期有效的决策放在
    `docs/product/`、`docs/architecture/`
    等基线文档中，并由审计脚本检查。
-   Figma/pen.dev 是设计来源，但不应成为唯一规格来源。关键业务规则、API
    契约和验收条件必须落到仓库。
-   第 13 步明确拆分为
    `feature-design`、`api-contract-design`、`frontend-detail-design`、`backend-detail-design`、`test-design`。后端详细设计必须明确每个接口涉及的
    Mapper/SQL、领域类/方法、File I/O、Feign、Redis、MQ 等 Client
    的职责与契约。
-   前后端可以并行开发，但必须先冻结 API 契约；契约变更要更新
    OpenAPI、测试和两端实现。
-   Superpowers 不是项目规格管理器。用它约束
    brainstorming、writing-plans、TDD、systematic-debugging、code-review、verification-before-completion
    等工作方式；具体可用 Skill 名称以当前安装版本为准。
-   脚本只负责可确定性验证：必需文件、Front Matter、OpenAPI
    格式、链接/追踪
    ID、测试、lint、构建、差异检查。脚本不能代替需求判断或人工验收。

------------------------------------------------------------------------

## 2. 目录建议

``` text
repo/
├── openspec/
│   ├── specs/                         # OpenSpec 当前规格（按实际 CLI 版本）
│   └── changes/
│       └── <change-id>/
│           ├── proposal.md
│           ├── design.md
│           ├── tasks.md
│           └── specs/<capability>/spec.md
├── docs/
│   ├── product/
│   │   ├── glossary.md
│   │   ├── workflows.md
│   │   ├── use-cases.md
│   │   ├── user-stories.md
│   │   ├── business-rules.md
│   │   └── acceptance-policy.md
│   ├── architecture/
│   │   ├── system-context.md
│   │   ├── technology-decisions.md
│   │   ├── containers-and-deployment.md
│   │   ├── data-flows.md
│   │   ├── logical-erd.md
│   │   ├── domain-boundaries.md
│   │   ├── api-conventions.md
│   │   ├── frontend-conventions.md
│   │   └── test-strategy.md
│   ├── design/
│   │   ├── page-inventory.csv
│   │   ├── interaction-map.csv
│   │   └── figma-audit.md
│   └── adr/
├── .claude/skills/
│   ├── project-bootstrap/SKILL.md
│   ├── requirements-analysis/SKILL.md
│   ├── prototype-audit/SKILL.md
│   ├── product-baseline/SKILL.md
│   ├── project-architecture-baseline/SKILL.md
│   ├── data-domain-baseline/SKILL.md
│   ├── project-contract-baseline/SKILL.md
│   ├── baseline-audit/SKILL.md
│   ├── proposal-planning/SKILL.md
│   ├── feature-requirements/SKILL.md
│   ├── page-interaction-inventory/SKILL.md
│   ├── figma-ui-audit/SKILL.md
│   ├── feature-design/SKILL.md
│   ├── api-contract-design/SKILL.md
│   ├── frontend-detail-design/SKILL.md
│   ├── backend-detail-design/SKILL.md
│   ├── test-design/SKILL.md
│   ├── implementation-orchestrator/SKILL.md
│   └── acceptance-audit/SKILL.md
└── scripts/
    ├── check-required-files.sh
    ├── check-change.sh
    ├── validate-openapi.sh
    ├── test-all.sh
    └── verify-before-completion.sh
```

> 目录只是建议。先用当前安装的 OpenSpec CLI
> 查看真实命令与目录约定，不要让脚本假设所有版本都完全相同。项目中已有约定优先于本模板。

------------------------------------------------------------------------

## 3. 每个阶段的 Skill、Prompt 与 Script

以下 Skill 内容可以分别保存为对应的 `SKILL.md`。Prompt
是每次调用时复制并填入变量的任务模板。Script
是仓库内可执行的基础脚本；按项目技术栈补充具体命令。

### 阶段 1：项目初始化与工具链检查

**Skill：** `project-bootstrap`

**SKILL.md**

``` markdown
---
name: project-bootstrap
description: 初始化 AI 研发工作区，核对 OpenSpec、Superpowers、pen.dev/Figma 产物路径及仓库约定。
---

# 工作规则
1. 先检查仓库现状，不覆盖已有约定。
2. 读取 README、目录结构、构建文件、CI 配置和 OpenSpec 配置。
3. 检查 OpenSpec CLI 的当前版本与可用命令；不得凭记忆臆造 CLI 参数。
4. 检查 Superpowers 是否安装及可用 Skill；不可用时报告，不得声称已执行。
5. 仅创建缺失的目录与模板，禁止覆盖业务文件。
6. 输出工具状态、缺口、初始化变更清单和下一步建议。
7. 未经用户批准，不安装依赖、不修改 CI、不提交代码。
```

**Prompt**

``` text
请执行 project-bootstrap。
仓库路径：<repo>
项目背景：<project-summary>
目标：建立 OpenSpec + Superpowers 的研发工作区。
先检查仓库和工具实际状态，再提出最小初始化方案。不得覆盖已有文件。
输出：工具状态表、建议目录、需要创建/修改的文件、待确认问题。
完成后运行仓库内可用的检查脚本；没有执行的检查必须标记为“未执行”。
```

**Script：** 使用 `scripts/check-required-files.sh`（见第 4
节）；工具版本检查命令按本机安装情况执行。

------------------------------------------------------------------------

### 阶段 2：需求发现与整理

**Skill：** `requirements-analysis`

**SKILL.md**

``` markdown
---
name: requirements-analysis
description: 将访谈、现有文档和业务材料整理为可追踪的业务流程、用例、用户故事与验收标准。
---

# 输入
访谈记录、现有需求、业务资料、角色清单、限制条件。

# 流程
1. 区分已确认事实、合理推断、待确认问题，不得把推断写成事实。
2. 梳理参与者、触发条件、前置条件、主流程、替代流程、异常流程、后置条件。
3. 建立业务流程 → 用例 → 用户故事 → 验收标准的追踪 ID。
4. 识别权限、数据范围、幂等、并发、审计、性能、安全、可访问性等非功能要求。
5. 对每条需求检查可测试性、边界条件和失败路径。
6. 将冲突与缺失整理成问题清单，等待产品/客户确认。
7. 不在此阶段决定数据库表结构或实现细节。
# 输出
docs/product/workflows.md、use-cases.md、user-stories.md、business-rules.md、open-questions.md。
```

**Prompt**

``` text
请执行 requirements-analysis，分析以下材料：
<materials>
<paste-or-reference>
</materials>

请输出：
1. 业务流程（含主流程、替代流程、异常流程）
2. 功能用例
3. 用户故事列表（统一 ID，例如 US-001）
4. 每个故事的 Given/When/Then 验收标准
5. 业务规则、权限与非功能需求
6. 需求冲突、缺口和需要客户回答的问题
7. 需求追踪矩阵：来源 → 流程 → 用例 → 故事 → 验收标准

要求：标记确认状态；不擅自补齐未知业务规则；不提前设计实现方案。
```

**Script：** 此阶段以文档审阅为主；后续 `check-change.sh` 检查 ID
与必需文件。

------------------------------------------------------------------------

### 阶段 3：pen.dev 原型评审与需求澄清

**Skill：** `prototype-audit`

**SKILL.md**

``` markdown
---
name: prototype-audit
description: 用页面和交互原型反查用户故事完整性，并把原型差异转为待确认需求。
---

# 工作规则
1. 为每个用户故事标注涉及的页面、入口和完成状态。
2. 逐页检查默认、加载、空数据、成功、失败、无权限、边界值、重复提交等状态。
3. 检查返回、取消、关闭、刷新、跳转、表单校验、未保存提示等交互。
4. 原型中出现但需求中没有定义的元素，列为“待确认”，不直接视为已批准需求。
5. 需求中要求但原型缺失的页面/状态，列为遗漏。
6. 输出原型—故事覆盖矩阵和客户确认问题。
7. 客户确认后记录决策日期、负责人和版本。
```

**Prompt**

``` text
请执行 prototype-audit。
需求基线：<requirements-docs>
pen.dev 原型链接/导出：<prototype>
请逐个用户故事检查原型覆盖情况，并逐个页面检查状态和交互完整性。
输出：
- 故事 ID → 页面 → 元素/交互 → 覆盖状态
- 原型存在但需求未定义的内容
- 需求存在但原型缺失的内容
- 空/错/加载/权限/边界状态检查
- 客户澄清问题及建议决策
不要直接修改已确认的业务规则；先列差异，确认后再更新需求。
```

**Script：**
不建议用脚本判断视觉原型是否正确；可以将人工确认后的导出清单纳入版本控制。

------------------------------------------------------------------------

### 阶段 4：项目级产品基线

**Skill：** `product-baseline`

**SKILL.md**

``` markdown
---
name: product-baseline
description: 建立跨提案复用的产品规则基线，避免各功能提案重复定义或互相矛盾。
---

1. 统一术语、角色、权限、业务实体名称。
2. 汇总跨流程的业务规则、状态机、数据所有权和审计要求。
3. 明确全局错误处理、时区、金额精度、分页、软删除等产品规则（仅在项目确实需要时）。
4. 标记已确认、待确认、废弃规则；保留决策来源。
5. 将功能专属规则留在对应 OpenSpec Change。
6. 不在本阶段定义所有具体数据库字段。
```

**Prompt**

``` text
请执行 product-baseline。
输入：已确认的业务流程、用例、用户故事、原型评审结论。
建立项目级产品基线：术语表、角色/权限模型、跨功能业务规则、核心状态机、全局异常语义。
将内容分为“全局基线”和“功能级规则”，每条规则给出 ID 和来源。
对冲突只提出决策选项，不自行选择。
输出至 docs/product/，并列出待审批项。
```

**Script：** `check-required-files.sh`
检查文件存在；业务一致性需要人工评审。

------------------------------------------------------------------------

### 阶段 5：项目总体架构设计

**Skill：** `project-architecture-baseline`

**SKILL.md**

``` markdown
---
name: project-architecture-baseline
description: 设计项目级系统边界、技术选型、部署、前后端结构和端到端数据流。
---

1. 描述用户、外部系统、前端、后端服务、存储、消息系统之间的边界。
2. 给出技术选型及备选方案、取舍理由、约束和 ADR。
3. 绘制关键数据流与调用链，标记同步/异步、可信边界和失败处理。
4. 明确鉴权、授权、日志、指标、追踪、配置、密钥管理和部署策略。
5. 明确模块边界、依赖方向、事务边界和一致性策略。
6. 标记性能、可用性、容量、安全和可观测性要求。
7. 不把某一功能的所有类/方法提前设计到项目基线。
```

**Prompt**

``` text
请执行 project-architecture-baseline。
输入：产品基线、系统约束、团队能力、部署环境。
输出：
1. 系统上下文图与模块/容器图
2. 前后端技术栈及选型比较
3. 关键业务数据流、外部调用流、异步消息流
4. 安全与权限、事务和一致性、可观测性方案
5. 部署与环境配置策略
6. 主要风险、架构决策 ADR、未决问题
7. 项目级约束和功能提案可以自由决定的范围
不要设计单个提案的具体 Mapper、Feign 方法或领域类方法。
```

**Script：** 将架构图以 Mermaid/Markdown 保存；代码仓库中可对 Mermaid
做语法检查，但架构合理性由评审负责。

------------------------------------------------------------------------

### 阶段 6：项目级数据与领域基线

**Skill：** `data-domain-baseline`

**SKILL.md**

``` markdown
---
name: data-domain-baseline
description: 确定项目级逻辑数据模型、领域边界、公共实体和数据所有权。
---

1. 识别核心业务概念、领域边界、实体/值对象及其生命周期。
2. 绘制逻辑 ERD，说明实体关系、数据所有权和跨模块引用。
3. 定义命名、主键、审计字段、时间字段、软删除、版本控制等通用规范。
4. 明确事务边界、唯一性约束、并发控制和数据保留策略。
5. 仅定义稳定的项目级概念，不提前穷举每个提案的全部字段。
6. 功能需要突破既定领域边界或改变共享实体时，触发基线变更评审。
```

**Prompt**

``` text
请执行 data-domain-baseline。
基于已确认业务规则与总体架构，输出逻辑 ERD、领域边界、核心实体及关系、数据所有权、事务边界、数据一致性与并发策略。
将每项标记为“项目级稳定约束”或“功能级待细化”。
不直接生成所有物理表 DDL；指出哪些决策必须在提案设计时再确定。
```

**Script：** 基线审计时检查 ERD、领域边界、命名规范等文档是否存在。

------------------------------------------------------------------------

### 阶段 7：项目级接口、前端与测试规范

**Skill：** `project-contract-baseline`

**SKILL.md**

``` markdown
---
name: project-contract-baseline
description: 建立跨功能复用的 API、前端工程和测试规范。
---

1. 约定 API 版本、认证、授权、错误结构、分页、幂等、并发冲突和兼容性。
2. 约定前端路由、模块组织、状态管理、请求层、表单校验和错误提示。
3. 约定前后端测试分层、契约测试、集成测试、E2E 与覆盖重点。
4. 明确可访问性、性能、安全和日志脱敏标准。
5. 功能级设计必须继承基线；例外通过 ADR 或基线变更处理。
```

**Prompt**

``` text
请执行 project-contract-baseline。
根据架构基线，生成 API 规范、前端代码组织规范、组件/状态管理原则、错误处理规范和测试策略。
明确哪些规则是强制项、哪些是推荐项、哪些可由功能提案覆盖。
为 OpenAPI lint、前后端测试、构建和安全检查提供可自动化的质量门禁建议。
```

**Script：** 后续通过 `validate-openapi.sh`、`test-all.sh`
执行可自动化检查。

------------------------------------------------------------------------

### 阶段 8：项目基线审计与冻结

**Skill：** `baseline-audit`

**SKILL.md**

``` markdown
---
name: baseline-audit
description: 检查产品、架构、数据、接口和测试基线是否足以支撑功能提案。
---

1. 检查各基线文件齐备、互相引用一致。
2. 列出尚未决策的事项及影响范围。
3. 对技术选型、模块边界、核心数据模型、API 约定进行交叉检查。
4. 形成“已批准基线版本”和变更规则。
5. 阻止未批准的关键架构决策被功能提案默认为事实。
```

**Prompt**

``` text
请执行 baseline-audit。
检查 docs/product、docs/architecture、docs/adr。
输出：缺失项、矛盾项、待决策项、可冻结项、风险项。
只有在关键决策已确认后才建议冻结；不得把未知事项标成已批准。
生成基线清单和版本/日期/审批人字段。
```

**Script：** `scripts/check-required-files.sh`，示例见第 4 节。

------------------------------------------------------------------------

### 阶段 9：提案拆分、依赖排序与路线图

**Skill：** `proposal-planning`

**SKILL.md**

``` markdown
---
name: proposal-planning
description: 将产品需求切分为可独立验收的 OpenSpec Change，并按依赖、价值和风险排序。
---

1. 按用户可感知的业务能力切分提案，不按前端/后端/数据库分拆。
2. 每个提案必须有明确用户、业务价值、范围、非目标和验收标准。
3. 识别依赖、数据迁移、外部系统、权限和发布风险。
4. 优先交付可验证的纵向切片：界面 + API + 领域逻辑 + 持久化 + 测试。
5. 对基础设施型提案，说明为什么无法与业务提案一起交付。
6. 形成依赖图、排序依据、MVP 与延期项。
7. 每个提案有唯一 change-id，并且大小适合一次规划和评审。
```

**Prompt**

``` text
请执行 proposal-planning。
输入：已冻结产品/架构基线、用户故事、业务流程和依赖。
将需求切分为 OpenSpec Change。每个 Change 输出：
- change-id、名称、目标、业务价值
- 包含/不包含范围
- 关联 US/UC/BR ID
- 依赖项和解锁条件
- 风险、数据迁移、兼容性
- 可独立验收的 Given/When/Then
- 推荐顺序及理由
请提供 Mermaid 依赖图。避免按技术层切分，除非确实是独立基础设施交付。
```

**Script：** 依赖图可用 Mermaid；排序由产品与技术负责人审批。

------------------------------------------------------------------------

### 阶段 10：功能级 OpenSpec Change 与需求细化

**Skill：** `feature-requirements`

**SKILL.md**

``` markdown
---
name: feature-requirements
description: 为单个提案建立 OpenSpec Change，细化行为规格并分析对既有基线的影响。
---

1. 先读取项目基线和相关已归档 Change，不凭空重新定义通用规则。
2. 明确目标、非目标、用户路径、权限、业务规则、异常和边界条件。
3. 按 OpenSpec 当前格式更新 proposal.md、specs/**/spec.md、design.md、tasks.md。
4. 规格描述外部可观察行为，使用 SHALL/MUST 或 Given/When/Then，避免过早绑定实现。
5. 每个需求关联用户故事 ID 和验收标准。
6. 对 pen.dev 原型差异提出修改清单；修改后记录版本或导出快照。
7. 如果超出项目基线，先提出基线/ADR 变更，不在功能 Change 中偷偷绕过。
8. 先评审提案和规格，再进入详细设计。
```

**Prompt**

``` text
请执行 feature-requirements，针对 Change：<change-id>。
阅读项目基线、相关 OpenSpec specs 和既有实现。
生成/更新该 Change 的 proposal.md、specs/**/spec.md、design.md、tasks.md。
要求：
- 写清目标、非目标、业务规则、权限、异常、边界条件
- 每条需求关联 US/UC/BR ID
- 验收标准可测试，覆盖成功、失败、权限、空数据和边界
- 标记 pen.dev 需要新增/修改的页面和状态
- 输出基线影响分析：无影响 / 需要 ADR / 需要修改项目基线
不得直接开始编码；先列出需要产品/架构负责人批准的事项。
```

**Script：** `scripts/check-change.sh <change-dir>`。

------------------------------------------------------------------------

### 阶段 11：页面、元素、按钮与交互事件清单

**Skill：** `page-interaction-inventory`

**SKILL.md**

``` markdown
---
name: page-interaction-inventory
description: 把已确认的提案需求和 pen.dev 原型转成可追踪的页面元素与交互清单。
---

1. 每个页面使用稳定 ID，例如 PAGE-001；元素使用 ELEM-001；事件使用 EVT-001。
2. 记录元素类型、文案、可见条件、禁用条件、校验、触发事件和结果。
3. 对每个事件记录输入、输出、页面状态变化、导航、错误反馈和权限条件。
4. 区分纯前端事件、调用 API 的事件、异步事件、外部跳转。
5. API 只给稳定的 operationId 建议，不在此阶段重复设计完整 OpenAPI。
6. 每个页面/元素/事件都关联 US/AC/REQ ID。
7. 覆盖加载、空态、错误态、成功态、禁用态和无权限态。
```

**Prompt**

``` text
请执行 page-interaction-inventory。
Change：<change-id>
已确认需求：<spec-files>
pen.dev 原型：<prototype-link-or-export>

输出页面清单、元素清单、事件清单和追踪矩阵。
字段至少包含：
PAGE: page_id、名称、路由、关联故事、权限、状态
ELEMENT: element_id、page_id、类型、文案、显示/禁用条件、校验、关联事件
EVENT: event_id、触发元素、输入、前置条件、处理步骤、输出、错误处理、页面状态变化、API operationId（若适用）
不要把 UI 上的每个视觉图层都机械地变成业务元素；只纳入对交互、业务或测试有意义的元素。
列出原型缺失和需求未定义项。
```

**Script：** 可将清单导出为 CSV/Markdown 并纳入版本控制；建议后续增加 ID
唯一性校验。

------------------------------------------------------------------------

### 阶段 12：Figma UI 设计与 MCP 审计

**Skill：** `figma-ui-audit`

**SKILL.md**

``` markdown
---
name: figma-ui-audit
description: 基于已批准需求和页面清单设计/审计 Figma，并检查视觉稿与交互规格的映射。
---

1. 先复用项目 Design System、组件和风格参考，不自行创建重复组件。
2. 设计页面主状态、响应式布局、表单校验、加载/空/错误/成功/禁用状态。
3. 通过 Figma MCP 读取实际可用的页面、节点、组件和设计变量；不得假设 MCP 返回未提供的数据。
4. 把 Figma node/component 与 PAGE/ELEMENT ID 关联。
5. 对缺失、命名不一致、不可实现或与需求冲突的设计列出差异。
6. 视觉稿不能推翻已确认业务规则；冲突必须回到需求评审。
7. 输出设计审计报告与未解决问题。
```

**Prompt**

``` text
请执行 figma-ui-audit。
Change：<change-id>
页面/事件清单：<inventory>
设计系统与风格参考：<design-system>
Figma 文件/页面：<figma-link>

使用可用的 Figma MCP 读取设计数据，不要虚构节点或属性。
输出：
- PAGE/ELEMENT ID → Figma page/node/component 的映射
- 组件复用和设计变量
- 各页面状态覆盖情况
- 与需求/事件清单不一致的差异
- 响应式、可访问性和交互实现注意事项
- 需产品/设计确认的问题
未批准差异不得自动改写需求。
```

**Script：** Figma
的视觉正确性主要靠设计评审；可自动化部分是导出映射后的 ID
完整性与差异报告。

------------------------------------------------------------------------

### 阶段 13：功能级详细设计

本阶段先生成总的 `design.md`，再分别完成
API、前端、后端、测试设计。项目级基线负责稳定的共性；本阶段负责当前
Change 的具体实现决策。

#### 13A. 功能设计总控

**Skill：** `feature-design`

**SKILL.md**

``` markdown
---
name: feature-design
description: 协调单个 Change 的 API、前端、后端和测试详细设计，确保契约一致。
---

1. 读取规格、页面/事件清单、Figma 审计和项目基线。
2. 列出需要设计的接口、页面组件、领域对象、数据变更和外部 IO。
3. 按依赖顺序先定义 API 契约，再完成前后端详细设计。
4. 所有关键对象使用稳定 ID，并维护需求到实现/测试的追踪。
5. 输出设计决策、未决问题和评审清单。
6. 不允许前后端各自独立猜测请求/响应字段。
```

**Prompt**

``` text
请执行 feature-design，Change：<change-id>。
输入：OpenSpec specs、页面/事件清单、Figma 审计、项目架构与契约基线。
生成详细设计任务清单并安排顺序：
1. API 契约与 operationId
2. 前端路由/组件/状态/函数
3. 后端接口/领域类/数据库与 IO Client
4. 单元、契约、集成、E2E 测试
确保每个设计项关联需求 ID；识别冲突后先提出问题，不要自行统一成未经批准的规则。
```

#### 13B. OpenAPI 与 API 逻辑设计

**Skill：** `api-contract-design`

**SKILL.md**

``` markdown
---
name: api-contract-design
description: 设计 OpenAPI 契约、接口业务逻辑、错误语义和契约测试。
---

1. 每个 API 定义稳定 operationId、方法、路径、权限、请求、响应和错误。
2. 定义字段类型、必填、范围、枚举、格式、分页和幂等语义。
3. 说明业务处理流程、事务边界、重复请求和并发冲突。
4. 业务规则放在规格/逻辑说明中，OpenAPI 描述可观察契约。
5. 为成功、校验失败、未认证、无权限、资源不存在、冲突和服务失败设计测试。
6. 前后端共同使用同一份契约；契约变化必须更新消费者和测试。
```

**Prompt**

``` text
请执行 api-contract-design。
基于 Change 规格与事件清单，生成 OpenAPI 3.x 文件和接口逻辑说明。
每个 operation 必须包含 operationId、权限、参数、请求体、响应 schema、错误响应和示例。
另输出接口逻辑表：operationId、业务步骤、事务边界、领域调用、数据访问/外部 IO、幂等/并发处理。
生成契约测试用例，覆盖正常、边界、错误、权限和重复请求。
不得猜测未确定字段；用问题清单标注。
```

#### 13C. 前端详细设计

**Skill：** `frontend-detail-design`

**SKILL.md**

``` markdown
---
name: frontend-detail-design
description: 把页面与交互清单映射为路由、组件、状态、函数和 API 调用。
---

1. 遵守项目级前端技术栈、目录与状态管理基线。
2. 为页面、组件、状态、事件处理函数分配清晰职责。
3. 定义父子组件传参、事件回调、跨页面状态与服务层边界。
4. 所有网络请求引用 OpenAPI operationId，不重复定义接口字段。
5. 定义 loading/empty/error/success/disabled 状态及表单校验。
6. 给关键函数写输入、输出、副作用、异常和测试要求。
7. 不在组件中堆积领域业务规则或直接绕过统一请求层。
```

**Prompt**

``` text
请执行 frontend-detail-design。
输入：OpenAPI、页面/元素/事件清单、Figma 审计、前端项目基线。
输出前端设计文档：
- 技术栈与目录结构（遵循基线，例外需说明）
- 路由与页面组件树
- 组件职责、Props/Emits 或等价传参
- 状态管理与状态流转
- 每个事件处理函数的入参、返回值、副作用和业务步骤
- API operationId 与调用位置映射
- 表单校验、加载/空/错误/成功状态
- 组件测试、页面测试和 E2E 测试
不得与 OpenAPI 重复定义或修改接口契约。
```

#### 13D. 后端详细设计

**Skill：** `backend-detail-design`

**SKILL.md**

``` markdown
---
name: backend-detail-design
description: 将接口业务逻辑细化为应用服务、领域对象、数据库访问和外部 IO Client 契约。
---

1. 遵守项目级技术栈、模块边界、领域边界和公共规范。
2. 对每个 operationId 定义 Controller、应用服务、领域对象的职责与调用链。
3. 设计功能级字段、DDL/迁移、索引、约束、SQL 与 Mapper 方法。
4. 对每个数据库操作说明读写对象、过滤条件、事务、锁/乐观并发和异常。
5. 对每个 File I/O、Feign/HTTP、Redis、MQ 等 Client 定义接口、入参、出参、超时、重试、幂等、错误处理和可观测性。
6. 领域类方法说明职责、参数、返回、前置条件、后置条件和不变量。
7. 定义事务边界，禁止把远程 IO 无条件放在长事务内。
8. 不重复发明项目已有公共 Client；优先复用基线中的抽象。
9. 设计测试替身与集成测试策略。
```

**Prompt**

``` text
请执行 backend-detail-design。
输入：OpenSpec 规格、OpenAPI、接口逻辑、项目架构/领域/数据基线。
输出：
1. 后端模块/包结构与依赖方向
2. operationId → Controller → Application Service → Domain → Repository/Client 调用链
3. 领域类/值对象/方法清单（参数、返回、职责、不变量）
4. 本提案的数据库变更：表字段、类型、约束、索引、迁移与回滚策略
5. 每个 Mapper/SQL：方法签名、查询条件、排序分页、事务和并发说明
6. 每个 File I/O/Feign/HTTP/Redis/MQ Client：接口签名、数据契约、超时、重试、幂等、错误映射
7. 事务边界、异常映射、日志/指标/追踪
8. 单元、集成、契约测试
必须区分项目级既有能力与本提案新增内容。若需要改变领域边界、公共接口或全局技术约定，先提出基线变更。
```

#### 13E. 测试设计

**Skill：** `test-design`

**SKILL.md**

``` markdown
---
name: test-design
description: 从验收标准和技术风险反推测试层级、测试数据与自动化用例。
---

1. 每条验收标准至少映射一个测试用例或说明人工验证原因。
2. 覆盖业务规则边界、权限、异常、幂等、并发、数据一致性。
3. 区分单元、API 契约、集成、组件、E2E 和人工验收。
4. 说明测试数据、外部服务模拟、环境前提和清理方式。
5. 测试不能只验证 happy path；不得为了通过测试而弱化断言。
```

**Prompt**

``` text
请执行 test-design。
输入：验收标准、OpenAPI、前后端详细设计、风险清单。
输出测试矩阵：REQ/AC ID、测试层级、用例 ID、前置条件、步骤、预期结果、自动化方式。
至少覆盖正常、边界、失败、权限、重复请求、并发/一致性（适用时）。
指出无法自动化的验收点及人工验证步骤。
```

**Script：** `validate-openapi.sh`、`test-all.sh`。

------------------------------------------------------------------------

### 阶段 14：前后端实现、测试与代码审查

**Skill：** `implementation-orchestrator`

**SKILL.md**

``` markdown
---
name: implementation-orchestrator
description: 按批准的设计与任务清单使用 Superpowers 研发方法实施并验证功能。
---

# 执行顺序
1. 读取批准的 OpenSpec Change、设计文档、tasks.md 和项目约定。
2. 使用 Superpowers brainstorming/plan 类技能检查方案；使用 writing-plans 拆成小任务。
3. 对行为变化采用 test-driven-development：先写失败测试，再写最小实现，再重构。
4. 按纵向切片实现；不要一次性生成整个功能后才测试。
5. 前后端并行时，以冻结的 OpenAPI 为契约；先生成/共享客户端类型（若项目支持）。
6. 遇到失败使用 systematic-debugging，先复现和定位根因，再修改。
7. 完成后运行相关测试、全量测试、lint、构建、契约校验和安全检查。
8. 使用 code-review 类技能审查正确性、边界、可维护性、安全与性能。
9. 完成验证前不得声称“已完成”；提供命令与真实结果。
10. 发现规格冲突时暂停相关任务，先更新规格/设计并审批。
```

**Prompt**

``` text
请执行 implementation-orchestrator，实施 Change：<change-id>。
先阅读 proposal/specs/design/tasks 和项目开发规范。
使用已安装的 Superpowers 技能完成计划、TDD、调试和代码审查；如果技能不存在，明确说明并采用等价的显式步骤，不要声称调用了未安装的技能。
每次只执行一个可验证的小任务：
- 先写/更新测试
- 运行测试确认失败原因符合预期
- 写最小实现
- 运行相关测试
- 重构并复测
每个任务完成后更新 tasks.md。不得擅自改变 OpenAPI 或业务规格。
最终运行全量验证并报告真实命令、退出码、失败项和未执行项。
```

**前后端协作规则** - API 契约先冻结，前后端可据此并行。 - 先以
Mock/契约测试解耦联调，不要等待另一端全部完成。 -
数据库迁移必须可审查；破坏性变更必须有兼容与回滚策略。 -
每个任务完成后运行局部测试，合并前运行集成测试。 -
代码审查不是"看起来没问题"，应检查规格覆盖、错误路径、安全、数据一致性和测试质量。

------------------------------------------------------------------------

### 阶段 15：人工验收、归档与基线回写

**Skill：** `acceptance-audit`

**SKILL.md**

``` markdown
---
name: acceptance-audit
description: 对照验收标准检查实现、测试证据、原型和规格，完成 OpenSpec 归档与基线更新。
---

1. 逐条检查验收标准，记录通过/失败/不适用及证据。
2. 检查 UI 与批准的 Figma/pen.dev 规格是否一致。
3. 检查 API 契约、权限、数据迁移、日志与可观测性。
4. 区分缺陷、需求变更和可接受偏差；变更不能伪装成缺陷修复。
5. 未通过的验收标准不得标记完成；列出遗留风险与责任人。
6. 仅在测试、审查和产品验收通过后，使用当前 OpenSpec 版本支持的归档流程。
7. 将已确认的通用决策回写项目基线；功能特有细节留在规格/实现中。
8. 归档前检查工作区、提交差异和生成物，不自动提交或发布。
```

**Prompt**

``` text
请执行 acceptance-audit，Change：<change-id>。
对照 OpenSpec 验收标准、页面/事件清单、Figma 审计、OpenAPI 和测试报告逐项验收。
输出：
- 每条 AC 的结果、证据、关联测试
- UI/接口/数据/权限差异
- 缺陷、需求变更、已批准偏差的分类
- 未解决风险和发布阻断项
- 是否允许归档及理由
- 应回写项目基线的通用决策
不得仅因代码已合并就判定验收通过；不得在存在阻断项时建议直接归档。
```

**Script：** `verify-before-completion.sh`；归档命令以当前 OpenSpec CLI
帮助信息为准。

------------------------------------------------------------------------

## 4. 可直接放进仓库的基础脚本

### 4.1 `scripts/check-required-files.sh`

``` bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

required=(
  "docs/product/glossary.md"
  "docs/product/workflows.md"
  "docs/product/use-cases.md"
  "docs/product/user-stories.md"
  "docs/architecture/system-context.md"
  "docs/architecture/technology-decisions.md"
  "docs/architecture/data-flows.md"
  "docs/architecture/logical-erd.md"
  "docs/architecture/domain-boundaries.md"
  "docs/architecture/api-conventions.md"
  "docs/architecture/test-strategy.md"
)

missing=0
for file in "${required[@]}"; do
  if [[ ! -s "$file" ]]; then
    echo "MISSING: $file"
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "Required baseline files are missing or empty."
  exit 1
fi

echo "Required baseline files exist."
```

### 4.2 `scripts/check-change.sh`

``` bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 openspec/changes/<change-id>"
  exit 2
fi

CHANGE_DIR="${1%/}"
required=(
  "$CHANGE_DIR/proposal.md"
  "$CHANGE_DIR/design.md"
  "$CHANGE_DIR/tasks.md"
)

missing=0
for file in "${required[@]}"; do
  if [[ ! -s "$file" ]]; then
    echo "MISSING: $file"
    missing=1
  fi
done

if [[ ! -d "$CHANGE_DIR/specs" ]]; then
  echo "MISSING DIR: $CHANGE_DIR/specs"
  missing=1
elif ! find "$CHANGE_DIR/specs" -type f -name 'spec.md' -print -quit | grep -q .; then
  echo "MISSING: at least one specs/**/spec.md"
  missing=1
fi

if [[ "$missing" -ne 0 ]]; then
  echo "Change structure check failed."
  exit 1
fi

echo "Change structure check passed."
echo "Note: this script checks file presence, not OpenSpec semantic validity."
```

### 4.3 `scripts/validate-openapi.sh`

``` bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <openapi.yaml|openapi.yml|openapi.json>"
  exit 2
fi

SPEC="$1"
if [[ ! -s "$SPEC" ]]; then
  echo "OpenAPI file not found or empty: $SPEC"
  exit 1
fi

if command -v npx >/dev/null 2>&1; then
  npx --yes @redocly/cli lint "$SPEC"
elif command -v docker >/dev/null 2>&1; then
  docker run --rm -v "$PWD:/work" -w /work redocly/cli lint "$SPEC"
else
  echo "Neither npx nor docker is available; OpenAPI lint was not run."
  exit 2
fi
```

### 4.4 `scripts/test-all.sh`

``` bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Replace these examples with the real commands for your repository.
# Do not leave a placeholder in CI and treat it as a successful test.
if [[ -f "package.json" ]]; then
  if command -v npm >/dev/null 2>&1; then
    npm test
  else
    echo "npm not available"
    exit 2
  fi
fi

if [[ -f "pom.xml" ]]; then
  if command -v ./mvnw >/dev/null 2>&1; then
    ./mvnw verify
  elif command -v mvn >/dev/null 2>&1; then
    mvn verify
  else
    echo "Maven not available"
    exit 2
  fi
fi

if [[ -f "build.gradle" || -f "build.gradle.kts" ]]; then
  if [[ -x "./gradlew" ]]; then
    ./gradlew check
  else
    echo "Gradle wrapper not found"
    exit 2
  fi
fi

echo "Configured test commands completed."
```

> 注意：上面的 `test-all.sh`
> 是示例编排器。如果仓库存在多个独立前后端目录，应改成显式目录配置；没有配置测试命令的模块不能被静默跳过。

### 4.5 `scripts/verify-before-completion.sh`

``` bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Working tree =="
git status --short

echo "== Diff summary =="
git diff --stat

echo "== Untracked files =="
git ls-files --others --exclude-standard

echo "== TODO/FIXME in changed tracked files =="
git diff --name-only --diff-filter=ACM | while IFS= read -r file; do
  [[ -f "$file" ]] || continue
  grep -nE 'TODO|FIXME|XXX' "$file" || true
done

echo "== Verification reminder =="
echo "Run OpenSpec validation, OpenAPI lint, relevant tests, full tests, build and code review."
echo "This script does not prove correctness; inspect the command outputs before declaring completion."
```

### 4.6 设置执行权限

``` bash
chmod +x scripts/*.sh
```

------------------------------------------------------------------------

## 5. 推荐的 OpenSpec Change 生命周期

``` text
项目级基线已批准
       |
       v
proposal.md（目标、范围、价值、风险）
       |
       v
specs/**/spec.md（可观察行为、验收标准）
       |
       v
pen.dev 需求/原型更新 + 页面/事件清单
       |
       v
Figma UI + MCP 审计
       |
       v
design.md（架构与实现方案）
       |
       +--> OpenAPI 契约
       +--> 前端详细设计
       +--> 后端详细设计
       +--> 测试设计
       |
       v
tasks.md（可验证的小任务）
       |
       v
Superpowers 计划 + TDD + 调试 + 代码审查
       |
       v
契约检查 + 自动化测试 + 人工验收
       |
       v
OpenSpec 归档 + 通用决策回写项目基线
```

### 建议的门禁

  门禁          必须满足
  ------------- -------------------------------------------
  G1 需求门禁   用户故事、验收标准和关键业务规则已确认
  G2 基线门禁   技术选型、系统边界、领域与公共契约已批准
  G3 提案门禁   Change 范围清楚、依赖明确、规格可测试
  G4 设计门禁   页面/事件、Figma、OpenAPI、前后端设计一致
  G5 开发门禁   任务拆分完成；测试先行；契约未被私自修改
  G6 完成门禁   相关测试、全量测试、构建、代码审查通过
  G7 验收门禁   产品验收有证据；阻断项关闭；归档内容完整

------------------------------------------------------------------------

## 6. 需求追踪矩阵建议

为避免文档越写越多却无法核对，所有产物至少保留以下追踪关系：

  来源       目标             示例 ID
  ---------- ---------------- ----------------------------------------------
  业务流程   用例             FLOW-001 → UC-001
  用例       用户故事         UC-001 → US-001
  用户故事   验收标准         US-001 → AC-001
  验收标准   OpenSpec 需求    AC-001 → REQ-001
  需求       页面/元素/事件   REQ-001 → PAGE-001 / ELEM-001 / EVT-001
  事件       API              EVT-001 → `operationId`
  API        后端逻辑         `operationId` → Service/Domain/Mapper/Client
  API/页面   测试             `operationId` / PAGE-001 → TEST-001
  验收标准   验收证据         AC-001 → 测试报告/人工验收记录

建议每个 Change 维护一份 `traceability.md`。对不适用的关联明确写
`N/A + 原因`，不要留空让人猜测。

------------------------------------------------------------------------

## 7. 一次功能提案的最小交付清单

``` text
openspec/changes/<change-id>/
├── proposal.md
├── specs/<capability>/spec.md
├── design.md
├── tasks.md
├── traceability.md
├── api/openapi.yaml
├── design/frontend-design.md
├── design/backend-design.md
├── design/test-design.md
└── evidence/
    ├── openapi-lint.txt
    ├── test-report.txt
    ├── build-report.txt
    ├── code-review.md
    └── acceptance.md
```

这些附加目录不是所有 OpenSpec
版本的强制结构；可按仓库规范调整。重点是每项产物可找到、可审查、可追踪。

------------------------------------------------------------------------

## 8. 落地顺序

1.  先确认 OpenSpec CLI 版本与当前项目实际目录约定。
2.  建立项目级产品、架构、领域、公共契约基线；先不要批量生成大量功能代码。
3.  选一个中等规模、可独立验收的 Change 试跑全流程。
4.  先完善追踪矩阵和门禁，再把高频步骤固化为 Skill。
5.  将确定性检查接入本地脚本和 CI；LLM
    负责分析与生成，人负责审批业务规则和架构决策。
6.  试跑后删除重复文档，确保 OpenSpec
    spec、OpenAPI、设计文档之间没有多个互相冲突的"真相来源"。

**最终原则：** 项目级决定稳定边界，功能级决定本次变化；OpenSpec
保存变化的规格与任务，Superpowers保证实施纪律，pen.dev/Figma提供设计输入，脚本提供可重复验证，人工审批承担业务与架构决策。
