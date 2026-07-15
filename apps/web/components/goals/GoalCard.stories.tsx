import type { Meta, StoryObj } from '@storybook/react'
import { GoalCard } from './GoalCard'
import type { Goal } from '@/lib/types'

const mockGoal: Goal = {
  id: '1',
  user_id: 'user-1',
  title: 'Master React Ecosystem',
  description: 'Complete advanced courses in React, Next.js, and state management',
  category: 'skill',
  status: 'active',
  target_date: '2026-12-31T00:00:00Z',
  hours_per_day: 2,
  days_per_week: 5,
  progress: 35,
  milestones: [
    { id: 'm1', goal_id: '1', title: 'Complete React Fundamentals', completed: true },
    { id: 'm2', goal_id: '1', title: 'Build a full-stack app with Next.js', completed: false },
    { id: 'm3', goal_id: '1', title: 'Learn state management patterns', completed: false },
    { id: 'm4', goal_id: '1', title: 'Deploy to production', completed: false },
  ],
  created_at: '2026-01-01T00:00:00Z',
}

const meta = {
  title: 'Goals/GoalCard',
  component: GoalCard,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof GoalCard>

export default meta
type Story = StoryObj<typeof meta>

export const Active: Story = {
  args: { goal: { ...mockGoal, status: 'active' } },
}

export const Paused: Story = {
  args: { goal: { ...mockGoal, status: 'paused' } },
}

export const Completed: Story = {
  args: { goal: { ...mockGoal, status: 'completed', progress: 100 } },
}

export const NoMilestones: Story = {
  args: { goal: { ...mockGoal, milestones: [] } },
}
