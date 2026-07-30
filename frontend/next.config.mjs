/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Tree shaking recomendado pela doc do Mantine para o App Router.
  // Continua sob `experimental` no Next 16 (conferido na doc da v16.2).
  experimental: {
    optimizePackageImports: [
      '@mantine/core',
      '@mantine/hooks',
      '@mantine/dates',
      '@mantine/form',
    ],
  },

  // Proxy para o backend: o browser fala com /api e o Next repassa para o FastAPI.
  //
  // ATENCAO: este rewrite captura TODO /api/*. Se algum dia a equipe criar um
  // Route Handler em `src/app/api/...`, ele sera sombreado por este proxy.
  // Nesse caso, mude o prefixo do backend (ex.: /backend/:path*) em vez de
  // remover o rewrite.
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.BACKEND_INTERNAL_URL ?? 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
};

// Notas de compatibilidade com Next 16 (nada a fazer, so registrado):
//   - Turbopack e o bundler PADRAO em `next dev` e `next build` -> nao passar --turbopack
//   - Node.js minimo passou para 20.9 -> usamos Node 22 no Docker e no CI
//   - `next dev` grava em .next/dev (coberto pelo `.next/` do .gitignore)
//   - `serverRuntimeConfig`/`publicRuntimeConfig` foram REMOVIDOS -> usar NEXT_PUBLIC_*
//   - a opcao `eslint` do config foi REMOVIDA junto com `next lint`
//   - `middleware.ts` virou `proxy.ts` (nao usamos; guardas ficam no layout do route group)

export default nextConfig;
