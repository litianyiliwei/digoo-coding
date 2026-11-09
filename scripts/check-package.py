#!/usr/bin/env python3
"""Validate that every configured Skill has a matching Prompt and valid frontmatter."""
from pathlib import Path
import json, re, subprocess, sys, shutil
ROOT = Path(__file__).resolve().parents[1]
skills_dir = ROOT / ".claude/skills" if (ROOT / ".claude/skills").is_dir() else ROOT / ".agents/skills"
prompts_dir = ROOT / "prompts"
errors=[]
skill_paths=sorted(skills_dir.glob("*/SKILL.md"))
prompt_paths=sorted(prompts_dir.glob("*.md"))
if not skill_paths: errors.append(f"No skills/*/SKILL.md found under {skills_dir.relative_to(ROOT)}")
ids=set()
for p in skill_paths:
    body=p.read_text(encoding="utf-8")
    dirname=p.parent.name
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", dirname): errors.append(f"Invalid Skill directory name: {dirname}")
    if not body.startswith("---\n"): errors.append(f"Missing YAML frontmatter: {p.relative_to(ROOT)}"); continue
    parts=body.split("---",2)
    if len(parts)<3: errors.append(f"Unclosed frontmatter: {p.relative_to(ROOT)}"); continue
    fm=parts[1]
    name=re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$",fm)
    desc=re.search(r"(?m)^description:\s*(.+)$",fm)
    if not name: errors.append(f"Frontmatter name missing: {p.relative_to(ROOT)}")
    elif name.group(1)!=dirname: errors.append(f"name != directory: {p.relative_to(ROOT)}")
    if not desc or not desc.group(1).strip(): errors.append(f"Frontmatter description missing: {p.relative_to(ROOT)}")
    ids.add(dirname)
    if len(body.strip())<500: errors.append(f"Skill suspiciously short: {p.relative_to(ROOT)}")
missing_prompts=[]
SPECIAL_PROMPT_PAIRS = {"workflow-orchestrator": "00-next-step.md", "independent-verifier": "09-independent-verification.md"}
# openspec-* skills are OpenSpec CLI helpers, not workflow stages; they have no stage prompt.
for skill in ids:
    if skill.startswith("openspec-"): continue
    paired = (prompts_dir / SPECIAL_PROMPT_PAIRS[skill]).is_file() if skill in SPECIAL_PROMPT_PAIRS else bool(list(prompts_dir.glob(f"*-{skill}.md")))
    if not paired:
        missing_prompts.append(skill)
if missing_prompts: errors.append("Skills missing paired Prompt: " + ", ".join(sorted(missing_prompts)))
for p in prompt_paths:
    if len(p.read_text(encoding="utf-8").strip())<100: errors.append(f"Prompt suspiciously short: {p.relative_to(ROOT)}")
# Validate per-step input/output/handoff contracts.
contract_check = subprocess.run([sys.executable, str(ROOT / "scripts/check-step-contracts.py")], capture_output=True, text=True)
if contract_check.returncode:
    errors.append("Step artifact contract check failed: " + (contract_check.stdout + contract_check.stderr).strip().replace("\n", " | "))

# Validate the output-template registry points to actual files.
r = subprocess.run([sys.executable, str(ROOT / "scripts/check-output-template-matrix.py")], capture_output=True, text=True)
if r.returncode:
    errors.append("Output template matrix check failed: " + (r.stdout + r.stderr).strip().replace("\n", " | "))

# Validate the derived stage input/output overview matches the authoritative contracts.
r = subprocess.run([sys.executable, str(ROOT / "scripts/stage-io-report.py"), "--check"], capture_output=True, text=True)
if r.returncode:
    errors.append("Stage I/O overview check failed: " + (r.stdout + r.stderr).strip().replace("\n", " | "))

# Validate every file output has a declared consumer or is explicitly evidence-only.
r = subprocess.run([sys.executable, str(ROOT / "scripts/check-output-consumption.py")], capture_output=True, text=True)
if r.returncode:
    errors.append("Output consumption check failed: " + (r.stdout + r.stderr).strip().replace("\n", " | "))

# Validate bash syntax of every shell script if bash exists.
if shutil.which("bash"):
    for p in sorted((ROOT/"scripts").glob("*.sh")):
        r=subprocess.run(["bash","-n",str(p)],capture_output=True,text=True)
        if r.returncode: errors.append(f"Bash syntax error in {p.relative_to(ROOT)}: {r.stderr.strip()}")
    contract_test = ROOT / "scripts/test-api-io-mapping.sh"
    if contract_test.is_file():
        r=subprocess.run(["bash", str(contract_test)],capture_output=True,text=True)
        if r.returncode: errors.append(f"API→IO checker regression test failed: {(r.stdout + r.stderr).strip().replace(chr(10), ' | ')}")
# Python syntax-check scripts without generating __pycache__ files.
for p in sorted((ROOT/"scripts").glob("*.py")):
    r=subprocess.run([sys.executable,"-m","py_compile",str(p)],capture_output=True,text=True)
    if r.returncode: errors.append(f"Python syntax error in {p.relative_to(ROOT)}: {r.stderr.strip()}")
# Cleanup pycache created by py_compile.
for p in (ROOT/"scripts").glob("__pycache__/*"):
    try: p.unlink()
    except OSError: pass
try: (ROOT/"scripts/__pycache__").rmdir()
except OSError: pass
print(f"Skills: {len(skill_paths)}; prompts: {len(prompt_paths)}")
# Expected counts derive from the contract registry: one Skill per contract step,
# plus the contract prompts and the standalone workflow-prompts.md overview.
expected_steps = len(json.loads((ROOT / "docs/STEP-ARTIFACT-CONTRACTS.json").read_text(encoding="utf-8"))["steps"])
if len(skill_paths) < expected_steps: errors.append(f"Expected at least {expected_steps} Skills (one per contract step); found {len(skill_paths)}")
if len(prompt_paths) != expected_steps + 1: errors.append(f"Expected {expected_steps + 1} Prompts (contract prompts + workflow-prompts.md); found {len(prompt_paths)}")
if errors:
    for e in errors: print("ERROR:",e)
    print(f"Package checks failed: {len(errors)} issue(s).")
    sys.exit(1)
print("Package checks passed: Skill names/frontmatter, prompt pairs, step input/output contracts, stage I/O overview freshness, output consumption, template matrix, Bash/Python syntax, API→IO regression tests.")
