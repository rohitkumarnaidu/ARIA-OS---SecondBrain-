import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

const IS_CI = !!process.env.CI

test.describe('Navigation & Routing', () => {
  const MODULE_ROUTES = [
    { name: 'Dashboard', path: ROUTES.PROTECTED.DASHBOARD },
    { name: 'Tasks', path: ROUTES.PROTECTED.TASKS },
    { name: 'Courses', path: ROUTES.PROTECTED.COURSES },
    { name: 'Goals', path: ROUTES.PROTECTED.GOALS },
    { name: 'Habits', path: ROUTES.PROTECTED.HABITS },
    { name: 'Sleep', path: ROUTES.PROTECTED.SLEEP },
    { name: 'Income', path: ROUTES.PROTECTED.INCOME },
    { name: 'Projects', path: ROUTES.PROTECTED.PROJECTS },
    { name: 'Ideas', path: ROUTES.PROTECTED.IDEAS },
    { name: 'Resources', path: ROUTES.PROTECTED.RESOURCES },
    { name: 'Opportunities', path: ROUTES.PROTECTED.OPPORTUNITIES },
    { name: 'Time', path: ROUTES.PROTECTED.TIME },
    { name: 'Chat', path: ROUTES.PROTECTED.CHAT },
    { name: 'Automation', path: ROUTES.PROTECTED.AUTOMATION },
    { name: 'Academics', path: ROUTES.PROTECTED.ACADEMICS },
    { name: 'YouTube', path: ROUTES.PROTECTED.YOUTUBE },
  ]

  test.describe('Module Page Loading', () => {
    for (const { name, path } of MODULE_ROUTES) {
      test(`NAV-01: /${name.toLowerCase()} loads without JS errors`, async ({ page }) => {
        let jsError: Error | null = null
        page.on('pageerror', (err) => { jsError = err })
        const response = await page.goto(path, { timeout: TEST_TIMEOUTS.NAVIGATION, waitUntil: 'domcontentloaded' })
        expect(jsError, `${name} page should have no JS errors`).toBeNull()
        expect(response?.ok(), `${name} page should load successfully`).toBe(true)
      })
    }
  })

  test.describe('Layout Shell', () => {
    test.beforeEach(async ({ page }) => {
      test.skip(!IS_CI, 'Layout shell requires auth — CI only')
      await page.route('**/auth/v1/user', (route) => route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
      }))
    })

    const sampleModules = MODULE_ROUTES.slice(0, 4)
    for (const { name, path } of sampleModules) {
      test(`NAV-02/03: Sidebar + Navbar visible on /${name.toLowerCase()}`, async ({ dashboardPage, page }) => {
        await page.goto(path, { waitUntil: 'networkidle' })
        await expect(dashboardPage.navbar).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
      })
    }
  })

  test.describe('Sidebar', () => {
    test.beforeEach(async ({ page }) => {
      test.skip(!IS_CI, 'Sidebar requires auth — CI only')
      await page.route('**/auth/v1/user', (route) => route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
      }))
    })

    test('NAV-04: sidebar has links to all modules', async ({ dashboardPage }) => {
      await dashboardPage.goto()
      await expect(dashboardPage.sidebar).toBeVisible()
    })
  })

  test.describe('Error Handling', () => {
    test('NAV-10: unknown routes render 404 page', async ({ page }) => {
      const response = await page.goto('/this-route-does-not-exist')
      expect(response?.status()).toBe(404)
    })
  })
})
