import { test, expect } from '@/e2e/fixtures/test'
import { Page } from '@playwright/test'

async function mockSkillsApi(page: Page) {
  await page.route('**/api/v1/skills/categories', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { category_id: 'cat-1', name: 'Frontend', slug: 'frontend', description: 'Frontend skills', sort_order: 0, level: 0, is_active: true, metadata: {}, created_at: 0, updated_at: 0 },
        { category_id: 'cat-2', name: 'Backend', slug: 'backend', description: 'Backend skills', sort_order: 1, level: 0, is_active: true, metadata: {}, created_at: 0, updated_at: 0 },
      ]),
    })
  })

  await page.route('**/api/v1/skills/', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { skill_id: 'skill-1', category_id: 'cat-1', name: 'React', slug: 'react', description: 'React framework', level_min: 0, level_max: 5, aliases: [], is_deprecated: false, created_at: 0, updated_at: 0 },
        { skill_id: 'skill-2', category_id: 'cat-2', name: 'Python', slug: 'python', description: 'Python language', level_min: 0, level_max: 5, aliases: [], is_deprecated: false, created_at: 0, updated_at: 0 },
      ]),
    })
  })

  await page.route('**/api/v1/skills/user-skills', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { user_skill_id: 'us-1', skill_id: 'skill-1', user_id: 'test-user', level: 3, state: 'active', confidence_score: 0.8, evidence_score: 0.7, level_change_90d: 0, is_emerging: false, is_stale: false, metadata: {}, created_at: 0, updated_at: 0 },
      ]),
    })
  })

  await page.route('**/api/v1/skills/evidence', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/targets', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/assessments', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/market-data', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/income', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/certifications', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/topics', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/resources', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/learning-paths', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/recommendations', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/activity', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/external-mappings', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/roadmap-definitions', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('**/api/v1/skills/forecasts', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })
}

async function mockFailedSkillsApi(page: Page) {
  await page.route('**/api/v1/skills/**', async route => {
    await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ error: 'Internal server error' }) })
  })
}

async function mockEmptySkillsApi(page: Page) {
  await page.route('**/api/v1/skills/categories', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })
  await page.route('**/api/v1/skills/', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })
  await page.route('**/api/v1/skills/**', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })
}

async function login(page: Page) {
  await page.goto('/login')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('[type="submit"]')
  await page.waitForURL('**/dashboard')
}

test.describe('Skills Page', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
  })

  test('renders skills page with categories and skills', async ({ page }) => {
    await mockSkillsApi(page)
    await page.goto('/skills')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('text=Skills')).toBeVisible()
    await expect(page.locator('text=Frontend')).toBeVisible()
    await expect(page.locator('text=Backend')).toBeVisible()
    await expect(page.locator('text=React')).toBeVisible()
    await expect(page.locator('text=Python')).toBeVisible()
  })

  test('filters skills by search', async ({ page }) => {
    await mockSkillsApi(page)
    await page.goto('/skills')
    await page.waitForLoadState('networkidle')

    await page.fill('input[placeholder="Search skills..."]', 'React')
    await expect(page.locator('text=React')).toBeVisible()
    await expect(page.locator('text=Python')).not.toBeVisible()
  })

  test('shows skill radar chart with user skills', async ({ page }) => {
    await mockSkillsApi(page)
    await page.goto('/skills')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('text=Skill Radar')).toBeVisible()
    await expect(page.locator('text=Active Skills')).toBeVisible()
  })

  test('add skill to user portfolio', async ({ page }) => {
    await mockSkillsApi(page)
    await page.goto('/skills')
    await page.waitForLoadState('networkidle')

    await page.click('text=Add Skill')
    await expect(page.locator('text=Add Skill').first()).toBeVisible()

    await page.route('**/api/v1/skills/user-skills', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({ user_skill_id: 'us-2', skill_id: 'skill-2', user_id: 'test-user', level: 0, state: 'planned', confidence_score: 0, evidence_score: 0, level_change_90d: 0, is_emerging: false, is_stale: false, metadata: {}, created_at: 0, updated_at: 0 }),
        })
      } else {
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
      }
    })
  })

  test('shows empty state when no skills data exists', async ({ page }) => {
    await mockEmptySkillsApi(page)
    await page.goto('/skills')
    await page.waitForLoadState('networkidle')

    const emptyState = page.locator('text=No skills, text=Get started, text=Add your first, text=empty, [class*="empty"]').first()
    await expect(emptyState).toBeVisible()
  })

  test('shows error state when API calls fail', async ({ page }) => {
    await mockFailedSkillsApi(page)
    await page.goto('/skills')
    await page.waitForLoadState('networkidle')

    const errorElement = page.locator('text=error, text=failed, text=unavailable, text=try again, [class*="error"]').first()
    await expect(errorElement).toBeVisible()
  })

  test('loading skeleton appears while skills are fetching', async ({ page }) => {
    await page.route('**/api/v1/skills/**', async route => {
      await new Promise(r => setTimeout(r, 3000))
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.goto('/skills')
    await page.waitForLoadState('domcontentloaded')

    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="placeholder"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible()
  })

  test('retry button appears after API failure', async ({ page }) => {
    await mockFailedSkillsApi(page)
    await page.goto('/skills')
    await page.waitForLoadState('networkidle')

    const retryButton = page.locator('button:has-text("Retry"), button:has-text("Try again"), button:has-text("Reload")').first()
    await expect(retryButton).toBeVisible()
  })

  test('network error shows offline state', async ({ page }) => {
    await page.route('**/api/v1/skills/**', async route => {
      await route.abort('internetdisconnected')
    })
    await page.goto('/skills', { waitUntil: 'load' })

    const errorElement = page.locator('text=error, text=failed, text=offline, text=network, [class*="error"], [class*="offline"]').first()
    await expect(errorElement).toBeVisible()
  })
})

test.describe('Skill Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
  })

  test('renders skill detail with tabs', async ({ page }) => {
    await mockSkillsApi(page)
    await page.goto('/skills/skill-1')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('text=React').first()).toBeVisible()
    await expect(page.locator('text=Overview')).toBeVisible()
    await expect(page.locator('text=Market')).toBeVisible()
    await expect(page.locator('text=Learning')).toBeVisible()
    await expect(page.locator('text=Forecasts')).toBeVisible()
    await expect(page.locator('text=Activity')).toBeVisible()
  })

  test('navigates between tabs on detail page', async ({ page }) => {
    await mockSkillsApi(page)
    await page.goto('/skills/skill-1')
    await page.waitForLoadState('networkidle')

    await page.click('text=Market')
    await expect(page.locator('text=Market Data')).toBeVisible()

    await page.click('text=Learning')
    await expect(page.locator('text=Learning Paths')).toBeVisible()

    await page.click('text=Forecasts')
    await expect(page.locator('text=Skill Forecasts')).toBeVisible()
  })

  test('shows back button and navigates to skills list', async ({ page }) => {
    await mockSkillsApi(page)
    await page.goto('/skills/skill-1')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('text=Back')).toBeVisible()
    await page.click('text=Back')
    await page.waitForURL('**/skills')
  })

  test('detail page shows error when skill not found', async ({ page }) => {
    await page.route('**/api/v1/skills/skill-999', async route => {
      await route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ error: 'Skill not found' }) })
    })
    await page.goto('/skills/skill-999')
    await page.waitForLoadState('networkidle')

    const errorElement = page.locator('text=not found, text=doesn\'t exist, text=error, [class*="error"], [class*="not-found"]').first()
    await expect(errorElement).toBeVisible()
  })
})
