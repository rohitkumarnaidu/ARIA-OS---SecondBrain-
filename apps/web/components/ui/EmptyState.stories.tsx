import type { Meta, StoryObj } from '@storybook/react'
import { Inbox, Search, FolderOpen } from 'lucide-react'
import { EmptyState } from './EmptyState'

const meta: Meta<typeof EmptyState> = {
  title: 'UI/EmptyState',
  component: EmptyState,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof EmptyState>

export const Default: Story = {
  args: {
    title: 'No items found',
    description: 'Get started by creating your first item.',
  },
}

export const WithIcon: Story = {
  args: {
    title: 'Inbox zero',
    description: "You're all caught up. No new messages.",
    icon: <Inbox size={40} />,
  },
}

export const WithAction: Story = {
  args: {
    title: 'No tasks yet',
    description: 'Create your first task to get started.',
    icon: <FolderOpen size={40} />,
    action: { label: 'Create Task', onClick: () => {} },
  },
}

export const SearchMode: Story = {
  args: {
    title: 'No results found',
    description: 'Try adjusting your search terms or filters.',
    icon: <Search size={40} />,
  },
}

export const Compact: Story = {
  args: {
    title: 'Nothing here',
    description: 'This section is empty.',
    action: { label: 'Add Item', onClick: () => {} },
  },
}
