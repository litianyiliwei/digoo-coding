# Prompt: Overall Project Architecture Design

```text
Execute `@project-architecture-baseline`, Change: N/A.

Requirement business analysis: <product-paths>
Open questions: <open-questions>
Technical constraints/environment: <constraints>
Non-functional requirements: <nfr>

Merge output the overall project architecture design: system context, domain boundaries, deployment, data flows, logical ERD, technology selection decisions, and shared API/frontend/test contracts, and freeze the project baseline in the stage-end audit.
Technical requirements:
1. Do the technical selection interview first, asking item by item and recording the confirmer and date of the user/technical lead; do not use defaults or make your own assumptions. You must also complete the "platform and integration boundary interview", recorded in the same table as the technical selection interview:
   - Client form: Web/H5, WeChat Mini Program, Android, iOS, HarmonyOS, PDA/handheld, tablet, desktop;
   - Cross-platform approach: native dual-platform, Flutter, React Native, uni-app, Taro, hybrid; record candidates, trade-offs, confirmer/date;
   - If uni-app is chosen: target platforms, native plugin list, JS Bridge interfaces (name/parameters/returns/errors/callbacks/timeout), platform difference matrix, permission denial/degradation, offline cache/sync conflicts, push/deep links, hot update/store compliance, plugin license/version;
   - Devices/IoT: sensors, cameras, smart terminals, industrial equipment, gateways; protocols BLE/Modbus/LoRa/MQTT/HTTP; edge/cloud sync; offline cache;
   - Third-party platforms: GIS/maps, weather, payment, SMS, real-name verification, government traceability, logistics;
   - Interface boundaries: UI↔API, App↔Native, App↔Device, Backend↔Third-party, Backend↔IoT, asynchronous events, file/object storage.
   Record for each boundary: protocol, authentication, contract, error semantics, timeout/retry/idempotency, version compatibility, testing/real device, owner; write the results into the "Platform and Integration Boundary Interview Records" in `technology-decisions.md`, and add "Cross-Boundary Interface and Integration Conventions" to `api-conventions.md`, "Multi-Platform and Native Capabilities" to `frontend-conventions.md`, and client/native/device data flows to `data-flows.md`.
1a. System origin and existing code/third-party interface interview (mandatory): clarify whether it is a new system, secondary development based on an existing system, or a hybrid. If it is secondary development based on an existing system, require the user to provide the code location (repository URL/local path/branch/commit), actually explore the code structure and technology stack, module boundaries, API/data model, build/test/release commands, existing conventions, and technical debt, write them into the "Existing System Secondary-Development Constraints" in `technology-decisions.md`, and convert them into `LEGACY-*` constraints in `constraint-registry.json` (including source section, level, scope, enforcement method, owner); when code is inaccessible, mark BLOCKED and do not assume from memory. Regardless of whether it is secondary development, you must list the third-party interfaces depended on: provider, purpose, protocol, authentication, SLA/quota, sandbox/test account, approval, data sharing/privacy, errors/timeouts, owner, written into the "Third-Party Interface Dependency List", the EXTERNAL data flows in `data-flows.md`, and the "Third-Party Interface and Integration Conventions" in `api-conventions.md`; when there are no third-party interfaces, write NONE + reason.
2. Data flows must be fully registered as DF-xxx: sync/async, transaction boundaries, failures and compensation, and reference FLOW/NODE/DO/RD entries.
3. The logical ERD must cover the business data objects in data-objects.csv and the read/write relationships in rd-matrix.csv; distinguish the logical model from physical DDL.
4. The shared API/frontend/test contracts only state cross-feature reuse rules; feature-level schemas/pages/physical tables remain in the Change. The test strategy must state the test levels and real-device/emulator/double strategy for native bridging, devices, and third-party boundaries.
5. Stage-end audit: run `bash scripts/check-required-files.sh --strict`, and run `python scripts/check-architecture-baseline.py --strict` (validates "Existing System Secondary-Development Constraints", "Third-Party Interface Dependency List", `LEGACY-*`/`EXT-*` constraints, and third-party data flows/API conventions); complete baseline-status/manifest/registry, run `python scripts/baseline-governance.py refresh-hashes`, have the owner `freeze`, then run `python scripts/baseline-governance.py audit --require-frozen`; if blockers exist, do not freeze.
6. Write the audit report into docs/project/baseline-audit-report.md, distinguishing updated baseline, Change-local records, and amendments pending approval.
7. Method evidence: the stage evidence must write `methods`, recording at least 4 platform/integration clarification questions, 2 alternatives, and 1 decision, and the questions/decisions must cover the four topics "new system/existing system/code location/third-party interfaces"; write the landing points into `docs/architecture/technology-decisions.md#existing-system-secondary-development-constraints` or `#1-technical-selection-interview-records`; run `python scripts/check-method-evidence.py --step 03-project-architecture-baseline --evidence <evidence.json>`.
For formal artifacts, follow the templates specified by `docs/TEMPLATE-POLICY.md` and `docs/OUTPUT-TEMPLATE-MATRIX.csv`; do not delete template fields, and write PENDING for unknown items with the reason.
```

Context: First run `python scripts/agent-context.py --stage <id> --change <change-id>` to obtain condensed inputs; the full `inputs` are only for audit, and by default read the condensed/on-demand list. At stage end, run `python scripts/check-output-context.py --stage <id> --strict` to check the summary output budget.

## Variables to Fill Before Running

- Input materials: replace the `<...>` placeholders with real paths, links, or content.
- Change ID: this stage is project-level, so write `N/A`.
- Loading the Skill: in an environment that supports Agent Skills, use `@project-architecture-baseline`, or explicitly load the Skill of the same name first.

## Execution Tool Protocol (mandatory)

- **Load this project's Skill:** Load `.claude/skills/<skill-id>/SKILL.md` according to the current Agent's real mechanism; do not treat the Skill name as ordinary text. If the repository Skill cannot be loaded, report explicitly and execute according to the Prompt.
- **Superpowers:** Use the stage-scoped mode of `brainstorming` to compare architecture, platform, and integration boundary alternatives, and record questions/alternatives/decisions; write conclusions into existing stage artifacts such as `technology-decisions.md`; do not write a separate design document. First confirm the skills are really installed/discoverable; when unavailable, use `mode=equivalent` and write `reason`. The stage evidence must write `methods` and run `python scripts/check-method-evidence.py --step 03-project-architecture-baseline --evidence <evidence.json>`.
- **OpenSpec:** If the CLI is available, run `openspec list --specs` and `openspec list --changes` to check the relationship between the baseline and existing specs; this stage does not create feature Changes. Commands must actually run and their exit codes/results must be reported.
- **Figma MCP:** Only as an accessible reference input; do not treat unreadable content as already reviewed.
- **State and gates:** Read/update `workflow-state.json`. Mark the stage complete only after the artifacts are written to the specified paths, the script and freezing audit pass, and the required approvals are complete.
- **Output report:** List the files actually read, the Skills/CLI/scripts actually invoked, generated/modified files, check results, items not executed, and the next step. Do not auto-commit, publish, archive, or overwrite existing files.

## Mandatory Deliverable Handoff

Before execution, read the `skill="project-architecture-baseline"` record in `docs/STEP-ARTIFACT-CONTRACTS.md` and `docs/STEP-ARTIFACT-CONTRACTS.json`.

- Input verification: approved requirements-analysis/workflows/data-objects/rd-matrix/business-rules/glossary/acceptance-policy/open-questions; BASELINE-BRIEF/role-permission-matrix/change-sizing/decisions/assumptions/id-conventions/BASELINE-INDEX (resident baseline); existing repository structure/technical constraints; non-functional requirements; technology selection preferences. Report item by item existence, version, and approval status; pause if not satisfied.
- Required output: docs/architecture/system-context.md; domain-boundaries.md; containers-and-deployment.md; data-flows.md; logical-erd.md; technology-decisions.md; api-conventions.md; frontend-conventions.md; test-strategy.md; docs/adr/README.md; baseline-status.md; baseline-manifest.json; constraint-registry.json; docs/project/baseline-audit-report.md. Write to the repository according to the templates.
- Inputs for the next step: the frozen overall project architecture baseline, data flows, logical ERD, shared contracts/test strategy, ACTIVE constraint catalog, audit report, and approval records. Clearly state in the report how stages 04/05 consume them.
- When the stage completes, present the handoff report according to `templates/workflow/step-handoff-report.md`; distinguish generated, draft, proposed, pending confirmation, and not executed.
- **Stage boundary (mandatory):** Stage completion ≠ permission to enter the next stage. After the artifacts are written and checks pass, run `python scripts/workflow.py request-review --step 03-project-architecture-baseline --summary "<review submission summary>"` (the workflow freezes into pending review), present the report according to the handoff template, and **end the turn immediately**; before the user explicitly replies "review approved 03-project-architecture-baseline", reading/executing the next stage's Prompt/Skill and creating next-stage artifacts are forbidden. After approval, run `python scripts/workflow.py approve --step 03-project-architecture-baseline --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval record>`, then run `transition`. Do not fill in approver/approved_at yourself, and do not treat artifact completion or self-check passing as approval.
- Update `workflow-state.json` only after the gates pass and approval completes; do not automatically cross approval points.

## Stage-End Audit and Freezing (mandatory)

- Run `bash scripts/check-required-files.sh --strict`; the exit code must be 0.
- After completing Manifest/Registry, run in order:
  `python scripts/baseline-governance.py refresh-hashes`
  `python scripts/baseline-governance.py freeze --approved-by <owner> --approved-at <ISO date> --evidence <approval evidence path>`
  `python scripts/baseline-governance.py audit --require-frozen`
- Evidence must include the two outputs `docs/architecture/baseline-manifest.json` and `docs/architecture/constraint-registry.json`; if not frozen, hashes mismatch, or artifacts are missing, do not proceed.
- Write the audit report into `docs/project/baseline-audit-report.md`; when blockers exist, do not recommend freezing.
