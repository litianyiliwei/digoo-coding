# TypeScript / JavaScript Pack

## Target Stack and Version

- Node.js 20 or 22 LTS; TypeScript 5.x (≥5.3 for `projectService`); ESLint 9.x flat config; typescript-eslint 8.x; Prettier 3.x.
- Vue projects: `eslint-plugin-vue` 9.x. React projects: `eslint-plugin-react` 7.x.
- Pin the exact versions chosen at 03 in `docs/architecture/technology-decisions.md` and the project lockfile.

## Config Files

| File | Landing path (stack-relative) | Purpose |
|---|---|---|
| `eslint.config.js` | `eslint.config.js` | ESLint flat config (exports an array) |
| `.prettierrc.json` | `.prettierrc.json` | Prettier formatting |
| `tsconfig.strict.json` | `tsconfig.strict.json` | Strict `tsc` type check |

Save `eslint.config.js` in the stack root. If `package.json` sets `"type": "module"`, rename it to `eslint.config.cjs` (or convert `require()` to `import`) and keep the `quality-gates.json` config path in sync. The Vue and React blocks are optional: the config loads `eslint-plugin-vue`/`eslint-plugin-react` only when installed (a missing plugin is skipped via `optionalRequire`, not a `MODULE_NOT_FOUND` failure). Delete the framework block you do not need and remove its packages below before installing dependencies.

## Blocking Commands (offline)

```bash
npx --no-install eslint .
npx --no-install tsc --noEmit -p tsconfig.strict.json
npx --no-install prettier --check .   # advisory
```

Copy these into `quality-gates.json` with `eslint` and `tsc` as blocking tools and `prettier` as an advisory tool, each with `configs` pointing at the files above. They use only locally installed packages; the runner rejects `npx` without `--no-install`. ESLint errors block; warnings and Prettier formatting findings are recorded but never fail a gate. If the project's `tsconfig.json` extends `tsconfig.strict.json`, keep `npx --no-install tsc --noEmit` and list both configs. For Vue `<script setup>` type checking, use `npx --no-install vue-tsc --noEmit` (optional package) instead of `tsc`.

## Packages to Install (task-authorized)

Install these as an **explicitly authorized task** recorded in `tasks.md`; the quality-gates runner never installs packages.

| Package | Target | Required when | Purpose |
|---|---|---|---|
| `eslint` | 9.x | always | Flat-config linter |
| `@eslint/js` | 9.x | always | `js.configs.recommended` |
| `typescript-eslint` | 8.x | always | Type-checked TypeScript rules |
| `typescript` | 5.x | always | `tsc` type check |
| `prettier` | 3.x | always | Formatting check |
| `eslint-plugin-vue` | 9.x | Vue projects | Vue flat configs |
| `vue-eslint-parser` | 9.x | Vue projects | Parser used by `eslint-plugin-vue` |
| `eslint-plugin-react` | 7.x | React projects | React rules |

Optional: `eslint-config-prettier` (disable stylistic ESLint rules), `vue-tsc` (Vue type checking).

## Rule Choices That Differ From Tool Defaults

- **ESLint:** errors block; warnings are advisory and never fail the gate (no `--max-warnings 0`). `typescript-eslint` `recommendedTypeChecked` enables type-aware rules. `@typescript-eslint/no-explicit-any`, `no-floating-promises`, and `consistent-type-imports` are errors. `no-console` and `no-debugger` are errors (common rule 3). Unused-variable reports allow `_`-prefixed names. Generated/build directories are ignored.
- **Prettier:** advisory formatter. `printWidth` 100 (Prettier default 80), `singleQuote`, `trailingComma: "all"`, `endOfLine: "lf"`; findings are recorded but never fail a gate.
- **tsc:** `strict` plus `noUncheckedIndexedAccess`, `noImplicitOverride`, `noUnusedLocals`, `noUnusedParameters`, and `noFallthroughCasesInSwitch`; `jsx: "preserve"` so `.tsx` files type-check without requiring React's JSX runtime; standalone config so the gate does not depend on the app's build config (React projects may override `jsx` to `react-jsx`/`react-jsxdev` in their app tsconfig).
