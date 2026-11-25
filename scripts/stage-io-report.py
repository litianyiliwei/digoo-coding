#!/usr/bin/env python3
"""Generate or verify the stage input/output overview from authoritative JSON sources."""
from pathlib import Path
import hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "process/STEP-ARTIFACT-CONTRACTS.json"
DAG = ROOT / "process/WORKFLOW-STAGES.json"
TARGET = ROOT / "process/STAGE-IO-OVERVIEW.md"
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


CONTENT_STARTS = ("next-stage determination report", "conditionally applicable", "OpenSpec archive result")


def is_doc(value):
    text = str(value).strip()
    if any(text.lower().startswith(prefix.lower()) for prefix in CONTENT_STARTS):
        return False
    if "OpenAPI" in text or "OpenSpec specs" in text or text.lower().startswith("figma file"):
        return True
    return bool(re.search(r"(docs|templates|openspec|workflow|prompts|scripts)/|\.(md|csv|json|yaml|yml|pen|sh|py)\b", text))


def split_content_docs(items):
    docs = [x for x in items if is_doc(x)]
    contents = [x for x in items if not is_doc(x)]
    return contents, docs


def deps_for(step):
    if step == "00":
        return "N/A (orchestration entry point; not a DAG stage)"
    for s in stages:
        if s["id"].startswith(step + "-"):
            deps = s.get("dependencies", [])
            return ", ".join(f"`{d}`" for d in deps) if deps else "none (process start)"
    return "PENDING"


lines = [
    "# Stage Input/Output Overview",
    "",
    "> Language: English | [简体中文](STAGE-IO-OVERVIEW-zh.md)",
    "",
    "> Status: DERIVED (auto-generated from the authoritative contracts; do not edit by hand)",
    "> Change ID: N/A (project-level process overview)",
    "> Source baseline: `process/STEP-ARTIFACT-CONTRACTS.json` (inputs/outputs/approval/gates), `process/WORKFLOW-STAGES.json` (dependency DAG)",
    "> Related requirements/AC: N/A (process document)",
    f"> Generation version: `src-sha256:{source_hash}`",
    "",
    "> This file summarizes only the stage handoff surface. Field-level artifact templates are in `process/OUTPUT-TEMPLATE-MATRIX.csv`; the process entry point is `prompts/00-next-step.md`.",
    "> To change stage handoffs, first change the two JSON source files, then regenerate with `python scripts/stage-io-report.py --out process/STAGE-IO-OVERVIEW.md`; `scripts/check-package.py` verifies that this file is current.",
    "",
    f"{len(contracts)} contract stages: {len(stages)} DAG stages + 00 next-step orchestration (non-DAG stage).",
    "",
    "## Stage Groups",
    "",
    "| Group | Stage chain | Description |",
    "|---|---|---|",
    "| Project baseline chain | 00 → 01 → 02 → 03 → 04 | Initialization → requirements business analysis → architecture/baseline freeze → roadmap |",
    "| Proposal delivery chain | 04 → 05 → 06 → 07 → 08 → 09 → 10 | Proposal requirements → UI design/review → detailed design (incl. interfaces/tests) → implementation → independent verification → acceptance |",
    "",
    "## Overview",
    "",
    "> The overview merges inputs and outputs; per-stage details further split them into \"content/material\" and \"documents/files\".",
    "> The \"Lean inputs\" column is each stage's default read set; the full contract audit set and on-demand inputs are listed in the per-stage details.",
    "",
    "| Stage | Name | Scope | Skill | Dependencies (DAG) | Lean inputs (default reads) | Outputs | On-demand inputs (when triggered) |",
    "|---|---|---|---|---|---|---|---|",
]
for r in contracts:
    profile = (contract_doc.get("input_policy") or {}).get("stage_profiles", {}).get(r["step"])
    lean = profile.get("lean", []) if profile else r.get("inputs", [])
    on_demand = profile.get("on_demand", []) if profile else []
    on_demand_cell = f"{len(on_demand)} items (see details)" if on_demand else "N/A"
    lines.append(
        "| {step} | {title} | {scope} | `{skill}` | {deps} | {inputs} | {outputs} | {on_demand} |".format(
            step=r["step"], title=cell(r["title"]), scope=cell(r.get("scope", "PENDING")),
            skill=r["skill"], deps=deps_for(r["step"]),
            inputs=join(lean), outputs=join(r.get("outputs", [])), on_demand=on_demand_cell,
        )
    )

lines += ["", "## Per-Stage Details", ""]
for r in contracts:
    in_contents, in_docs = split_content_docs(r.get("inputs", []))
    out_contents, out_docs = split_content_docs(r.get("outputs", []))
    profile = (contract_doc.get("input_policy") or {}).get("stage_profiles", {}).get(r["step"])
    lines += [
        f"### {r['step']} {r['title']}",
        "",
        f"- Scope: {r.get('scope', 'PENDING')}",
        f"- Skill: `{r['skill']}`",
        f"- Prompt: `{r.get('prompt', 'PENDING')}`",
        f"- Dependencies (DAG): {deps_for(r['step'])}",
        "",
    ]
    if profile:
        lines += [
            "**Lean inputs (default reads, advisory budget)**",
            "",
            bullets(profile.get("lean", [])),
            "",
            f"> Budget (advisory): {len(profile.get('lean', []))}/{profile.get('max_files', 'N/A')} items; when exceeded, narrow the scope or record why the extra reads are needed.",
            "",
            "**On-demand inputs (read after a trigger; not counted in the default budget)**",
            "",
            bullets(profile.get("on_demand", [])),
            "",
        ]
    lines += [
        "**Full contract inputs (content/material, audit set)**",
        "",
        bullets(in_contents),
        "",
        "**Full contract inputs (documents/files, audit set)**",
        "",
        bullets(in_docs),
        "",
        "**Outputs (content/material)**",
        "",
        bullets(out_contents),
        "",
        "**Outputs (documents/files)**",
        "",
        bullets(out_docs),
        "",
    ]
    step_consumption = [c for c in consumption if c.get("step") == r["step"]]
    if step_consumption:
        lines += ["**Output consumers**", ""]
        for c in step_consumption:
            target = "evidence-only" if c.get("evidence_only") else (", ".join(c.get("consumed_by", [])) or "none")
            lines.append(f"- {c['artifact']} → {target}")
        lines.append("")
    lines += [
        "**Downstream handoff**",
        "",
        bullets(r.get("next_inputs", [])),
        "",
    ]
    if r.get("approval") or r.get("gate"):
        lines += ["**Approval and gates**", ""]
        if r.get("approval"):
            lines.append(f"- Approval: {r['approval']}")
        if r.get("gate"):
            lines.append(f"- Gate: {r['gate']}")
        lines.append("")
    bi = r.get("baseline_interaction")
    if bi:
        lines += ["**Baseline interaction**", ""]
        for key, label in (("read", "Read-only"), ("produce", "Produce/review"), ("gate", "Gate")):
            if bi.get(key):
                value = bi[key] if isinstance(bi[key], str) else "; ".join(bi[key])
                lines.append(f"- {label}: {value}")
        lines.append("")
    lines += ["---", ""]

text = "\n".join(lines).rstrip() + "\n"

if mode == "check":
    if not TARGET.is_file():
        print(f"ERROR: missing derived overview: {TARGET.relative_to(ROOT)}", file=sys.stderr)
        print("Run: python scripts/stage-io-report.py --out process/STAGE-IO-OVERVIEW.md", file=sys.stderr)
        sys.exit(1)
    current = TARGET.read_text(encoding="utf-8")
    if current != text:
        print(f"ERROR: {TARGET.relative_to(ROOT)} is stale; regenerate with:", file=sys.stderr)
        print("  python scripts/stage-io-report.py --out process/STAGE-IO-OVERVIEW.md", file=sys.stderr)
        sys.exit(1)
    print(f"Stage I/O overview is current ({len(contracts)} stages, src-sha256:{source_hash}).")
elif mode == "write":
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote {out_path} ({len(contracts)} stages, src-sha256:{source_hash}).")
else:
    sys.stdout.write(text)
