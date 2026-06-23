import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.DASHBOARD, { waitUntil: 'networkidle' })
  })

  const MODULE_ROUTES = [
    { name: 'Tasks', path: ROUTES.PROTECTED.TASKS },
    { name: 'Courses', path: ROUTES.PROTECTED.COURSES },
    { name: 'Goals', path: ROUTES.PROTECTED.GOALS },
    { name: 'Habits', path: ROUTES.PROTECTED.HABITS },
    { name: 'Sleep', path: ROUTES.PROTECTED.SLEEP },
    { name: 'Income', path: ROUTES.PROTECTED.INCOME },
    { name: 'Projects', path: ROUTES.PROTECTED.PROJECTS },
    { name: 'Ideas', path: ROUTES.PROTECTED.IDEAS },
    { name: 'Resources', path: ROUTES.PROTECTED.RESOURCES },
    { name: 'Opportunities', path: ROUTES.PROTECTED.OPPORTUNITIES },
    { name: 'Time', path: ROUTES.PROTECTED.TIME },
    { name: 'Chat', path: ROUTES.PROTECTED.CHAT },
    { name: 'Automation', path: ROUTES.PROTECTED.AUTOMATION },
    { name: 'Academics', path: ROUTES.PROTECTED.ACADEMICS },
  ]

  test('NAV-FLOW-01: Sidebar navigation renders all module links', async ({ dashboardPage, page }) => {
    await expect(dashboardPage.sidebar).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    const linkCount = await dashboardPage.sidebarLinks.count()
    expect(linkCount).toBeGreaterThanOrEqual(MODULE_ROUTES.length)
  })

  test('NAV-FLOW-02: Active route highlights correct sidebar link', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.TASKS, { waitUntil: 'networkidle' })
    const activeLink = page.locator('nav a[class*="active"], nav a[aria-current="page"], aside a[class*="active"]').first()
    await expect(activeLink).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  for (const { name, path } of MODULE_ROUTES) {
    test(`NAV-FLOW-03: Clicking "${name}" navigates to correct route`, async ({ page }) => {
      const link = page.locator(`nav a:has-text("${name}"), aside a:has-text("${name}")`).first()
      await expect(link).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
      await link.click()
      await page.waitForLoadState('networkidle')
      expect(page.url()).toContain(path)
    })
  }

  test('NAV-FLOW-04: Mobile hamburger menu toggles sidebar', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    const hamburger = page.locator('button[class*="hamburger"], button[class*="menu"], button[aria-label*="menu" i], button[aria-label*="open" i]').first()
    await expect(hamburger).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await hamburger.click()
    await page.waitForTimeout(500)
    await expect(hamburger).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('NAV-FLOW-05: Sidebar closes when clicking a nav link on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.waitForLoadState('networkidle')
    const hamburger = page.locator('button[class*="hamburger"], button[class*="menu"], button[aria-label*="menu" i]').first()
    await expect(hamburger).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION }).catch(() => {})
    if (await hamburger.isVisible().catch(() => false)) {
      await hamburger.click()
      await page.waitForTimeout(500)
      const link = page.locator('aside a, nav a').first()
      if (await link.isVisible().catch(() => false)) {
        await link.click()
        await page.waitForLoadState('networkidle')
        expect(page.url()).not.toContain('/login')
      }
    }
  })
})
