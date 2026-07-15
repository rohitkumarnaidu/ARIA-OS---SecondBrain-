import type { Meta, StoryObj } from '@storybook/react'
import { Breadcrumbs } from './Breadcrumbs'

const meta = {
  title: 'Layout/Breadcrumbs',
  component: Breadcrumbs,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof Breadcrumbs>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => (
    <div className="p-4 bg-background-card rounded-lg">
      <Breadcrumbs />
    </div>
  ),
}

export const WithOverrides: Story = {
  render: () => (
    <div className="p-4 bg-background-card rounded-lg">
      <Breadcrumbs overrides={{ 'tasks': 'My Tasks' }} />
    </div>
  ),
}

export const WithoutHome: Story = {
  render: () => (
    <div className="p-4 bg-background-card rounded-lg">
      <Breadcrumbs showHome={false} />
    </div>
  ),
}
