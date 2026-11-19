# Python Pack

## Target Stack and Version

- Python 3.12 or newer; Ruff 0.9.x or newer (Ruff is a 0.x tool — pin the exact version chosen at 03 in `docs/architecture/technology-decisions.md` and `quality-gates.json`).
- mypy is optional/advisory (see below).

## Config Files

| File | Landing path (stack-relative) | Purpose |
|---|---|---|
| `ruff.toml` | `ruff.toml` | Lint and format-check rules (`[lint] select`) |

## Blocking Commands (offline)

```bash
ruff check . --select F,S,B,ASYNC,DTZ,PTH,RET,RSE,T20,RUF
ruff check . --select E,W,I,C4,UP,SIM   # advisory style pass
ruff format --check .                   # advisory
```

Copy the correctness invocation into `quality-gates.json` as the blocking tool (`ruff-lint`) with `configs: ["ruff.toml"]`; register the style-rule invocation and `ruff format --check .` as advisory tools. Only correctness/security errors block; style/format findings are recorded but never fail a gate (zero-warning is not required). They use the locally installed `ruff` binary and never fetch anything.

## Packages to Install (task-authorized)

| Package | Target | Required when | Purpose |
|---|---|---|---|
| `ruff` | 0.9.x+ | always | Blocking linter and formatter check |
| `mypy` | 1.x | optional | Advisory type checking |

Install as an **explicitly authorized task** recorded in `tasks.md` (for example `pip install ruff==<pinned>` or `uv tool install ruff==<pinned>`); after installation the gate runs offline. The quality-gates runner never installs packages.

## Rule Choices That Differ From Tool Defaults

- Ruff's default selection is `E4`, `E7`, `E9`, `F`; this pack adds `W`, `I`, `B`, `C4`, `UP`, `SIM`, `S`, `ASYNC`, `DTZ`, `PTH`, `RET`, `RSE`, `T20`, and `RUF`.
- `line-length` 100 (Ruff defaults to 88).
- `T20` bans `print()`/`pprint` in production paths (common rule 3); tests may use prints via per-file ignores.
- `S101` (`assert`) and `T201` (`print`) are allowed in tests only; `__init__.py` may re-export (`F401` ignored there).
- Ambiguous-Unicode rules `RUF001`/`RUF002`/`RUF003` are ignored because full-width punctuation in Chinese comments/strings is intentional for this toolkit's projects.
- `ruff format --check` enforces double quotes, spaces, LF endings, and formatted docstring code.
- Suppressions (`# noqa`) must map to a Change-scoped waiver; the config ships no blanket ignores.

## mypy Note

mypy is optional/advisory. If adopted, pin the version, add a `mypy.ini`/`pyproject.toml` `[tool.mypy]` section (`strict = true`, `disallow_untyped_defs = true`), run it offline (`mypy .`), and register it in `quality-gates.json` with `mode: "advisory"` plus the reason in `test-strategy.md`. Advisory findings never satisfy acceptance.
