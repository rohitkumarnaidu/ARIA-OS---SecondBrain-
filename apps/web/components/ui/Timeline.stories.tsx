import type { Meta, StoryObj } from '@storybook/react'
import { Timeline } from './Timeline'

const meta: Meta<typeof Timeline> = {
  title: 'UI/Timeline',
  component: Timeline,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof Timeline>

const sampleItems = [
  { id: '1', title: 'Project Kickoff', description: 'Initial planning and team alignment', date: 'Jun 1', status: 'completed' as const },
  { id: '2', title: 'Design Phase', description: 'Wireframes and mockups', date: 'Jun 5', status: 'completed' as const },
  { id: '3', title: 'Development Sprint', description: 'Core feature implementation', date: 'Jun 12', status: 'current' as const },
  { id: '4', title: 'Testing & QA', description: 'Integration and unit testing', date: 'Jun 19', status: 'upcoming' as const },
  { id: '5', title: 'Deployment', description: 'Production release', date: 'Jun 26', status: 'upcoming' as const },
]

export const Vertical: Story = {
  args: { items: sampleItems },
}

export const Horizontal: Story = {
  args: { items: sampleItems, orientation: 'horizontal' },
}

export const AllCompleted: Story = {
  args: {
    items: [
      { id: '1', title: 'Research', description: 'Market analysis complete', date: 'May 1', status: 'completed' },
      { id: '2', title: 'Planning', description: 'Scope defined', date: 'May 8', status: 'completed' },
      { id: '3', title: 'Execution', description: 'All tasks delivered', date: 'May 15', status: 'completed' },
    ],
  },
}

export const WithSkipped: Story = {
  args: {
    items: [
      { id: '1', title: 'Phase 1', status: 'completed' },
      { id: '2', title: 'Phase 2', status: 'skipped' },
      { id: '3', title: 'Phase 3', status: 'current' },
    ],
  },
}

export const SingleItem: Story = {
  args: {
    items: [
      { id: '1', title: 'Current Task', status: 'current' },
    ],
  },
}
