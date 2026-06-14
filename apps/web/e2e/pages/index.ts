import { Locator, Page } from '@playwright/test'

export class LoginPage {
  readonly page: Page
  readonly emailInput: Locator
  readonly passwordInput: Locator
  readonly submitButton: Locator
  readonly errorMessage: Locator
  readonly googleSignInButton: Locator

  constructor(page: Page) {
    this.page = page
    this.emailInput = page.locator('input[type="email"], input[name="email"]')
    this.passwordInput = page.locator('input[type="password"]')
    this.submitButton = page.locator('button[type="submit"], button:has-text("Sign In")')
    this.errorMessage = page.locator('[role="alert"], .text-accent-error')
    this.googleSignInButton = page.locator('button:has-text("Google")')
  }

  async goto() {
    await this.page.goto('/login')
  }

  async signInWithEmail(email: string, password: string) {
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
    await this.submitButton.click()
  }

  async isLoggedIn(): Promise<boolean> {
    await this.page.goto('/dashboard')
    return !this.page.url().includes('/login')
  }
}

export class DashboardPage {
  readonly page: Page
  readonly sidebar: Locator
  readonly navbar: Locator
  readonly greeting: Locator
  readonly statsGrid: Locator
  readonly taskSection: Locator
  readonly ariaPickSection: Locator
  readonly sidebarLinks: Locator

  constructor(page: Page) {
    this.page = page
    this.sidebar = page.locator('nav, aside, [class*="sidebar"]').first()
    this.navbar = page.locator('header, [class*="navbar"], [class*="nav"]').first()
    this.greeting = page.locator('h1, h2, [class*="greeting"]').first()
    this.statsGrid = page.locator('[class*="stats"], [class*="grid"]').first()
    this.taskSection = page.locator('section:has-text("Task"), [class*="task"]').first()
    this.ariaPickSection = page.locator('section:has-text("ARIA"), [class*="aria"]').first()
    this.sidebarLinks = page.locator('nav a, aside a')
  }

  async goto() {
    await this.page.goto('/dashboard')
    await this.page.waitForLoadState('networkidle')
  }

  async navigateToModule(moduleName: string) {
    await this.sidebarLinks.filter({ hasText: moduleName }).first().click()
    await this.page.waitForLoadState('networkidle')
  }
}

export class ModulePage {
  readonly page: Page
  readonly pageTitle: Locator
  readonly loadingSpinner: Locator
  readonly errorState: Locator
  readonly emptyState: Locator
  readonly createButton: Locator

  constructor(page: Page, private modulePath: string) {
    this.page = page
    this.pageTitle = page.locator('h1').first()
    this.loadingSpinner = page.locator('[class*="loading"], [class*="spinner"], [class*="skeleton"]').first()
    this.errorState = page.locator('[class*="error"], [role="alert"]').first()
    this.emptyState = page.locator('[class*="empty"]').first()
    this.createButton = page.locator('button:has-text("Create"), button:has-text("Add")').first()
  }

  async goto() {
    await this.page.goto(this.modulePath)
    await this.page.waitForLoadState('networkidle')
  }

  async isLoaded(): Promise<boolean> {
    await this.page.waitForLoadState('networkidle')
    return !(await this.loadingSpinner.isVisible().catch(() => false))
  }
}

export class OfflineBanner {
  readonly page: Page
  readonly banner: Locator
  readonly retryButton: Locator

  constructor(page: Page) {
    this.page = page
    this.banner = page.locator('[class*="offline"], [role="alert"]:has-text("offline")').first()
    this.retryButton = page.locator('button:has-text("Retry")').first()
  }

  async isVisible(): Promise<boolean> {
    return this.banner.isVisible().catch(() => false)
  }
}
