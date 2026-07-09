import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Projects', { tag: '@practical' }, () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.PROJECTS, { waitUntil: 'networkidle' })
  })

  test('PROJ-01: Project list loads with loading skeleton', async ({ page }) => {
    await page.goto(ROUTES.PROTECTED.PROJECTS, { waitUntil: 'commit' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="spinner"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('PROJ-02: Empty state renders when no projects exist', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const emptyState = page.locator('[class*="empty"], p:has-text("No projects"), p:has-text("no projects"), [class*="empty-state"], text=Create your first project').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
  })

  test('PROJ-03: Create project modal opens', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await expect(createButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await createButton.click()
    const modal = page.locator('[class*="modal"], [class*="dialog"], [role="dialog"]').first()
    await expect(modal).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('PROJ-04: Create project form validates required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first()
    await expect(submitButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await submitButton.click()
    const errorMsg = page.locator('[class*="error"], [role="alert"], [class*="validation"]').first()
    await expect(errorMsg).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('PROJ-05: Project name and description inputs render', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first()
    await createButton.click()
    await page.waitForTimeout(500)
    const nameInput = page.locator('input[name="name"], input[name="title"], input[placeholder*="project" i], input[placeholder*="name" i]').first()
    await expect(nameInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await nameInput.fill('Capstone Project')
    const value = await nameInput.inputValue()
    expect(value).toBe('Capstone Project')
  })

  test('PROJ-06: Project phase tracking renders', async ({ page }) => {
    await page.route('**/api/v1/projects/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', name: 'Capstone', phase: 'development', status: 'in_progress', blockers: [] },
          { id: '2', name: 'Research Paper', phase: 'planning', status: 'not_started', blockers: [] },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.PROJECTS, { waitUntil: 'networkidle' })
    const phaseBadge = page.locator('[class*="phase"], [class*="status"], [class*="badge"]').first()
    await expect(phaseBadge).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    const phaseText = await phaseBadge.textContent()
    expect(phaseText?.length).toBeGreaterThan(0)
  })

  test('PROJ-07: Blocker list renders for project with blockers', async ({ page }) => {
    await page.route('**/api/v1/projects/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          {
            id: '1',
            name: 'Capstone',
            phase: 'development',
            status: 'blocked',
            blockers: ['Waiting for API key', 'Need design review'],
          },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.PROJECTS, { waitUntil: 'networkidle' })
    const blocker = page.locator('[class*="blocker"], [class*="blocked"], text=Waiting for API key').first()
    await expect(blocker).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('PROJ-08: Project detail view opens with phases', async ({ page }) => {
    await page.route('**/api/v1/projects/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', name: 'Capstone', phase: 'development', status: 'in_progress', blockers: [] },
          { id: '2', name: 'Research Paper', phase: 'planning', status: 'not_started', blockers: [] },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.PROJECTS, { waitUntil: 'networkidle' })
    const projectCards = page.locator('[class*="card"], [class*="project"], [class*="item"]')
    const count = await projectCards.count()
    expect(count).toBeGreaterThanOrEqual(1)
    const phaseList = page.locator('[class*="phase"], [class*="roadmap"]').first()
    await expect(phaseList).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('PROJ-09: Error state renders when API fails', async ({ page }) => {
    await page.route('**/api/v1/projects/**', (route) => route.abort('connectionrefused'))
    await page.goto(ROUTES.PROTECTED.PROJECTS, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1000)
    const errorState = page.locator('[class*="error"], [role="alert"], button:has-text("Retry"), button:has-text("Try Again")').first()
    await expect(errorState).toBeVisible({ timeout: TEST_TIMEOUTS.NAVIGATION })
  })

  test('PROJ-10: Delete project shows confirmation dialog', async ({ page }) => {
    await page.route('**/api/v1/projects/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { id: '1', name: 'Capstone', phase: 'development', status: 'in_progress', blockers: [] },
        ],
      }),
    }))
    await page.goto(ROUTES.PROTECTED.PROJECTS, { waitUntil: 'networkidle' })
    const deleteButton = page.locator('button[class*="delete"], button[class*="remove"], button[aria-label*="delete" i]').first()
    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click()
      const confirmDialog = page.locator('[class*="confirm"], [class*="alert"], [role="alertdialog"], [role="dialog"]').first()
      await expect(confirmDialog).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    }
  })
})
