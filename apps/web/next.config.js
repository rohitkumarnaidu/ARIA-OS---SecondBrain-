/** @type {import('next').NextConfig} */
const withBundleAnalyzer = process.env.ANALYZE === 'true'
  ? require('@next/bundle-analyzer')({ enabled: true })
  : (config) => config

const withSerwist = require('@serwist/next').default({
  swSrc: 'sw.ts',
  swDest: 'public/sw.js',
  disable: process.env.NEXT_PUBLIC_PWA_ENABLED !== 'true',
})

const nextConfig = withBundleAnalyzer(withSerwist({
  output: 'standalone',
  reactStrictMode: true,
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [375, 768, 1024, 1440, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
    minimumCacheTTL: 60 * 60 * 24 * 30,
    domains: ['localhost', 'supabase.co', 'img.youtube.com'],
  },
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    NEXT_PUBLIC_PWA_ENABLED: process.env.NEXT_PUBLIC_PWA_ENABLED,
  },
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion', 'recharts', 'd3', 'three', '@xyflow/react', '@tanstack/react-table', '@tanstack/react-virtual'],
  },
}))

module.exports = nextConfig
