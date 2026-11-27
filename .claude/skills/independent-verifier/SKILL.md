---
name: independent-verifier
description: Perform independent, read-only verification of implemented code against specs, ACs, contracts, UI assertions, static gates, and footprint.
---

# Stage 09: Independent Verification and Acceptance Evidence

## Role
Act as an independent, read-only Verifier in a separate context from the Builder. Verify the exact implemented revision against specs, ACs, API/IO/UI contracts, static gates, and footprint without modifying business code or `baseline-binding.json`.

## Required Methods
- Use `verification-before-completion`: every PASS claim requires a freshly executed command and real exit code.

## Execution Flow
1. **Entry**: Run `python scripts/workflow.py check-entry --step 09-independent-verification --change-id <change-id>` and `python scripts/agent-context.py --stage 09 --change <change-id>`. Read truth contracts and the code diff first; avoid anchoring on Builder narratives.
2. **Read-Only & Footprint Verification (Mandatory)**:
   - Run `python scripts/check-change-footprint.py <change-id> --verify` to confirm revision stability (`diff_sha256` matches Stage 08 `implementation-diff.json`) and slice compliance.
3. **Independent Test & Contract Verification**:
   - Re-run automated unit/integration/contract tests independently and map every AC in `design/user-stories.md` and `design/test-cases.csv` to real execution results.
   - Verify `api/openapi.yaml`, `api-io-mapping.csv`, `io-catalog.csv`, `interface-catalog.csv`, and `baseline-binding.json` against the actual diff.
4. **Independent Static Analysis (when `docs/architecture/quality-gates.json` exists)**:
   - Run `python scripts/run-quality-gates.py <change-id> --independent --identity <verifier-id> --builder-identity <builder-id>` → writes `design/evidence/static-analysis-independent.json` (distinct from `builder_identity`).
   - Run `python scripts/check-static-analysis.py --change <change-id> --expect-independent`.
5. **Independent UI Verification (when UI is involved)**:
   - Re-run `python scripts/check-figma-layout.py --change <change-id> --base-url <url> --out openspec/changes/<change-id>/design/evidence/independent-figma-layout-check.json` (never overwrite Stage 08's `figma-layout-check.json`).
   - Re-run `python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>`. Never use screenshots.
6. **Produce Independent Verification Evidence**:
   - Write `openspec/changes/<change-id>/design/evidence/independent-verification.json` (conforming to `templates/change-assets/design/independent-verification.schema.json`, referencing `static-analysis-independent.json` and `independent-figma-layout-check.json`).
   - Write `openspec/changes/<change-id>/design/evidence/independent-verification-report.md` (≤ 150 lines; reference-style summary of Verdict `PASS`/`FAIL`/`BLOCKED`, AC/test results, findings, and non-executed items).
   - Verdict rules: any failed AC/test, unapproved UI deviation, missing evidence, or footprint/static failure must be `FAIL` or `BLOCKED` (never `PASS`).
7. **Stage-End Gates**:
   - `python scripts/check-independent-verification.py --report openspec/changes/<change-id>/design/evidence/independent-verification-report.md --evidence openspec/changes/<change-id>/design/evidence/independent-verification.json`
   - `python scripts/check-output-context.py --stage 09 --change <change-id>`
   - `python scripts/check-method-evidence.py --step 09-independent-verification --evidence workflow/evidence/<change-id>/09-independent-verification.json`

## Input/Output/Handoff Contract
- **Inputs**: Run `python scripts/agent-context.py --stage 09 --change <change-id>` for the lean read set (diff, specs/ACs/test-cases, contracts, UI CSVs, baseline binding, acceptance policy).
- **Outputs**: `design/evidence/independent-verification-report.md`, `design/evidence/independent-verification.json`, and conditional `design/evidence/static-analysis-independent.json`, `design/evidence/independent-figma-layout-check.json`.
- **Downstream Handoff**: Independent `PASS` report, AC/test/UI/static evidence, and verified revision fingerprint for Stage 10.
- **Review & Boundaries**:
  - Generate `workflow/evidence/<change-id>/09-independent-verification.json` and run:
    `python scripts/workflow.py request-review --step 09-independent-verification --change-id <change-id> --evidence workflow/evidence/<change-id>/09-independent-verification.json --summary "<summary>"`
  - Present `templates/workflow/step-handoff-report.md` and end the turn. Advance (`approve` → `transition`) only after explicit user approval (only `PASS` may proceed to Stage 10). Follow `AGENTS.md`.
