#!/usr/bin/env python3
"""Machine-enforced project baseline manifest, constraint registry and Change binding gates."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/architecture/baseline-manifest.json"
REGISTRY = ROOT / "docs/architecture/constraint-registry.json"
DOMAINS = ("product", "architecture", "data_domain", "api", "frontend", "test_quality")
STATUSES = {"DRAFT", "FROZEN", "UNDER_AMENDMENT"}
CONSTRAINT_STATUSES = {"DRAFT", "ACTIVE", "RETIRED"}
LEVELS = {"MUST", "SHOULD", "MAY", "PROHIBITED"}
HEX = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+\.\d+$")
CHANGE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_sha(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def safe_file(rel: str) -> Path:
    if not isinstance(rel, str) or not rel.strip():
        raise ValueError("empty repository-relative path")
    path = (ROOT / rel).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        raise ValueError(f"path escapes project root: {rel}")
    return path


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"required JSON file missing: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def save_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_inputs():
    return load_json(MANIFEST), load_json(REGISTRY)


def domain_fingerprints(manifest, registry):
    result = {}
    for domain, cfg in manifest.get("domains", {}).items():
        # Fingerprint every constraint field (including enforcement metadata and approvals),
        # not only its prose rule. A validator or approval change is a baseline change too.
        domain_constraints = [
            c for c in registry.get("constraints", [])
            if c.get("domain") == domain and c.get("status") != "RETIRED"
        ]
        file_rows = sorted(
            [{"path": f.get("path"), "sha256": f.get("sha256", "")} for f in cfg.get("files", [])],
            key=lambda x: x["path"] or ""
        )
        domain_meta = {
            key: cfg.get(key, "")
            for key in ("version", "status", "owner", "approver", "approved_at", "effective_revision", "approval_evidence")
        }
        result[domain] = {
            "version": cfg.get("version", ""),
            "status": cfg.get("status", ""),
            "fingerprint": canonical_sha({"domain": domain_meta, "files": file_rows, "constraints": domain_constraints}),
        }
    return result


def validate_registry(manifest, registry, require_frozen=False):
    errors = []
    if registry.get("schema_version") != "1.0":
        errors.append("constraint registry schema_version must be 1.0")
    if not VERSION.match(str(registry.get("registry_version", ""))):
        errors.append("constraint registry registry_version must be semantic x.y.z")
    constraints = registry.get("constraints")
    if not isinstance(constraints, list):
        return errors + ["constraint registry constraints must be an array"]
    ids = set()
    domain_files = {
        d: {x.get("path") for x in cfg.get("files", [])}
        for d, cfg in manifest.get("domains", {}).items()
    }
    for c in constraints:
        cid = c.get("id", "<missing-id>")
        if not re.match(r"^[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+-\d{3,}$", str(cid)):
            errors.append(f"invalid constraint ID: {cid}")
        if cid in ids:
            errors.append(f"duplicate constraint ID: {cid}")
        ids.add(cid)
        if c.get("domain") not in DOMAINS:
            errors.append(f"{cid}: unknown domain {c.get('domain')}")
        if c.get("status") not in CONSTRAINT_STATUSES:
            errors.append(f"{cid}: status must be one of {sorted(CONSTRAINT_STATUSES)}")
        if c.get("level") not in LEVELS:
            errors.append(f"{cid}: level must be one of {sorted(LEVELS)}")
        for key in ("title", "rule", "rationale", "scope"):
            if not str(c.get(key, "")).strip():
                errors.append(f"{cid}: {key} is required")
        enforcement = c.get("enforcement") or {}
        enforcement_type = enforcement.get("type")
        if enforcement_type not in ("AUTOMATED", "MANUAL", "HYBRID"):
            errors.append(f"{cid}: enforcement.type must be AUTOMATED, MANUAL or HYBRID")
        if enforcement_type in ("AUTOMATED", "HYBRID"):
            validator = enforcement.get("validator", "")
            try:
                validator_path = safe_file(validator)
                if not validator_path.is_file():
                    errors.append(f"{cid}: validator does not exist: {validator}")
            except Exception as exc:
                errors.append(f"{cid}: invalid validator path: {exc}")
        if enforcement_type in ("MANUAL", "HYBRID") and enforcement.get("evidence_required") is not True:
            errors.append(f"{cid}: manual/hybrid enforcement must require evidence")
        source = c.get("source") or {}
        src = source.get("file", "")
        section = source.get("section", "")
        if not str(section).strip():
            errors.append(f"{cid}: source.section is required")
        if src not in domain_files.get(c.get("domain"), set()):
            errors.append(f"{cid}: source file must be listed in its domain manifest: {src}")
        try:
            source_path = safe_file(src)
            if not source_path.is_file():
                errors.append(f"{cid}: source file missing: {src}")
            elif section:
                source_text = source_path.read_text(encoding="utf-8")
                heading_re = re.compile(r"^#{1,6}\s+" + re.escape(section) + r"\s*#*\s*$", re.M)
                if not heading_re.search(source_text):
                    errors.append(f"{cid}: source heading not found: {src} :: {section}")
        except Exception as exc:
            errors.append(f"{cid}: invalid source path: {exc}")
        if c.get("status") == "ACTIVE":
            if not c.get("owner") or not c.get("approved_by") or not c.get("approved_at"):
                errors.append(f"{cid}: ACTIVE constraint requires owner, approved_by and approved_at")
        if require_frozen and c.get("status") == "DRAFT":
            errors.append(f"{cid}: DRAFT constraint cannot be part of a frozen project baseline")
    if require_frozen and not any(c.get("status") == "ACTIVE" for c in constraints):
        errors.append("frozen baseline must contain at least one ACTIVE constraint")
    return errors


def validate_manifest(manifest, registry, require_frozen=False):
    errors = []
    if manifest.get("schema_version") != "1.0":
        errors.append("baseline manifest schema_version must be 1.0")
    if (require_frozen or manifest.get("status") == "FROZEN") and (not str(manifest.get("project_id", "")).strip() or manifest.get("project_id") == "REPLACE_WITH_PROJECT_ID"):
        errors.append("baseline manifest project_id must be configured before freeze")
    if not VERSION.match(str(manifest.get("overall_version", ""))):
        errors.append("baseline manifest overall_version must be semantic x.y.z")
    if manifest.get("status") not in STATUSES:
        errors.append(f"baseline manifest status must be one of {sorted(STATUSES)}")
    domains = manifest.get("domains") or {}
    missing_domains = set(DOMAINS) - set(domains)
    extra_domains = set(domains) - set(DOMAINS)
    if missing_domains:
        errors.append("missing baseline domains: " + ", ".join(sorted(missing_domains)))
    if extra_domains:
        errors.append("unknown baseline domains: " + ", ".join(sorted(extra_domains)))
    for domain in DOMAINS:
        cfg = domains.get(domain)
        if not isinstance(cfg, dict):
            continue
        if not VERSION.match(str(cfg.get("version", ""))):
            errors.append(f"{domain}: version must be semantic x.y.z")
        if cfg.get("status") not in STATUSES:
            errors.append(f"{domain}: invalid status")
        files = cfg.get("files")
        if not isinstance(files, list) or not files:
            errors.append(f"{domain}: at least one authoritative file is required")
            continue
        seen = set()
        for item in files:
            rel = item.get("path", "")
            if rel in seen:
                errors.append(f"{domain}: duplicate file path {rel}")
            seen.add(rel)
            try:
                p = safe_file(rel)
                if not p.is_file():
                    errors.append(f"{domain}: baseline file missing: {rel}")
                    continue
                digest = item.get("sha256", "")
                if digest:
                    if not HEX.match(str(digest)):
                        errors.append(f"{domain}: invalid SHA-256 for {rel}")
                    elif cfg.get("status") == "FROZEN" and sha256(p) != digest:
                        errors.append(f"{domain}: baseline file drift: {rel}")
                elif require_frozen or cfg.get("status") == "FROZEN":
                    errors.append(f"{domain}: missing SHA-256 for frozen baseline file: {rel}")
            except Exception as exc:
                errors.append(f"{domain}: unsafe path {rel}: {exc}")
        if cfg.get("status") == "FROZEN":
            for field in ("owner", "approver", "approved_at", "effective_revision", "approval_evidence"):
                if not str(cfg.get(field, "")).strip():
                    errors.append(f"{domain}: FROZEN domain requires {field}")
            try:
                if cfg.get("approval_evidence") and not safe_file(cfg["approval_evidence"]).is_file():
                    errors.append(f"{domain}: approval evidence file missing: {cfg['approval_evidence']}")
            except Exception as exc:
                errors.append(f"{domain}: invalid approval evidence path: {exc}")
    reg = manifest.get("constraint_registry") or {}
    if reg.get("path") != "docs/architecture/constraint-registry.json":
        errors.append("constraint_registry.path must be docs/architecture/constraint-registry.json")
    reg_hash = reg.get("sha256", "")
    if reg_hash:
        if not HEX.match(str(reg_hash)):
            errors.append("constraint_registry.sha256 is not a valid SHA-256")
        elif manifest.get("status") == "FROZEN" and sha256(REGISTRY) != reg_hash:
            errors.append("constraint registry drift: docs/architecture/constraint-registry.json")
    elif require_frozen or manifest.get("status") == "FROZEN":
        errors.append("frozen baseline requires constraint_registry.sha256")
    if manifest.get("status") == "FROZEN":
        approval = manifest.get("approval") or {}
        for field in ("approver", "approved_at", "evidence"):
            if not str(approval.get(field, "")).strip():
                errors.append(f"FROZEN overall baseline requires approval.{field}")
        try:
            if approval.get("evidence") and not safe_file(approval["evidence"]).is_file():
                errors.append(f"overall baseline approval evidence file missing: {approval['evidence']}")
        except Exception as exc:
            errors.append(f"invalid overall baseline approval evidence path: {exc}")
        for domain in DOMAINS:
            if domains.get(domain, {}).get("status") != "FROZEN":
                errors.append(f"overall baseline is FROZEN but domain {domain} is not FROZEN")
        history = manifest.get("amendment_history", [])
        if history and history[-1].get("status") == "OPEN":
            errors.append(f"baseline amendment {history[-1].get('request_id')} is still OPEN; close-amendment is required")
        if history and history[-1].get("status") == "CLOSED":
            item = history[-1]
            for domain in item.get("domains", []):
                if domains.get(domain, {}).get("version") == item.get("previous_versions", {}).get(domain):
                    errors.append(f"{domain}: domain version was not incremented after amendment {item.get('request_id')}")
    if require_frozen and manifest.get("status") != "FROZEN":
        errors.append(f"project baseline is {manifest.get('status')}, not FROZEN")
    errors.extend(validate_registry(manifest, registry, require_frozen=require_frozen))
    return errors


def binding_path(change_id):
    if not CHANGE_ID.match(change_id):
        raise ValueError("Change ID must be lowercase kebab-case")
    return safe_file(f"openspec/changes/{change_id}/design/baseline-binding.json")


def make_binding(change_id, manifest, registry):
    entries = []
    for c in registry.get("constraints", []):
        if c.get("status") != "ACTIVE":
            continue
        entries.append({
            "constraint_id": c["id"],
            "domain": c["domain"],
            "constraint_revision": c.get("revision", "1.0"),
            "applicability": "UNASSESSED",
            "decision": "PENDING",
            "rationale": "",
            "design_evidence": [],
            "implementation_verification": {"status": "PENDING", "method": "", "evidence": [], "reason": ""},
            "acceptance_verification": {"status": "PENDING", "method": "", "evidence": [], "reason": ""},
            "exception": None
        })
    return {
        "schema_version": "1.0",
        "change_id": change_id,
        "created_at": now(),
        "baseline_snapshot": {
            "overall_version": manifest.get("overall_version", ""),
            "overall_status": manifest.get("status", ""),
            "manifest_sha256": sha256(MANIFEST),
            "registry_sha256": sha256(REGISTRY),
            "domains": domain_fingerprints(manifest, registry)
        },
        "constraints": entries,
        "rebase_reviews": {},
        "approval": {"status": "PENDING", "reviewer": "", "reviewed_at": "", "evidence": ""}
    }


def validate_evidence_paths(paths, label, errors):
    if not isinstance(paths, list) or not paths:
        errors.append(f"{label}: at least one evidence path is required")
        return
    for rel in paths:
        try:
            p = safe_file(rel)
            if not p.is_file():
                errors.append(f"{label}: evidence file missing: {rel}")
        except Exception as exc:
            errors.append(f"{label}: invalid evidence path {rel}: {exc}")


def check_change(change_id, phase):
    errors = []
    try:
        manifest, registry = read_inputs()
    except Exception as exc:
        return [str(exc)]
    errors.extend(validate_manifest(manifest, registry, require_frozen=True))
    p = binding_path(change_id)
    if not p.is_file():
        return errors + [f"missing Change baseline binding: {p.relative_to(ROOT)}; run init-binding"]
    try:
        binding = load_json(p)
    except Exception as exc:
        return errors + [str(exc)]
    if binding.get("schema_version") != "1.0":
        errors.append("baseline binding schema_version must be 1.0")
    if binding.get("change_id") != change_id:
        errors.append("baseline binding Change ID mismatch")
    approval = binding.get("approval") or {}
    if phase in ("requirement", "design", "implementation", "acceptance"):
        if approval.get("status") != "APPROVED" or not approval.get("reviewer") or not approval.get("reviewed_at"):
            errors.append("baseline binding approval must be APPROVED with reviewer and reviewed_at")
        try:
            ev = approval.get("evidence", "")
            if not ev or not safe_file(ev).is_file():
                errors.append("baseline binding approval evidence file is missing")
        except Exception as exc:
            errors.append(f"invalid binding approval evidence: {exc}")
    snap = binding.get("baseline_snapshot") or {}
    current_domains = domain_fingerprints(manifest, registry)
    old_domains = snap.get("domains") or {}
    if snap.get("overall_version") != manifest.get("overall_version"):
        overall_fp = canonical_sha({"overall_version": manifest.get("overall_version"), "domains": current_domains})
        review = (binding.get("rebase_reviews") or {}).get("overall") or {}
        if (review.get("current_version") != manifest.get("overall_version") or
                review.get("current_fingerprint") != overall_fp or review.get("conclusion") != "NO_IMPACT" or
                not review.get("reviewer") or not review.get("reviewed_at")):
            errors.append("overall baseline version changed; a current NO_IMPACT overall rebase review is required")
        else:
            try:
                if not review.get("evidence") or not safe_file(review["evidence"]).is_file():
                    errors.append("overall rebase review evidence is missing")
            except Exception as exc:
                errors.append(f"overall rebase review evidence invalid: {exc}")
    for domain in DOMAINS:
        old = old_domains.get(domain) or {}
        cur = current_domains.get(domain) or {}
        if old.get("fingerprint") != cur.get("fingerprint") or old.get("version") != cur.get("version"):
            review = (binding.get("rebase_reviews") or {}).get(domain) or {}
            expected = review.get("current_fingerprint") == cur.get("fingerprint") and review.get("current_version") == cur.get("version")
            if not expected or review.get("conclusion") != "NO_IMPACT" or not review.get("reviewer") or not review.get("reviewed_at"):
                errors.append(f"baseline domain {domain} changed since Change snapshot; a current NO_IMPACT rebase review or refresh-binding is required")
            else:
                try:
                    if not review.get("evidence") or not safe_file(review["evidence"]).is_file():
                        errors.append(f"{domain}: rebase review evidence is missing")
                except Exception as exc:
                    errors.append(f"{domain}: invalid rebase review evidence: {exc}")
    active = {c["id"]: c for c in registry.get("constraints", []) if c.get("status") == "ACTIVE"}
    entries = binding.get("constraints")
    if not isinstance(entries, list):
        return errors + ["baseline binding constraints must be an array"]
    entry_map = {}
    for e in entries:
        cid = e.get("constraint_id")
        if cid in entry_map:
            errors.append(f"duplicate constraint binding: {cid}")
        entry_map[cid] = e
    for cid in sorted(set(active) - set(entry_map)):
        errors.append(f"active project constraint not bound by Change: {cid}")
    for cid in sorted(set(entry_map) - set(active)):
        errors.append(f"binding references non-active/unknown constraint: {cid}")
    for cid, c in active.items():
        e = entry_map.get(cid)
        if not e:
            continue
        if e.get("domain") != c.get("domain") or e.get("constraint_revision") != c.get("revision", "1.0"):
            errors.append(f"{cid}: binding domain/revision differs from current registry")
        applicability = e.get("applicability")
        decision = e.get("decision")
        if phase in ("requirement", "design", "implementation", "acceptance"):
            if applicability not in ("APPLICABLE", "NOT_APPLICABLE"):
                errors.append(f"{cid}: applicability must be APPLICABLE or NOT_APPLICABLE")
            if not str(e.get("rationale", "")).strip():
                errors.append(f"{cid}: applicability/rule rationale is required")
        if applicability == "NOT_APPLICABLE":
            if decision != "NOT_APPLICABLE":
                errors.append(f"{cid}: NOT_APPLICABLE constraint must use decision NOT_APPLICABLE")
            if phase in ("implementation", "acceptance"):
                v = e.get("implementation_verification") or {}
                if v.get("status") != "NOT_APPLICABLE" or not str(v.get("reason", "")).strip():
                    errors.append(f"{cid}: implementation verification must be NOT_APPLICABLE with reason")
            if phase == "acceptance":
                av = e.get("acceptance_verification") or {}
                if av.get("status") != "NOT_APPLICABLE" or not str(av.get("reason", "")).strip():
                    errors.append(f"{cid}: acceptance verification must be NOT_APPLICABLE with reason")
            continue
        if applicability != "APPLICABLE":
            continue
        if phase in ("design", "implementation", "acceptance"):
            if decision not in ("COMPLIANT", "EXCEPTION_APPROVED"):
                errors.append(f"{cid}: design decision must be COMPLIANT or EXCEPTION_APPROVED")
            validate_evidence_paths(e.get("design_evidence"), f"{cid} design_evidence", errors)
        if decision == "EXCEPTION_APPROVED":
            ex = e.get("exception") or {}
            for field in ("exception_id", "reason", "scope", "approver", "approved_at"):
                if not str(ex.get(field, "")).strip():
                    errors.append(f"{cid}: approved exception requires {field}")
            try:
                if not ex.get("evidence") or not safe_file(ex["evidence"]).is_file():
                    errors.append(f"{cid}: approved exception evidence file is missing")
            except Exception as exc:
                errors.append(f"{cid}: invalid exception evidence: {exc}")
            if ex.get("status") != "APPROVED":
                errors.append(f"{cid}: exception status must be APPROVED")
        elif e.get("exception") is not None:
            errors.append(f"{cid}: exception details must be null unless decision is EXCEPTION_APPROVED")
        if phase in ("implementation", "acceptance"):
            v = e.get("implementation_verification") or {}
            if v.get("status") != "PASS":
                errors.append(f"{cid}: implementation_verification.status must be PASS")
            if not str(v.get("method", "")).strip():
                errors.append(f"{cid}: implementation verification method is required")
            validate_evidence_paths(v.get("evidence"), f"{cid} implementation evidence", errors)
        if phase == "acceptance":
            av = e.get("acceptance_verification") or {}
            if av.get("status") != "PASS":
                errors.append(f"{cid}: acceptance_verification.status must be PASS")
            if not str(av.get("method", "")).strip():
                errors.append(f"{cid}: acceptance verification method is required")
            validate_evidence_paths(av.get("evidence"), f"{cid} acceptance evidence", errors)
    if phase == "requirement":
        # The approval at this point is the human sign-off of the applicability assessment.
        pass
    return errors


def cmd_audit(args):
    manifest, registry = read_inputs()
    errors = validate_manifest(manifest, registry, require_frozen=args.require_frozen)
    if errors:
        print("BASELINE_INVALID")
        for e in errors: print(" - " + e)
        return 1
    print("BASELINE_VALID" if not args.require_frozen else "BASELINE_FROZEN_AND_VALID")
    print(f"OVERALL_VERSION={manifest['overall_version']}")
    print(f"ACTIVE_CONSTRAINTS={sum(1 for c in registry.get('constraints', []) if c.get('status') == 'ACTIVE')}")
    return 0


def cmd_refresh_hashes(args):
    manifest, registry = read_inputs()
    if manifest.get("status") == "FROZEN":
        raise ValueError("refusing to refresh hashes while baseline is FROZEN; run open-amendment before editing frozen baseline files")
    for cfg in manifest.get("domains", {}).values():
        for item in cfg.get("files", []):
            p = safe_file(item["path"])
            if not p.is_file(): raise ValueError(f"missing baseline file: {item['path']}")
            item["sha256"] = sha256(p)
    manifest.setdefault("constraint_registry", {})["sha256"] = sha256(REGISTRY)
    save_json(MANIFEST, manifest)
    print("BASELINE_HASHES_REFRESHED")
    return 0


def cmd_open_amendment(args):
    manifest, registry = read_inputs()
    if manifest.get("status") != "FROZEN":
        raise ValueError("open-amendment requires an overall FROZEN baseline")
    chosen = [x.strip() for x in args.domains.split(",") if x.strip()]
    unknown = set(chosen) - set(DOMAINS)
    if unknown or not chosen:
        raise ValueError("--domains must contain one or more valid domain IDs: " + ", ".join(DOMAINS))
    if not args.request_id.strip():
        raise ValueError("--request-id is required")
    manifest["status"] = "UNDER_AMENDMENT"
    for domain in chosen:
        manifest["domains"][domain]["status"] = "UNDER_AMENDMENT"
    history = manifest.setdefault("amendment_history", [])
    if any(item.get("request_id") == args.request_id for item in history):
        raise ValueError(f"amendment request ID already exists: {args.request_id}")
    history.append({
        "request_id": args.request_id,
        "domains": chosen,
        "previous_overall_version": manifest.get("overall_version", ""),
        "previous_versions": {d: manifest["domains"][d].get("version", "") for d in chosen},
        "previous_fingerprints": domain_fingerprints(manifest, registry),
        "opened_at": now(),
        "opened_by": args.opened_by or "",
        "status": "OPEN"
    })
    save_json(MANIFEST, manifest)
    print("BASELINE_AMENDMENT_OPENED; feature workflow gates are now blocked until re-freeze")
    return 0


def cmd_freeze(args):
    manifest, registry = read_inputs()
    if manifest.get("status") != "DRAFT":
        raise ValueError("freeze is only for the initial DRAFT baseline; use close-amendment for revisions")
    if not args.approved_by.strip() or not args.approved_at.strip() or not args.evidence.strip():
        raise ValueError("--approved-by, --approved-at and --evidence are required")
    evidence = safe_file(args.evidence)
    if not evidence.is_file(): raise ValueError(f"approval evidence missing: {args.evidence}")
    manifest["status"] = "FROZEN"
    manifest["approval"] = {"approver": args.approved_by, "approved_at": args.approved_at, "evidence": args.evidence}
    errors = validate_manifest(manifest, registry, require_frozen=True)
    if errors:
        print("FREEZE_BLOCKED")
        for error in errors: print(" - " + error)
        return 1
    save_json(MANIFEST, manifest)
    print("BASELINE_FROZEN=" + manifest["overall_version"])
    return 0


def cmd_close_amendment(args):
    manifest, registry = read_inputs()
    history = manifest.setdefault("amendment_history", [])
    if not history or history[-1].get("status") != "OPEN" or history[-1].get("request_id") != args.request_id:
        raise ValueError("latest amendment must be OPEN and match --request-id")
    if not args.approved_by.strip() or not args.approved_at.strip() or not args.effective_revision.strip() or not args.evidence.strip():
        raise ValueError("--approved-by, --approved-at, --effective-revision and --evidence are required")
    evidence = safe_file(args.evidence)
    if not evidence.is_file(): raise ValueError(f"approval evidence missing: {args.evidence}")
    candidate = json.loads(json.dumps(manifest))
    item = candidate["amendment_history"][-1]
    try:
        old_overall = tuple(int(x) for x in item.get("previous_overall_version", "").split("."))
        new_overall = tuple(int(x) for x in candidate.get("overall_version", "").split("."))
    except Exception:
        old_overall, new_overall = (), ()
    if len(old_overall) != 3 or len(new_overall) != 3 or new_overall <= old_overall:
        raise ValueError("overall_version must be incremented (semantic version) for every baseline amendment")
    for domain in item.get("domains", []):
        cfg = candidate["domains"][domain]
        cfg["status"] = "FROZEN"
        cfg["approver"] = args.approved_by
        cfg["approved_at"] = args.approved_at
        cfg["approval_evidence"] = args.evidence
        cfg["effective_revision"] = args.effective_revision
    candidate["status"] = "FROZEN"
    candidate["approval"] = {"approver": args.approved_by, "approved_at": args.approved_at, "evidence": args.evidence}
    item["status"] = "CLOSED"
    item["closed_at"] = now()
    item["closed_by"] = args.approved_by
    item["approval_evidence"] = args.evidence
    prior_fingerprints = item.get("previous_fingerprints", {})
    post_fingerprints = domain_fingerprints(candidate, registry)
    selected_domains = set(item.get("domains", []))
    unexpected = [d for d in DOMAINS if prior_fingerprints.get(d, {}).get("fingerprint") != post_fingerprints.get(d, {}).get("fingerprint") and d not in selected_domains]
    errors = []
    if unexpected:
        errors.append("amendment changed domains not declared in --domains: " + ", ".join(unexpected))
    errors.extend(validate_manifest(candidate, registry, require_frozen=True))
    if errors:
        print("AMENDMENT_CLOSE_BLOCKED")
        for error in errors: print(" - " + error)
        return 1
    save_json(MANIFEST, candidate)
    print("BASELINE_AMENDMENT_CLOSED_AND_FROZEN=" + candidate["overall_version"])
    return 0


def cmd_init_binding(args):
    manifest, registry = read_inputs()
    errors = validate_manifest(manifest, registry, require_frozen=True)
    if errors:
        raise ValueError("cannot bind Change to invalid/unfrozen baseline: " + "; ".join(errors))
    p = binding_path(args.change_id)
    if p.exists() and not args.force:
        raise ValueError(f"binding already exists: {p.relative_to(ROOT)}; use --refresh only after completing a documented rebase")
    binding = make_binding(args.change_id, manifest, registry)
    save_json(p, binding)
    print(f"BASELINE_BINDING_CREATED={p.relative_to(ROOT)}")
    print(f"BOUND_CONSTRAINTS={len(binding['constraints'])}")
    return 0


def cmd_refresh_binding(args):
    p = binding_path(args.change_id)
    if not p.is_file():
        raise ValueError("baseline binding does not exist; run init-binding")
    manifest, registry = read_inputs()
    errors = validate_manifest(manifest, registry, require_frozen=True)
    if errors:
        raise ValueError("cannot refresh against invalid/unfrozen baseline: " + "; ".join(errors))
    old = load_json(p)
    prior_snapshot = old.get("baseline_snapshot", {})
    old_snap = prior_snapshot.get("domains", {})
    current = domain_fingerprints(manifest, registry)
    if prior_snapshot.get("overall_version") != manifest.get("overall_version"):
        overall_fp = canonical_sha({"overall_version": manifest.get("overall_version"), "domains": current})
        review = (old.get("rebase_reviews") or {}).get("overall") or {}
        if (review.get("conclusion") != "REBASE_COMPLETED" or review.get("current_version") != manifest.get("overall_version") or
                review.get("current_fingerprint") != overall_fp or not review.get("reviewer") or not review.get("reviewed_at")):
            raise ValueError("overall version changed; record a REBASE_COMPLETED overall review against the current fingerprint before refresh-binding")
        if not review.get("evidence") or not safe_file(review["evidence"]).is_file():
            raise ValueError("overall REBASE_COMPLETED evidence file missing")
    old_entries = {x.get("constraint_id"): x for x in old.get("constraints", [])}
    new_entries = []
    changed_domains = set()
    for domain in DOMAINS:
        before, after = old_snap.get(domain, {}), current.get(domain, {})
        if before.get("fingerprint") != after.get("fingerprint") or before.get("version") != after.get("version"):
            changed_domains.add(domain)
            review = (old.get("rebase_reviews") or {}).get(domain) or {}
            if review.get("conclusion") != "REBASE_COMPLETED" or review.get("current_fingerprint") != after.get("fingerprint") or review.get("current_version") != after.get("version") or not review.get("reviewer") or not review.get("reviewed_at"):
                raise ValueError(f"{domain} must have a REBASE_COMPLETED review against current fingerprint/version before refresh-binding")
            try:
                if not review.get("evidence") or not safe_file(review["evidence"]).is_file():
                    raise ValueError(f"{domain} rebase evidence missing")
            except Exception as exc:
                raise ValueError(f"{domain} rebase evidence invalid: {exc}")
    fresh = make_binding(args.change_id, manifest, registry)
    for entry in fresh["constraints"]:
        prior = old_entries.get(entry["constraint_id"])
        if prior and entry["domain"] not in changed_domains:
            entry.update(prior)
    old.update({
        "baseline_snapshot": fresh["baseline_snapshot"],
        "constraints": fresh["constraints"],
        "approval": {"status": "PENDING", "reviewer": "", "reviewed_at": "", "evidence": ""},
        "last_rebased_at": now(),
        "rebased_domains": sorted(changed_domains)
    })
    save_json(p, old)
    print(f"BASELINE_BINDING_REFRESHED={p.relative_to(ROOT)}")
    print("REBASED_DOMAINS=" + (",".join(sorted(changed_domains)) or "NONE"))
    print("Changed-domain constraints were reset for reassessment; re-approve the binding.")
    return 0


def cmd_check_change(args):
    errors = check_change(args.change_id, args.phase)
    if errors:
        print("CHANGE_BASELINE_BLOCKED")
        for e in errors: print(" - " + e)
        return 3
    print(f"CHANGE_BASELINE_{args.phase.upper()}_PASS={args.change_id}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("audit"); p.add_argument("--require-frozen", action="store_true")
    p = sub.add_parser("refresh-hashes")
    p = sub.add_parser("freeze"); p.add_argument("--approved-by", required=True); p.add_argument("--approved-at", required=True); p.add_argument("--evidence", required=True)
    p = sub.add_parser("open-amendment"); p.add_argument("--request-id", required=True); p.add_argument("--domains", required=True); p.add_argument("--opened-by", default="")
    p = sub.add_parser("close-amendment"); p.add_argument("--request-id", required=True); p.add_argument("--approved-by", required=True); p.add_argument("--approved-at", required=True); p.add_argument("--effective-revision", required=True); p.add_argument("--evidence", required=True)
    p = sub.add_parser("init-binding"); p.add_argument("--change-id", required=True); p.add_argument("--force", action="store_true")
    p = sub.add_parser("refresh-binding"); p.add_argument("--change-id", required=True)
    p = sub.add_parser("check-change"); p.add_argument("--change-id", required=True); p.add_argument("--phase", choices=("requirement", "design", "implementation", "acceptance"), required=True)
    args = ap.parse_args()
    try:
        return {
            "audit": cmd_audit,
            "refresh-hashes": cmd_refresh_hashes,
            "freeze": cmd_freeze,
            "open-amendment": cmd_open_amendment,
            "close-amendment": cmd_close_amendment,
            "init-binding": cmd_init_binding,
            "refresh-binding": cmd_refresh_binding,
            "check-change": cmd_check_change,
        }[args.cmd](args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
