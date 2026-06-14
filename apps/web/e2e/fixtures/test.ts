import { test as base } from '@playwright/test'
import { LoginPage, DashboardPage, ModulePage, OfflineBanner } from '../pages'

type TestFixtures = {
  loginPage: LoginPage
  dashboardPage: DashboardPage
  offlineBanner: OfflineBanner
  modulePages: Record<string, ModulePage>
}

const MODULES = [
  'dashboard', 'tasks', 'courses', 'goals', 'habits', 'sleep',
  'income', 'projects', 'ideas', 'resources', 'opportunities',
  'time', 'chat', 'automation', 'academics', 'youtube',
] as const

export const test = base.extend<TestFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page))
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page))
  },
  offlineBanner: async ({ page }, use) => {
    await use(new OfflineBanner(page))
  },
  modulePages: async ({ page }, use) => {
    const pages: Record<string, ModulePage> = {}
    for (const mod of MODULES) {
      pages[mod] = new ModulePage(page, `/${mod}`)
    }
    await use(pages)
  },
})

export { expect } from '@playwright/test'
