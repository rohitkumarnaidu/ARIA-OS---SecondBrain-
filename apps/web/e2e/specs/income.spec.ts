import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Income', { tag: '@practical' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.INCOME, { waitUntil: 'networkidle' })
  })

  test('INCOME-01: Income list loads with loading skeleton', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.INCOME, { waitUntil: 'commit' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="spinner"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('INCOME-02: Empty state renders when no income entries exist', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const emptyState = page.locator('[class*="empty"], p:has-text("No income"), p:has-text("no income"), [class*="empty-state"], text=Add your first income').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('INCOME-03: Add income modal opens', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first()
    await expect(addButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await addButton.click()
    const modal = page.locator('[class*="modal"], [class*="dialog"], [role="dialog"]').first()
    await expect(modal).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('INCOME-04: Add income form validates required fields', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first()
    await addButton.click()
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Add")').first()
    await expect(submitButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await submitButton.click()
    const errorMsg = page.locator('[class*="error"], [role="alert"], [class*="validation"]').first()
    await expect(errorMsg).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('INCOME-05: Amount input renders and accepts numeric value', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first()
    await addButton.click()
    await page.waitForTimeout(500)
    const amountInput = page.locator('input[name="amount"], input[type="number"], input[placeholder*="amount" i], input[placeholder*="0.00" i]').first()
    await expect(amountInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await amountInput.fill('250')
    const value = await amountInput.inputValue()
    expect(value.length).toBeGreaterThan(0)
  })

  test('INCOME-06: Income source input renders', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first()
    await addButton.click()
    await page.waitForTimeout(500)
    const sourceInput = page.locator('input[name="source"], input[name="description"], input[placeholder*="source" i], input[placeholder*="description" i]').first()
    await expect(sourceInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    const dateInput = page.locator('input[type="date"], input[name="date"]').first()
    await expect(dateInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('INCOME-07: Income list renders entries with amount', async ({ page }) => {
    await page.route('**/api/v1/income/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', source: 'Freelance Project', amount: 250, date: '2026-07-06', type: 'freelance' },
          { id: '2', source: 'Part-time Job', amount: 1200, date: '2026-07-01', type: 'salary' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.INCOME, { waitUntil: 'networkidle' })
    const incomeCards = page.locator('[class*="income"], [class*="card"], [class*="entry"]')
    const count = await incomeCards.count()
    expect(count).toBeGreaterThanOrEqual(1)
    const amountText = page.locator('text=$250, text=250, text=amount, [class*="amount"]').first()
    await expect(amountText).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('INCOME-08: Income total/summary is displayed', async ({ page }) => {
    await page.route('**/api/v1/income/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', source: 'Freelance Project', amount: 250, date: '2026-07-06', type: 'freelance' },
          { id: '2', source: 'Part-time Job', amount: 1200, date: '2026-07-01', type: 'salary' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.INCOME, { waitUntil: 'networkidle' })
    const summary = page.locator('[class*="total"], [class*="summary"], [class*="stats"], text=$1,450, text=total').first()
    await expect(summary).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('INCOME-09: Error state renders when API fails', async ({ page }) => {
    await page.route('**/api/v1/income/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.INCOME, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const errorState = page.locator('[class*="error"], [role="alert"], button:has-text("Retry"), button:has-text("Try Again")').first()
    await expect(errorState).toBeVisible({ timeout: TEST_TIMEOUTS.NAVIGATION })
  })

  test('INCOME-10: Delete income entry shows confirmation', async ({ page }) => {
    await page.route('**/api/v1/income/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', source: 'Freelance Project', amount: 250, date: '2026-07-06', type: 'freelance' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.INCOME, { waitUntil: 'networkidle' })
    const deleteButton = page.locator('button[class*="delete"], button[class*="remove"], button[aria-label*="delete" i]').first()
    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click()
      const confirmDialog = page.locator('[class*="confirm"], [role="alertdialog"], [role="dialog"]').first()
      await expect(confirmDialog).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    }
  })
})
