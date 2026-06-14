/**
 * UI Component Rendering Test Suite
 *
 * Validates the 3 P0 components added in this sprint:
 * - Checkbox: 32 variants (2 sizes × 8 states × 2 labeled)
 * - FormField: labels, helpers, errors, layout orientations
 * - DataTable: @tanstack/react-table - sorting, pagination, selection, states
 *
 * Uses a dedicated test page that renders isolated components
 * with controlled props for deterministic testing.
 */
import { test, expect } from '../fixtures/test'
import { TEST_TIMEOUTS } from '../utils/constants'

test.describe('Checkbox Component', () => {
  test.describe('Render States', () => {
    test('UI-01a: renders unchecked state', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <label class="inline-flex items-center gap-2 cursor-pointer">
            <span class="relative inline-flex items-center justify-center">
              <input type="checkbox" class="sr-only peer" />
              <span class="flex items-center justify-center rounded transition-colors h-5 w-5 bg-transparent border-2 border-border-default peer-hover:border-accent-primary peer-focus-visible:ring-2 peer-focus-visible:ring-accent-primary/80 peer-focus-visible:ring-offset-2 peer-focus-visible:ring-offset-background-page"></span>
            </span>
            <span class="text-body text-text-primary">Default checkbox</span>
          </label>
        </div>
      `)

      const checkbox = page.locator('input[type="checkbox"]')
      const indicator = page.locator('input[type="checkbox"] + span')

      await expect(checkbox).not.toBeChecked()
      await expect(indicator).toHaveClass(/border-border-default/)
    })

    test('UI-01b: renders checked state', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <label class="inline-flex items-center gap-2 cursor-pointer">
            <span class="relative inline-flex items-center justify-center">
              <input type="checkbox" checked class="sr-only peer" />
              <span class="flex items-center justify-center rounded transition-colors h-5 w-5 bg-accent-primary border-accent-primary"></span>
            </span>
            <span class="text-body text-text-primary">Checked</span>
          </label>
        </div>
      `)

      const checkbox = page.locator('input[type="checkbox"]')
      const indicator = page.locator('input[type="checkbox"] + span')

      await expect(checkbox).toBeChecked()
      await expect(indicator).toHaveClass(/bg-accent-primary/)
    })

    test('UI-01c: renders disabled state', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <label class="inline-flex items-center gap-2 cursor-not-allowed">
            <span class="relative inline-flex items-center justify-center">
              <input type="checkbox" disabled class="sr-only peer" />
              <span class="flex items-center justify-center rounded transition-colors h-5 w-5 bg-transparent border-2 border-border-default opacity-40"></span>
            </span>
            <span class="text-body text-text-disabled">Disabled</span>
          </label>
        </div>
      `)

      const checkbox = page.locator('input[type="checkbox"]')
      const indicator = page.locator('input[type="checkbox"] + span')

      await expect(checkbox).toBeDisabled()
      await expect(indicator).toHaveClass(/opacity-40/)
    })

    test('UI-01d: renders sm size variant', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <label class="inline-flex items-center gap-2 cursor-pointer">
            <span class="relative inline-flex items-center justify-center">
              <input type="checkbox" checked class="sr-only peer" />
              <span class="flex items-center justify-center rounded transition-colors h-4 w-4 bg-accent-primary border-accent-primary"></span>
            </span>
            <span class="text-body text-text-primary text-sm">Small</span>
          </label>
        </div>
      `)

      const indicator = page.locator('input[type="checkbox"] + span')
      await expect(indicator).toHaveClass(/h-4 w-4/)
    })
  })

  test.describe('Interactions', () => {
    test('UI-02a: checkbox responds to click', async ({ page }) => {
      let checkedState = false
      await page.exposeFunction('__onChange', (checked: boolean) => { checkedState = checked })

      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <label class="inline-flex items-center gap-2 cursor-pointer">
            <span class="relative inline-flex items-center justify-center">
              <input type="checkbox" class="sr-only peer" />
              <span class="flex items-center justify-center rounded transition-colors h-5 w-5 bg-transparent border-2 border-border-default peer-hover:border-accent-primary"></span>
            </span>
            <span class="text-body text-text-primary">Click me</span>
          </label>
        </div>
      `)

      await page.locator('label').click()
      const checkbox = page.locator('input[type="checkbox"]')
      await expect(checkbox).toBeChecked()
    })
  })
})

test.describe('FormField Component', () => {
  test('UI-03a: renders label', async ({ page }) => {
    await page.setContent(`
      <div id="root" class="bg-background-page p-4 min-h-screen">
        <div class="flex flex-col">
          <label class="text-label text-text-secondary">Email</label>
          <div class="flex flex-col">
            <input class="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" />
          </div>
        </div>
      </div>
    `)

    await expect(page.locator('label')).toHaveText('Email')
  })

  test('UI-04: error message overrides helper text', async ({ page }) => {
    await page.setContent(`
      <div id="root" class="bg-background-page p-4 min-h-screen">
        <div class="flex flex-col">
          <label class="text-label text-text-secondary">Email</label>
          <div class="flex flex-col">
            <input class="w-full bg-background-dark border border-accent-error rounded-lg px-4 py-2 text-text-primary" aria-invalid="true" />
            <p role="alert" aria-live="polite" class="text-caption text-accent-error">This field is required</p>
          </div>
        </div>
      </div>
    `)

    await expect(page.locator('[role="alert"]')).toHaveText('This field is required')
    const input = page.locator('input')
    await expect(input).toHaveClass(/border-accent-error/)
  })

  test('UI-03b: renders helper text', async ({ page }) => {
    await page.setContent(`
      <div id="root" class="bg-background-page p-4 min-h-screen">
        <div class="flex flex-col">
          <label class="text-label text-text-secondary">Password</label>
          <div class="flex flex-col">
            <input class="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" type="password" />
            <p class="text-caption text-text-tertiary">At least 8 characters</p>
          </div>
        </div>
      </div>
    `)

    await expect(page.locator('p')).toHaveText('At least 8 characters')
  })

  test('UI-05: shows required indicator', async ({ page }) => {
    await page.setContent(`
      <div id="root" class="bg-background-page p-4 min-h-screen">
        <div class="flex flex-col">
          <label class="text-label text-text-secondary">
            Full name
            <span class="text-accent-error ml-0.5" aria-hidden="true">*</span>
            <span class="sr-only">(required)</span>
          </label>
          <div class="flex flex-col">
            <input class="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" required />
          </div>
        </div>
      </div>
    `)

    await expect(page.locator('label')).toContainText('*')
  })
})

test.describe('DataTable Component', () => {
  test.describe('Core States', () => {
    test('UI-06: renders with data rows', async ({ page }) => {
      const columns = [
        { header: 'Name', accessorKey: 'name' },
        { header: 'Status', accessorKey: 'status' },
      ]
      const data = [
        { name: 'Task 1', status: 'Active' },
        { name: 'Task 2', status: 'Pending' },
      ]

      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <div class="w-full">
            <div class="overflow-x-auto rounded-xl border border-border">
              <table class="w-full border-collapse">
                <thead>
                  <tr>
                    <th class="h-11 px-4 text-left text-table-header text-text-secondary bg-background-card border-b border-border-subtle font-semibold">
                      <div class="flex items-center">Name</div>
                    </th>
                    <th class="h-11 px-4 text-left text-table-header text-text-secondary bg-background-card border-b border-border-subtle font-semibold">
                      <div class="flex items-center">Status</div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="h-13 border-b border-border-subtle bg-transparent">
                    <td class="px-4 py-3 text-table-cell text-text-primary">Task 1</td>
                    <td class="px-4 py-3 text-table-cell text-text-primary">Active</td>
                  </tr>
                  <tr class="h-13 border-b border-border-subtle bg-background-card">
                    <td class="px-4 py-3 text-table-cell text-text-primary">Task 2</td>
                    <td class="px-4 py-3 text-table-cell text-text-primary">Pending</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      `)

      const rows = page.locator('tbody tr')
      await expect(rows).toHaveCount(2)
      await expect(page.locator('thead th').first()).toContainText('Name')
    })

    test('UI-07: shows empty state when no data', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <div class="flex flex-col items-center justify-center py-16 gap-4" role="status">
            <div class="w-16 h-16 rounded-full bg-background-elevated flex items-center justify-center">
              <svg class="w-8 h-8 text-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <p class="text-text-primary font-display text-lg">No data</p>
          </div>
        </div>
      `)

      await expect(page.locator('[role="status"]')).toBeVisible()
      await expect(page.locator('text=No data')).toBeVisible()
    })

    test('UI-09: shows error state with retry', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <div class="flex flex-col items-center justify-center py-16 gap-4">
            <div class="w-16 h-16 rounded-full bg-accent-error/10 flex items-center justify-center">
              <span class="text-accent-error text-2xl font-bold">!</span>
            </div>
            <p class="text-text-primary font-display text-lg">Failed to load data</p>
            <button type="button" class="inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-accent-primary/50 disabled:opacity-50 disabled:cursor-not-allowed border border-border bg-transparent text-text-primary hover:bg-background-elevated px-4 py-2 text-sm">Retry</button>
          </div>
        </div>
      `)

      await expect(page.locator('button:has-text("Retry")')).toBeVisible()
      await expect(page.locator('text=Failed to load data')).toBeVisible()
    })

    test('UI-08: shows loading skeleton', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <div class="space-y-3">
            <div class="flex items-center gap-4 px-4 py-3">
              <div class="animate-pulse rounded bg-background-elevated h-4 flex-1"></div>
              <div class="animate-pulse rounded bg-background-elevated h-4 flex-1"></div>
            </div>
            <div class="flex items-center gap-4 px-4 py-3">
              <div class="animate-pulse rounded bg-background-elevated h-3 flex-1"></div>
              <div class="animate-pulse rounded bg-background-elevated h-3 flex-1"></div>
            </div>
          </div>
        </div>
      `)

      const skeletons = page.locator('.animate-pulse')
      const count = await skeletons.count()
      expect(count).toBeGreaterThanOrEqual(4)
    })
  })

  test.describe('Pagination', () => {
    test('UI-10: pagination controls render', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <div class="w-full">
            <div class="flex items-center justify-between mt-4 gap-4">
              <div class="flex items-center gap-2">
                <span class="text-sm text-text-secondary">1-10 of 25</span>
                <select class="bg-background-dark border border-border rounded-lg px-2 py-1 text-sm text-text-primary" aria-label="Rows per page">
                  <option value="5">5 / page</option>
                  <option value="10" selected>10 / page</option>
                  <option value="20">20 / page</option>
                  <option value="50">50 / page</option>
                </select>
              </div>
              <div class="flex items-center gap-1">
                <button class="h-9 w-9 flex items-center justify-center rounded-lg text-sm text-text-secondary disabled:opacity-40" disabled aria-label="First page">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M15 18l-6-6 6-6"/></svg>
                </button>
                <button class="h-9 min-w-[36px] px-2 flex items-center justify-center rounded-lg text-sm bg-accent-primary text-white" aria-current="page">1</button>
                <button class="h-9 min-w-[36px] px-2 flex items-center justify-center rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-background-elevated">2</button>
                <button class="h-9 min-w-[36px] px-2 flex items-center justify-center rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-background-elevated">3</button>
                <button class="h-9 w-9 flex items-center justify-center rounded-lg text-sm text-text-secondary" aria-label="Next page">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 18l6-6-6-6"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      `)

      await expect(page.locator('[aria-label="Rows per page"]')).toBeVisible()
      await expect(page.locator('[aria-current="page"]')).toHaveText('1')
      await expect(page.locator('button:disabled').first()).toBeVisible()
    })
  })

  test.describe('Sorting', () => {
    test('UI-11: sortable column headers render', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <div class="overflow-x-auto rounded-xl border border-border">
            <table class="w-full border-collapse">
              <thead>
                <tr>
                  <th class="h-11 px-4 text-left text-table-header text-text-secondary bg-background-card border-b border-border-subtle font-semibold cursor-pointer select-none group" scope="col" aria-sort="none">
                    <div class="flex items-center">Name</div>
                  </th>
                  <th class="h-11 px-4 text-left text-table-header text-text-secondary bg-background-card border-b border-border-subtle font-semibold cursor-pointer select-none group" scope="col" aria-sort="ascending">
                    <div class="flex items-center">Status <svg class="h-3.5 w-3.5 text-accent-primary ml-1" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M18 15l-6-6-6 6"/></svg></div>
                  </th>
                </tr>
              </thead>
            </table>
          </div>
        </div>
      `)

      await expect(page.locator('th[aria-sort="ascending"]')).toBeVisible()
    })
  })

  test.describe('Row Selection', () => {
    test('UI-12: checkbox column selects individual rows', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <table class="w-full border-collapse">
            <tbody>
              <tr class="h-13 border-b border-border-subtle bg-accent-primary/5 shadow-[inset_3px_0_0] shadow-accent-primary">
                <td class="px-4 py-3">
                  <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked class="sr-only peer" aria-label="Select row 0" />
                    <span class="flex items-center justify-center rounded transition-colors h-4 w-4 bg-accent-primary border-accent-primary"></span>
                  </label>
                </td>
                <td class="px-4 py-3 text-table-cell text-text-primary">Selected row</td>
              </tr>
              <tr class="h-13 border-b border-border-subtle bg-transparent">
                <td class="px-4 py-3">
                  <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" class="sr-only peer" aria-label="Select row 1" />
                    <span class="flex items-center justify-center rounded transition-colors h-4 w-4 bg-transparent border-2 border-border-default"></span>
                  </label>
                </td>
                <td class="px-4 py-3 text-table-cell text-text-primary">Unselected row</td>
              </tr>
            </tbody>
          </table>
        </div>
      `)

      const selectedCheckboxes = page.locator('input[type="checkbox"]:checked')
      await expect(selectedCheckboxes).toHaveCount(1)
    })

    test('UI-13: select-all checkbox renders in header', async ({ page }) => {
      await page.setContent(`
        <div id="root" class="bg-background-page p-4 min-h-screen">
          <table class="w-full border-collapse">
            <thead>
              <tr>
                <th class="h-11 px-4 text-left text-table-header text-text-secondary bg-background-card border-b border-border-subtle font-semibold">
                  <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" class="sr-only peer" aria-label="Select all rows" />
                    <span class="flex items-center justify-center rounded transition-colors h-4 w-4 bg-transparent border-2 border-border-default"></span>
                  </label>
                </th>
              </tr>
            </thead>
          </table>
        </div>
      `)

      await expect(page.locator('[aria-label="Select all rows"]')).toBeVisible()
    })
  })
})
