#!/usr/bin/env bash
# Run every script-level regression suite (not application tests).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
fail=0
for test in scripts/test-*.py; do
  echo "=== $test"
  python "$test" || fail=1
done
for test in scripts/test-*.sh; do
  case "$test" in
    scripts/test-all.sh|scripts/test-scripts.sh) continue ;;
  esac
  echo "=== $test"
  bash "$test" || fail=1
done
if (( fail )); then
  echo "SCRIPT_REGRESSION_FAILED"
  exit 1
fi
echo "SCRIPT_REGRESSION_PASSED"
