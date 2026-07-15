import type { Meta, StoryObj } from '@storybook/react'
import { IncomeChart } from './IncomeChart'
import type { IncomeEntry } from '@/lib/types'

const generateEntries = (count: number): IncomeEntry[] => {
  const entries: IncomeEntry[] = []
  for (let i = 0; i < count; i++) {
    const date = new Date(2026, 6, i + 1)
    entries.push({
      id: `${i}`,
      user_id: 'user-1',
      source_type: 'Freelance',
      amount: Math.round(Math.random() * 2000 + 200),
      platform: 'Upwork',
      date: date.toISOString().split('T')[0],
      created_at: date.toISOString(),
    })
  }
  return entries
}

const meta = {
  title: 'Income/IncomeChart',
  component: IncomeChart,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof IncomeChart>

export default meta
type Story = StoryObj<typeof meta>

export const Monthly: Story = {
  args: { entries: generateEntries(30), period: 'month' },
}

export const Weekly: Story = {
  args: { entries: generateEntries(7), period: 'week' },
}

export const Empty: Story = {
  args: { entries: [], period: 'month' },
}

export const Loading: Story = {
  args: { entries: [], loading: true },
}
