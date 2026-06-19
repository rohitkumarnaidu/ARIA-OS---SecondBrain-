import type { Meta, StoryObj } from '@storybook/react'
import { Avatar } from './Avatar'

const meta: Meta<typeof Avatar> = {
  title: 'UI/Avatar',
  component: Avatar,
  tags: ['autodocs'],
  argTypes: {
    size: { control: 'select', options: ['sm', 'md', 'lg', 'xl'] },
    status: { control: 'select', options: ['online', 'away', 'busy', 'offline', undefined] },
  },
}

export default meta
type Story = StoryObj<typeof Avatar>

export const WithImage: Story = {
  args: {
    src: 'https://i.pravatar.cc/150?u=alice',
    name: 'Alice Johnson',
    size: 'md',
  },
}

export const Initials: Story = {
  args: {
    name: 'John Doe',
    size: 'md',
  },
}

export const SingleInitial: Story = {
  args: {
    name: 'Alex',
    size: 'md',
  },
}

export const Online: Story = {
  args: {
    src: 'https://i.pravatar.cc/150?u=bob',
    name: 'Bob Smith',
    status: 'online',
    size: 'md',
  },
}

export const Away: Story = {
  args: {
    src: 'https://i.pravatar.cc/150?u=carol',
    name: 'Carol Williams',
    status: 'away',
    size: 'md',
  },
}

export const Busy: Story = {
  args: {
    name: 'Dave Brown',
    status: 'busy',
    size: 'lg',
  },
}

export const Offline: Story = {
  args: {
    name: 'Eve Davis',
    status: 'offline',
    size: 'sm',
  },
}

export const Small: Story = {
  args: {
    name: 'Frank Miller',
    size: 'sm',
  },
}

export const Large: Story = {
  args: {
    src: 'https://i.pravatar.cc/150?u=grace',
    name: 'Grace Lee',
    size: 'xl',
    status: 'online',
  },
}

export const BrokenImage: Story = {
  args: {
    src: 'https://invalid-url.example.com/photo.jpg',
    name: 'Henry Wilson',
    size: 'md',
  },
}
