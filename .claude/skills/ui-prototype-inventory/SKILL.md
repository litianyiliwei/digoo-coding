---
name: ui-prototype-inventory
description: 原型、页面与交互清单。合并原型生成/评审、PAGE→BLOCK→ELEM→EVT 清单与 Figma 审计（涉及 UI 时必做）；输出页面/交互权威清单与初始追踪。
---

# 原型、页面与交互清单

## 何时使用
当流程进入阶段 06「原型、页面与交互清单」时加载本 Skill。一次处理一个 Change；不要提前执行详细设计或实现。

## 输入
已批准的提案级需求与 AC（proposal/specs/design/user-stories）；项目业务流程/RD 矩阵/业务规则；项目级前端规范；当前 Change 的 `design/baseline-impact.md` 与 `design/baseline-binding.json`；pen.dev / Figma MCP 的实际可访问能力（涉及 UI 时必须；Figma MCP 不可用或读不到真实文件/节点时阻断）。

## 执行流程

1. **原型（可选但优先）**：在 `design/prototype.md` 登记原型范围、PAGE ID 草案、页面→AC/FLOW/BR 映射。使用 pen.dev MCP 时，先 `read_skill` 加载画布指引、`get_app_state` 核验状态，再逐页绘制；每页绘制后核验真实渲染。MCP 不可用时如实登记 blocked，不得伪造链接或页面。
2. **原型评审**：逐页核对默认、加载、空、成功、失败、无权限、禁用、边界值、重复提交、返回/取消/关闭/刷新/未保存提示和表单校验；把差异、决策、负责人和待确认项写入 `design/prototype.md` 的评审结论。
3. **页面与交互清单**：生成 `design/page-inventory.csv`、`block-inventory.csv`、`interaction-map.csv`。层级固定为 PAGE → BLOCK → ELEM/EVT；每个页面至少一个功能区块；每个按钮/可交互元素必须且只能归属一个区块；事件登记触发元素、输入、前置条件、步骤、输出、状态变化、导航、错误处理和权限，涉及 API 时引用 operationId（未冻结时标候选）。
4. **追踪初始化**：在 `traceability.csv` 初始化 PAGE/BLOCK/ELEM/EVT → AC 追踪行；后续阶段只追加，不重建。
5. **Figma 审计（涉及 UI 时必做）**：必须通过 Figma MCP 实际读取真实 Figma 文件/节点/组件/变量（可用 `get_design_context`、`get_metadata`、`get_variable_defs`、`get_screenshot` 等实际可用工具），按 `design/page-inventory.csv`、`block-inventory.csv`、`interaction-map.csv` 建立 node/component/variable 映射，输出 `design/figma-audit.md`，登记实际读取到的 node/component/variable 与差异。以 06 清单为唯一权威，不新增/重命名 PAGE/BLOCK。MCP 不可用或读不到真实设计时阻断，不得用截图或臆造替代。需要结构化几何/交接时生成 `design/design-spec.json`（按 page_id 登记画板尺寸与角色外壳，按 block_id 登记布局：direction/order 为 must，间距/高度按 should/free 分档，以及元素几何；只引用 PAGE/BLOCK/ELEM ID，不复制页面名称/路由/需求/AC；states 覆盖清单；颜色/字号只写 `token:` 路径；装饰性原语可省略 elementId。优先从 pen.dev `.pen` 经 pencil MCP `execute` 导出几何；MCP 不可用则阻断，不得用截图替代），并用脚本生成只读 `design/generated/figma-handoff.json/md`。
6. **无 UI 时**：保留三份清单模板并说明原因，使用 `--no-ui --reason "<原因>" --strict` 显式验证；不得用空清单掩盖遗漏。

## 输出
`design/prototype.md`、`design/page-inventory.csv`、`design/block-inventory.csv`、`design/interaction-map.csv`、`traceability.csv`（初始化）；涉及 UI 时 `design/figma-audit.md` 必填；需要几何/交接时 `design/design-spec.json`、`design/generated/figma-handoff.json/md`。

## 质量与安全边界
ID 稳定唯一；页面/区块/元素/事件引用闭合且跨页/跨区块归属一致；没有定义的行为明确标为待确认。原型与需求差异必须登记，不得擅自决策。涉及 UI 时 Figma MCP 不可用或读不到真实设计即阻断，不得声称已审计或用截图替代。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 proposal、delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 校验。
- 需要澄清交互时可用 Superpowers `brainstorming`；只有确认真实安装且可调用时才声称使用。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`python scripts/check-prototype-build.py --change <change-id> --strict`；`python scripts/check-inventory.py --change <change-id> --strict`；涉及 UI 时 `python scripts/check-figma-audit.py --change <change-id> --strict`；需要几何/交接时 `python scripts/check-design-spec.py --change <change-id> --strict` 与 `python scripts/build-figma-handoff.py --change <change-id> --check`。

## 实际工具调用要求
- **Superpowers：** `brainstorming`（若实际可用）；不可用时说明并执行等价澄清步骤。
- **OpenSpec：** 运行 `openspec status --change <id>` 并读取已批准规格；命令必须真实执行并报告退出码/结果。
- **pen.dev / Figma MCP：** 以实际可访问能力为准；不可用时标记“未执行/阻断”，不得伪造结果。
- **状态更新：** 仅在产物落盘且门禁通过后更新 `workflow-state.json`。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="ui-prototype-inventory"` 的契约记录。

- **本阶段输入：** 已批准提案需求与 AC；项目业务流程/数据对象/RD 矩阵/业务规则；前端规范；`design/baseline-impact.md` 与 `design/baseline-binding.json`；pen.dev/Figma MCP 实际能力（涉及 UI 时必须）。逐项核验存在、版本与批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** `design/prototype.md`；`design/page-inventory.csv`；`design/block-inventory.csv`；`design/interaction-map.csv`；`traceability.csv`（初始化）；涉及 UI 时 `design/figma-audit.md` 必填；需要几何/交接时 `design/design-spec.json`、`design/generated/figma-handoff.json/md`。
- **下游交接：** PAGE/BLOCK/ELEM/EVT 权威清单、区块归属、状态/跳转、事件与 AC/operationId 关联；`traceability.csv` 由本阶段初始化，07 只追加合并。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。

## 项目基线约束（只读继承）
- 执行前读取 `docs/architecture/baseline-manifest.json`、`docs/architecture/constraint-registry.json` 与当前 Change 的 `design/baseline-binding.json`。
- 页面、元素、事件不得绕过已批准产品/前端/权限约束；冲突时记录约束 ID 并提交例外/BCR，不得自行修改 binding。
- 通过前执行 `python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`。
