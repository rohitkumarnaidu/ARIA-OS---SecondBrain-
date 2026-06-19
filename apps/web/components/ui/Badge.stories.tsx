import type { Meta, StoryObj } from '@storybook/react'
import { Badge } from './Badge'

const meta: Meta<typeof Badge> = {
  title: 'UI/Badge',
  component: Badge,
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['default', 'success', 'warning', 'danger', 'info'] },
  },
}

export default meta
type Story = StoryObj<typeof Badge>

export const Default: Story = {
  args: { variant: 'default', children: 'Default' },
}

export const Success: Story = {
  args: { variant: 'success', children: 'Completed' },
}

export const Warning: Story = {
  args: { variant: 'warning', children: 'Pending' },
}

export const Danger: Story = {
  args: { variant: 'error', children: 'Overdue' },
}

export const Info: Story = {
  args: { variant: 'info', children: 'In Progress' },
}
