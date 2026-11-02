#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <project-dir> [project-dir ...]" >&2
  echo "Pass each frontend/backend/module directory explicitly; no project is silently skipped." >&2
  exit 2
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ran=0
failed=0

for input_dir in "$@"; do
  if [[ "$input_dir" = /* ]]; then dir="$input_dir"; else dir="$(cd "$ROOT" && cd "$input_dir" 2>/dev/null && pwd)" || { echo "ERROR: project directory not found: $input_dir" >&2; exit 2; }; fi
  [[ -d "$dir" ]] || { echo "ERROR: not a directory: $dir" >&2; exit 2; }
  echo "== Testing: $dir =="
  kind=""
  if [[ -f "$dir/package.json" ]]; then
    command -v node >/dev/null 2>&1 || { echo "node required for $dir/package.json" >&2; exit 2; }
    package_info="$(node -e 'try { const p=require(process.argv[1]); process.stdout.write(JSON.stringify({test:!!(p.scripts&&p.scripts.test),pm:(p.packageManager||"").split("@")[0]})) } catch(e) { process.exit(2) }' "$dir/package.json")" || { echo "Invalid package.json: $dir/package.json" >&2; exit 1; }
    has_test="$(node -e 'process.stdout.write(JSON.parse(process.argv[1]).test ? "yes" : "no")' "$package_info")"
    pm="$(node -e 'process.stdout.write(JSON.parse(process.argv[1]).pm)' "$package_info")"
    [[ "$has_test" == "yes" ]] || { echo "ERROR: $dir/package.json has no scripts.test; configure a real test command." >&2; exit 2; }
    [[ -n "$pm" ]] || { [[ ! -f "$dir/pnpm-lock.yaml" ]] || pm="pnpm"; [[ ! -f "$dir/yarn.lock" ]] || pm="yarn"; [[ ! -f "$dir/bun.lockb" && ! -f "$dir/bun.lock" ]] || pm="bun"; [[ -n "$pm" ]] || pm="npm"; }
    case "$pm" in
      npm) command -v npm >/dev/null 2>&1 || { echo "npm unavailable in $dir" >&2; exit 2; }; (cd "$dir" && npm test) || failed=1 ;;
      pnpm) command -v pnpm >/dev/null 2>&1 || { echo "pnpm unavailable in $dir" >&2; exit 2; }; (cd "$dir" && pnpm test) || failed=1 ;;
      yarn) command -v yarn >/dev/null 2>&1 || { echo "yarn unavailable in $dir" >&2; exit 2; }; (cd "$dir" && yarn test) || failed=1 ;;
      bun) command -v bun >/dev/null 2>&1 || { echo "bun unavailable in $dir" >&2; exit 2; }; (cd "$dir" && bun test) || failed=1 ;;
      *) echo "Unsupported packageManager '$pm' in $dir/package.json" >&2; exit 2 ;;
    esac
    kind="$pm"
  elif [[ -f "$dir/pom.xml" ]]; then
    if [[ -x "$dir/mvnw" ]]; then (cd "$dir" && ./mvnw test) || failed=1
    elif command -v mvn >/dev/null 2>&1; then (cd "$dir" && mvn test) || failed=1
    else echo "Maven unavailable for $dir" >&2; exit 2; fi
    kind="maven"
  elif [[ -f "$dir/build.gradle" || -f "$dir/build.gradle.kts" ]]; then
    if [[ -x "$dir/gradlew" ]]; then (cd "$dir" && ./gradlew test) || failed=1
    elif command -v gradle >/dev/null 2>&1; then (cd "$dir" && gradle test) || failed=1
    else echo "Gradle unavailable for $dir" >&2; exit 2; fi
    kind="gradle"
  elif [[ -f "$dir/pyproject.toml" || -f "$dir/pytest.ini" || -d "$dir/tests" ]]; then
    PY="$(command -v python3 || command -v python)" || true
    [[ -n "$PY" ]] || { echo "Neither python3 nor python is available" >&2; exit 2; }
    (cd "$dir" && "$PY" -m pytest) || failed=1
    kind="pytest"
  elif [[ -f "$dir/go.mod" ]]; then
    command -v go >/dev/null 2>&1 || { echo "go unavailable" >&2; exit 2; }
    (cd "$dir" && go test ./...) || failed=1
    kind="go"
  else
    echo "ERROR: no recognized test project or command in $dir. Add support explicitly rather than treating it as passed." >&2
    exit 2
  fi
  ran=$((ran + 1))
  echo "Test command dispatched: $kind ($dir)"
done

if (( ran == 0 )); then echo "ERROR: no test commands ran." >&2; exit 2; fi
if (( failed )); then echo "One or more test commands failed." >&2; exit 1; fi
echo "All $ran requested project test commands passed. Note: this runs the detected default test command only, not lint/build/contract tests unless configured in that command."
