#!/usr/bin/env python3
"""End-to-end upgrade rehearsal: init v1 -> upgrade v2 -> conflict -> repair -> rollback.

Runs entirely in a temporary directory. The vendored fixture toolkit includes
stub regeneration/check scripts so apply exercises its full post-upgrade path.
"""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("toolkit-sync.py")
QUALITY_GATES_SCRIPT = Path(__file__).with_name("check-quality-gates.py")
QUALITY_GATES_MODULE = Path(__file__).with_name("quality_gates.py")
MANIFEST_REL = "process/TOOLKIT-MANIFEST.json"

STUB_REPORT = """from pathlib import Path
Path("process/STAGE-IO-OVERVIEW.md").write_text("generated\\n", encoding="utf-8")
"""
STUB_LAYOUT = "raise SystemExit(0)\n"
# Mirrors ci-check.sh's real static-gate block so the rehearsal proves the
# dormant path: a project without quality-gates.json prints the skip message.
REAL_CI = """#!/usr/bin/env bash
set -euo pipefail
if [[ ! -f toolkit-lock.json ]]; then python scripts/gen-manifest.py --check; fi
python scripts/check-layout.py --mode auto
if [[ -f toolkit-lock.json ]]; then python scripts/toolkit-sync.py verify --require-lock; fi
if [[ -f docs/architecture/quality-gates.json ]]; then
  python scripts/check-quality-gates.py --root . --strict --require-materialized
else
  echo SKIP_STATIC_GATES=not-adopted
fi
echo CI_CHECKS_PASSED
"""

TEMPLATE_FILES = {
    "templates/workflow/agents-managed.md": "# managed\nrule\n",
    "templates/workflow/agents-managed-zh.md": "# 托管\n规则\n",
    "templates/project-setup/agents-ignore": "",
}


def load():
    spec = importlib.util.spec_from_file_location("toolkit_sync_rehearsal", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def norm_sha(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def write_source(base: Path, version: str, files: dict[str, bytes]) -> None:
    entries = []
    for rel, data in sorted(files.items()):
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        entries.append({"path": rel, "install": rel, "sha256": norm_sha(data),
                        "class": "toolkit", "vendor": True})
    manifest = {"version": version, "state_schema": "1.0", "files": entries, "exclude": []}
    (base / MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
    (base / MANIFEST_REL).write_text(json.dumps(manifest), encoding="utf-8")
    (base / "VERSION").write_text(version + "\n", encoding="utf-8")
    for rel in ["templates/workflow", "templates/project-setup"]:
        (base / rel).mkdir(parents=True, exist_ok=True)
    (base / "templates/workflow/agents-managed.md").write_text("# managed\nrule\n", encoding="utf-8")
    (base / "templates/workflow/agents-managed-zh.md").write_text("# 托管\n规则\n", encoding="utf-8")
    (base / "templates/project-setup/gitignore-block.txt").write_text(
        "# toolkit:begin\n*.tmp\n# toolkit:end\n", encoding="utf-8"
    )
    (base / "templates/project-setup/openspec-config.yaml").write_text(
        "# toolkit:begin\nschema: spec-driven\n# toolkit:end\ncontext: |\n  PENDING\n", encoding="utf-8"
    )
    (base / "templates/workflow/workflow-state.default.json").write_text(
        json.dumps({"current_step": "01-project-bootstrap", "completed_steps": [],
                    "pending_approvals": []}), encoding="utf-8"
    )


V1_FILES = {
    "prompts/01.md": b"# prompt v1\n",
    "process/PROCESS-MAP.md": b"# map\n",
    "scripts/a.py": b"print('a')\n",
    "scripts/toolkit-sync.py": SCRIPT.read_bytes(),
    "scripts/stage-io-report.py": STUB_REPORT.encode(),
    "scripts/check-layout.py": STUB_LAYOUT.encode(),
    "scripts/check-quality-gates.py": QUALITY_GATES_SCRIPT.read_bytes(),
    "scripts/quality_gates.py": QUALITY_GATES_MODULE.read_bytes(),
    "scripts/ci-check.sh": REAL_CI.encode(),
}
V2_FILES = {
    "prompts/01.md": b"# prompt v2\n",
    "prompts/02.md": b"# prompt two\n",
    "process/PROCESS-MAP.md": b"# map\n",
    "scripts/toolkit-sync.py": SCRIPT.read_bytes(),
    "scripts/stage-io-report.py": STUB_REPORT.encode(),
    "scripts/check-layout.py": STUB_LAYOUT.encode(),
    "scripts/check-quality-gates.py": QUALITY_GATES_SCRIPT.read_bytes(),
    "scripts/quality_gates.py": QUALITY_GATES_MODULE.read_bytes(),
    "scripts/ci-check.sh": REAL_CI.encode(),
}


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        toolkit = root / "toolkit"
        project = root / "project"
        toolkit.mkdir()
        project.mkdir()
        write_source(toolkit, "2.0.0", V1_FILES)
        sync = load()

        lock = sync.init(project, sync.open_source(str(toolkit), None, root / "work"), "v2.0.0", "c1")
        assert (project / ".claude").exists() is False  # no third-party files created
        (project / "docs/product").mkdir(parents=True)
        (project / "docs/product/baseline.md").write_text("keep\n", encoding="utf-8")
        print("STEP init: v2.0.0 installed")

        write_source(toolkit, "2.1.0", V2_FILES)
        plan = sync.plan(project, sync.open_source(str(toolkit), None, root / "work2"))
        assert "prompts/02.md" in plan["added"]
        assert "prompts/01.md" in plan["changed"]
        assert "scripts/a.py" in plan["removed"]
        print("STEP plan: added/changed/removed reported")

        assert sync.apply(project, sync.open_source(str(toolkit), None, root / "work3"), "v2.1.0") == 0
        assert (project / "prompts/01.md").read_text(encoding="utf-8") == "# prompt v2\n"
        assert (project / "prompts/02.md").is_file()
        assert not (project / "scripts/a.py").exists()
        assert (project / "docs/product/baseline.md").read_text(encoding="utf-8") == "keep\n"
        assert json.loads((project / "toolkit-lock.json").read_text())["version"] == "2.1.0"
        assert (project / "process/STAGE-IO-OVERVIEW.md").read_text(encoding="utf-8") == "generated\n"
        print("STEP apply: upgraded, outputs untouched, derived file regenerated")

        ci = subprocess.run(["bash", "scripts/ci-check.sh"], cwd=str(project),
                            capture_output=True, text=True, encoding="utf-8")
        assert ci.returncode == 0, ci.stdout + ci.stderr
        assert "SKIP_STATIC_GATES=not-adopted" in ci.stdout, ci.stdout
        assert "CI_CHECKS_PASSED" in ci.stdout, ci.stdout
        print("STEP ci: upgraded project without quality-gates.json keeps CI green (dormant static gates)")

        write_source(toolkit, "2.2.0", V2_FILES)
        real_layout = Path(__file__).with_name("check-layout.py").read_bytes()
        (toolkit / "scripts/check-layout.py").write_bytes(real_layout)
        manifest = json.loads((toolkit / MANIFEST_REL).read_text(encoding="utf-8"))
        for entry in manifest["files"]:
            if entry["path"] == "scripts/check-layout.py":
                entry["sha256"] = norm_sha(real_layout)
        (toolkit / MANIFEST_REL).write_text(json.dumps(manifest), encoding="utf-8")
        (project / "backend").mkdir()
        assert sync.apply(project, sync.open_source(str(toolkit), None, root / "work-layout"),
                          "v2.2.0") == 2
        assert json.loads((project / "toolkit-lock.json").read_text())["version"] == "2.1.0"
        assert (project / "prompts/01.md").read_text(encoding="utf-8") == "# prompt v2\n"
        assert not (project / ".toolkit-upgrade.lock").exists()
        (project / "backend").rmdir()
        print("STEP preflight: undeclared root entry aborted before writing")
        write_source(toolkit, "2.1.0", V2_FILES)

        (project / "prompts/02.md").write_text("# local fork\n", encoding="utf-8")
        assert sync.apply(project, sync.open_source(str(toolkit), None, root / "work4"), "v2.1.0") == 2
        assert (project / "prompts/02.md").read_text(encoding="utf-8") == "# local fork\n"
        print("STEP conflict: locally modified vendored file aborted the upgrade")

        (project / "workflow-state.json").write_text("{ broken", encoding="utf-8")
        assert sync.repair(project) == 0
        assert json.loads((project / "workflow-state.json").read_text())["current_step"] == "01-project-bootstrap"
        print("STEP repair: managed blocks recomposed, workflow state restored from backup")

        write_source(toolkit, "2.0.0", V1_FILES)
        assert sync.apply(project, sync.open_source(str(toolkit), None, root / "work5"), "v2.0.0",
                          take_upstream=True) == 0
        assert json.loads((project / "toolkit-lock.json").read_text())["version"] == "2.0.0"
        assert (project / "prompts/01.md").read_text(encoding="utf-8") == "# prompt v1\n"
        print("STEP rollback: downgraded to 2.0.0 with --take-upstream")

    print("REHEARSAL_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
