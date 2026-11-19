# Shell Pack

## Target Stack and Version

- ShellCheck 0.10.x or newer; target shells are `sh`/`bash` (each script keeps its shebang). Pin the exact version chosen at 03 in `docs/architecture/technology-decisions.md` and `quality-gates.json`.

## Config Files

| File | Landing path (stack-relative) | Purpose |
|---|---|---|
| `shellcheckrc` | `.shellcheckrc` | Enables all checks, script sourcing, and style severity |

## Blocking Command (offline)

```bash
bash -c 'shellcheck -x -S warning $(git ls-files "*.sh")'
bash -c 'shellcheck -x -S style $(git ls-files "*.sh")'   # advisory style pass
```

Register the `-S warning` command in `quality-gates.json` as a blocking tool with `configs: [".shellcheckrc"]`; register the `-S style` pass as advisory so style findings are recorded but never fail a gate (zero-warning is not required). The `bash -c` wrapper expands `git ls-files "*.sh"` inside the shell because the runner passes a literal argument vector (no glob expansion). A project that keeps a fixed script list can instead write `shellcheck -x -S warning <file> <file> ...` directly. Both forms use the locally installed binary and never fetch anything. If the repository has no shell scripts, record `N/A + reason` in `test-strategy.md` instead of a stack.

## Packages to Install (task-authorized)

| Package | Target | Required when | Purpose |
|---|---|---|---|
| `shellcheck` binary | 0.10.x+ | always (when a shell stack exists) | Blocking linter |
| `git` | project baseline | always | File discovery in the wrapper command |

Install the pinned ShellCheck binary as an **explicitly authorized task** recorded in `tasks.md`; the gate runs offline afterward. The quality-gates runner never installs anything.

## Rule Choices That Differ From Tool Defaults

- `enable=all` turns on ShellCheck's optional checks (the default enables a subset).
- `external-sources=true` plus `-x` follows sourced files, and `source-path=SCRIPTDIR` keeps relative sources resolvable when the runner's working directory is the stack root.
- `-S warning` on the blocking command reports errors and warnings; style findings run through the advisory `-S style` pass. Severity is a CLI-only option — ShellCheck does not accept `severity=` in `.shellcheckrc`; advisory findings never fail a gate.
- No `disable=` entries ship in the file. An inline `# shellcheck disable=SCxxxx` must have a matching Change-scoped waiver; unrecorded markers are blocking 09 findings.
- Scripts are discovered through `git ls-files`, so untracked or generated scripts are not silently linted; commit them or add them explicitly.
