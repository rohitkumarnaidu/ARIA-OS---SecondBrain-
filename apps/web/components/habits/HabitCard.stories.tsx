import type { Meta, StoryObj } from '@storybook/react'
import { HabitCard } from './HabitCard'
import type { Habit } from '@/lib/types'

const mockHabit: Habit = {
  id: '1',
  user_id: 'user-1',
  name: 'Morning Meditation',
  frequency: 'daily',
  time_target_minutes: 15,
  is_active: true,
  current_streak: 12,
  best_streak: 45,
  consistency_percentage: 78.5,
  created_at: '2026-01-01T00:00:00Z',
}

const meta = {
  title: 'Habits/HabitCard',
  component: HabitCard,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof HabitCard>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: { habit: mockHabit },
}

export const TodayLogged: Story = {
  args: { habit: mockHabit, todayLogged: true },
}

export const Inactive: Story = {
  args: { habit: { ...mockHabit, is_active: false } },
}
