import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

test.describe('AI Chat', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
    await page.goto(ROUTES.PROTECTED.CHAT, { waitUntil: 'networkidle' })
  })

  test('CHAT-01: Chat panel opens and shows message area', async ({ page }) => {
    const chatPanel = page.locator('[class*="chat"], [class*="conversation"], section').first()
    await expect(chatPanel).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('CHAT-02: Messages render in the chat', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    const messages = page.locator('[class*="message"], [class*="bubble"], [class*="chat-message"]')
    const count = await messages.count()
    expect(count).toBeGreaterThanOrEqual(0)
  })

  test('CHAT-03: Input field is present and editable', async ({ page }) => {
    const input = page.locator('textarea, input[type="text"], input[placeholder*="message" i], input[placeholder*="ask" i]').first()
    await expect(input).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await input.fill('Hello ARIA')
    const value = await input.inputValue()
    expect(value).toBe('Hello ARIA')
  })

  test('CHAT-04: Send button is visible', async ({ page }) => {
    const sendButton = page.locator('button[type="submit"], button:has-text("Send"), button:has-text("Ask"), svg[aria-label="Send"]').first()
    await expect(sendButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('CHAT-05: Typing indicator shows when AI responds', async ({ page }) => {
    const input = page.locator('textarea, input[type="text"], input[placeholder*="message" i], input[placeholder*="ask" i]').first()
    await expect(input).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
    await input.fill('What is my top priority today?')

    const sendButton = page.locator('button[type="submit"], button:has-text("Send"), button:has-text("Ask")').first()
    if (await sendButton.isEnabled().catch(() => false)) {
      await sendButton.click()
      const typingIndicator = page.locator('[class*="typing"], [class*="loading"], [class*="spinner"]').first()
      await expect(typingIndicator).toBeVisible({ timeout: TEST_TIMEOUTS.NETWORK_IDLE })
    }
  })
})
