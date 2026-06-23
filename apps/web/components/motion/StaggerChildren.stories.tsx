import type { Meta, StoryObj } from '@storybook/react'
import { StaggerChildren } from './StaggerChildren'

const meta: Meta<typeof StaggerChildren> = {
  title: 'Motion/StaggerChildren',
  component: StaggerChildren,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof StaggerChildren>

const items = ['Task 1: Review PR', 'Task 2: Write documentation', 'Task 3: Update dependencies', 'Task 4: Run tests', 'Task 5: Deploy to staging'].map((text, i) => (
  <div key={i} className="p-3 bg-background-card rounded-lg border border-border text-text-primary text-sm">{text}</div>
))

export const Fast: Story = {
  args: { children: items, staggerDelay: 0.03 },
}

export const Normal: Story = {
  args: { children: items, staggerDelay: 0.05 },
}

export const Slow: Story = {
  args: { children: items, staggerDelay: 0.15 },
}
