import type { Meta, StoryObj } from '@storybook/react'
import { GoalProgress } from './GoalProgress'

const meta = {
  title: 'Goals/GoalProgress',
  component: GoalProgress,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
} satisfies Meta<typeof GoalProgress>

export default meta
type Story = StoryObj<typeof meta>

export const Halfway: Story = {
  args: { current: 50, target: 100, label: 'Course Progress' },
}

export const Complete: Story = {
  args: { current: 100, target: 100, label: 'Completed Goal' },
}

export const Small: Story = {
  args: { current: 7, target: 30, label: 'Daily Streak', size: 'sm' },
}

export const Large: Story = {
  args: { current: 7500, target: 10000, label: 'Revenue', size: 'lg' },
}

export const NoLabel: Story = {
  args: { current: 42, target: 100 },
}

export const Loading: Story = {
  args: { current: 0, target: 100, loading: true },
}
