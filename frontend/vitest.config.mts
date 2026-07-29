import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import { defineConfig } from 'vitest/config';

// Setup oficial do Next.js para Vitest + arquivo de mocks exigido pelo Mantine.
// Nota (ADR-007): async Server Components nao sao suportados pelo Vitest; por isso
// as telas testadas sao Client Components.
export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.mjs',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/**'],
    },
  },
});
