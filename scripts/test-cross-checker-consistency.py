#!/usr/bin/env python3
"""Cross-checker consistency fixture for the module-package slice gates.

One project fixture declares the same concrete module paths in
``docs/product/modules.csv`` and a Change slice without any ``<...>``
placeholder. The fixture must pass the stage-07 design-sections slice gate, the
``check-change-footprint.py --declaration-only`` gate, the module registry
check, and ``code-context.py`` with identical module paths/cards.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

CHECK_DESIGN = SCRIPTS_DIR / "check-design-sections.py"
CHECK_FOOTPRINT = SCRIPTS_DIR / "check-change-footprint.py"
CHECK_MODULES = SCRIPTS_DIR / "check-modules.py"
CODE_CONTEXT = SCRIPTS_DIR / "code-context.py"

DESIGN_REL = "openspec/changes/demo/design.md"
MANIFEST_REL = "openspec/changes/demo/design/context-manifest.json"

CAPABILITY_HEADER = (
    "capability_slug,capability_name,domain_id,owner_module,related_modules,"
    "code_packages,status,delivered_slices,remaining_slices,active_changes,notes"
)
MODULE_HEADER = (
    "module_slug,module_name,domain_id,frontend_paths,backend_paths,shared_paths,"
    "capabilities,status,notes"
)

ORDER_FE = "web/src/features/sales/order/"
ORDER_BE = "server/src/main/java/com/acme/sales/order/"
ORDER_SHARED = f"{ORDER_BE}shared/"

SLICE = """## Design Decisions

### Implementation Slice
- Primary capability: order-create
- Owner module: order
- Related modules: N/A + no other module is modified
- Slice type/coverage: initial / full
- Code packages: server/src/main/java/com/acme/sales/order/; web/src/features/sales/order/
- Owned paths: server/src/main/java/com/acme/sales/order/export/; web/src/features/sales/order/components/
- Integration paths: N/A + no thin registration point changed
- Module card: update web/src/features/sales/order/MODULE.md
- Frozen approvals: N/A
"""

FILES = {
    f"{ORDER_FE}MODULE.md": "# Order module\n",
    f"{ORDER_BE}MODULE.md": "# Order backend module\n",
    f"{ORDER_FE}components/OrderList.vue": "<template>list</template>\n",
    f"{ORDER_BE}export/ExportService.java": "class ExportService {}\n",
    DESIGN_REL: SLICE,
}


def load(path: Path, name: str, root: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


class CrossCheckerConsistencyTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test User")

        self.write(
            "docs/architecture/code-layout.json",
            json.dumps(
                {
                    "version": 1,
                    "strategy": "module-packages",
                    "roots": {"backend": "server/", "frontend": "web/"},
                    "integration_paths": ["web/src/router/routes.ts"],
                    "module_card": "MODULE.md",
                }
            ),
        )
        self.write(
            "docs/architecture/domain-boundaries.md",
            "# Domain Boundaries\n\n"
            "| DOM ID | Responsibility | Invariants | Dependency Direction |\n"
            "|---|---|---|---|\n"
            "| DOM-001 | Orders | none | inbound |\n",
        )
        self.write(
            "docs/product/modules.csv",
            "\n".join(
                [
                    MODULE_HEADER,
                    f"order,Order,DOM-001,{ORDER_FE},{ORDER_BE},"
                    f"{ORDER_SHARED},order-create,ACTIVE,N/A",
                ]
            )
            + "\n",
        )
        self.write(
            "docs/product/capabilities.csv",
            "\n".join(
                [
                    CAPABILITY_HEADER,
                    "order-create,Order Create,DOM-001,order,N/A,N/A,"
                    "ACTIVE,N/A,N/A,N/A,N/A",
                ]
            )
            + "\n",
        )
        for relpath, text in FILES.items():
            self.write(relpath, text)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def git(self, *args: str) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        return proc

    def run_module(self, path: Path, name: str, argv: list[str]):
        module = load(path, name, self.root)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = module.main(argv)
        return code, out.getvalue() + err.getvalue()

    def test_same_fixture_passes_all_slice_checkers(self):
        code, output = self.run_module(
            CHECK_DESIGN, "xcheck_design", ["--change", "demo", "--slice-only"]
        )
        self.assertEqual(0, code, output)

        code, output = self.run_module(
            CHECK_FOOTPRINT, "xcheck_footprint", ["demo", "--declaration-only"]
        )
        self.assertEqual(0, code, output)
        self.assertIn("FOOTPRINT_CHECK=PASSED", output)

        code, output = self.run_module(CHECK_MODULES, "xcheck_modules", [])
        self.assertEqual(0, code, output)
        self.assertIn("Modules check passed", output)

        code, output = self.run_module(CODE_CONTEXT, "xcheck_context", ["demo"])
        self.assertEqual(0, code, output)
        manifest = json.loads(
            (self.root / MANIFEST_REL).read_text(encoding="utf-8")
        )
        cards = {
            item["path"]
            for item in manifest["read_set"]
            if item["category"] == "module-card"
        }
        self.assertEqual({f"{ORDER_FE}MODULE.md", f"{ORDER_BE}MODULE.md"}, cards)
        self.assertEqual([], [
            item for item in manifest["read_set"]
            if item["category"] == "integration"
        ])


if __name__ == "__main__":
    unittest.main()
