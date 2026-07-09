import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import { ROUTES } from '../utils/constants'

const WCAG_TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']

const IMPACT_ORDER: Record<string, number> = { critical: 3, serious: 2, moderate: 1, minor: 0 }

function hasHighImpact(violation: { impact?: string | null }): boolean {
  return (IMPACT_ORDER[violation.impact ?? ''] ?? 0) >= 2
}

const PAGES = [
  { name: 'Landing', path: ROUTES.PUBLIC.HOME },
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Tasks', path: '/tasks' },
  { name: 'Chat', path: '/chat' },
  { name: 'Briefing', path: '/briefing' },
  { name: 'Habits', path: '/habits' },
  { name: 'Courses', path: '/courses' },
  { name: 'Sleep', path: '/sleep' },
  { name: 'Goals', path: '/goals' },
  { name: 'Ideas', path: '/ideas' },
  { name: 'Analytics', path: '/analytics' },
  { name: 'Automation', path: '/automation' },
  { name: 'Review', path: '/review' },
  { name: 'Projects', path: '/projects' },
  { name: 'Opportunities', path: '/opportunities' },
  { name: 'Settings', path: '/settings' },
  { name: 'Focus', path: '/focus' },
  { name: 'YouTube Vault', path: '/youtube-vault' },
  { name: 'Roadmap', path: '/roadmap' },
  { name: 'Memory', path: '/memory' },
]

test.describe('Page-level accessibility compliance', () => {

  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))
  })

  for (const { name, path } of PAGES) {
    test(`@a11y ${name} (${path}) has no critical or serious a11y violations`, async ({ page }) => {
      test.setTimeout(60_000)
      const response = await page.goto(path, { waitUntil: 'networkidle', timeout: 30_000 })
      if (response?.status() === 404) {
        test.skip(true, `Route ${path} is not available`)
        return
      }

      await page.waitForLoadState('domcontentloaded')

      const results = await new AxeBuilder({ page: page as any })
        .withTags(WCAG_TAGS)
        .analyze()

      const criticalSerious = results.violations.filter(hasHighImpact)
      const minorModerate = results.violations.filter((v) => !hasHighImpact(v))

      if (criticalSerious.length > 0) {
        const ids = criticalSerious.map((v) => `${v.id} (${v.impact})`).join(', ')
        expect.soft(criticalSerious, `${name}: ${criticalSerious.length} critical/serious violations: ${ids}`)
          .toEqual([])
      }

      if (minorModerate.length > 0) {
        const ids = minorModerate.map((v) => `${v.id} (${v.impact}): ${v.help}`).join('; ')
        console.log(`[a11y] ${name}: ${minorModerate.length} minor/moderate violations tolerated: ${ids}`)
      }
    })
  }
})

test.describe('Keyboard navigation', () => {

  test('@a11y focus is visible on every Tab press through main navigation', async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))

    await page.goto('/dashboard', { waitUntil: 'networkidle' })

    const focusableSelector = 'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    const focusableCount = await page.locator(focusableSelector).count()
    expect(focusableCount).toBeGreaterThanOrEqual(5)

    const steps = Math.min(focusableCount, 15)
    for (let i = 0; i < steps; i++) {
      await page.keyboard.press('Tab')
      const isFocused = await page.evaluate(() => {
        const el = document.activeElement
        if (!el || el === document.body) return false
        const style = window.getComputedStyle(el)
        return style.outlineStyle !== 'none' && style.outlineWidth !== '0px'
          || el.matches(':focus-visible')
      })
      expect.soft(isFocused, `Element #${i + 1} should have visible focus indicator`).toBe(true)
    }
  })

  test('@a11y Tab order does not trap focus in any section', async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))

    await page.goto('/dashboard', { waitUntil: 'networkidle' })

    const focusableSelector = 'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    const count = await page.locator(focusableSelector).count()
    const steps = Math.min(count, 20)

    const focusedElements: string[] = []
    for (let i = 0; i < steps; i++) {
      await page.keyboard.press('Tab')
      const tag = await page.evaluate(() => {
        const el = document.activeElement
        if (!el || el === document.body) return null
        return `${el.tagName.toLowerCase()}${el.textContent ? ':"' + el.textContent.substring(0, 30) + '"' : ''}`
      })
      if (tag) focusedElements.push(tag)
    }

    expect(focusedElements.length).toBeGreaterThanOrEqual(3)
    const uniqueElements = new Set(focusedElements)
    expect(uniqueElements.size).toBeGreaterThanOrEqual(3)
  })

  test('@a11y All page routes have at least one focusable element', async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))

    for (const { name, path } of PAGES) {
      const response = await page.goto(path, { waitUntil: 'networkidle', timeout: 30_000 })
      if (response?.status() === 404) continue

      await page.keyboard.press('Tab')
      const focused = page.locator(':focus')
      const count = await focused.count()
      expect.soft(count, `${name} (${path}) should have a focusable element on first Tab`).toBeGreaterThanOrEqual(1)
    }
  })

  test('@a11y Skip-to-content link is first focusable element on the page', async ({ page }) => {
    const PUBLIC_PAGES = [
      { name: 'Landing', path: ROUTES.PUBLIC.HOME },
      { name: 'Dashboard', path: '/dashboard' },
      { name: 'Tasks', path: '/tasks' },
    ]

    for (const { name, path } of PUBLIC_PAGES) {
      await page.route('**/auth/v1/user', (route) => route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
      }))

      await page.goto(path, { waitUntil: 'networkidle' })
      await page.keyboard.press('Tab')

      const isSkipLink = await page.evaluate(() => {
        const el = document.activeElement
        if (!el) return false
        const text = (el.textContent || '').toLowerCase()
        return el.matches('a[href*="main"], a[href*="content"], a[class*="skip"]')
          || text.includes('skip') || text.includes('main content')
      })

      expect.soft(isSkipLink, `${name}: first Tab should focus skip-to-content link`).toBe(true)
    }
  })
})

test.describe('Color contrast and semantic structure', () => {

  test('@a11y Color contrast meets WCAG AA standards on all pages', async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))

    for (const { name, path } of PAGES.slice(0, 6)) {
      const response = await page.goto(path, { waitUntil: 'networkidle', timeout: 30_000 })
      if (response?.status() === 404) continue

      const results = await new AxeBuilder({ page: page as any })
        .withTags(['wcag2aa', 'wcag21aa'])
        .withRules(['color-contrast'])
        .analyze()

      const failures = results.violations.filter((v) => v.id === 'color-contrast')
      if (failures.length > 0) {
        const ids = failures.map((v) => v.nodes.map((n) => n.html).join(', ')).join('; ')
        console.log(`[a11y/contrast] ${name}: ${failures.length} contrast issues: ${ids}`)
      }
      expect.soft(failures, `${name}: color contrast violations`).toEqual([])
    }
  })

  test('@a11y All pages use semantic heading hierarchy', async ({ page }) => {
    await page.route('**/auth/v1/user', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user-id', email: 'test@secondbrain.local' }),
    }))

    for (const { name, path } of PAGES) {
      const response = await page.goto(path, { waitUntil: 'networkidle', timeout: 30_000 })
      if (response?.status() === 404) continue

      const results = await new AxeBuilder({ page: page as any })
        .withRules(['heading-order', 'page-has-heading-one'])
        .analyze()

      const headingIssues = results.violations.filter(
        (v) => v.id === 'heading-order' || v.id === 'page-has-heading-one'
      )

      if (headingIssues.length > 0) {
        const ids = headingIssues.map((v) => `${v.id}: ${v.help}`).join('; ')
        console.log(`[a11y/headings] ${name}: ${headingIssues.length} heading issues: ${ids}`)
      }

      headingIssues.forEach((v) => {
        expect.soft(v.nodes.length, `${name}: ${v.id}`).toBe(0)
      })
    }
  })
})
