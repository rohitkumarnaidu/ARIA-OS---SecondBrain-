import type { Meta, StoryObj } from '@storybook/react'
import { Dialog } from './Dialog'
import { Button } from './Button'

const meta = {
  title: 'UI/Dialog',
  component: Dialog,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
  argTypes: {
    size: { control: 'select', options: ['sm', 'md', 'lg', 'xl', 'full'] },
  },
} satisfies Meta<typeof Dialog>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Confirm Delete',
    children: <p className="text-sm text-text-secondary font-body">Are you sure you want to delete this item? This action cannot be undone.</p>,
    size: 'md',
  },
}

export const WithActions: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Confirm Delete',
    children: (
      <div className="space-y-4">
        <p className="text-sm text-text-secondary font-body">Are you sure you want to delete this task? This action cannot be undone.</p>
        <div className="flex items-center justify-end gap-3">
          <Button variant="ghost" size="sm" onClick={() => {}}>Cancel</Button>
          <Button variant="destructive" size="sm" onClick={() => {}}>Delete</Button>
        </div>
      </div>
    ),
    size: 'sm',
  },
}

export const FormDialog: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Create Task',
    children: (
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-foreground mb-1.5">Title</label>
          <input
            className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm"
            placeholder="Enter task title"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-foreground mb-1.5">Description</label>
          <textarea
            className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm resize-none"
            rows={3}
            placeholder="Optional description"
          />
        </div>
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button variant="ghost" size="sm" onClick={() => {}}>Cancel</Button>
          <Button variant="primary" size="sm" onClick={() => {}}>Create</Button>
        </div>
      </div>
    ),
    size: 'md',
  },
}

export const Small: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Quick Note',
    children: <p className="text-sm text-text-secondary font-body">A small dialog for brief confirmations.</p>,
    size: 'sm',
  },
}

export const Large: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Edit Profile',
    children: (
      <div className="space-y-4">
        <p className="text-sm text-text-secondary font-body">A larger dialog for more complex content like forms with multiple fields and longer descriptions that need more space to breathe.</p>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">First Name</label>
            <input className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm" placeholder="John" />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">Last Name</label>
            <input className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm" placeholder="Doe" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-foreground mb-1.5">Bio</label>
          <textarea className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm resize-none" rows={4} placeholder="Tell us about yourself" />
        </div>
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button variant="ghost" size="sm" onClick={() => {}}>Cancel</Button>
          <Button variant="primary" size="sm" onClick={() => {}}>Save Changes</Button>
        </div>
      </div>
    ),
    size: 'lg',
  },
}

export const FullWidth: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Full Width Dialog',
    children: <p className="text-sm text-text-secondary font-body">This dialog takes the full width of the viewport with margins.</p>,
    size: 'full',
  },
}
