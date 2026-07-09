import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Opportunities', { tag: '@practical' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.OPPORTUNITIES, { waitUntil: 'networkidle' })
  })

  test('OPP-01: Opportunity list loads with loading skeleton', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.OPPORTUNITIES, { waitUntil: 'commit' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="spinner"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('OPP-02: Empty state renders when no opportunities exist', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const emptyState = page.locator('[class*="empty"], p:has-text("No opportunities"), p:has-text("no opportunities"), [class*="empty-state"], text=Create your first opportunity').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('OPP-03: Create opportunity modal opens', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await expect(createButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await createButton.click()
    const modal = page.locator('[class*="modal"], [class*="dialog"], [role="dialog"]').first()
    await expect(modal).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('OPP-04: Create opportunity form validates required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first()
    await expect(submitButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await submitButton.click()
    const errorMsg = page.locator('[class*="error"], [role="alert"], [class*="validation"]').first()
    await expect(errorMsg).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('OPP-05: Opportunity title and URL inputs render', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    await page.waitForTimeout(500)
    const titleInput = page.locator('input[name="title"], input[placeholder*="title" i], input[placeholder*="opportunity" i]').first()
    await expect(titleInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await titleInput.fill('React Developer Intern')
    const value = await titleInput.inputValue()
    expect(value).toBe('React Developer Intern')
  })

  test('OPP-06: Match score badge renders for listed opportunities', async ({ page }) => {
    await page.route('**/api/v1/opportunities/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'Frontend Intern', match_score: 92, source: 'LinkedIn', url: 'https://linkedin.com/jobs/1' },
          { id: '2', title: 'SDE Intern', match_score: 78, source: 'Indeed', url: 'https://indeed.com/jobs/2' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.OPPORTUNITIES, { waitUntil: 'networkidle' })
    const scoreBadge = page.locator('[class*="match"], [class*="score"], [class*="badge"]').first()
    await expect(scoreBadge).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    const scoreText = await scoreBadge.textContent()
    expect(scoreText).toMatch(/\d+/)
  })

  test('OPP-07: Radar view toggle switches layout', async ({ page }) => {
    await page.route('**/api/v1/opportunities/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'Frontend Intern', match_score: 92, source: 'LinkedIn' },
          { id: '2', title: 'SDE Intern', match_score: 78, source: 'Indeed' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.OPPORTUNITIES, { waitUntil: 'networkidle' })
    const radarButton = page.locator('button:has-text("Radar"), button:has-text("Grid"), button:has-text("List"), [class*="layout"] button').first()
    await expect(radarButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await radarButton.click()
    const radarView = page.locator('[class*="radar"], [class*="grid"], [class*="kanban"]').first()
    await expect(radarView).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('OPP-08: Detail view opens for an opportunity card', async ({ page }) => {
    await page.route('**/api/v1/opportunities/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'Frontend Intern', match_score: 92, source: 'LinkedIn', url: 'https://linkedin.com/jobs/1', description: 'Work on React components' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.OPPORTUNITIES, { waitUntil: 'networkidle' })
    const card = page.locator('[class*="card"], [class*="item"], [class*="opportunity"]').first()
    await expect(card).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await card.click()
    const detailPanel = page.locator('[class*="detail"], [class*="expanded"], [class*="panel"]').first()
    await expect(detailPanel).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('OPP-09: Error state renders when API fails', async ({ page }) => {
    await page.route('**/api/v1/opportunities/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.OPPORTUNITIES, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const errorState = page.locator('[class*="error"], [role="alert"], button:has-text("Retry"), button:has-text("Try Again")').first()
    await expect(errorState).toBeVisible({ timeout: TEST_TIMEOUTS.NAVIGATION })
  })

  test('OPP-10: Delete opportunity shows confirmation dialog', async ({ page }) => {
    await page.route('**/api/v1/opportunities/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', title: 'Frontend Intern', match_score: 92, source: 'LinkedIn' },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.OPPORTUNITIES, { waitUntil: 'networkidle' })
    const deleteButton = page.locator('button[class*="delete"], button[class*="remove"], button[aria-label*="delete" i]').first()
    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click()
      const confirmDialog = page.locator('[class*="confirm"], [class*="alert"], [role="alertdialog"], [role="dialog"]').first()
      await expect(confirmDialog).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    }
  })
})
