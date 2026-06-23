import type { Meta, StoryObj } from '@storybook/react'
import { SuggestionChips } from './SuggestionChips'

const meta: Meta<typeof SuggestionChips> = {
  title: 'AI/SuggestionChips',
  component: SuggestionChips,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof SuggestionChips>

export const Default: Story = {
  args: {
    suggestions: [
      { id: '1', label: 'Summarize my day' },
      { id: '2', label: 'What tasks are overdue?' },
      { id: '3', label: 'Suggest a focus session' },
    ],
    onSelect: (id: string) => console.log('Selected:', id),
  },
}

export const WithIcons: Story = {
  args: {
    suggestions: [
      { id: '1', label: 'Weekly Review', icon: <span>📊</span> },
      { id: '2', label: 'Sleep Analysis', icon: <span>🌙</span> },
      { id: '3', label: 'Habit Streak', icon: <span>🔥</span> },
      { id: '4', label: 'Task Report', icon: <span>📋</span> },
    ],
    onSelect: (id: string) => console.log('Selected:', id),
  },
}

export const ManySuggestions: Story = {
  args: {
    suggestions: [
      { id: '1', label: 'Create a task' },
      { id: '2', label: 'Log a habit' },
      { id: '3', label: 'Track sleep' },
      { id: '4', label: 'Add income' },
      { id: '5', label: 'Review goals' },
      { id: '6', label: 'Check calendar' },
    ],
    onSelect: (id: string) => console.log('Selected:', id),
  },
}
