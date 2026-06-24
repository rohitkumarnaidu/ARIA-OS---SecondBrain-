import { describe, it, expect } from 'vitest'

describe('@/components/ui barrel exports', () => {
  const expectedValues = [
    'Button', 'buttonVariants',
    'Input',
    'Card', 'CardHeader', 'CardTitle', 'CardContent', 'CardFooter', 'CardDescription',
    'Skeleton',
    'Badge',
    'Spinner',
    'EmptyCanvas',
    'ErrorState',
    'LoadingScreen',
    'PageHeader',
    'cn',
    'Dialog',
    'Sheet',
    'Drawer',
    'Popover',
    'Tooltip',
    'Select',
    'Switch',
    'Tabs',
    'DropdownMenu',
    'BentoGrid', 'BentoCard',
    'ProgressRing',
    'ActivityHeatmap',
    'Timeline',
    'ChartContainer',
    'Modal',
    'EmptyState',
  ]

  it('exports all expected value exports', async () => {
    const mod = await import('@/components/ui')
    for (const name of expectedValues) {
      expect(mod).toHaveProperty(name)
    }
  }, 60000)

  it('has enough exports to cover all components', async () => {
    const mod = await import('@/components/ui')
    const exportNames = Object.keys(mod)
    expect(exportNames.length).toBeGreaterThanOrEqual(expectedValues.length)
  }, 60000)
})

describe('@/components/ai barrel exports', () => {
  const expectedValues = [
    'ThinkingIndicator',
    'StreamingText',
    'GhostHint',
    'SuggestionChips',
    'AIInsightCard',
    'AIDock',
    'AIUndo',
    'ConfidenceBadge',
  ]

  it('exports all expected value exports', async () => {
    const mod = await import('@/components/ai')
    for (const name of expectedValues) {
      expect(mod).toHaveProperty(name)
    }
  }, 60000)
})

describe('@/components/shared barrel exports', () => {
  const expectedValues = [
    'ModuleLoading',
    'ModuleError',
    'ErrorBoundary',
    'PostHogProvider',
    'LiveRegion',
  ]

  it('exports all expected value exports', async () => {
    const mod = await import('@/components/shared')
    for (const name of expectedValues) {
      expect(mod).toHaveProperty(name)
    }
  }, 60000)
})
