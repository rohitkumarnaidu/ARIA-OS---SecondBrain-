import type { Meta, StoryObj } from '@storybook/react'
import { FileText, Settings, User, LogOut, Mail, Calendar, Globe } from 'lucide-react'
import { Command } from './Command'

const meta: Meta<typeof Command> = {
  title: 'UI/Command',
  component: Command,
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
}

export default meta
type Story = StoryObj<typeof Command>

const sampleGroups = [
  {
    heading: 'Pages',
    items: [
      { id: '1', label: 'Dashboard', icon: FileText },
      { id: '2', label: 'Settings', icon: Settings, shortcut: ['G', 'S'] },
      { id: '3', label: 'Profile', icon: User, shortcut: ['G', 'P'] },
    ],
  },
  {
    heading: 'Actions',
    items: [
      { id: '4', label: 'New Task', description: 'Create a new task', icon: Calendar },
      { id: '5', label: 'Send Email', description: 'Compose a new email', icon: Mail },
      { id: '6', label: 'Browse Web', description: 'Open web browser', icon: Globe },
    ],
  },
  {
    heading: 'Account',
    items: [
      { id: '7', label: 'Log Out', icon: LogOut, shortcut: ['⌘', 'Q'] },
    ],
  },
]

export const Open: Story = {
  args: {
    open: true,
    groups: sampleGroups,
    placeholder: 'Search or type a command...',
  },
}

export const WithResults: Story = {
  args: {
    open: true,
    groups: [
      {
        heading: 'Pages',
        items: [
          { id: '1', label: 'Dashboard', icon: FileText, description: 'Main overview page' },
          { id: '2', label: 'Settings', icon: Settings },
        ],
      },
    ],
  },
}

export const Empty: Story = {
  args: {
    open: true,
    groups: [],
    placeholder: 'No commands available',
  },
}

export const WithDisabled: Story = {
  args: {
    open: true,
    groups: [
      {
        heading: 'Items',
        items: [
          { id: '1', label: 'Available Action', icon: FileText },
          { id: '2', label: 'Locked Feature', icon: Settings, disabled: true, description: 'Upgrade to access' },
        ],
      },
    ],
  },
}

export const Closed: Story = {
  args: {
    open: false,
    groups: sampleGroups,
  },
}
