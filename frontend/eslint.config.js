import js from '@eslint/js';
import globals from 'globals';

export default [
  {
    ...js.configs.recommended,
    files: ['src/**/*.{js,jsx}'],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
  },
];
