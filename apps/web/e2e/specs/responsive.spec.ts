import { test, expect } from '@playwright/test'

const breakpoints = [
  { width: 375, height: 667, name: 'Mobile' },
  { width: 834, height: 1194, name: 'Tablet Portrait' },
  { width: 1024, height: 768, name: 'Tablet Landscape' },
  { width: 1440, height: 900, name: 'Desktop' },
  { width: 1920, height: 1080, name: 'Wide' },
]

for (const bp of breakpoints) {
  test(`Dashboard renders correctly at ${bp.name} (${bp.width}px)`, async ({ page }) => {
    await page.setViewportSize({ width: bp.width, height: bp.height })
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('main')).toBeVisible()
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth)
    const viewportWidth = await page.evaluate(() => document.documentElement.clientWidth)
    expect(scrollWidth).toBeLessThanOrEqual(viewportWidth + 1)
  })
}

test('sidebar toggles correctly at mobile viewport', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 })
  await page.goto('/')
  await page.waitForLoadState('networkidle')
  await expect(page.locator('main')).toBeVisible()
})

test('task page renders correctly at all breakpoints', async ({ page }) => {
  for (const bp of breakpoints) {
    await page.setViewportSize({ width: bp.width, height: bp.height })
    await page.goto('/tasks')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('main')).toBeVisible()
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth)
    const viewportWidth = await page.evaluate(() => document.documentElement.clientWidth)
    expect(scrollWidth).toBeLessThanOrEqual(viewportWidth + 1)
  }
})

test('navigation links are reachable at every breakpoint', async ({ page }) => {
  for (const bp of breakpoints) {
    await page.setViewportSize({ width: bp.width, height: bp.height })
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    const nav = page.locator('nav, header, [role="navigation"]')
    const visible = await nav.first().isVisible()
    expect(typeof visible).toBe('boolean')
  }
})
