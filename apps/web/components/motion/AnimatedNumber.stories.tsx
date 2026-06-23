import type { Meta, StoryObj } from '@storybook/react'
import { AnimatedNumber } from './AnimatedNumber'

const meta: Meta<typeof AnimatedNumber> = {
  title: 'Motion/AnimatedNumber',
  component: AnimatedNumber,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof AnimatedNumber>

export const Default: Story = {
  args: { value: 42 },
}

export const LargeNumber: Story = {
  args: { value: 1234567, formatFn: (n) => n.toLocaleString() },
}

export const Percentage: Story = {
  args: { value: 87, formatFn: (n) => `${n}%` },
}

export const Currency: Story = {
  args: { value: 2499, formatFn: (n) => `$${(n / 100).toFixed(2)}` },
}

export const FastAnimation: Story = {
  args: { value: 100, duration: 0.5 },
}

export const SlowAnimation: Story = {
  args: { value: 100, duration: 3 },
}
