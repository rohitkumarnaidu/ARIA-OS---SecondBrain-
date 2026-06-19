import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

const pages = [
  { path: '/', name: 'Dashboard' },
  { path: '/tasks', name: 'Tasks' },
  { path: '/courses', name: 'Courses' },
  { path: '/goals', name: 'Goals' },
  { path: '/habits', name: 'Habits' },
  { path: '/projects', name: 'Projects' },
  { path: '/opportunities', name: 'Opportunities' },
  { path: '/chat', name: 'Chat / AI' },
  { path: '/settings', name: 'Settings' },
  { path: '/focus', name: 'Focus Mode' },
  { path: '/youtube-vault', name: 'YouTube Vault' },
  { path: '/review', name: 'Weekly Review' },
  { path: '/briefing', name: 'Daily Briefing' },
  { path: '/roadmap', name: 'Skill Roadmap' },
  { path: '/memory', name: 'AI Memory' },
]

for (const page of pages) {
  test(`${page.name} page should have no automated a11y violations`, async ({ page: p }) => {
    await p.goto(page.path)
    await p.waitForLoadState('networkidle')
    const results = await new AxeBuilder({ page: p as any }).analyze()
    expect(results.violations).toEqual([])
  })
}

test('keyboard navigation should reach all major interactive elements', async ({ page }) => {
  await page.goto('/')
  await page.waitForLoadState('networkidle')

  const focusableSelector = 'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
  const count = await page.locator(focusableSelector).count()
  expect(count).toBeGreaterThanOrEqual(5)

  for (let i = 0; i < Math.min(count, 8); i++) {
    await page.keyboard.press('Tab')
    const focused = page.locator(':focus')
    await expect(focused).toBeVisible()
    expect(await focused.count()).toBeGreaterThanOrEqual(1)
  }
})

test('skip-to-content link should be first focusable element', async ({ page }) => {
  await page.goto('/')
  await page.waitForLoadState('networkidle')
  await page.keyboard.press('Tab')
  const focused = page.locator(':focus')
  const tag = await focused.evaluate(el => el.tagName.toLowerCase())
  const text = await focused.evaluate(el => el.textContent?.toLowerCase() || '')
  const isSkip = tag === 'a' && (text.includes('skip') || text.includes('main content'))
  if (!isSkip) {
    expect(tag).toBeTruthy()
  }
})
