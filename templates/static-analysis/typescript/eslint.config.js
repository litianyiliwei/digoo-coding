// ESLint flat config — TypeScript / JavaScript (Vue, React) starter.
// Target: Node.js 20/22 LTS, ESLint 9.x, typescript-eslint 8.x.
// Saved as `eslint.config.js`; if package.json sets "type": "module", rename
// this file to `eslint.config.cjs` (or convert require() to import) and keep
// the quality-gates.json config path in sync.
// The Vue and React blocks are optional: each plugin is loaded only when it is
// installed (a missing plugin is skipped instead of failing the config load).
// Delete the framework block you do not need and remove its package from
// packages.md before installing dependencies.
const js = require('@eslint/js');
const tseslint = require('typescript-eslint');

function optionalRequire(name) {
  try {
    return require(name);
  } catch (error) {
    if (error && error.code === 'MODULE_NOT_FOUND') {
      return null;
    }
    throw error;
  }
}

const vue = optionalRequire('eslint-plugin-vue');
const react = optionalRequire('eslint-plugin-react');

const typeCheckedFiles = ['**/*.ts', '**/*.tsx'];

module.exports = [
  {
    ignores: [
      'dist/**',
      'build/**',
      'coverage/**',
      'node_modules/**',
      '*.min.js',
    ],
  },
  js.configs.recommended,
  // typescript-eslint recommended-type-checked, restricted to TS/TSX files.
  ...tseslint.configs.recommendedTypeChecked.map((config) => ({
    ...config,
    files: typeCheckedFiles,
  })),
  {
    files: typeCheckedFiles,
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: __dirname,
      },
    },
    rules: {
      // Stricter than the typescript-eslint defaults.
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/consistent-type-imports': 'error',
      'no-console': 'error',
      'no-debugger': 'error',
    },
  },
  // Vue (optional): active only when eslint-plugin-vue is installed.
  ...(vue
    ? [
        ...vue.configs['flat/recommended'].map((config) => ({
          ...config,
          files: ['**/*.vue'],
        })),
        {
          files: ['**/*.vue'],
          rules: {
            'vue/multi-word-component-names': 'off',
          },
        },
      ]
    : []),
  // React (optional): active only when eslint-plugin-react is installed.
  ...(react
    ? [
        {
          ...react.configs.flat.recommended,
          files: ['**/*.jsx', '**/*.tsx'],
          settings: { react: { version: 'detect' } },
          rules: {
            ...react.configs.flat.recommended.rules,
            'react/react-in-jsx-scope': 'off',
          },
        },
        {
          files: ['**/*.jsx'],
          languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'module',
            parserOptions: { ecmaFeatures: { jsx: true } },
          },
        },
      ]
    : []),
];
