import { test, expect } from '../fixtures/test'
import { ROUTES, TEST_TIMEOUTS } from '../utils/constants'

const IS_CI = !!process.env.CI

test.describe('Offline Resilience', () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!IS_CI, 'Offline/network tests require CI — hook triggers on real network')
  })

  test.describe('Offline Banner', () => {
    test('OFFL-01: offline banner appears when network is disconnected', async ({ page, offlineBanner }) => {
      await page.goto(ROUTES.PROTECTED.DASHBOARD, { waitUntil: 'networkidle' })
      await page.context().setOffline(true)
      await page.waitForTimeout(TEST_TIMEOUTS.OFFLINE_DETECTION)
      expect(await offlineBanner.isVisible()).toBe(true)
      await page.context().setOffline(false)
    })

    test('OFFL-03: offline banner disappears when network is restored', async ({ page, offlineBanner }) => {
      await page.goto(ROUTES.PROTECTED.DASHBOARD, { waitUntil: 'networkidle' })
      await page.context().setOffline(true)
      await page.waitForTimeout(TEST_TIMEOUTS.OFFLINE_DETECTION)
      await page.context().setOffline(false)
      await page.waitForTimeout(TEST_TIMEOUTS.OFFLINE_DETECTION)
      expect(await offlineBanner.isVisible()).toBe(false)
    })
  })

  test.describe('Network Detection', () => {
    test('OFFL-06: online/offline events fire on network change', async ({ page }) => {
      const events: string[] = []
      await page.exposeFunction('__captureOnline', () => events.push('online'))
      await page.exposeFunction('__captureOffline', () => events.push('offline'))

      await page.goto(ROUTES.PROTECTED.DASHBOARD, { waitUntil: 'networkidle' })
      await page.evaluate(() => {
        window.addEventListener('online', () => (window as any).__captureOnline())
        window.addEventListener('offline', () => (window as any).__captureOffline())
      })

      await page.context().setOffline(true)
      await page.waitForTimeout(2_000)
      await page.context().setOffline(false)
      await page.waitForTimeout(2_000)

      expect(events).toContain('offline')
      expect(events).toContain('online')
    })
  })
})
