import type { Meta, StoryObj } from '@storybook/react'
import { AIInsightCard } from './AIInsightCard'

const meta: Meta<typeof AIInsightCard> = {
  title: 'AI/AIInsightCard',
  component: AIInsightCard,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof AIInsightCard>

export const Recommendation: Story = {
  args: {
    type: 'recommendation',
    title: 'Optimize your morning routine',
    description: 'Based on your sleep data, shifting your wake time 30 minutes earlier could improve your deep sleep phase by 15%.',
    action: { label: 'View Details', onClick: () => {} },
  },
}

export const Insight: Story = {
  args: {
    type: 'insight',
    title: 'Productivity peak detected',
    description: 'Your focus hours are consistently between 9-11 AM. Schedule your most demanding tasks during this window.',
    action: { label: 'Adjust Schedule', onClick: () => {} },
  },
}

export const Alert: Story = {
  args: {
    type: 'alert',
    title: 'Task deadline approaching',
    description: 'You have 3 tasks due tomorrow. Consider reprioritizing your evening to avoid last-minute rush.',
    action: { label: 'Review Tasks', onClick: () => {} },
  },
}

export const RecommendationNoAction: Story = {
  args: {
    type: 'recommendation',
    title: 'Try focused sprints',
    description: 'Short 25-minute work sessions with 5-minute breaks could boost your output by 22%.',
  },
}

export const InsightNoAction: Story = {
  args: {
    type: 'insight',
    title: 'Learning pattern detected',
    description: 'You retain information best when studying in 45-minute blocks with active recall.',
  },
}

export const AlertNoAction: Story = {
  args: {
    type: 'alert',
    title: 'Streak at risk',
    description: 'You haven\'t logged a habit in 3 days. A quick 5-minute session can keep your streak alive.',
  },
}

export const LongContent: Story = {
  args: {
    type: 'insight',
    title: 'Comprehensive weekly analysis of your productivity patterns and learning efficiency metrics across all tracked domains',
    description: 'This detailed analysis covers your task completion rates, focus session quality, learning retention scores, and energy level correlations. Key findings suggest that your optimal cognitive performance occurs in 90-minute blocks with strategic breaks.',
    action: { label: 'View Full Report', onClick: () => {} },
  },
}
