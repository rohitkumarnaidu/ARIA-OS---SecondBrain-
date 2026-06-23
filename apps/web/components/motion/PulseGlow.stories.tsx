import type { Meta, StoryObj } from '@storybook/react'
import { PulseGlow } from './PulseGlow'

const meta: Meta<typeof PulseGlow> = {
  title: 'Motion/PulseGlow',
  component: PulseGlow,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof PulseGlow>

export const Active: Story = {
  args: {
    children: <button className="px-6 py-3 bg-accent-primary text-white rounded-lg font-medium">Pulsing Button</button>,
    active: true,
  },
}

export const Inactive: Story = {
  args: {
    children: <button className="px-6 py-3 bg-accent-primary text-white rounded-lg font-medium">Static Button</button>,
    active: false,
  },
}

export const CustomColor: Story = {
  args: {
    children: <button className="px-6 py-3 bg-accent-success text-white rounded-lg font-medium">Green Pulse</button>,
    color: '#00FFA3',
    active: true,
  },
}
