import type { Meta, StoryObj } from '@storybook/react'
import RoadmapEditor from './RoadmapEditor'

const meta: Meta<typeof RoadmapEditor> = {
  title: 'Components/RoadmapEditor',
  component: RoadmapEditor,
  tags: ['autodocs'],
  parameters: {
    backgrounds: { default: 'dark' },
    layout: 'padded',
  },
}

export default meta
type Story = StoryObj<typeof RoadmapEditor>

export const Default: Story = {
  args: {
    goalId: 'goal-1',
    onSave: (nodes, edges) => console.log('Saved:', { nodes, edges }),
  },
}

export const WithCustomData: Story = {
  args: {
    goalId: 'goal-2',
    initialNodes: [
      { id: 'n1', type: 'goal', position: { x: 250, y: 0 }, data: { title: 'Build Portfolio', type: 'goal', status: 'in_progress', estimated_hours: 60 } },
      { id: 'n2', type: 'milestone', position: { x: 100, y: 100 }, data: { title: 'Design', type: 'milestone', status: 'completed' } },
      { id: 'n3', type: 'task', position: { x: 50, y: 200 }, data: { title: 'Figma mockups', type: 'task', status: 'completed', estimated_hours: 12 } },
    ],
    initialEdges: [
      { id: 'e1-2', source: 'n1', target: 'n2', animated: true, markerEnd: { type: 'arrowclosed' } },
      { id: 'e2-3', source: 'n2', target: 'n3', markerEnd: { type: 'arrowclosed' } },
    ],
    onSave: (nodes, edges) => console.log('Saved:', { nodes, edges }),
  },
}
