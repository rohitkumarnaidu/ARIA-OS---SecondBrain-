import type { Meta, StoryObj } from '@storybook/react'
import { AIActionConfirm } from './AIActionConfirm'

const meta: Meta<typeof AIActionConfirm> = {
  title: 'AI/AIActionConfirm',
  component: AIActionConfirm,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof AIActionConfirm>

export const Open: Story = {
  args: {
    open: true,
    title: 'Reschedule task?',
    description: 'The AI suggests moving "Review PR #42" from tomorrow to Friday at 2 PM to balance your workload.',
    onConfirm: async () => {},
    onCancel: () => {},
  },
}

export const Urgent: Story = {
  args: {
    open: true,
    title: 'Overlapping deadlines detected',
    description: 'You have 3 tasks due tomorrow. AI recommends postponing "Update documentation" to next Monday.',
    onConfirm: async () => {},
    onCancel: () => {},
  },
}

export const Closed: Story = {
  args: {
    open: false,
    title: '',
    description: '',
    onConfirm: async () => {},
    onCancel: () => {},
  },
}
