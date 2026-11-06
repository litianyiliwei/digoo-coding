# P0 运行时治理：状态机、阶段守卫、SHA-256 交接与独立验证

本工具包把流程规范从 Prompt 约定提升为可执行门禁。`docs/WORKFLOW-STAGES.json` 是阶段 DAG 的唯一权威定义；Skill/Prompt 负责工作方法，脚本负责状态转换和可验证约束。

## 1. 状态机与守卫

查看状态：

```bash
python3 scripts/workflow.py status
```

检查阶段能否进入（会核验依赖、当前阶段、审批/阻断项及所有上游交接哈希）：

```bash
python3 scripts/workflow.py check-entry --step 01-project-bootstrap
python3 scripts/workflow.py check-entry --step 10-feature-requirements --change-id <change-id>
```

阶段完成后，先准备 evidence JSON，再执行唯一允许的状态转换入口：

```bash
python3 scripts/workflow.py transition --step 01-project-bootstrap --evidence workflow/evidence/01-project-bootstrap.json
```

状态机仅在以下条件同时满足时推进：
- 当前阶段与 `workflow-state.json.current_step` 一致；
- 所有 DAG 前置阶段已完成；
- 无 pending approvals / blockers；
- 所有必需输出真实存在且位于项目根目录内；
- 至少一个门禁检查，所有自动化检查必须提供真实命令、`exit_code=0` 和仓库内日志文件；人工检查必须提供 reviewer 和证据文件；
- 阶段要求人工批准时，证据中有 `approval.status=approved`、approver、approved_at；
- 上游交接包存在且哈希未变化。

状态文件使用临时文件 + 原子替换和独占锁写入；每次成功转换追加 `transition_history`，保留证据路径、输出、门禁结果和审批摘要。不要直接编辑 `completed_steps` 或 `current_step`；修复状态必须先查明证据并走受控恢复流程。拓扑重构导致旧阶段 ID 失效时，使用 `python3 scripts/workflow.py migrate-state --reason <原因> --reset-step <需重跑阶段>`：失效阶段保留在 `legacy_completed_steps` 与 `topology_migrations`，当前阶段按新 DAG 重算。

### Evidence JSON 示例

可从 `templates/workflow/stage-evidence.example.json` 复制，结构参考 `templates/workflow/stage-evidence.schema.json`。每个阶段需要将示例中的文件路径、命令、退出码和审批信息替换为本次真实证据。

```json
{
  "step_id": "01-project-bootstrap",
  "change_id": null,
  "baseline_version": "",
  "outputs": [
    {"path": "AGENTS.md", "status": "created", "required": true},
    {"path": "docs/architecture/baseline-status.md", "status": "created", "required": true}
  ],
  "checks": [
    {"name": "toolchain-check", "kind": "automated", "status": "passed", "command": "python3 scripts/check-package.py", "exit_code": 0, "log": "workflow/evidence/logs/toolchain-check.log"}
  ],
  "approval": {"required": false, "status": "not-required"}
}
```

项目级转功能级时，阶段 10 的 evidence 必须包含真实 `change_id`；状态机据此绑定后续功能交接包。

## 2. SHA-256 交接包

`transition` 成功时，会为每个直接下游阶段生成不可静默漂移的交接清单：

```text
workflow/handoffs/
├── project/09-proposal-planning--10-feature-requirements.json
└── <change-id>/13b-api-contract-design--13c-frontend-detail-design.json
```

每个 manifest 记录源/目标阶段、Change ID、基线版本、审批/门禁摘要，以及每个输出文件的 SHA-256 和大小。SHA-256 计算会先把 CRLF 归一化为 LF，避免 Windows/Linux 检出差异被误报为漂移；内容变化仍会阻断。下游 `check-entry` 自动核验所有前置交接包。文件被修改、删除或路径越界都会阻断进入。

手动检查：

```bash
python3 scripts/workflow.py handoff-verify --manifest workflow/handoffs/<change-id>/13b-api-contract-design--13c-frontend-detail-design.json
```

`handoff-create` 仅用于人工确认的恢复/重建；不可用它绕过失败门禁或审批。若状态已经提交但进程在生成 manifest 前中断，应使用原阶段的已批准 evidence 重新生成：`python3 scripts/workflow.py handoff-create --from-step <from> --to-step <to> --change-id <id> --evidence <original-stage-evidence.json>`。对于项目级阶段不传 `--change-id`；不得使用手工 `--file` 方式重建 14b Verifier 交接，因为必须保留独立验证器检查证据。

## 3. 独立 Verifier

阶段 14 Builder 完成后，必须执行新增阶段 `14b-independent-verification`，然后才能进入阶段 15 人工验收。Verifier 使用与 Builder 不同的 Agent/独立会话标识，以只读方式检查代码和设计，只允许写报告；结构化证据必须记录 `verifier_identity` 与 `builder_identity` 且二者不同；不得修复实现或测试。

输出：
- `openspec/changes/<change-id>/design/evidence/independent-verification-report.md`
- `openspec/changes/<change-id>/design/evidence/independent-verification.json`

检查：

```bash
python3 scripts/check-independent-verification.py \
  --report openspec/changes/<change-id>/design/evidence/independent-verification-report.md \
  --evidence openspec/changes/<change-id>/design/evidence/independent-verification.json
```

只有 Verdict=PASS、所有 AC 有证据、所有测试真实执行且退出码为 0、revision 稳定、只读约束满足、没有 BLOCKER/CRITICAL 发现时才通过。NOT_RUN / SKIPPED / PENDING 不等于 PASS。

## 4. 边界与限制

- 此版本仍以单个 `workflow-state.json` 的一个活动 Change 为主；交接包按 project / change 分目录，支持项目阶段向 Change 阶段切换，但尚未实现多个 Change 的并发状态调度器。
- 脚本能验证文件、哈希、命令退出码和结构化证据，不能证明人工评审意见本身真实；审批人身份由团队现有权限体系保证。
- Verifier 的独立性需要 Agent 运行环境提供独立会话/不同 Agent；若同一 Agent 自己扮演 Builder 和 Verifier，应明确标记为非独立，不得声称独立验证通过。
- `workflow.py transition` 是本地仓库的受控入口，不是安全沙箱；有仓库写权限的 Agent 仍可能绕过脚本直接改文件。团队应通过 Agent 工具权限/CI 分支保护进一步限制。

## 5. 项目基线治理引擎

状态机还会调用 `scripts/baseline-governance.py`，确保“阶段可以进入”之外，阶段内产物也继承当前有效项目基线。机器权威文件为 `docs/architecture/baseline-manifest.json` 与 `constraint-registry.json`；每个 Change 在 `design/baseline-binding.json` 逐条绑定 ACTIVE Constraint ID。

首次冻结顺序、BCR 修订、版本升级、Change 约束适用性/例外、设计/实现/验收独立证据以及在途 Change rebase 详见 `docs/BASELINE-FEATURE-INTERACTION.md` 第 9 节。核心命令：

```bash
python3 scripts/baseline-governance.py audit
python3 scripts/baseline-governance.py audit --require-frozen
python3 scripts/baseline-governance.py init-binding --change-id <change-id>
python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement
python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase design
python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase implementation
python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase acceptance
```

工具包默认 Manifest 和示例约束均为 DRAFT，`audit` 通过只表示结构合法，不表示项目基线已冻结。真实项目必须完成负责人审批后再执行冻结；不得把示例规则或示例审批信息直接当作项目正式规范。
