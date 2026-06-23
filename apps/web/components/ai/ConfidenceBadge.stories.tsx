import type { Meta, StoryObj } from '@storybook/react'
import { ConfidenceBadge } from './ConfidenceBadge'

const meta: Meta<typeof ConfidenceBadge> = {
  title: 'AI/ConfidenceBadge',
  component: ConfidenceBadge,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof ConfidenceBadge>

export const HighConfidence: Story = {
  args: { value: 0.92, label: 'High confidence', size: 'md' },
}

export const MediumConfidence: Story = {
  args: { value: 0.65, label: 'Medium confidence', size: 'md' },
}

export const LowConfidence: Story = {
  args: { value: 0.35, label: 'Low confidence', size: 'md' },
}

export const Small: Story = {
  args: { value: 0.88, size: 'sm' },
}

export const Large: Story = {
  args: { value: 0.75, label: 'Moderate', size: 'lg' },
}

export const NoTooltip: Story = {
  args: { value: 0.95, showTooltip: false },
}
