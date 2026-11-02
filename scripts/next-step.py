#!/usr/bin/env python3
"""Print the next workflow prompt from workflow-state.json. Does not mutate state."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "workflow-state.json"
CONTRACTS = json.loads((ROOT / "docs/STEP-ARTIFACT-CONTRACTS.json").read_text(encoding="utf-8"))
CONTRACT_BY_SKILL = {row["skill"]: row for row in CONTRACTS["steps"]}
SKILLS_DIR = next((ROOT / d for d in (".claude/skills", ".agents/skills") if (ROOT / d).is_dir()), ROOT / ".claude/skills")
STEPS = [
    ('01-project-bootstrap', '项目初始化与工具链检查', 'project-bootstrap', '01-project-bootstrap.md', []),
    ('02-requirements-analysis', '需求发现与整理', 'requirements-analysis', '02-requirements-analysis.md', ['01-project-bootstrap']),
    ('03-prototype-audit', 'pen.dev 原型评审与需求澄清', 'prototype-audit', '03-prototype-audit.md', ['02-requirements-analysis']),
    ('04-product-baseline', '项目级产品基线', 'product-baseline', '04-product-baseline.md', ['03-prototype-audit']),
    ('05-project-architecture-baseline', '项目总体架构设计', 'project-architecture-baseline', '05-project-architecture-baseline.md', ['04-product-baseline']),
    ('06-data-domain-baseline', '项目级数据与领域基线', 'data-domain-baseline', '06-data-domain-baseline.md', ['05-project-architecture-baseline']),
    ('07-project-contract-baseline', '项目级接口/前端/测试规范', 'project-contract-baseline', '07-project-contract-baseline.md', ['05-project-architecture-baseline', '06-data-domain-baseline']),
    ('08-baseline-audit', '项目基线审计与冻结', 'baseline-audit', '08-baseline-audit.md', ['06-data-domain-baseline', '07-project-contract-baseline']),
    ('09-proposal-planning', '提案拆分、依赖排序与路线图', 'proposal-planning', '09-proposal-planning.md', ['08-baseline-audit']),
    ('10-feature-requirements', '功能级 OpenSpec Change 与需求细化', 'feature-requirements', '10-feature-requirements.md', ['09-proposal-planning']),
    ('11-page-interaction-inventory', '页面、元素、按钮与交互事件清单', 'page-interaction-inventory', '11-page-interaction-inventory.md', ['10-feature-requirements']),
    ('12-figma-ui-audit', 'Figma UI 设计与 MCP 审计', 'figma-ui-audit', '12-figma-ui-audit.md', ['11-page-interaction-inventory']),
    ('13a-feature-design', '功能详细设计总控', 'feature-design', '13a-feature-design.md', ['12-figma-ui-audit']),
    ('13b-api-contract-design', 'OpenAPI 与接口逻辑设计', 'api-contract-design', '13b-api-contract-design.md', ['13a-feature-design']),
    ('13c-frontend-detail-design', '前端详细设计', 'frontend-detail-design', '13c-frontend-detail-design.md', ['13b-api-contract-design']),
    ('13d-backend-detail-design', '后端详细设计', 'backend-detail-design', '13d-backend-detail-design.md', ['13b-api-contract-design']),
    ('13e-test-design', '测试设计', 'test-design', '13e-test-design.md', ['13c-frontend-detail-design', '13d-backend-detail-design']),
    ('14-implementation-orchestrator', '实现、TDD、验证与代码审查', 'implementation-orchestrator', '14-implementation-orchestrator.md', ['13e-test-design']),
    ('15-acceptance-audit', '人工验收、归档与基线回写', 'acceptance-audit', '15-acceptance-audit.md', ['14-implementation-orchestrator']),
]

def main():
    if not STATE.exists():
        print(f"ERROR: missing {STATE}", file=sys.stderr); return 2
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: invalid workflow-state.json: {exc}", file=sys.stderr); return 2
    approvals = state.get("pending_approvals", [])
    blockers = state.get("blocked_items", [])
    if approvals or blockers:
        print("BLOCKED: workflow cannot advance automatically.")
        if approvals:
            print("Pending approvals:")
            for item in approvals: print(f" - {item}")
        if blockers:
            print("Blockers:")
            for item in blockers: print(f" - {item}")
        return 3
    completed = set(state.get("completed_steps", []))
    for sid, title, skill, prompt, deps in STEPS:
        if sid in completed: continue
        missing = [d for d in deps if d not in completed]
        if missing:
            print(f"WARNING: prerequisite stages not marked complete: {', '.join(missing)}")
        p = ROOT / "prompts" / prompt
        s = SKILLS_DIR / skill / "SKILL.md"
        if not p.is_file() or not s.is_file():
            print(f"ERROR: missing prompt or skill for {sid}: {p} / {s}", file=sys.stderr); return 2
        print(f"NEXT_STEP={sid}")
        print(f"TITLE={title}")
        print(f"PROMPT={p.relative_to(ROOT)}")
        print(f"SKILL={s.relative_to(ROOT)}")
        contract = CONTRACT_BY_SKILL.get(skill)
        if contract:
            print("REQUIRED_INPUTS=" + " ; ".join(contract["inputs"]))
            print("EXPECTED_OUTPUTS=" + " ; ".join(contract["outputs"]))
            print("NEXT_STAGE_INPUTS=" + " ; ".join(contract["next_inputs"]))
            print(f"HANDOFF_REPORT=templates/workflow/step-handoff-report.md")
        print("NOTE=Verify actual files, approvals and OpenSpec status before executing; this script only reads state.")
        return 0
    print("ALL_STEPS_MARKED_COMPLETE")
    print("Verify final acceptance and archived OpenSpec state manually; no state was changed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
