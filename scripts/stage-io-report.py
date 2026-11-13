#!/usr/bin/env python3
"""Generate or verify the stage input/output overview from authoritative JSON sources."""
from pathlib import Path
import hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "docs/STEP-ARTIFACT-CONTRACTS.json"
DAG = ROOT / "docs/WORKFLOW-STAGES.json"
TARGET = ROOT / "docs/STAGE-IO-OVERVIEW.md"
args = sys.argv[1:]
mode = "stdout"
out_path = TARGET
if args == ["--check"]:
    mode = "check"
elif len(args) == 2 and args[0] == "--out":
    mode = "write"
    out_path = Path(args[1])
elif args:
    print("Usage: stage-io-report.py [--check | --out <path>]", file=sys.stderr)
    sys.exit(2)

contract_doc = json.loads(CONTRACTS.read_text(encoding="utf-8"))
contracts = contract_doc["steps"]
consumption = contract_doc.get("output_consumption", [])
stages = json.loads(DAG.read_text(encoding="utf-8"))["stages"]
source_hash = hashlib.sha256(
    CONTRACTS.read_bytes() + b"\n" + DAG.read_bytes()
).hexdigest()[:12]

dag_ids = [s["id"] for s in stages]
missing = [r["step"] for r in contracts if r["step"] != "00" and not any(x.startswith(r["step"] + "-") for x in dag_ids)]
if missing:
    print("ERROR: contract steps without a DAG stage: " + ", ".join(missing), file=sys.stderr)
    sys.exit(1)


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def join(items):
    return "<br>".join(cell(x) for x in items) if items else "N/A"


def bullets(items):
    return "\n".join(f"- {x}" for x in items) if items else "- N/A"


CONTENT_STARTS = ("下一阶段判定报告", "条件适用", "OpenSpec archive 结果")


def is_doc(value):
    text = str(value).strip()
    if any(text.startswith(prefix) for prefix in CONTENT_STARTS):
        return False
    if "OpenAPI" in text or "OpenSpec specs" in text or text.startswith("Figma 文件"):
        return True
    return bool(re.search(r"(docs|templates|openspec|workflow|prompts|scripts)/|\.(md|csv|json|yaml|yml|pen|sh|py)\b", text))


def split_content_docs(items):
    docs = [x for x in items if is_doc(x)]
    contents = [x for x in items if not is_doc(x)]
    return contents, docs


def deps_for(step):
    if step == "00":
        return "N/A（编排入口，不属于 DAG 阶段）"
    for s in stages:
        if s["id"].startswith(step + "-"):
            deps = s.get("dependencies", [])
            return "、".join(f"`{d}`" for d in deps) if deps else "无（流程起点）"
    return "PENDING"


lines = [
    "# 阶段输入输出总览",
    "",
    "> 状态：DERIVED（由权威契约自动生成，请勿手工编辑）",
    "> Change ID：N/A（项目级流程总览）",
    "> 来源基线：`docs/STEP-ARTIFACT-CONTRACTS.json`（输入/输出/审批/门禁）、`docs/WORKFLOW-STAGES.json`（依赖 DAG）",
    "> 关联需求/AC：N/A（流程文档）",
    f"> 生成版本：`src-sha256:{source_hash}`",
    "",
    "> 本文件只汇总阶段交接面。字段级产物模板见 `docs/OUTPUT-TEMPLATE-MATRIX.csv`；流程入口见 `prompts/00-next-step.md`。",
    "> 修改阶段交接必须先改两份 JSON 源文件，再执行 `python scripts/stage-io-report.py --out docs/STAGE-IO-OVERVIEW.md` 重新生成；`scripts/check-package.py` 会检查本文件是否过期。",
    "",
    f"共 {len(contracts)} 个契约阶段：{len(stages)} 个 DAG 阶段 + 00 下一步编排（非 DAG 阶段）。",
    "",
    "## 阶段分组",
    "",
    "| 分组 | 阶段链路 | 说明 |",
    "|---|---|---|",
    "| 项目基线链 | 00 → 01 → 02 → 03 → 04 | 初始化 → 需求业务梳理 → 总体架构/基线冻结 → 路线图 |",
    "| 提案交付链 | 04 → 05 → 06 → 07 → 08 → 09 → 10 | 提案需求 → 原型/页面清单 → 详细设计（含接口/测试） → 实现 → 独立验证 → 验收 |",
    "",
    "## 总览",
    "",
    "> 总览把输入/输出合并展示；逐阶段明细再拆分为“内容/材料”和“文档/文件”。",
    "> 总览“精简输入”列是每阶段默认读取组；完整契约审计集与按需输入见逐阶段明细。",
    "",
    "| 阶段 | 名称 | 范围 | Skill | 依赖（DAG） | 精简输入（默认读取） | 输出 | 按需输入（触发后） |",
    "|---|---|---|---|---|---|---|---|",
]
for r in contracts:
    profile = (contract_doc.get("input_policy") or {}).get("stage_profiles", {}).get(r["step"])
    lean = profile.get("lean", []) if profile else r.get("inputs", [])
    on_demand = profile.get("on_demand", []) if profile else []
    on_demand_cell = f"{len(on_demand)} 项（见明细）" if on_demand else "N/A"
    lines.append(
        "| {step} | {title} | {scope} | `{skill}` | {deps} | {inputs} | {outputs} | {on_demand} |".format(
            step=r["step"], title=cell(r["title"]), scope=cell(r.get("scope", "PENDING")),
            skill=r["skill"], deps=deps_for(r["step"]),
            inputs=join(lean), outputs=join(r.get("outputs", [])), on_demand=on_demand_cell,
        )
    )

lines += ["", "## 逐阶段明细", ""]
for r in contracts:
    in_contents, in_docs = split_content_docs(r.get("inputs", []))
    out_contents, out_docs = split_content_docs(r.get("outputs", []))
    profile = (contract_doc.get("input_policy") or {}).get("stage_profiles", {}).get(r["step"])
    lines += [
        f"### {r['step']} {r['title']}",
        "",
        f"- 范围：{r.get('scope', 'PENDING')}",
        f"- Skill：`{r['skill']}`",
        f"- Prompt：`{r.get('prompt', 'PENDING')}`",
        f"- 依赖（DAG）：{deps_for(r['step'])}",
        "",
    ]
    if profile:
        lines += [
            "**精简输入（默认读取，预算内）**",
            "",
            bullets(profile.get("lean", [])),
            "",
            f"> 预算：{len(profile.get('lean', []))}/{profile.get('max_files', 'N/A')} 条；超出时先拆分 Change 或缩小范围。",
            "",
            "**按需输入（触发后读取，不计入默认预算）**",
            "",
            bullets(profile.get("on_demand", [])),
            "",
        ]
    lines += [
        "**完整契约输入（内容/材料，审计集）**",
        "",
        bullets(in_contents),
        "",
        "**完整契约输入（文档/文件，审计集）**",
        "",
        bullets(in_docs),
        "",
        "**输出（内容/材料）**",
        "",
        bullets(out_contents),
        "",
        "**输出（文档/文件）**",
        "",
        bullets(out_docs),
        "",
    ]
    step_consumption = [c for c in consumption if c.get("step") == r["step"]]
    if step_consumption:
        lines += ["**输出消费者**", ""]
        for c in step_consumption:
            target = "evidence-only" if c.get("evidence_only") else ("、".join(c.get("consumed_by", [])) or "无")
            lines.append(f"- {c['artifact']} → {target}")
        lines.append("")
    lines += [
        "**下游交接**",
        "",
        bullets(r.get("next_inputs", [])),
        "",
    ]
    if r.get("approval") or r.get("gate"):
        lines += ["**审批与门禁**", ""]
        if r.get("approval"):
            lines.append(f"- 审批：{r['approval']}")
        if r.get("gate"):
            lines.append(f"- 门禁：{r['gate']}")
        lines.append("")
    bi = r.get("baseline_interaction")
    if bi:
        lines += ["**基线交互**", ""]
        for key, label in (("read", "只读"), ("produce", "产出/复核"), ("gate", "门禁")):
            if bi.get(key):
                value = bi[key] if isinstance(bi[key], str) else "；".join(bi[key])
                lines.append(f"- {label}：{value}")
        lines.append("")
    lines += ["---", ""]

text = "\n".join(lines).rstrip() + "\n"

if mode == "check":
    if not TARGET.is_file():
        print(f"ERROR: missing derived overview: {TARGET.relative_to(ROOT)}", file=sys.stderr)
        print("Run: python scripts/stage-io-report.py --out docs/STAGE-IO-OVERVIEW.md", file=sys.stderr)
        sys.exit(1)
    current = TARGET.read_text(encoding="utf-8")
    if current != text:
        print(f"ERROR: {TARGET.relative_to(ROOT)} is stale; regenerate with:", file=sys.stderr)
        print("  python scripts/stage-io-report.py --out docs/STAGE-IO-OVERVIEW.md", file=sys.stderr)
        sys.exit(1)
    print(f"Stage I/O overview is current ({len(contracts)} stages, src-sha256:{source_hash}).")
elif mode == "write":
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote {out_path} ({len(contracts)} stages, src-sha256:{source_hash}).")
else:
    sys.stdout.write(text)
