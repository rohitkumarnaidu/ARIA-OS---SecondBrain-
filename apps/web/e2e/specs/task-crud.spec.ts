import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Task CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.TASKS, { waitUntil: 'networkidle' })
  })

  test('TASK-01: Task list loads with loading skeleton', async ({ page }) => {
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await page.waitForLoadState('networkidle')
    const list = page.locator('[class*="task-list"], [class*="tasks"]').first()
    await expect(list.or(page.locator('[class*="empty"]'))).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('TASK-02: Create task modal opens', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await expect(createButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await createButton.click()
    const modal = page.locator('[class*="modal"], [class*="dialog"], [role="dialog"]').first()
    await expect(modal).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('TASK-03: Create task form validates required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first()
    await expect(submitButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await submitButton.click()
    const errorMsg = page.locator('[class*="error"], [role="alert"], [class*="validation"]').first()
    await expect(errorMsg).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('TASK-04: Task title input renders in modal', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    await page.waitForTimeout(500)
    const titleInput = page.locator('input[name="title"], input[placeholder*="title" i], input[placeholder*="task" i]').first()
    await expect(titleInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await titleInput.fill('Test E2E Task')
    const value = await titleInput.inputValue()
    expect(value).toBe('Test E2E Task')
  })

  test('TASK-05: Empty state renders for fresh task list', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const emptyState = page.locator('[class*="empty"], p:has-text("No tasks"), p:has-text("no tasks"), [class*="empty-state"]').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })
})
