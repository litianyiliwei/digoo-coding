# Java Pack

## Target Stack and Version

- JDK 17 or newer; Checkstyle 10.x. Pin the exact Checkstyle version chosen at 03 in `docs/architecture/technology-decisions.md` and `quality-gates.json`.
- SpotBugs is optional/advisory (see below) and never a substitute for the blocking Checkstyle gate.

## Config Files

| File | Landing path (stack-relative) | Purpose |
|---|---|---|
| `checkstyle.xml` | `config/checkstyle/checkstyle.xml` | Checkstyle rules (DTD `configuration_1_3`) |

## Blocking Command (offline)

```bash
java -jar tools/checkstyle.jar -c config/checkstyle/checkstyle.xml src/main/java
```

- Download the pinned `checkstyle-<version>-all.jar` once as an **explicitly authorized task** (recorded in `tasks.md`) and keep it in the stack, e.g. `tools/checkstyle.jar`; `java -jar` then runs fully offline. A Maven/Gradle Checkstyle plugin with a warmed local dependency cache is also offline; if you use it, pin the plugin and version in `quality-gates.json`.
- Register the command in `quality-gates.json` with `configs: ["config/checkstyle/checkstyle.xml"]` (paths relative to the stack root).

## Packages to Install (task-authorized)

| Package | Target | Required when | Purpose |
|---|---|---|---|
| Checkstyle all-in-one jar | 10.x | always | Blocking linter |
| SpotBugs + `spotbugs-annotations` | 4.8+ | optional | Advisory bug-pattern analysis |
| PMD | 7.x | optional | Advisory duplicate/complexity analysis |

Install/download only as an explicitly authorized task recorded in `tasks.md`; the quality-gates runner never installs or fetches anything.

## Rule Choices That Differ From Tool Defaults

- Tier policy: correctness/security checks are blocking; style rules are advisory. Keep style modules out of the blocking Checkstyle config, or register a style-only Checkstyle command with `mode: "advisory"`; advisory findings are recorded but never fail a gate.
- `severity=error` at the Checker level, so every violation in the blocking correctness configuration fails the gate; style checks must run advisory (zero-warning is not required). The tool default is warning.
- `LineLength` max 120 (default 80), ignoring package/import/URL lines.
- Requires `MissingJavadocType`/`MissingJavadocMethod` for public API (javadoc policy) and `SummaryJavadoc`.
- Complexity thresholds: `CyclomaticComplexity` 10, `NPathComplexity` 200, `MethodLength` 60, `FileLength` 1000.
- `MagicNumber` allows only `-1, 0, 1, 2`; other literals must be named constants.
- Bans star imports, enforces import order, bans `System.out`/`System.err` prints (common rule 3), and flags `TODO`/`FIXME`/`HACK` (common rule 1).
- Suppressions are not configured here: every exception is a Change-scoped waiver in `design/static-waivers.json`.

## SpotBugs Note

SpotBugs is optional and advisory in the starter defaults. If adopted, pin it in `technology-decisions.md`, run it offline (`spotbugs -effort:max -low ...` from a local install, or a Gradle/Maven plugin with cached dependencies), and record it in `quality-gates.json` with `mode: "advisory"` plus the reason in `test-strategy.md`. Advisory findings never satisfy acceptance.
