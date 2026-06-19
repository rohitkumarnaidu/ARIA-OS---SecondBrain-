import type { Meta, StoryObj } from '@storybook/react'
import { Skeleton } from './Skeleton'

const meta = {
  title: 'UI/Skeleton',
  component: Skeleton,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['text', 'circle', 'card', 'chart', 'table-row'] },
  },
} satisfies Meta<typeof Skeleton>

export default meta
type Story = StoryObj<typeof meta>

export const Text: Story = {
  args: { variant: 'text', className: 'w-48' },
}

export const Circle: Story = {
  args: { variant: 'circle' },
}

export const Card: Story = {
  args: { variant: 'card', className: 'w-80' },
}

export const Chart: Story = {
  args: { variant: 'chart', className: 'w-96' },
}

export const TableRow: Story = {
  args: { variant: 'table-row', className: 'w-full' },
}

export const TextBlock: Story = {
  render: () => (
    <div className="space-y-3 w-64">
      <Skeleton variant="text" className="w-3/4" />
      <Skeleton variant="text" className="w-full" />
      <Skeleton variant="text" className="w-full" />
      <Skeleton variant="text" className="w-2/3" />
    </div>
  ),
}

export const ProfileCard: Story = {
  render: () => (
    <div className="flex items-center gap-4 p-4 rounded-xl border border-border w-72">
      <Skeleton variant="circle" />
      <div className="flex-1 space-y-2">
        <Skeleton variant="text" className="w-1/2" />
        <Skeleton variant="text" className="w-3/4" />
      </div>
    </div>
  ),
}

export const DashboardRow: Story = {
  render: () => (
    <div className="space-y-2 w-full max-w-md">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 px-4 py-3 rounded-lg border border-border">
          <Skeleton variant="circle" className="w-8 h-8" />
          <Skeleton variant="text" className="flex-1" />
          <Skeleton variant="text" className="w-16" />
        </div>
      ))}
    </div>
  ),
}
