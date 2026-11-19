#!/usr/bin/env bash
# Repository-level CI entry point. Safe to run locally; does not mutate state.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python scripts/check-package.py
bash scripts/test-scripts.sh
python scripts/check-step-contracts.py
python scripts/check-output-consumption.py
python scripts/check-output-template-matrix.py
python scripts/gen-manifest.py --check
python scripts/check-layout.py --mode auto
if [[ -f toolkit-lock.json ]]; then
  python scripts/toolkit-sync.py verify --require-lock
fi

if [[ -f docs/architecture/baseline-manifest.json ]]; then
  bash scripts/check-required-files.sh --strict
  python scripts/baseline-governance.py audit --require-frozen
  python scripts/check-requirements.py --strict
  python scripts/check-reference-research.py --strict
  python scripts/check-architecture-baseline.py --strict
else
  echo "SKIP_PROJECT_BASELINE_CHECKS=not-initialized"
fi

echo "CI_CHECKS_PASSED"
