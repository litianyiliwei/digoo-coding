#!/usr/bin/env bash
set -euo pipefail

usage() { echo "Usage: $0 <change-id> [--openapi <file>] [--test-dir <dir>]... [--skip-tests]"; }
if [[ $# -lt 1 ]]; then usage >&2; exit 2; fi
CHANGE_ID="$1"; shift
OPENAPI=""; SKIP_TESTS=0; TEST_DIRS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --openapi) [[ $# -ge 2 ]] || { usage >&2; exit 2; }; OPENAPI="$2"; shift 2 ;;
    --test-dir) [[ $# -ge 2 ]] || { usage >&2; exit 2; }; TEST_DIRS+=("$2"); shift 2 ;;
    --skip-tests) SKIP_TESTS=1; shift ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v git >/dev/null 2>&1 || { echo "git is required for diff checks" >&2; exit 2; }

# OpenSpec validation is required, and strict warnings fail the gate.
command -v openspec >/dev/null 2>&1 || { echo "OpenSpec CLI is required for completion verification." >&2; exit 2; }
openspec validate "$CHANGE_ID" --strict
git diff --check
git diff --cached --check
# Check both unstaged and staged diffs for common placeholders in changed text files.
changed="$(git diff --name-only; git diff --cached --name-only; git ls-files --others --exclude-standard)"
if [[ -n "$changed" ]]; then
  while IFS= read -r file; do
    [[ -n "$file" && -f "$file" ]] || continue
    case "$file" in *.md|*.java|*.kt|*.ts|*.tsx|*.js|*.jsx|*.py|*.go|*.yaml|*.yml|*.json|*.sql|*.sh)
      if grep -nE 'TODO|FIXME|XXX' "$file"; then echo "WARN: unresolved marker in $file"; fi
      ;;
    esac
  done <<< "$(printf '%s\n' "$changed" | sort -u)"
fi
if [[ -n "$OPENAPI" ]]; then bash scripts/validate-openapi.sh "$OPENAPI"; fi
if (( ! SKIP_TESTS )); then
  if (( ${#TEST_DIRS[@]} == 0 )); then echo "Provide at least one --test-dir or explicitly use --skip-tests; tests are not silently skipped." >&2; exit 2; fi
  bash scripts/test-all.sh "${TEST_DIRS[@]}"
else
  echo "WARNING: tests explicitly skipped by --skip-tests. Do not treat this run as full verification."
fi

echo "Git status (inspect; this script never commits or archives):"
git status --short
if (( SKIP_TESTS )); then
  echo "Partial verification completed; NOT a full completion gate because tests were skipped."
else
  echo "Configured verification commands completed. Human/code review and product acceptance still required."
fi
