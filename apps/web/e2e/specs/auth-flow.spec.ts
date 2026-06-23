import { test, expect } from '../fixtures/test'
import { ROUTES, AUTH, TEST_TIMEOUTS } from '../utils/constants'

test.describe('Auth Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(ROUTES.PUBLIC.LOGIN, { waitUntil: 'networkidle' })
  })

  test('AUTH-01: Login page loads with correct elements', async ({ loginPage, page }) => {
    await expect(page).toHaveTitle(/Sign In|Login|ARIA|Second Brain/)
    await expect(loginPage.emailInput).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await expect(loginPage.passwordInput).toBeVisible()
    await expect(loginPage.submitButton).toBeVisible()
    await expect(loginPage.googleSignInButton).toBeVisible()
  })

  test('AUTH-02: Form validation shows errors for empty fields', async ({ loginPage }) => {
    await loginPage.submitButton.click()
    await expect(loginPage.errorMessage).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    const errorText = await loginPage.errorMessage.textContent()
    expect(errorText?.length).toBeGreaterThan(0)
  })

  test('AUTH-03: Shows error for invalid credentials', async ({ loginPage, page }) => {
    await loginPage.signInWithEmail('invalid@test.com', 'wrongpassword')
    await expect(loginPage.errorMessage).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
    const errorText = await loginPage.errorMessage.textContent()
    expect(errorText?.toLowerCase()).toContain('invalid')
  })

  test('AUTH-04: Google OAuth button is clickable', async ({ loginPage }) => {
    await expect(loginPage.googleSignInButton).toBeEnabled({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('AUTH-05: Redirects to dashboard when already authenticated', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('sb-auth-token', 'mock-token')
    })
    await page.goto(ROUTES.PUBLIC.LOGIN, { waitUntil: 'networkidle' })
    await page.waitForTimeout(2000)
    const currentUrl = page.url()
    expect(currentUrl === ROUTES.PROTECTED.DASHBOARD || currentUrl.includes('/dashboard')).toBe(true)
  })
})
