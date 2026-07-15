import type { Meta, StoryObj } from '@storybook/react'
import { IncomeCard } from './IncomeCard'
import type { IncomeEntry } from '@/lib/types'

const mockEntry: IncomeEntry = {
  id: '1',
  user_id: 'user-1',
  source_type: 'Freelance Development',
  amount: 2500.00,
  platform: 'Upwork',
  description: 'Full-stack web application for client',
  date: '2026-07-14',
  hours_spent: 40,
  effective_hourly_rate: 62.50,
  created_at: '2026-07-14T12:00:00Z',
}

const meta = {
  title: 'Income/IncomeCard',
  component: IncomeCard,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof IncomeCard>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: { entry: mockEntry },
}

export const WithHourlyRate: Story = {
  args: {
    entry: {
      ...mockEntry,
      amount: 500,
      hours_spent: 5,
      effective_hourly_rate: 100,
    },
  },
}

export const NoPlatform: Story = {
  args: {
    entry: {
      ...mockEntry,
      platform: undefined,
      hours_spent: undefined,
      effective_hourly_rate: undefined,
      description: undefined,
    },
  },
}
