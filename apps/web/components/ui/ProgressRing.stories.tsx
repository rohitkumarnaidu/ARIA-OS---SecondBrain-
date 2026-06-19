import type { Meta, StoryObj } from '@storybook/react'
import { ProgressRing } from './ProgressRing'

const meta: Meta<typeof ProgressRing> = {
  title: 'UI/ProgressRing',
  component: ProgressRing,
  tags: ['autodocs'],
  argTypes: {
    size: { control: { type: 'number', min: 40, max: 300 } },
    strokeWidth: { control: { type: 'number', min: 2, max: 32 } },
    progress: { control: { type: 'number', min: 0, max: 100 } },
  },
}

export default meta
type Story = StoryObj<typeof ProgressRing>

export const Quarter: Story = {
  args: { progress: 25 },
}

export const Half: Story = {
  args: { progress: 50 },
}

export const ThreeQuarters: Story = {
  args: { progress: 75 },
}

export const Complete: Story = {
  args: { progress: 100 },
}

export const Empty: Story = {
  args: { progress: 0 },
}

export const Small: Story = {
  args: { progress: 65, size: 64, strokeWidth: 6 },
}

export const Large: Story = {
  args: { progress: 80, size: 200, strokeWidth: 12 },
}

export const CustomColor: Story = {
  args: { progress: 70, color: 'var(--accent-neon)' },
}

export const CustomBgColor: Story = {
  args: { progress: 45, bgColor: 'var(--accent-danger)' },
}

export const ThickStroke: Story = {
  args: { progress: 60, strokeWidth: 20, size: 120 },
}

export const ThinStroke: Story = {
  args: { progress: 90, strokeWidth: 3, size: 120 },
}

export const WithChildren: Story = {
  args: {
    progress: 72,
    size: 140,
    children: (
      <div className="text-center">
        <span className="block text-2xl font-bold text-text-primary">72%</span>
        <span className="block text-xs text-text-tertiary">Complete</span>
      </div>
    ),
  },
}

export const WithEmoji: Story = {
  args: {
    progress: 100,
    size: 100,
    children: <span className="text-2xl">&#10003;</span>,
  },
}

export const WithCustomIcon: Story = {
  args: {
    progress: 33,
    size: 120,
    children: <span className="text-xl" style={{ color: 'var(--accent-warning)' }}>&#9888;</span>,
  },
}
