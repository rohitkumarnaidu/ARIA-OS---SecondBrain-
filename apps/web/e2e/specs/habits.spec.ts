import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Habits', { tag: '@practical' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.HABITS, { waitUntil: 'networkidle' })
  })

  test('HABIT-01: Habit list loads with loading skeleton', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.HABITS, { waitUntil: 'commit' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="spinner"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('HABIT-02: Empty state renders when no habits exist', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const emptyState = page.locator('[class*="empty"], p:has-text("No habits"), p:has-text("no habits"), [class*="empty-state"], text=Create your first habit').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('HABIT-03: Create habit modal opens', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await expect(createButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await createButton.click()
    const modal = page.locator('[class*="modal"], [class*="dialog"], [role="dialog"]').first()
    await expect(modal).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('HABIT-04: Create habit form validates required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first()
    await expect(submitButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await submitButton.click()
    const errorMsg = page.locator('[class*="error"], [role="alert"], [class*="validation"]').first()
    await expect(errorMsg).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('HABIT-05: Habit name input renders and accepts text', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    await page.waitForTimeout(500)
    const nameInput = page.locator('input[name="name"], input[name="title"], input[placeholder*="habit" i], input[placeholder*="name" i]').first()
    await expect(nameInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await nameInput.fill('Morning Meditation')
    const value = await nameInput.inputValue()
    expect(value).toBe('Morning Meditation')
  })

  test('HABIT-06: Habit frequency selector renders', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    await page.waitForTimeout(500)
    const frequencySelect = page.locator('select[name="frequency"], select[name="period"], [class*="frequency"] select, [class*="period"] select').first()
    await expect(frequencySelect).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('HABIT-07: Habit log toggle renders for existing habits', async ({ page }) => {
    await page.route('**/api/v1/habits/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', name: 'Read Daily', frequency: 'daily', streak: 5, completed_today: false },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.HABITS, { waitUntil: 'networkidle' })
    const toggle = page.locator('[class*="toggle"], [class*="checkbox"], [class*="switch"], [role="switch"], button:has-text("Log"), button:has-text("Complete")').first()
    await expect(toggle).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('HABIT-08: Habit list renders habit cards with streak info', async ({ page }) => {
    await page.route('**/api/v1/habits/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', name: 'Read Daily', frequency: 'daily', streak: 5, completed_today: false },
          { id: '2', name: 'Exercise', frequency: 'daily', streak: 12, completed_today: true },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.HABITS, { waitUntil: 'networkidle' })
    const habitCards = page.locator('[class*="habit"], [class*="card"]')
    const count = await habitCards.count()
    expect(count).toBeGreaterThanOrEqual(1)
    const streakText = page.locator('text=streak, [class*="streak"]').first()
    await expect(streakText).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('HABIT-09: Error state renders when API fails', async ({ page }) => {
    await page.route('**/api/v1/habits/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.HABITS, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const errorState = page.locator('[class*="error"], [role="alert"], button:has-text("Retry"), button:has-text("Try Again")').first()
    await expect(errorState).toBeVisible({ timeout: TEST_TIMEOUTS.NAVIGATION })
  })

  test('HABIT-10: Delete habit shows confirmation', async ({ page }) => {
    await page.route('**/api/v1/habits/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', name: 'Read Daily', frequency: 'daily', streak: 5, completed_today: false },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.HABITS, { waitUntil: 'networkidle' })
    const deleteButton = page.locator('button[class*="delete"], button[class*="remove"], button[aria-label*="delete" i]').first()
    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click()
      const confirmDialog = page.locator('[class*="confirm"], [class*="alert"], [role="alertdialog"], [role="dialog"]').first()
      await expect(confirmDialog).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    }
  })
})
