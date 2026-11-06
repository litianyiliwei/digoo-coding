#!/usr/bin/env python3
"""Regression tests for machine-readable baseline and per-Change constraint enforcement."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("baseline-governance.py")
spec = importlib.util.spec_from_file_location("baseline_governance", SCRIPT)
bg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bg)


class BaselineGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs/architecture").mkdir(parents=True)
        (self.root / "docs/product").mkdir(parents=True)
        (self.root / "docs/adr").mkdir(parents=True)
        (self.root / "openspec/changes/demo-feature/design").mkdir(parents=True)
        (self.root / "openspec/changes/demo-feature/evidence").mkdir(parents=True)
        self.domain_files = {
            "product": "docs/product/product.md",
            "architecture": "docs/architecture/architecture.md",
            "data_domain": "docs/architecture/data.md",
            "api": "docs/architecture/api.md",
            "frontend": "docs/architecture/frontend.md",
            "test_quality": "docs/architecture/quality.md",
        }
        headings = {
            "product": "产品基线",
            "architecture": "架构基线",
            "data_domain": "数据基线",
            "api": "API 基线",
            "frontend": "前端基线",
            "test_quality": "测试基线",
        }
        for domain, rel in self.domain_files.items():
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"# {headings[domain]}\n\nApproved rule.\n", encoding="utf-8")
        self.evidence_rel = "openspec/changes/demo-feature/evidence/approval.md"
        (self.root / self.evidence_rel).write_text("Approved by human reviewer.\n", encoding="utf-8")
        self.design_rel = "openspec/changes/demo-feature/design/design.md"
        (self.root / self.design_rel).write_text("Design complies with ARCH-BOUNDARY-001.\n", encoding="utf-8")
        self.impl_rel = "openspec/changes/demo-feature/evidence/verification.md"
        (self.root / self.impl_rel).write_text("Verification passed.\n", encoding="utf-8")
        self.acceptance_rel = "openspec/changes/demo-feature/evidence/acceptance.md"
        (self.root / self.acceptance_rel).write_text("Acceptance passed.\n", encoding="utf-8")
        self.registry = {
            "schema_version": "1.0",
            "registry_version": "1.0.0",
            "constraints": [{
                "id": "ARCH-BOUNDARY-001", "domain": "architecture", "revision": "1.0",
                "status": "ACTIVE", "level": "MUST", "scope": "ALL_CHANGES",
                "title": "Module contract", "rule": "Use declared module contracts.",
                "rationale": "Avoid hidden coupling.",
                "source": {"file": self.domain_files["architecture"], "section": headings["architecture"]},
                "enforcement": {"type": "MANUAL", "validator": "", "evidence_required": True},
                "owner": "Architecture Owner", "approved_by": "Tech Lead", "approved_at": "2026-11-03"
            }]
        }
        self.registry_path = self.root / "docs/architecture/constraint-registry.json"
        self.registry_path.write_text(json.dumps(self.registry, indent=2), encoding="utf-8")
        domains = {}
        for domain, rel in self.domain_files.items():
            p = self.root / rel
            domains[domain] = {
                "version": "1.0.0", "status": "FROZEN", "owner": f"{domain}-owner",
                "approver": "Tech Lead", "approved_at": "2026-11-03",
                "effective_revision": "git:0123456789abcdef", "approval_evidence": self.evidence_rel,
                "files": [{"path": rel, "sha256": bg.sha256(p)}]
            }
        self.manifest = {
            "schema_version": "1.0", "project_id": "demo-project", "overall_version": "1.0.0",
            "status": "FROZEN", "approval": {"approver": "Project Owner", "approved_at": "2026-11-03", "evidence": self.evidence_rel},
            "constraint_registry": {"path": "docs/architecture/constraint-registry.json", "sha256": bg.sha256(self.registry_path)},
            "domains": domains, "amendment_history": []
        }
        self.manifest_path = self.root / "docs/architecture/baseline-manifest.json"
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")
        bg.ROOT = self.root
        bg.MANIFEST = self.manifest_path
        bg.REGISTRY = self.registry_path
        self.binding_path = self.root / "openspec/changes/demo-feature/design/baseline-binding.json"
        self.binding = bg.make_binding("demo-feature", self.manifest, self.registry)
        self.binding["approval"] = {"status": "APPROVED", "reviewer": "Product Owner", "reviewed_at": "2026-11-03", "evidence": self.evidence_rel}
        entry = self.binding["constraints"][0]
        entry.update({
            "applicability": "APPLICABLE", "decision": "COMPLIANT", "rationale": "The feature calls through the documented module boundary.",
            "design_evidence": [self.design_rel],
            "implementation_verification": {"status": "PASS", "method": "Automated architecture test and manual review", "evidence": [self.impl_rel], "reason": ""},
            "acceptance_verification": {"status": "PASS", "method": "Independent acceptance review", "evidence": [self.acceptance_rel], "reason": ""},
            "exception": None
        })
        self.save_binding()

    def tearDown(self):
        self.tmp.cleanup()

    def save_binding(self):
        self.binding_path.write_text(json.dumps(self.binding, indent=2), encoding="utf-8")

    def test_frozen_manifest_and_registry_pass(self):
        manifest, registry = bg.read_inputs()
        self.assertEqual([], bg.validate_manifest(manifest, registry, require_frozen=True))

    def test_hash_drift_blocks_frozen_baseline(self):
        (self.root / self.domain_files["architecture"]).write_text("# 架构基线\nUnapproved edit.\n", encoding="utf-8")
        errors = bg.validate_manifest(self.manifest, self.registry, require_frozen=True)
        self.assertTrue(any("baseline file drift" in x for x in errors), errors)

    def test_requirement_design_implementation_and_acceptance_pass(self):
        for phase in ("requirement", "design", "implementation", "acceptance"):
            with self.subTest(phase=phase):
                self.assertEqual([], bg.check_change("demo-feature", phase))

    def test_missing_constraint_binding_blocks(self):
        self.binding["constraints"] = []
        self.save_binding()
        errors = bg.check_change("demo-feature", "requirement")
        self.assertTrue(any("not bound" in x for x in errors), errors)

    def test_pending_design_blocks_design_phase(self):
        self.binding["constraints"][0]["decision"] = "PENDING"
        self.save_binding()
        errors = bg.check_change("demo-feature", "design")
        self.assertTrue(any("design decision" in x for x in errors), errors)

    def test_missing_implementation_evidence_blocks(self):
        self.binding["constraints"][0]["implementation_verification"]["evidence"] = ["missing.log"]
        self.save_binding()
        errors = bg.check_change("demo-feature", "implementation")
        self.assertTrue(any("evidence file missing" in x for x in errors), errors)

    def test_acceptance_requires_its_own_verification_evidence(self):
        self.binding["constraints"][0]["acceptance_verification"] = {
            "status": "PENDING", "method": "", "evidence": [], "reason": ""
        }
        self.save_binding()
        errors = bg.check_change("demo-feature", "acceptance")
        self.assertTrue(any("acceptance_verification.status must be PASS" in x for x in errors), errors)

    def test_pending_exception_blocks(self):
        entry = self.binding["constraints"][0]
        entry["decision"] = "COMPLIANT"
        entry["exception"] = {"status": "REJECTED", "exception_id": "EX-1", "reason": "temporary", "scope": "demo feature"}
        self.save_binding()
        errors = bg.check_change("demo-feature", "design")
        self.assertTrue(any("exception details must be null" in x for x in errors), errors)

    def test_changed_domain_requires_explicit_no_impact_rebase(self):
        doc = self.root / self.domain_files["architecture"]
        doc.write_text("# 架构基线\nApproved clarification.\n", encoding="utf-8")
        self.manifest["domains"]["architecture"]["version"] = "1.0.1"
        self.manifest["domains"]["architecture"]["files"][0]["sha256"] = bg.sha256(doc)
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")
        errors = bg.check_change("demo-feature", "design")
        self.assertTrue(any("changed since Change snapshot" in x for x in errors), errors)
        manifest, registry = bg.read_inputs()
        current = bg.domain_fingerprints(manifest, registry)["architecture"]
        self.binding["rebase_reviews"]["architecture"] = {
            "current_version": current["version"], "current_fingerprint": current["fingerprint"],
            "conclusion": "NO_IMPACT", "reviewer": "Architecture Owner", "reviewed_at": "2026-11-03",
            "evidence": self.evidence_rel
        }
        self.save_binding()
        self.assertEqual([], bg.check_change("demo-feature", "design"))


    def test_initial_freeze_requires_all_domain_approvals_and_hashes(self):
        self.manifest["status"] = "DRAFT"
        self.manifest["approval"] = {"approver": "", "approved_at": "", "evidence": ""}
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")
        args = type("Args", (), {"approved_by": "Project Owner", "approved_at": "2026-11-03", "evidence": self.evidence_rel})()
        self.assertEqual(0, bg.cmd_freeze(args))
        self.assertEqual("FROZEN", bg.read_inputs()[0]["status"])

    def test_amendment_lifecycle_blocks_then_refreezes_with_version_bump(self):
        open_args = type("Args", (), {"request_id": "BCR-2026-001", "domains": "architecture", "opened_by": "Tech Lead"})()
        self.assertEqual(0, bg.cmd_open_amendment(open_args))
        self.assertNotEqual([], bg.validate_manifest(bg.read_inputs()[0], bg.read_inputs()[1], require_frozen=True))
        doc = self.root / self.domain_files["architecture"]
        doc.write_text("# 架构基线\nApproved amended architecture.\n", encoding="utf-8")
        current, _ = bg.read_inputs()
        current["domains"]["architecture"]["version"] = "1.1.0"
        current["overall_version"] = "1.0.1"
        bg.save_json(bg.MANIFEST, current)
        self.assertEqual(0, bg.cmd_refresh_hashes(type("Args", (), {})()))
        close_args = type("Args", (), {
            "request_id": "BCR-2026-001", "approved_by": "Architecture Owner",
            "approved_at": "2026-11-03", "effective_revision": "git:abcdef0123456789",
            "evidence": self.evidence_rel
        })()
        self.assertEqual(0, bg.cmd_close_amendment(close_args))
        manifest, registry = bg.read_inputs()
        self.assertEqual([], bg.validate_manifest(manifest, registry, require_frozen=True))


    def test_amendment_requires_overall_version_bump(self):
        open_args = type("Args", (), {"request_id": "BCR-2026-002", "domains": "architecture", "opened_by": "Tech Lead"})()
        self.assertEqual(0, bg.cmd_open_amendment(open_args))
        doc = self.root / self.domain_files["architecture"]
        doc.write_text("# 架构基线\nApproved change.\n", encoding="utf-8")
        current, _ = bg.read_inputs()
        current["domains"]["architecture"]["version"] = "1.1.0"
        bg.save_json(bg.MANIFEST, current)
        self.assertEqual(0, bg.cmd_refresh_hashes(type("Args", (), {})()))
        close_args = type("Args", (), {
            "request_id": "BCR-2026-002", "approved_by": "Architecture Owner",
            "approved_at": "2026-11-03", "effective_revision": "git:abcdef0123456789",
            "evidence": self.evidence_rel
        })()
        with self.assertRaisesRegex(ValueError, "overall_version must be incremented"):
            bg.cmd_close_amendment(close_args)

    def test_frozen_baseline_rejects_unrecorded_open_amendment(self):
        self.manifest["amendment_history"] = [{"request_id": "BCR-1", "domains": ["architecture"], "previous_versions": {"architecture": "1.0.0"}, "status": "OPEN"}]
        errors = bg.validate_manifest(self.manifest, self.registry, require_frozen=True)
        self.assertTrue(any("still OPEN" in x for x in errors), errors)

    def test_should_not_allow_frozen_file_edit_even_with_stale_binding(self):
        doc = self.root / self.domain_files["api"]
        doc.write_text("# API 基线\nUnapproved.\n", encoding="utf-8")
        errors = bg.check_change("demo-feature", "requirement")
        self.assertTrue(any("baseline file drift" in x for x in errors), errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
