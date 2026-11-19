# Toolkit Static Analysis Rule Packs

Starter defaults for `templates/static-analysis/`. These files are **copied** into a business project at 08 — they are never executed inside the toolkit repository. Rule packs are starter defaults, not normative: stage 03 selects the tools, versions, config landing paths, and severity policy, then freezes them in `docs/architecture/quality-gates.json`. The machine file wins for execution; deviations are recorded in `docs/architecture/test-strategy.md`.

## Pack Matrix

| Language | Tools | Config files | Blocking command (offline) | Pack |
|---|---|---|---|---|
| TypeScript / JavaScript (Vue / React) | ESLint + typescript-eslint + `eslint-plugin-vue` (React plugin optional) and TypeScript (`tsc`) blocking; Prettier advisory | `eslint.config.js`, `.prettierrc.json`, `tsconfig.strict.json` | `npx --no-install eslint .`; `npx --no-install tsc --noEmit -p tsconfig.strict.json`; `npx --no-install prettier --check .` (advisory) | `typescript/` |
| Java | Checkstyle correctness rules blocking; Checkstyle style rules advisory; SpotBugs optional advisory | `checkstyle.xml` | `java -jar <local-checkstyle-jar> -c <config-path>/checkstyle.xml src/main/java` | `java/` |
| Python | Ruff correctness rules blocking; `ruff format` and Ruff style subset advisory; mypy optional advisory | `ruff.toml` | `ruff check . --select F,S,B,ASYNC,DTZ,PTH,RET,RSE,T20,RUF`; `ruff check . --select E,W,I,C4,UP,SIM` + `ruff format --check .` (advisory) | `python/` |
| Go | golangci-lint correctness linters (staticcheck, govet, errcheck, ineffassign, unused, gosimple) blocking; revive style subset advisory | `.golangci.yml` | `golangci-lint run ./...` | `go/` |
| SQL | SQLFluff parse/templating errors blocking; style rules advisory | `.sqlfluff` | `sqlfluff lint .` | `sql/` |
| Shell | ShellCheck errors/warnings blocking; style findings advisory | `shellcheckrc` (install as `.shellcheckrc` in the stack root) | `bash -c 'shellcheck -x -S warning $(git ls-files "*.sh")'`; style pass: `bash -c 'shellcheck -x -S style $(git ls-files "*.sh")'` (advisory) | `shell/` |
| Cross-language | manual review at 08/09 | — | — | `common-rules.md` |

Tier policy: correctness/security/type-error rules are **blocking**; style/format/suggestion rules are **advisory**. Register advisory tools with `mode: "advisory"` and explain them in `test-strategy.md`; their findings are recorded in evidence but never fail a gate. A zero-warning run is not required.

Commands are examples that a project copies into `quality-gates.json` and adjusts to its stack root and pinned binaries. The runner executes commands as a plain argument vector (no shell globbing), so list concrete files or use the `bash -c` wrapper shown above. On Windows, quote absolute executable paths (for example `"C:\\tools\\ruff.exe"`); `shlex` treats unquoted backslashes as escapes, so forward slashes are preferable when the executable resolves from `PATH`.

## How 03 Selects and 08 Installs

1. **03 Overall architecture (selection + freeze):** the technology interview is a mandatory topic — per selected language, choose tools, pin versions, list packages/plugins, decide config landing paths, severity policy, and waiver policy. Record the decisions in `docs/architecture/technology-decisions.md` (`## Static Analysis Toolchain`) and `docs/architecture/test-strategy.md` (`## Static Analysis and Quality Gates`), then write `docs/architecture/quality-gates.json` with one stack per language and the copied commands/configs. Run `python scripts/check-quality-gates.py --strict`.
2. **08 Implementation (materialize):** copy the selected pack files into the stack root at the approved paths, edit the PENDING values from the selection, and record the copy in the Change. Installing packages/binaries is an **explicitly authorized task** recorded in `tasks.md`; nothing is auto-installed. Then run `python scripts/check-quality-gates.py --strict --require-materialized`, `python scripts/run-quality-gates.py <change-id> --output openspec/changes/<change-id>/design/evidence/static-analysis.json`, and `python scripts/check-static-analysis.py --change <change-id> --strict`.

## Severity and Waiver Policy

- Blocking policy: only `error`-severity correctness/security/type findings block (`policy.blocking_severities: ["error"]`). Warnings, style, format, and suggestion findings are advisory; a zero-warning run is not required and never fails a gate.
- An `advisory` tool's findings are recorded in evidence and never affect the verdict; an advisory tool is allowed only when the project records it as non-blocking in `test-strategy.md`. Advisory results never satisfy acceptance.
- Waivers are Change-scoped (`design/static-waivers.json`), require a real approver, expire with the Change, and default to at most 90 days. They are summarized in `code-review.md` `## Static analysis`. Inline suppression without a matching waiver is a blocking 09 finding.

## Offline Rule

- `policy.allow_network_install` is `false` by default. Use `npx --no-install` or installed local binaries; the runner rejects known auto-fetch forms (`npx` without `--no-install`, `pnpm dlx`, `uvx`, `pipx run`, `go run`, `pip install`, `npm`/`pnpm`/`yarn` installs, `go get`, `cargo install`, `docker pull`, fetching `mvn` goals, similar) as BLOCKED unless the frozen policy explicitly allows network installs with an approval record. The screen reads the literal command text only: wrapper forms such as `bash -c 'npx ...'` or fetching scripts are not detected and must be reviewed manually.
- Missing tools are BLOCKED with the probe output — never silently skipped and never auto-installed.
