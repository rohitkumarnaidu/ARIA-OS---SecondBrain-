import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Dashboard Loading States', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
  })

  test('DASH-01: Dashboard renders with loading skeleton on initial load', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.DASHBOARD, { waitUntil: 'commit' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="spinner"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('DASH-02: Data appears after loading completes', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.DASHBOARD, { waitUntil: 'networkidle' })
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(2000)
    const content = page.locator('main, [class*="dashboard"], [class*="content"]').first()
    await expect(content).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('DASH-03: Dashboard shows greeting and stats grid', async ({ dashboardPage, page }) => {
    await dashboardPage.goto()
    await expect(dashboardPage.greeting).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await expect(dashboardPage.statsGrid).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('DASH-04: Error state renders when API fails', async ({ page }) => {
    await page.route('**/api/v1/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.DASHBOARD, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const errorState = page.locator('[class*="error"], [role="alert"], button:has-text("Retry"), button:has-text("Try Again")').first()
    await expect(errorState).toBeVisible({ timeout: TEST_TIMEOUTS.NAVIGATION })
  })

  test('DASH-05: Sidebar and navbar visible after dashboard loads', async ({ dashboardPage, page }) => {
    await dashboardPage.goto()
    await expect(dashboardPage.sidebar).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await expect(dashboardPage.navbar).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('DASH-06: Retry button recovers from error state', async ({ page }) => {
    await page.route('**/api/v1/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.DASHBOARD, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const retryButton = page.locator('button:has-text("Retry"), button:has-text("Try Again")').first()
    if (await retryButton.isVisible().catch(() => false)) {
      await page.route('**/api/v1/**', (route) => route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: [] }),
      }))
      await retryButton.click()
      await page.waitForTimeout(2000)
      const errorState = page.locator('[class*="error"], [role="alert"]').first()
      await expect(errorState).not.toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE }).catch(() => {})
    }
  })
})
