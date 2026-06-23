import type { Meta, StoryObj } from '@storybook/react'
import { NeonBorder } from './NeonBorder'

const meta: Meta<typeof NeonBorder> = {
  title: 'Motion/NeonBorder',
  component: NeonBorder,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof NeonBorder>

export const Default: Story = {
  args: {
    children: <div className="p-6 text-text-primary font-medium">Neon bordered content</div>,
  },
}

export const Indigo: Story = {
  args: {
    children: <div className="p-6 text-text-primary font-medium">Indigo neon border</div>,
    color: '#6366F1',
  },
}

export const Green: Story = {
  args: {
    children: <div className="p-6 text-text-primary font-medium">Green neon border</div>,
    color: '#00FFA3',
  },
}

export const FastSpeed: Story = {
  args: {
    children: <div className="p-6 text-text-primary font-medium">Fast animation</div>,
    speed: 1,
  },
}

export const SlowSpeed: Story = {
  args: {
    children: <div className="p-6 text-text-primary font-medium">Slow animation</div>,
    speed: 6,
  },
}
