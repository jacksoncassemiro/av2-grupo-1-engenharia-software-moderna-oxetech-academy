// Flat config oficial do Next.js 16.
// `next lint` foi REMOVIDO na v16 — o lint agora roda pela CLI do ESLint (`eslint .`).
// Fonte: https://nextjs.org/docs/app/api-reference/config/eslint
import { defineConfig, globalIgnores } from 'eslint/config';
import nextVitals from 'eslint-config-next/core-web-vitals';
import nextTs from 'eslint-config-next/typescript';

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  globalIgnores([
    // Ignores padrão do eslint-config-next, que precisam ser repetidos ao sobrescrever:
    '.next/**',
    'out/**',
    'build/**',
    'next-env.d.ts',
    // Do projeto:
    'node_modules/**',
    'coverage/**',
  ]),
]);
