import type { Meta, StoryObj } from '@storybook/react'
import { BentoGrid, BentoCard } from './BentoGrid'

const meta: Meta<typeof BentoGrid> = {
  title: 'UI/BentoGrid',
  component: BentoGrid,
  tags: ['autodocs'],
  argTypes: {
    cols: { control: 'select', options: [2, 3, 4] },
  },
}

export default meta
type Story = StoryObj<typeof BentoGrid>

export const ThreeColumns: Story = {
  render: (args) => (
    <BentoGrid {...args}>
      <BentoCard span={2}>
        <div className="flex h-32 items-center justify-center text-text-secondary">
          Featured Content (span 2)
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-32 items-center justify-center text-text-secondary">
          Side Card
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Card 3
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Card 4
        </div>
      </BentoCard>
      <BentoCard span={2}>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Wide Card (span 2)
        </div>
      </BentoCard>
    </BentoGrid>
  ),
  args: { cols: 3 },
}

export const TwoColumns: Story = {
  render: (args) => (
    <BentoGrid {...args}>
      <BentoCard span={2}>
        <div className="flex h-32 items-center justify-center text-text-secondary">
          Hero Card (span 2)
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Card A
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Card B
        </div>
      </BentoCard>
    </BentoGrid>
  ),
  args: { cols: 2 },
}

export const FourColumns: Story = {
  render: (args) => (
    <BentoGrid {...args}>
      <BentoCard span={4}>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Full Width Banner (span 4)
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-28 items-center justify-center text-text-secondary">
          Card 1
        </div>
      </BentoCard>
      <BentoCard span={2}>
        <div className="flex h-28 items-center justify-center text-text-secondary">
          Center Feature (span 2)
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-28 items-center justify-center text-text-secondary">
          Card 3
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-28 items-center justify-center text-text-secondary">
          Card 4
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-28 items-center justify-center text-text-secondary">
          Card 5
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-28 items-center justify-center text-text-secondary">
          Card 6
        </div>
      </BentoCard>
    </BentoGrid>
  ),
  args: { cols: 4 },
}

export const UniformCards: Story = {
  render: (args) => (
    <BentoGrid {...args}>
      <BentoCard>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Card 1
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Card 2
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Card 3
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Card 4
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Card 5
        </div>
      </BentoCard>
      <BentoCard>
        <div className="flex h-24 items-center justify-center text-text-secondary">
          Card 6
        </div>
      </BentoCard>
    </BentoGrid>
  ),
  args: { cols: 3 },
}

export const WithContent: Story = {
  render: (args) => (
    <BentoGrid {...args}>
      <BentoCard span={2}>
        <h3 className="text-lg font-semibold text-text-primary mb-2">Weekly Overview</h3>
        <p className="text-sm text-text-secondary">
          Tasks completed: 24/30 · Habits tracked: 5/7 · Study hours: 18.5
        </p>
      </BentoCard>
      <BentoCard>
        <h3 className="text-sm font-semibold text-text-primary mb-1">Next Deadline</h3>
        <p className="text-2xl font-bold text-accent-primary">3d</p>
        <p className="text-xs text-text-tertiary">Database Systems project</p>
      </BentoCard>
      <BentoCard>
        <h3 className="text-sm font-semibold text-text-primary mb-1">Focus Score</h3>
        <p className="text-2xl font-bold text-accent-neon">85%</p>
        <p className="text-xs text-text-tertiary">+12% from last week</p>
      </BentoCard>
      <BentoCard>
        <h3 className="text-sm font-semibold text-text-primary mb-1">Upcoming</h3>
        <p className="text-xs text-text-secondary">Study group at 3PM · Meeting at 5PM</p>
      </BentoCard>
    </BentoGrid>
  ),
  args: { cols: 3 },
}
