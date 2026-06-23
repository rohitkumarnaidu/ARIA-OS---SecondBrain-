import type { Meta, StoryObj } from '@storybook/react'
import { AIDock } from './AIDock'

const meta: Meta<typeof AIDock> = {
  title: 'AI/AIDock',
  component: AIDock,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof AIDock>

export const Default: Story = {
  args: {},
}
