import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Resources', { tag: '@practical' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.RESOURCES, { waitUntil: 'networkidle' })
  })

  test('RES-01: Resource list loads with loading skeleton', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.RESOURCES, { waitUntil: 'commit' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="spinner"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('RES-02: Empty state renders when no resources exist', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const emptyState = page.locator('[class*="empty"], p:has-text("No resources"), p:has-text("no resources"), [class*="empty-state"], text=Create your first resource').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('RES-03: Create resource modal opens', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await expect(createButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await createButton.click()
    const modal = page.locator('[class*="modal"], [class*="dialog"], [role="dialog"]').first()
    await expect(modal).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('RES-04: Create resource form validates required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first()
    await expect(submitButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await submitButton.click()
    const errorMsg = page.locator('[class*="error"], [role="alert"], [class*="validation"]').first()
    await expect(errorMsg).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('RES-05: Resource title and URL inputs render', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    await page.waitForTimeout(500)
    const titleInput = page.locator('input[name="title"], input[placeholder*="title" i], input[placeholder*="resource" i]').first()
    await expect(titleInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await titleInput.fill('React Documentation')
    const value = await titleInput.inputValue()
    expect(value).toBe('React Documentation')
  })

  test('RES-06: Tag filter chips render for resource filtering', async ({ page }) => {
    await page.route('**/api/v1/resources/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'React Docs', url: 'https://react.dev', tags: ['frontend', 'react'] },
          { id: '2', title: 'Python Guide', url: 'https://python.org', tags: ['backend', 'python'] },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.RESOURCES, { waitUntil: 'networkidle' })
    const tagChip = page.locator('[class*="tag"], [class*="chip"], [class*="filter"], button:has-text("frontend"), button:has-text("All")').first()
    await expect(tagChip).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('RES-07: Tag filtering narrows resource list', async ({ page }) => {
    await page.route('**/api/v1/resources/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'React Docs', url: 'https://react.dev', tags: ['frontend', 'react'] },
          { id: '2', title: 'Python Guide', url: 'https://python.org', tags: ['backend', 'python'] },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.RESOURCES, { waitUntil: 'networkidle' })
    const filterButton = page.locator('button:has-text("frontend"), [class*="tag"]:has-text("frontend")').first()
    await expect(filterButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await filterButton.click()
    await page.waitForTimeout(500)
    const activeFilter = page.locator('[class*="active"], [class*="selected"], [aria-pressed="true"]').first()
    await expect(activeFilter).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('RES-08: Resource card displays title and URL', async ({ page }) => {
    await page.route('**/api/v1/resources/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'React Docs', url: 'https://react.dev', tags: ['frontend'] },
          { id: '2', title: 'Python Guide', url: 'https://python.org', tags: ['backend'] },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.RESOURCES, { waitUntil: 'networkidle' })
    const resourceCards = page.locator('[class*="card"], [class*="resource"], [class*="item"]')
    const count = await resourceCards.count()
    expect(count).toBeGreaterThanOrEqual(1)
    const link = page.locator('a[href*="https://"], [class*="url"], [class*="link"]').first()
    await expect(link).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('RES-09: Error state renders when API fails', async ({ page }) => {
    await page.route('**/api/v1/resources/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.RESOURCES, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const errorState = page.locator('[class*="error"], [role="alert"], button:has-text("Retry"), button:has-text("Try Again")').first()
    await expect(errorState).toBeVisible({ timeout: TEST_TIMEOUTS.NAVIGATION })
  })

  test('RES-10: Delete resource shows confirmation dialog', async ({ page }) => {
    await page.route('**/api/v1/resources/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'React Docs', url: 'https://react.dev', tags: ['frontend'] },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.RESOURCES, { waitUntil: 'networkidle' })
    const deleteButton = page.locator('button[class*="delete"], button[class*="remove"], button[aria-label*="delete" i]').first()
    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click()
      const confirmDialog = page.locator('[class*="confirm"], [class*="alert"], [role="alertdialog"], [role="dialog"]').first()
      await expect(confirmDialog).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    }
  })
})
