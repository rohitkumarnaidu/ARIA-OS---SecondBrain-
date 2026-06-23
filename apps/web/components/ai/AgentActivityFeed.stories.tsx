import type { Meta, StoryObj } from '@storybook/react'
import { AgentActivityFeed } from './AgentActivityFeed'

const meta: Meta<typeof AgentActivityFeed> = {
  title: 'AI/AgentActivityFeed',
  component: AgentActivityFeed,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof AgentActivityFeed>

export const Default: Story = {
  args: {
    activities: [
      { id: '1', agentName: 'Briefing Agent', action: 'Generated daily briefing', timestamp: '2 min ago', status: 'completed' },
      { id: '2', agentName: 'Memory Agent', action: 'Consolidated 12 memories', timestamp: '5 min ago', status: 'completed' },
      { id: '3', agentName: 'Opportunity Radar', action: 'Scanning for opportunities...', timestamp: 'Just now', status: 'running' },
      { id: '4', agentName: 'Learning Agent', action: 'Analyzed study patterns', timestamp: '1 hour ago', status: 'failed' },
      { id: '5', agentName: 'Sleep Agent', action: 'Generated wind-down routine', timestamp: '3 hours ago', status: 'completed' },
    ],
  },
}

export const Empty: Story = {
  args: { activities: [] },
}

export const Running: Story = {
  args: {
    activities: [
      { id: '1', agentName: 'Weekly Review Agent', action: 'Compiling weekly metrics...', timestamp: 'Just now', status: 'running' },
      { id: '2', agentName: 'Nudge Agent', action: 'Checking course deadlines...', timestamp: '30 sec ago', status: 'running' },
    ],
  },
}
