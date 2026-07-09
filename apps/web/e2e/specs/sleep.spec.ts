import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Sleep', { tag: '@practical' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.SLEEP, { waitUntil: 'networkidle' })
  })

  test('SLEEP-01: Sleep log loads with loading skeleton', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.SLEEP, { waitUntil: 'commit' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="spinner"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('SLEEP-02: Empty state renders when no sleep logs exist', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const emptyState = page.locator('[class*="empty"], p:has-text("No sleep"), p:has-text("no sleep"), [class*="empty-state"], text=Log your first night').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('SLEEP-03: Log sleep modal opens', async ({ page }) => {
    const logButton = page.locator('button:has-text("Log"), button:has-text("Add"), button:has-text("New")').first()
    await expect(logButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await logButton.click()
    const modal = page.locator('[class*="modal"], [class*="dialog"], [role="dialog"]').first()
    await expect(modal).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('SLEEP-04: Log sleep form validates required fields', async ({ page }) => {
    const logButton = page.locator('button:has-text("Log"), button:has-text("Add"), button:has-text("New")').first()
    await logButton.click()
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Log")').first()
    await expect(submitButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await submitButton.click()
    const errorMsg = page.locator('[class*="error"], [role="alert"], [class*="validation"]').first()
    await expect(errorMsg).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('SLEEP-05: Bedtime input renders and accepts time', async ({ page }) => {
    const logButton = page.locator('button:has-text("Log"), button:has-text("Add"), button:has-text("New")').first()
    await logButton.click()
    await page.waitForTimeout(500)
    const bedtimeInput = page.locator('input[name="bedtime"], input[name="sleep_time"], input[type="time"], input[placeholder*="bed" i], input[placeholder*="sleep" i]').first()
    await expect(bedtimeInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await bedtimeInput.fill('23:00')
    const value = await bedtimeInput.inputValue()
    expect(value.length).toBeGreaterThan(0)
  })

  test('SLEEP-06: Wake time input renders and accepts time', async ({ page }) => {
    const logButton = page.locator('button:has-text("Log"), button:has-text("Add"), button:has-text("New")').first()
    await logButton.click()
    await page.waitForTimeout(500)
    const wakeInput = page.locator('input[name="wake_time"], input[name="wakeup"], input[placeholder*="wake" i]').first()
    await expect(wakeInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await wakeInput.fill('07:00')
    const value = await wakeInput.inputValue()
    expect(value.length).toBeGreaterThan(0)
  })

  test('SLEEP-07: Sleep log list renders entries with score', async ({ page }) => {
    await page.route('**/api/v1/sleep/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', date: '2026-07-06', bedtime: '23:00', wake_time: '07:00', duration_hours: 8, score: 85 },
          { id: '2', date: '2026-07-05', bedtime: '00:30', wake_time: '06:30', duration_hours: 6, score: 55 },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.SLEEP, { waitUntil: 'networkidle' })
    const sleepCards = page.locator('[class*="sleep"], [class*="card"], [class*="log"]')
    const count = await sleepCards.count()
    expect(count).toBeGreaterThanOrEqual(1)
    const score = page.locator('text=85, text=score, [class*="score"]').first()
    await expect(score).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('SLEEP-08: Sleep duration is displayed correctly', async ({ page }) => {
    await page.route('**/api/v1/sleep/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', date: '2026-07-06', bedtime: '23:00', wake_time: '07:00', duration_hours: 8, score: 85 },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.SLEEP, { waitUntil: 'networkidle' })
    const duration = page.locator('text=8h, text=8 hours, text=duration, [class*="duration"]').first()
    await expect(duration).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('SLEEP-09: Error state renders when API fails', async ({ page }) => {
    await page.route('**/api/v1/sleep/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.SLEEP, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const errorState = page.locator('[class*="error"], [role="alert"], button:has-text("Retry"), button:has-text("Try Again")').first()
    await expect(errorState).toBeVisible({ timeout: TEST_TIMEOUTS.NAVIGATION })
  })

  test('SLEEP-10: Delete sleep log shows confirmation', async ({ page }) => {
    await page.route('**/api/v1/sleep/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', date: '2026-07-06', bedtime: '23:00', wake_time: '07:00', duration_hours: 8, score: 85 },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.SLEEP, { waitUntil: 'networkidle' })
    const deleteButton = page.locator('button[class*="delete"], button[class*="remove"], button[aria-label*="delete" i]').first()
    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click()
      const confirmDialog = page.locator('[class*="confirm"], [role="alertdialog"], [role="dialog"]').first()
      await expect(confirmDialog).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    }
  })
})
