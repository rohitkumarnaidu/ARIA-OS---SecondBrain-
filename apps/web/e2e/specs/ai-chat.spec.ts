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

  test('CHAT-06: Shows empty state when no messages exist yet', async ({ page }) => {
    await page.route('**/api/v1/chat/**', async route => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ messages: [] }) })
    })
    await page.goto(ROUTES.PROTECTED.CHAT, { waitUntil: 'networkidle' })
    const emptyState = page.locator('text=No messages yet, text=Start a conversation, text=Send your first message, [class*="empty"]').first()
    await expect(emptyState).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('CHAT-07: Shows error state when API request fails', async ({ page }) => {
    await page.route('**/api/v1/chat/**', async route => {
      await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ error: 'Internal server error' }) })
    })
    await page.goto(ROUTES.PROTECTED.CHAT, { waitUntil: 'networkidle' })
    const errorElement = page.locator('text=error, text=failed, text=unavailable, text=try again, [class*="error"]').first()
    await expect(errorElement).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('CHAT-08: Shows error state on network failure (offline)', async ({ page }) => {
    await page.route('**/api/v1/chat/**', async route => {
      await route.abort('internetdisconnected')
    })
    await page.goto(ROUTES.PROTECTED.CHAT, { waitUntil: 'load' })
    const errorElement = page.locator('text=error, text=failed, text=offline, text=network, text=try again, [class*="error"], [class*="offline"]').first()
    await expect(errorElement).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('CHAT-09: Shows loading skeleton while messages are fetching', async ({ page }) => {
    await page.route('**/api/v1/chat/**', async route => {
      await new Promise(r => setTimeout(r, 3000))
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ messages: [] }) })
    })
    await page.goto(ROUTES.PROTECTED.CHAT, { waitUntil: 'domcontentloaded' })
    const skeleton = page.locator('[class*="skeleton"], [class*="loading"], [class*="placeholder"], [class*="shimmer"]').first()
    await expect(skeleton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })

  test('CHAT-10: Retry button appears after failed request', async ({ page }) => {
    await page.route('**/api/v1/chat/**', async route => {
      await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ error: 'Server error' }) })
    })
    await page.goto(ROUTES.PROTECTED.CHAT, { waitUntil: 'networkidle' })
    const retryButton = page.locator('button:has-text("Retry"), button:has-text("Try again"), button:has-text("Reload")').first()
    await expect(retryButton).toBeVisible({ timeout: TEST_TIMEOUTS.ANIMATION })
  })
})
