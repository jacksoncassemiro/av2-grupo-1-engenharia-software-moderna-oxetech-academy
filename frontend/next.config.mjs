/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Tree shaking recomendado pela doc oficial do Mantine para o App Router.
  experimental: {
    optimizePackageImports: [
      '@mantine/core',
      '@mantine/hooks',
      '@mantine/dates',
      '@mantine/form',
    ],
  },
  // Proxy para o backend: o browser fala com /api e o Next repassa para o FastAPI.
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.BACKEND_INTERNAL_URL ?? 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
