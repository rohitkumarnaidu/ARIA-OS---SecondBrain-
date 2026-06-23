import type { Meta, StoryObj } from '@storybook/react'
import { AIAssistant } from './AIAssistant'

const meta: Meta<typeof AIAssistant> = {
  title: 'AI/AIAssistant',
  component: AIAssistant,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof AIAssistant>

export const Open: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    children: <div className="p-4 text-sm text-text-secondary">AI Assistant panel content goes here.</div>,
  },
}

export const OpenWithSuggestions: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    suggestions: ['Summarize my day', 'Find pending tasks', 'Check deadlines'],
    onSuggestionClick: (s: string) => console.log(s),
    children: <div className="p-4 text-sm text-text-secondary">Ask me anything about your tasks, habits, or productivity.</div>,
  },
}

export const Closed: Story = {
  args: {
    isOpen: false,
    onClose: () => {},
  },
}
