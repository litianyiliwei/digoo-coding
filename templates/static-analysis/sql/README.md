# SQL Pack

## Target Stack and Version

- SQLFluff 3.x. Pin the exact version chosen at 03 in `docs/architecture/technology-decisions.md` and `quality-gates.json`.
- The dialect is **PENDING** in the shipped `.sqlfluff`: stage 03 selects it from the project's database (postgres, mysql, bigquery, tsql, snowflake, ...). SQLFluff has no default dialect, so the gate cannot run until `dialect` is set and the stack is materialized.

## Config Files

| File | Landing path (stack-relative) | Purpose |
|---|---|---|
| `.sqlfluff` | `.sqlfluff` | Dialect, line length, and rule configuration |

## Blocking Command (offline)

```bash
sqlfluff lint .
```

Register it in `quality-gates.json` as a blocking tool with `configs: [".sqlfluff"]`. Parse/templating errors are blocking; style (layout) rules are advisory — configure `.sqlfluff` so style rules report warnings, or run the style rule set as a separate advisory tool; advisory findings are recorded but never fail a gate. `sqlfluff lint` recurses through the stack root and reads `.sqlfluff`; it uses the locally installed Python package and never fetches anything.

## Packages to Install (task-authorized)

| Package | Target | Required when | Purpose |
|---|---|---|---|
| `sqlfluff` | 3.x | always | Blocking SQL linter |
| `sqlfluff-templater-dbt` + `dbt-*` adapter | matching dbt version | only when SQL lives in a dbt project | Jinja/dbt templating (otherwise keep `templater = raw`) |

Install as an **explicitly authorized task** recorded in `tasks.md` (`pip install sqlfluff==<pinned>`); after installation the gate runs offline. The quality-gates runner never installs packages.

## Rule Choices That Differ From Tool Defaults

- `max_line_length` 100 (SQLFluff defaults to 80).
- Keywords/functions/literals uppercase; identifiers/types lowercase (`extended_capitalisation_policy = lower`, consistent for quoted and unquoted identifiers).
- Explicit table and column aliasing (`aliasing = explicit`) instead of permitting implicit aliases.
- Trailing commas in multiline select lists.
- Statements must end with a semicolon (`require_final_semicolon = True`, `multiline_newline = False`).
- `templater = raw` by default: no Jinja/dbt assumptions until the project selects the dbt path. Inline `-- noqa` markers must map to a Change-scoped waiver.
