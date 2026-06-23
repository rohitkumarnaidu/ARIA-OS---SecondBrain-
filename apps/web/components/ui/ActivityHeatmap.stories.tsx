import type { Meta, StoryObj } from '@storybook/react'
import { ActivityHeatmap } from './ActivityHeatmap'

function generateData(days: number, maxCount: number) {
  const data: { date: string; count: number }[] = []
  const now = new Date()
  for (let i = days; i >= 0; i--) {
    const d = new Date(now)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    data.push({ date: dateStr, count: Math.floor(Math.random() * maxCount) })
  }
  return data
}

const meta: Meta<typeof ActivityHeatmap> = {
  title: 'UI/ActivityHeatmap',
  component: ActivityHeatmap,
  tags: ['autodocs'],
  parameters: {
    backgrounds: { default: 'dark' },
  },
}

export default meta
type Story = StoryObj<typeof ActivityHeatmap>

export const Default: Story = {
  args: { data: generateData(365, 20) },
}

export const Sparse: Story = {
  args: { data: generateData(365, 3) },
}

export const Empty: Story = {
  args: { data: [] },
}

export const Heavy: Story = {
  args: { data: generateData(365, 50) },
}
