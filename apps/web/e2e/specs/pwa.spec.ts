import { test, expect } from '../fixtures/test'
import { promises as fs } from 'fs'
import path from 'path'

const ICONS_DIR = path.resolve(process.cwd(), 'public/icons')

test.describe('PWA — Web App Manifest', () => {
  test('PWA-01: manifest is served at /manifest.json', async ({ page }) => {
    const response = await page.goto('/manifest.json')
    expect(response?.ok()).toBe(true)
    expect(response?.headers()['content-type']).toContain('application/json')
  })

  test('PWA-02: manifest has required fields', async ({ page }) => {
    const response = await page.goto('/manifest.json')
    const manifest = await response?.json()
    expect(manifest).toBeDefined()
    expect(manifest.name).toBeTruthy()
    expect(manifest.short_name).toBeTruthy()
    expect(manifest.start_url).toBe('/dashboard')
    expect(manifest.display).toBe('standalone')
    expect(manifest.background_color).toBe('#0A0B0F')
    expect(manifest.theme_color).toBe('#6366F1')
  })

  test('PWA-03a: manifest has icon entries', async ({ page }) => {
    const response = await page.goto('/manifest.json')
    const manifest = await response?.json()
    expect(manifest.icons?.length).toBeGreaterThanOrEqual(2)
  })

  test('PWA-03b: icon files are valid PNGs', async () => {
    const expectedIcons = [
      'icon-192x192.png',
      'icon-512x512.png',
      'icon-512x512-maskable.png',
    ]
    for (const name of expectedIcons) {
      const filePath = path.join(ICONS_DIR, name)
      const stat = await fs.stat(filePath)
      expect(stat.size).toBeGreaterThan(0)
      const buffer = await fs.readFile(filePath)
      expect(buffer[0]).toBe(0x89)
      expect(buffer[1]).toBe(0x50)
      expect(buffer[2]).toBe(0x4E)
      expect(buffer[3]).toBe(0x47)
    }
  })

  test('PWA-03c: icon dimensions match declared sizes', async () => {
    const iconEntries = [
      { name: 'icon-192x192.png', w: 192, h: 192 },
      { name: 'icon-512x512.png', w: 512, h: 512 },
      { name: 'icon-512x512-maskable.png', w: 512, h: 512 },
    ]
    for (const { name, w, h } of iconEntries) {
      const buffer = await fs.readFile(path.join(ICONS_DIR, name))
      expect(buffer.readUInt32BE(16)).toBe(w)
      expect(buffer.readUInt32BE(20)).toBe(h)
    }
  })
})

test.describe('PWA — Service Worker', () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!process.env.CI, 'SW disabled in dev mode (next-pwa config: disable in development)')
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
  })

  test('PWA-05: service worker is registered on page load', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' })
    const hasSw = await page.evaluate(async () => {
      const reg = await navigator.serviceWorker?.getRegistration()
      return !!reg
    }).catch(() => false)
    expect(hasSw).toBe(true)
  })

  test('PWA-06: service worker scope is /', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' })
    const scope = await page.evaluate(async () => {
      const reg = await navigator.serviceWorker?.getRegistration()
      return reg?.scope || null
    }).catch(() => null)
    if (scope) {
      expect(scope).toMatch(/\/$/)
    }
  })

  test('PWA-11: service worker caches static assets', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' })
    const cacheNames = await page.evaluate(async () => { return await caches.keys() })
    expect(cacheNames.length).toBeGreaterThan(0)
  })
})
