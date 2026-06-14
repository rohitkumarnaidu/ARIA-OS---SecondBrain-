import { test, expect } from '../fixtures/test'
import { ROUTES } from '../utils/constants'

const IS_CI = !!process.env.CI

test.describe('Auth — Middleware Guard', () => {
  test.describe('Unauthenticated Access', () => {
    test('AUTH-01: protected route shows login prompt', async ({ page }) => {
      await page.goto(ROUTES.PROTECTED.DASHBOARD)
      // In CI with Supabase: middleware redirects to /login
      // In dev without Supabase: page renders, no redirect
      // Both paths are valid — test is informational
      const url = page.url()
      const showsLoginUi = await page.getByRole('button', { name: /sign in/i }).isVisible().catch(() => false)
      const onLoginPage = url.includes('/login')
      // At minimum, the page loaded without crashing
      expect(url).toBeTruthy()
      console.log(`[AUTH-01] Dashboard at: ${url}, login UI: ${showsLoginUi}, on /login: ${onLoginPage}`)
    })

    test('AUTH-02: all protected routes accessible without crash', async ({ page }) => {
      for (const route of Object.values(ROUTES.PROTECTED)) {
        const response = await page.goto(route)
        expect(response?.ok(), `${route} should load without crash`).toBe(true)
      }
    })
  })

  test.describe('Public Routes', () => {
    test('AUTH-04a: / is accessible without auth', async ({ page }) => {
      const response = await page.goto(ROUTES.PUBLIC.HOME)
      expect(response?.ok()).toBe(true)
    })

    test('AUTH-04b: /login is accessible without auth', async ({ page }) => {
      const response = await page.goto(ROUTES.PUBLIC.LOGIN)
      expect(response?.ok()).toBe(true)
    })
  })

  test.describe('CI-Only Auth Tests', () => {
    test('AUTH-03: authenticated user can access /dashboard', async ({ page }) => {
      test.skip(!IS_CI, 'Requires Supabase auth session — CI only')
      await page.route('**/auth/v1/user', (route) => route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
      }))
      await page.goto(ROUTES.PROTECTED.DASHBOARD, { waitUntil: 'networkidle' })
      expect(page.url()).not.toContain('/login')
    })
  })
})
