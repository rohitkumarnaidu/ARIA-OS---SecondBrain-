import type { Meta, StoryObj } from '@storybook/react'
import { AnimatedList } from './AnimatedList'

const meta: Meta<typeof AnimatedList> = {
  title: 'Motion/AnimatedList',
  component: AnimatedList,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof AnimatedList>

export const Default: Story = {
  args: {
    items: [
      <div key="1" className="p-3 bg-background-card rounded-lg border border-border text-text-primary text-sm">Complete project proposal</div>,
      <div key="2" className="p-3 bg-background-card rounded-lg border border-border text-text-primary text-sm">Review team pull requests</div>,
      <div key="3" className="p-3 bg-background-card rounded-lg border border-border text-text-primary text-sm">Update sprint backlog</div>,
      <div key="4" className="p-3 bg-background-card rounded-lg border border-border text-text-primary text-sm">Prepare demo environment</div>,
    ],
    className: 'flex flex-col gap-2',
  },
}

export const ManyItems: Story = {
  args: {
    items: Array.from({ length: 10 }, (_, i) => (
      <div key={i} className="p-2 bg-background-card rounded border border-border text-text-secondary text-xs">Item #{i + 1}: Animated entry</div>
    )),
    className: 'flex flex-col gap-1.5',
  },
}
