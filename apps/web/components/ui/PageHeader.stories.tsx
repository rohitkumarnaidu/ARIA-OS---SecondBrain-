import type { Meta, StoryObj } from '@storybook/react'
import { Plus, Settings } from 'lucide-react'
import { Button } from './Button'
import { PageHeader } from './PageHeader'

const meta = {
  title: 'UI/PageHeader',
  component: PageHeader,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof PageHeader>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    title: 'Tasks',
    description: 'Manage and track your daily tasks.',
  },
}

export const WithActions: Story = {
  args: {
    title: 'Tasks',
    description: 'Manage and track your daily tasks.',
    actions: (
      <>
        <Button variant="primary" size="sm">
          <Plus size={16} />
          Add Task
        </Button>
        <Button variant="ghost" size="sm">
          <Settings size={16} />
        </Button>
      </>
    ),
  },
}

export const WithBreadcrumb: Story = {
  args: {
    title: 'Edit Profile',
    description: 'Update your personal information and preferences.',
    breadcrumb: [
      { label: 'Home', href: '/' },
      { label: 'Settings', href: '/settings' },
      { label: 'Profile' },
    ],
  },
}

export const FullHeader: Story = {
  args: {
    title: 'Weekly Review',
    description: 'Review your progress, accomplishments, and areas for improvement this week.',
    breadcrumb: [
      { label: 'Dashboard', href: '/' },
      { label: 'Reports', href: '/reports' },
      { label: 'Weekly Review' },
    ],
    actions: (
      <>
        <Button variant="secondary" size="sm">Export</Button>
        <Button variant="primary" size="sm">Share</Button>
      </>
    ),
  },
}

export const TitleOnly: Story = {
  args: {
    title: 'Dashboard',
  },
}

export const DeepBreadcrumb: Story = {
  args: {
    title: 'Project Settings',
    breadcrumb: [
      { label: 'Home', href: '/' },
      { label: 'Projects', href: '/projects' },
      { label: 'My App', href: '/projects/my-app' },
      { label: 'Settings' },
    ],
  },
}

export const LongTitle: Story = {
  args: {
    title: 'This is a very long page header title that should be truncated gracefully on smaller screens',
    description: 'And this is a correspondingly long description that provides additional context about what this page contains and what the user can do here.',
    actions: (
      <Button variant="primary" size="sm">Action</Button>
    ),
  },
}
