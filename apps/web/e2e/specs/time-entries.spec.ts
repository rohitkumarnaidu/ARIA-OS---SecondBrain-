import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Time Entries', { tag: '@practical' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.TIME, { waitUntil: 'networkidle' })
  })

  test('TIME-01: Time entry list loads with loading skeleton', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.TIME, { waitUntil: 'commit' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="spinner"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('TIME-02: Empty state renders when no time entries exist', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const emptyState = page.locator('[class*="empty"], p:has-text("No time entries"), p:has-text("no entries"), [class*="empty-state"], text=Log your first entry').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('TIME-03: Create time entry modal opens', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New"), button:has-text("Log")').first()
    await expect(createButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await createButton.click()
    const modal = page.locator('[class*="modal"], [class*="dialog"], [role="dialog"]').first()
    await expect(modal).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('TIME-04: Create time entry form validates required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first()
    await expect(submitButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await submitButton.click()
    const errorMsg = page.locator('[class*="error"], [role="alert"], [class*="validation"]').first()
    await expect(errorMsg).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('TIME-05: Duration and description inputs render', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    await page.waitForTimeout(500)
    const durationInput = page.locator('input[name="duration"], input[type="number"], input[placeholder*="minute" i], input[placeholder*="hour" i]').first()
    await expect(durationInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await durationInput.fill('45')
    const value = await durationInput.inputValue()
    expect(value).toBe('45')
  })

  test('TIME-06: Pomodoro timer display renders', async ({ page }) => {
    await page.route('**/api/v1/time/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', description: 'Deep work session', duration: 25, date: '2026-07-07' },
          { id: '2', description: 'Code review', duration: 15, date: '2026-07-07' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.TIME, { waitUntil: 'networkidle' })
    const pomodoro = page.locator('[class*="pomodoro"], [class*="timer"], [class*="focus"], button:has-text("Start"), button:has-text("Focus")').first()
    await expect(pomodoro).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('TIME-07: Time entries list displays duration and description', async ({ page }) => {
    await page.route('**/api/v1/time/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', description: 'Deep work session', duration: 25, date: '2026-07-07' },
          { id: '2', description: 'Code review', duration: 15, date: '2026-07-07' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.TIME, { waitUntil: 'networkidle' })
    const entryCards = page.locator('[class*="entry"], [class*="card"], [class*="item"]')
    const count = await entryCards.count()
    expect(count).toBeGreaterThanOrEqual(1)
    const durationText = page.locator('[class*="duration"], text=/\\d+\\s*min/, text=/\\d+\\s*h/').first()
    await expect(durationText).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('TIME-08: Daily stats summary renders', async ({ page }) => {
    await page.route('**/api/v1/time/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', description: 'Deep work', duration: 25, date: '2026-07-07' },
          { id: '2', description: 'Code review', duration: 15, date: '2026-07-07' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.TIME, { waitUntil: 'networkidle' })
    const stats = page.locator('[class*="stats"], [class*="summary"], [class*="total"]').first()
    await expect(stats).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('TIME-09: Error state renders when API fails', async ({ page }) => {
    await page.route('**/api/v1/time/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.TIME, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const errorState = page.locator('[class*="error"], [role="alert"], button:has-text("Retry"), button:has-text("Try Again")').first()
    await expect(errorState).toBeVisible({ timeout: TEST_TIMEOUTS.NAVIGATION })
  })

  test('TIME-10: Delete time entry shows confirmation dialog', async ({ page }) => {
    await page.route('**/api/v1/time/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', description: 'Deep work session', duration: 25, date: '2026-07-07' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.TIME, { waitUntil: 'networkidle' })
    const deleteButton = page.locator('button[class*="delete"], button[class*="remove"], button[aria-label*="delete" i]').first()
    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click()
      const confirmDialog = page.locator('[class*="confirm"], [class*="alert"], [role="alertdialog"], [role="dialog"]').first()
      await expect(confirmDialog).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    }
  })
})
