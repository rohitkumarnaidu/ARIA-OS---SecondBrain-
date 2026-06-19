import type { Meta, StoryObj } from '@storybook/react'
import { AIUndo } from './AIUndo'

const meta: Meta<typeof AIUndo> = {
  title: 'AI/AIUndo',
  component: AIUndo,
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
}

export default meta
type Story = StoryObj<typeof AIUndo>

export const Default: Story = {
  args: {
    message: 'Task moved to completed',
    onUndo: () => alert('Undo clicked'),
    onExpired: () => console.log('Expired'),
    duration: 10000,
  },
}

export const LongMessage: Story = {
  args: {
    message: 'Your weekly review has been generated and all tasks have been reorganized based on priority',
    onUndo: () => alert('Undo clicked'),
    onExpired: () => console.log('Expired'),
    duration: 10000,
  },
}

export const ShortDuration: Story = {
  args: {
    message: 'Habit log updated',
    onUndo: () => alert('Undo clicked'),
    onExpired: () => console.log('Expired'),
    duration: 3000,
  },
}
