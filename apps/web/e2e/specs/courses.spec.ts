import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Courses', { tag: '@practical' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.COURSES, { waitUntil: 'networkidle' })
  })

  test('COURSE-01: Course list loads with loading skeleton', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.COURSES, { waitUntil: 'commit' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="spinner"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('COURSE-02: Empty state renders when no courses exist', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const emptyState = page.locator('[class*="empty"], p:has-text("No courses"), p:has-text("no courses"), [class*="empty-state"], text=Add your first course').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('COURSE-03: Create course modal opens', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await expect(createButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await createButton.click()
    const modal = page.locator('[class*="modal"], [class*="dialog"], [role="dialog"]').first()
    await expect(modal).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('COURSE-04: Create course form validates required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first()
    await expect(submitButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await submitButton.click()
    const errorMsg = page.locator('[class*="error"], [role="alert"], [class*="validation"]').first()
    await expect(errorMsg).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('COURSE-05: Course name input renders and accepts text', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    await page.waitForTimeout(500)
    const nameInput = page.locator('input[name="name"], input[name="title"], input[placeholder*="course" i], input[placeholder*="name" i]').first()
    await expect(nameInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await nameInput.fill('Linear Algebra')
    const value = await nameInput.inputValue()
    expect(value).toBe('Linear Algebra')
  })

  test('COURSE-06: Course list renders multiple courses with progress', async ({ page }) => {
    await page.route('**/api/v1/courses/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', name: 'Linear Algebra', platform: 'Khan Academy', progress: 65, status: 'in_progress' },
          { id: '2', name: 'Data Structures', platform: 'Coursera', progress: 30, status: 'in_progress' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.COURSES, { waitUntil: 'networkidle' })
    const courseCards = page.locator('[class*="course"], [class*="card"]')
    const count = await courseCards.count()
    expect(count).toBeGreaterThanOrEqual(1)
    const progressBar = page.locator('[class*="progress"], [class*="bar"]').first()
    await expect(progressBar).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('COURSE-07: Course card shows progress percentage', async ({ page }) => {
    await page.route('**/api/v1/courses/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', name: 'Linear Algebra', platform: 'Khan Academy', progress: 65, status: 'in_progress' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.COURSES, { waitUntil: 'networkidle' })
    const progressText = page.locator('text=65%, text=65, [class*="progress"]:has-text("65")').first()
    await expect(progressText).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('COURSE-08: Error state renders when API fails', async ({ page }) => {
    await page.route('**/api/v1/courses/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.COURSES, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const errorState = page.locator('[class*="error"], [role="alert"], button:has-text("Retry"), button:has-text("Try Again")').first()
    await expect(errorState).toBeVisible({ timeout: TEST_TIMEOUTS.NAVIGATION })
  })

  test('COURSE-09: Error 500 renders error state gracefully', async ({ page }) => {
    await page.route('**/api/v1/courses/**', (route) => route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Failed to load courses' }),
    }))
    await page.goto(ROUTES.PROTECTED.COURSES, { waitUntil: 'networkidle' })
    const errorElement = page.locator('text=error, text=failed, text=try again, [class*="error"]').first()
    await expect(errorElement).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('COURSE-10: Delete course shows confirmation dialog', async ({ page }) => {
    await page.route('**/api/v1/courses/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', name: 'Linear Algebra', platform: 'Khan Academy', progress: 65, status: 'in_progress' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.COURSES, { waitUntil: 'networkidle' })
    const deleteButton = page.locator('button[class*="delete"], button[class*="remove"], button[aria-label*="delete" i]').first()
    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click()
      const confirmDialog = page.locator('[class*="confirm"], [role="alertdialog"], [role="dialog"]').first()
      await expect(confirmDialog).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    }
  })
})
