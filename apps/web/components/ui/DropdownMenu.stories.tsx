import type { Meta, StoryObj } from '@storybook/react'
import { Settings, User, LogOut, Edit, Copy, Trash2, Share2, Download, HelpCircle } from 'lucide-react'
import { DropdownMenu } from './DropdownMenu'
import { Button } from './Button'

const meta: Meta<typeof DropdownMenu> = {
  title: 'UI/DropdownMenu',
  component: DropdownMenu,
  tags: ['autodocs'],
  argTypes: {
    align: { control: 'select', options: ['start', 'end'] },
  },
}

export default meta
type Story = StoryObj<typeof DropdownMenu>

export const SimpleItems: Story = {
  args: {
    trigger: <Button variant="secondary">Actions</Button>,
    items: [
      { label: 'Edit', icon: Edit, onClick: () => {} },
      { label: 'Duplicate', icon: Copy, onClick: () => {} },
      { label: 'Share', icon: Share2, onClick: () => {} },
    ],
  },
}

export const WithDividers: Story = {
  args: {
    trigger: <Button variant="secondary">More</Button>,
    items: [
      { label: 'Edit', icon: Edit, onClick: () => {} },
      { label: 'Duplicate', icon: Copy, onClick: () => {} },
      { divider: true, label: '', onClick: () => {} },
      { label: 'Download', icon: Download, onClick: () => {} },
      { divider: true, label: '', onClick: () => {} },
      { label: 'Delete', icon: Trash2, onClick: () => {} },
    ],
  },
}

export const WithDisabled: Story = {
  args: {
    trigger: <Button variant="secondary">Manage</Button>,
    items: [
      { label: 'Edit', icon: Edit, onClick: () => {} },
      { label: 'Duplicate', icon: Copy, onClick: () => {}, disabled: true },
      { divider: true, label: '', onClick: () => {} },
      { label: 'Delete', icon: Trash2, onClick: () => {}, disabled: true },
    ],
  },
}

export const WithIcons: Story = {
  args: {
    trigger: <Button variant="secondary">Profile</Button>,
    items: [
      { label: 'Profile', icon: User, onClick: () => {} },
      { label: 'Settings', icon: Settings, onClick: () => {} },
      { divider: true, label: '', onClick: () => {} },
      { label: 'Help', icon: HelpCircle, onClick: () => {} },
      { divider: true, label: '', onClick: () => {} },
      { label: 'Log out', icon: LogOut, onClick: () => {} },
    ],
  },
}

export const AlignEnd: Story = {
  args: {
    trigger: <Button variant="secondary">Aligned right</Button>,
    align: 'end',
    items: [
      { label: 'Edit', icon: Edit, onClick: () => {} },
      { label: 'Delete', icon: Trash2, onClick: () => {} },
    ],
  },
}

export const ManyItems: Story = {
  args: {
    trigger: <Button variant="secondary">All actions</Button>,
    items: Array.from({ length: 12 }, (_, i) => ({
      label: `Action ${i + 1}`,
      icon: i % 2 === 0 ? Edit : Copy,
      onClick: () => {},
      divider: i === 5,
    })),
  },
}
