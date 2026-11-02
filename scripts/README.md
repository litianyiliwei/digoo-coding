# Scripts

Most scripts resolve the project root from their own location; file arguments to `validate-openapi.sh` may be absolute or relative to the current directory/project root. After copying, place scripts under the project root `scripts/` folder.

| Script | Purpose | Success means | Does not mean |
|---|---|---|---|
| `check-output-template-matrix.py` | Validates that registered L1/L2 template paths exist | Template registry references real files | Template content is complete/correct |
| `check-api-io-mapping.py <openapi> <mapping.csv> <catalog.csv> [--strict]` | Every OpenAPI operationId maps to one or more concrete IO IDs; catalog contracts are complete in strict mode; intentional no-API change must declare `x-api-scope: none` | Design has correct business behavior or safe transaction semantics |
| `test-api-io-mapping.sh` | Temporary positive/negative fixtures verify API→IO checker behavior, including explicit no-API scope | Basic checker regressions are caught | Real project API/IO design is correct |
| `check-acceptance.py <id>` | Acceptance result, evidence, reviewer and AC rows | Evidence sheet has no pending fields and includes accepted AC rows | Business acceptance is actually justified |
| `check-package.py` | Skill/Prompt pairing, frontmatter and syntax checks | Package structure is consistent | Content/logic is correct |
| `check-requirements.py [--strict]` | Declared workflow/use-case/story/AC/business-rule IDs and duplicates | Required IDs exist and declarations are unique | Semantic completeness is proven |
| `check-roadmap.py [--strict]` | Roadmap table IDs and duplicates | Proposal plan structurally consistent | Priority/business value are correct |
| `check-required-files.sh [--strict]` | Baseline file presence and placeholder warnings | Required baseline files exist; strict rejects placeholders | Requirements/architecture are sound |
| `new-change-assets.sh <id>` | Add supplemental design/evidence templates to an existing Change without overwriting files | Custom asset skeletons exist | OpenSpec artifacts are created/valid |
| `check-design-assets.sh <id> [--strict] [--lint-api]` | Required API/frontend/backend/test/API→IO/catalog/traceability files; validates every operationId mapping | Detail-design assets exist and API→IO references are consistent | Design quality and runtime behavior are correct |
| `check-change.sh <id> [--no-openspec]` | Change structure/tasks/specs and OpenSpec validation | Change structure validates | AC/business completeness is proven |
| `check-inventory.py [--change <id>] [--strict]` or `--change <id> --no-ui --reason "..." --strict` | Page/event CSV columns, IDs and page references; with `--change` use that Change's design inventory | Inventory links are structurally sound | UI/interaction behavior is correct |
| `check-traceability.py [--file <csv>] [--strict]` | Traceability CSV columns, duplicate links and states | Trace edges are structurally sound | All semantic coverage exists |
| `validate-openapi.sh <file>` | Redocly OpenAPI lint | Linter accepts the contract | Business semantics are correct |
| `test-all.sh <dir>...` | Run detected test entrypoints | All requested detected test commands passed | Lint/build/E2E ran unless included in command |
| `verify-before-completion.sh <id> ...` | Run strict OpenSpec, diff and optional API/tests checks | Configured checks ran successfully | Human acceptance/release approval complete |

The scripts are intentionally fail-closed when they cannot run a required check. Adapt for Windows PowerShell if the repository does not use Bash/WSL/macOS/Linux.
