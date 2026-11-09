# Prompt：人工验收、归档与基线回写

```text
执行 `@acceptance-audit`，Change：<change-id>。

独立验证报告与 JSON：<independent-verification-report-and-json>
AC/specs：<spec-paths>
提案级 US/AC：<user-stories-and-ac>
验收政策与 DoD：<acceptance-policy-and-sizing>
教训清单：<lessons>
测试/构建报告：<evidence-paths>
Figma/原型审计：<design-evidence>

先确认阶段 09 的独立验证 Verdict=PASS，且验证 revision 与当前代码一致；不满足则停止验收。然后逐条验收 AC，记录结果、证据和责任人；核对 UI（涉及 UI 时对照 Figma 设计与 `figma-audit.md`）、接口、数据迁移、权限与可观测性。对照 `docs/product/change-sizing.md` 的 DoD 逐项核对；验收后向 `docs/product/lessons.md` 追加本次可复用教训（无则 N/A + 理由），并更新 `decisions.md`/`assumptions.md` 中受验收结果影响的条目状态。将发现分类为缺陷、需求变更或已批准偏差。列出阻断项、遗留风险、回滚/发布事项。验收通过后先判断并回写已批准的项目基线修订（更新基线域版本/审批/生效日期/在途 Change 复核），再单独执行 OpenSpec archive 合并行为规格。两者不是同一动作；功能专属细节保留在 Change。不要用 `-y` 绕过未完成任务或确认。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：仅将已批准、已实现、已验证且具有跨功能复用价值的决策回写项目基线。功能专属 API、页面、表迁移、IO 和测试保留在归档 Change。更新基线版本和审批记录，并列出需重新核对的在途 Change。OpenSpec 主规格归档与项目设计基线回写是两项独立判断。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@acceptance-audit`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 按验收/归档阶段使用 `verification-before-completion`；若需代码审查，使用 `requesting-code-review`/`receiving-code-review`。先检查技能是否真实安装/可发现，使用宿主 Agent 支持的调用方式读取其指引；不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 验收前运行 `openspec status --change <id>`、`openspec validate <id> --strict`；只有所有门禁通过并获明确批准后才执行 `openspec archive <id>`，不得加 `-y` 绕过确认。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="acceptance-audit"` 的记录。

- 输入核验：已实现代码与测试证据；已批准 AC/规格/追踪矩阵；design/user-stories.md、design/test-cases.csv；docs/product/acceptance-policy.md、change-sizing.md、lessons.md、BASELINE-BRIEF.md；代码审查记录；涉及 UI 时 design/figma-audit.md、design/design-spec.json 与 Figma 设计；部署/演示或验收环境证据。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：openspec/changes/<change-id>/design/evidence/acceptance.md；验收报告与批准记录；OpenSpec archive 结果及更新后的主规格（仅批准后）；项目路线图/基线状态回写（适用时）；更新后的 docs/product/lessons.md（以及必要的 decisions.md/assumptions.md 状态变更）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：已验收并归档的能力规格、验收证据、后续 Change 依赖。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 基线交互：必须按 `docs/BASELINE-FEATURE-INTERACTION.md` 核验基线读取/变更归属；阶段 05 创建/更新 `design/baseline-impact.md`，后续阶段复核；未经批准不得修改冻结基线。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。


## 独立验证前置门禁（P0）

阶段 10 必须读取阶段 09 的 `independent-verification-report.md` 和 `.json`。若不是 PASS、验证后代码有变化或报告缺失，必须退回阶段 09 重新验证，不得继续归档。


## 机器基线验收门禁（必须执行）

验收/归档前逐条核对基线绑定的实现验证证据、已批准例外和当前 rebase 结论；为每条 ACTIVE 约束单独填写 `acceptance_verification`（PASS/NOT_APPLICABLE、方法、真实验收证据），不得直接复制实现阶段的 PASS。执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase acceptance`。未覆盖的 ACTIVE 约束、PENDING 例外、缺少验收证据或未完成 rebase 均阻断归档。
