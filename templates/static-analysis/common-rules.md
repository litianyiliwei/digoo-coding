# Common Cross-Language Rules

These five rules cover issues that language linters do not reliably catch. They are reviewed manually at 08 (code review) and 09 (independent verification); each finding must be fixed or covered by a Change-scoped waiver recorded in `design/static-waivers.json` and summarized in `code-review.md` `## Static analysis`.

1. **No TODO/FIXME in production paths.**
   Production code must not ship unresolved `TODO`, `FIXME`, `XXX`, or `HACK` markers. Work that must be deferred becomes a tracked Change/task; comments stay in `test/`, fixtures, or documentation only.

2. **No hardcoded secrets or credentials.**
   Passwords, API keys, tokens, private keys, connection strings with credentials, and certificates must not be committed in code or config. Use environment variables or the project's secret store; a detected secret is a security finding (not waivable for a public repository).

3. **No debug prints in production paths.**
   Remove ad-hoc debugging output from production code: `console.log`/`console.debug`, `System.out.println`/`System.err.println`, bare `print(...)` in Python, and similar markers. Structured logging through the project's logging layer is allowed.

4. **No unrecorded suppression markers.**
   Every inline suppression must map to a Change-scoped waiver: `// eslint-disable-next-line`, `// @ts-ignore`/`@ts-expect-error`, `# noqa`, `//nolint`, `# shellcheck disable`, `<!-- suppressions -->`, and equivalent. An unrecorded marker is a blocking 09 finding even when the tool exits 0.

5. **No disabled rules without a waiver.**
   Removing or weakening a rule from the shipped pack (config `ignore`/`disable`, rule `off`, excluded paths) requires a recorded decision in `test-strategy.md` and a matching waiver. Silent rule removal is not accepted as a fix.

## Review Checklist

| Rule | Automated signal | Manual check at 08/09 | Waiver needed |
|---|---|---|---|
| TODO/FIXME in production paths | linter/regex note | yes | yes, with expiry |
| Hardcoded secrets/credentials | secret scanner if available | yes | no for public repositories |
| Debug prints in production paths | ESLint `no-console`, Ruff `T20`, Checkstyle regex, golangci-lint `forbidigo` (optional) | yes | yes, with expiry |
| Unrecorded suppression markers | tool output + `git diff` review | yes | the marker's matching waiver |
| Disabled rules without a waiver | config diff review | yes | the matching waiver |
