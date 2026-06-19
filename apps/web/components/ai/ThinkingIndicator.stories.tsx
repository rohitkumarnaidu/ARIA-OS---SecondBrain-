import type { Meta, StoryObj } from '@storybook/react'
import { ThinkingIndicator } from './ThinkingIndicator'

const meta: Meta<typeof ThinkingIndicator> = {
  title: 'AI/ThinkingIndicator',
  component: ThinkingIndicator,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof ThinkingIndicator>

const thinkingMessages = [
  'Analyzing your data...',
  'Searching for patterns...',
  'Generating insights...',
  'Almost done...',
]

export const Idle: Story = {
  args: {
    state: 'idle',
  },
}

export const Thinking: Story = {
  args: {
    state: 'thinking',
    messages: thinkingMessages,
  },
}

export const ThinkingNoMessages: Story = {
  args: {
    state: 'thinking',
  },
}

export const Complete: Story = {
  args: {
    state: 'complete',
  },
}

export const Error: Story = {
  args: {
    state: 'error',
  },
}

export const Cancelled: Story = {
  args: {
    state: 'cancelled',
  },
}
