import type { Meta, StoryObj } from '@storybook/react'
import { Plus, Upload, Search } from 'lucide-react'
import { EmptyCanvas } from './EmptyCanvas'

const meta = {
  title: 'UI/EmptyCanvas',
  component: EmptyCanvas,
  parameters: { layout: 'fullscreen' },
  tags: ['autodocs'],
} satisfies Meta<typeof EmptyCanvas>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    title: 'No tasks yet',
    description: 'Get started by creating your first task. Tasks help you track what needs to be done.',
  },
}

export const WithAction: Story = {
  args: {
    title: 'No tasks yet',
    description: 'Get started by creating your first task. Tasks help you track what needs to be done.',
    actions: [{ label: 'Create Task', primary: true, onClick: () => alert('Clicked!') }],
  },
}

export const WithBadge: Story = {
  args: {
    title: 'No tasks yet',
    description: 'Get started by creating your first task.',
    badge: 'Getting Started',
    actions: [{ label: 'Create Task', primary: true, onClick: () => {} }],
  },
}

export const MultipleActions: Story = {
  args: {
    title: 'Empty project',
    description: 'This project has no items yet. Add files or create content to get started.',
    badge: 'Project',
    actions: [
      { label: 'Create File', primary: true, onClick: () => {} },
      { label: 'Import', onClick: () => {} },
    ],
  },
}

export const CustomIcon: Story = {
  args: {
    icon: <Upload size={28} className="text-accent-primary" />,
    title: 'No uploads yet',
    description: 'Drag and drop files here or click to browse your device.',
    actions: [{ label: 'Upload Files', primary: true, onClick: () => {} }],
  },
}

export const SearchEmpty: Story = {
  args: {
    icon: <Search size={28} className="text-accent-primary" />,
    title: 'No results found',
    description: 'Try adjusting your search terms or filters to find what you are looking for.',
    actions: [{ label: 'Clear Filters', onClick: () => {} }],
  },
}

export const LongDescription: Story = {
  args: {
    title: 'Welcome to your dashboard',
    description: 'This is your personal command center. You can manage tasks, track habits, review your weekly progress, and much more. Start by exploring the modules in the sidebar or create your first item.',
    actions: [
      { label: 'Get Started', primary: true, onClick: () => {} },
      { label: 'Learn More', onClick: () => {} },
    ],
  },
}
