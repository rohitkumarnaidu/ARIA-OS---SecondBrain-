import { defaultCache } from '@serwist/next/worker'
import type { PrecacheEntry, SerwistGlobalConfig } from 'serwist'
import { Serwist, ExpirationPlugin, StaleWhileRevalidate, NetworkOnly, NetworkFirst, CacheFirst } from 'serwist'

declare global {
  interface WorkerGlobalScope extends SerwistGlobalConfig {
    __SW_MANIFEST: (PrecacheEntry | string)[] | undefined
  }
}

declare const self: WorkerGlobalScope

const serwist = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  precacheOptions: {
    navigateFallback: '/offline',
  },
  skipWaiting: true,
  clientsClaim: true,
  navigationPreload: true,
  runtimeCaching: [
    ...defaultCache,
    {
      matcher: /^https:\/\/[a-z0-9-]+\.supabase\.co\/rest\/v1\//,
      handler: new StaleWhileRevalidate({
        cacheName: 'supabase-api-cache',
        plugins: [new ExpirationPlugin({ maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 7 })],
      }),
    },
    {
      matcher: /^https:\/\/[a-z0-9-]+\.supabase\.co\/auth\/v1\//,
      handler: new NetworkOnly(),
    },
    {
      matcher: /\/api\/v1\//,
      handler: new NetworkFirst({
        cacheName: 'app-api-cache',
        plugins: [new ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 60 * 60 })],
      }),
    },
    {
      matcher: /\.(?:png|jpg|jpeg|gif|svg|ico|webp|avif)$/,
      handler: new CacheFirst({
        cacheName: 'image-cache',
        plugins: [new ExpirationPlugin({ maxEntries: 200, maxAgeSeconds: 60 * 60 * 24 * 30 })],
      }),
    },
  ],
})

serwist.addEventListeners()
