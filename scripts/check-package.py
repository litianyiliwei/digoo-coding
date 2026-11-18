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
    text=p.read_text(encoding="utf-8")
    if len(text.strip())<100: errors.append(f"Prompt suspiciously short: {p.relative_to(ROOT)}")
    if p.name=='workflow-prompts.md': continue
    lowered=text.lower()
    if 'check-entry' not in text: errors.append(f"Prompt missing check-entry gate: {p.relative_to(ROOT)}")
    if 'request-review' not in text: errors.append(f"Prompt missing request-review step: {p.relative_to(ROOT)}")
    if 'approve' not in lowered: errors.append(f"Prompt missing approve step: {p.relative_to(ROOT)}")
    if 'review passed' not in lowered: errors.append(f"Prompt missing canonical 'review passed' phrase: {p.relative_to(ROOT)}")
    if 'update `workflow-state.json`' in lowered or 'read/update `workflow-state.json`' in lowered:
        errors.append(f"Prompt instructs direct workflow-state update: {p.relative_to(ROOT)}")
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

# Validate bash syntax of every shell script using an executable Bash.
def usable_bash_candidates():
    """Yield Bash executables that can actually be launched on this host.

    WindowsApps may expose a ``bash.exe`` alias when WSL is unavailable.
    Prefer Git for Windows Bash in that case, while retaining PATH discovery
    for Unix hosts and custom installations.
    """
    candidates = []
    path_bash = shutil.which("bash")
    if path_bash:
        candidates.append(Path(path_bash))
    if sys.platform == "win32":
        git = shutil.which("git")
        if git:
            git_root = Path(git).resolve().parent.parent
            candidates.extend((git_root / "bin" / "bash.exe", git_root / "usr" / "bin" / "bash.exe"))
    seen = set()
    bash_start_errors = []
    for candidate in candidates:
        key = str(candidate.resolve()).lower()
        if key in seen or not candidate.is_file():
            continue
        seen.add(key)
        try:
            probe = subprocess.run([str(candidate), "--version"], capture_output=True, text=True, timeout=5)
        except (OSError, subprocess.TimeoutExpired) as exc:
            bash_start_errors.append(f"{candidate}: {exc}")
            continue
        if probe.returncode == 0:
            yield candidate
        else:
            detail = (probe.stderr or probe.stdout).strip().replace("\n", " | ")
            bash_start_errors.append(f"{candidate}: exit {probe.returncode}" + (f" ({detail})" if detail else ""))
    usable_bash_candidates.start_errors = bash_start_errors


bash_candidates = list(usable_bash_candidates())
if bash_candidates:
    bash = str(bash_candidates[0])
    for p in sorted((ROOT/"scripts").glob("*.sh")):
        r=subprocess.run([bash,"-n",str(p)],capture_output=True,text=True)
        if r.returncode: errors.append(f"Bash syntax error in {p.relative_to(ROOT)}: {r.stderr.strip()}")
else:
    details = "; ".join(usable_bash_candidates.start_errors)
    message = "No usable Bash could be started. Check WSL/Git for Windows Bash availability and execution permissions; WindowsApps aliases may be unavailable."
    errors.append(message + (f" Start errors: {details}" if details else ""))
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
# Claude Code hook scripts must stay importable/compilable.
hooks_dir=ROOT/".claude"/"hooks"
if hooks_dir.is_dir():
    for p in sorted(hooks_dir.glob("*.py")):
        r=subprocess.run([sys.executable,"-m","py_compile",str(p)],capture_output=True,text=True)
        if r.returncode: errors.append(f"Python syntax error in {p.relative_to(ROOT)}: {r.stderr.strip()}")
    for p in (hooks_dir/"__pycache__").glob("*"):
        try: p.unlink()
        except OSError: pass
    try: (hooks_dir/"__pycache__").rmdir()
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
print("Package checks passed: Skill names/frontmatter, prompt pairs, step input/output contracts, stage I/O overview freshness, output consumption, template matrix, Bash/Python syntax. Regression tests are separate commands.")
