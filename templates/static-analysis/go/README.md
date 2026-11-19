# Go Pack

## Target Stack and Version

- Go 1.22 or newer; golangci-lint v1.64.x (the configuration targets the v1 schema). Pin the exact version chosen at 03 in `docs/architecture/technology-decisions.md` and `quality-gates.json`.
- If the project pins golangci-lint v2, run `golangci-lint migrate` and commit the migrated config.

## Config Files

| File | Landing path (stack-relative) | Purpose |
|---|---|---|
| `.golangci.yml` | `.golangci.yml` | Linter selection and settings |

## Blocking Command (offline)

```bash
golangci-lint run ./...
```

Register it in `quality-gates.json` as a blocking tool with `configs: [".golangci.yml"]`. staticcheck, govet, errcheck, ineffassign, unused, and gosimple are the blocking correctness linters; the revive style subset is advisory (run it as a separate advisory tool or configure it to report warnings only), and its findings never fail a gate. The command runs the locally installed binary and does not fetch tools. Set `modules-download-mode: readonly` and make sure the module cache is warm before the gate runs; a missing module cache or tool is BLOCKED, not auto-installed.

## Packages to Install (task-authorized)

| Package | Target | Required when | Purpose |
|---|---|---|---|
| `golangci-lint` binary | v1.64.x | always | Blocking linter aggregator |

Install as an **explicitly authorized task** recorded in `tasks.md` — a pinned release binary or `go install github.com/golangci/golangci-lint/cmd/golangci-lint@v1.64.x`. The install step may use the network; every quality-gate run is offline. The quality-gates runner never installs anything.

## Rule Choices That Differ From Tool Defaults

- `disable-all: true` plus an explicit list (`staticcheck`, `govet`, `errcheck`, `ineffassign`, `unused`, `gosimple`, `revive`): no surprise linters are enabled by default.
- `issues.exclude-use-default: false` removes golangci-lint's built-in exclusions, so findings are not silently hidden.
- `max-issues-per-linter: 0` and `max-same-issues: 0` report every finding; the defaults cap output.
- `govet` runs all analyzers except `fieldalignment` (it is a performance hint, not correctness; enable it explicitly if the project wants it).
- `revive` runs a small documented subset (`exported`, `package-comments`, `indent-error-flow`, `errorf`, `range`, `superfluous-else`) instead of its full default set.
- `staticcheck` runs all checks; `errcheck` is relaxed only for `_test.go`.

## Linux/macOS and Windows Notes

The command is identical on both platforms when the binary is on `PATH`. On Windows with Git Bash the binary is `golangci-lint.exe`; the runner resolves it through `PATH`.
