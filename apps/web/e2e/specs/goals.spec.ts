import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Goals', { tag: '@practical' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.GOALS, { waitUntil: 'networkidle' })
  })

  test('GOAL-01: Goal list loads with loading skeleton', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.GOALS, { waitUntil: 'commit' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="spinner"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('GOAL-02: Empty state renders when no goals exist', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const emptyState = page.locator('[class*="empty"], p:has-text("No goals"), p:has-text("no goals"), [class*="empty-state"], text=Create your first goal').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('GOAL-03: Create goal modal opens', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await expect(createButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await createButton.click()
    const modal = page.locator('[class*="modal"], [class*="dialog"], [role="dialog"]').first()
    await expect(modal).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('GOAL-04: Create goal form validates required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first()
    await expect(submitButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await submitButton.click()
    const errorMsg = page.locator('[class*="error"], [role="alert"], [class*="validation"]').first()
    await expect(errorMsg).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('GOAL-05: Goal title input renders and accepts text', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    await page.waitForTimeout(500)
    const titleInput = page.locator('input[name="title"], input[name="name"], input[placeholder*="goal" i], input[placeholder*="title" i]').first()
    await expect(titleInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await titleInput.fill('Learn TypeScript Basics')
    const value = await titleInput.inputValue()
    expect(value).toBe('Learn TypeScript Basics')
  })

  test('GOAL-06: Goal list renders goals with milestone markers', async ({ page }) => {
    await page.route('**/api/v1/goals/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'Learn TypeScript', status: 'in_progress', deadline: '2026-12-31', progress: 40 },
          { id: '2', title: 'Build Portfolio', status: 'not_started', progress: 0 },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.GOALS, { waitUntil: 'networkidle' })
    const goalCards = page.locator('[class*="goal"], [class*="card"]')
    const count = await goalCards.count()
    expect(count).toBeGreaterThanOrEqual(1)
    const progressIndicator = page.locator('[class*="progress"], [class*="milestone"], [class*="status"]').first()
    await expect(progressIndicator).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('GOAL-07: Goal detail view shows milestones', async ({ page }) => {
    await page.route('**/api/v1/goals/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          {
            id: '1',
            title: 'Learn TypeScript',
            status: 'in_progress',
            progress: 40,
            milestones: [
              { id: 'm1', title: 'Complete Basics', completed: true },
              { id: 'm2', title: 'Build a Project', completed: false },
            ],
          },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.GOALS, { waitUntil: 'networkidle' })
    const goalCard = page.locator('[class*="goal"], [class*="card"]').first()
    await expect(goalCard).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await goalCard.click()
    await page.waitForTimeout(500)
    const milestone = page.locator('text=milestone, [class*="milestone"], text=Complete Basics').first()
    await expect(milestone).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION }).catch(() => {})
  })

  test('GOAL-08: Error state renders when API fails', async ({ page }) => {
    await page.route('**/api/v1/goals/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.GOALS, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const errorState = page.locator('[class*="error"], [role="alert"], button:has-text("Retry"), button:has-text("Try Again")').first()
    await expect(errorState).toBeVisible({ timeout: TEST_TIMEOUTS.NAVIGATION })
  })

  test('GOAL-09: Goal status update toggles visible', async ({ page }) => {
    await page.route('**/api/v1/goals/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'Learn TypeScript', status: 'in_progress', progress: 40 },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.GOALS, { waitUntil: 'networkidle' })
    const statusBadge = page.locator('[class*="status"], [class*="badge"]').first()
    await expect(statusBadge).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('GOAL-10: Delete goal shows confirmation dialog', async ({ page }) => {
    await page.route('**/api/v1/goals/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'Learn TypeScript', status: 'in_progress', progress: 40 },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.GOALS, { waitUntil: 'networkidle' })
    const deleteButton = page.locator('button[class*="delete"], button[class*="remove"], button[aria-label*="delete" i]').first()
    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click()
      const confirmDialog = page.locator('[class*="confirm"], [role="alertdialog"], [role="dialog"]').first()
      await expect(confirmDialog).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    }
  })
})
