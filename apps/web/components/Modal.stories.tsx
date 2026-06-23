import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Modal } from './Modal'
import { Button } from '@/components/ui/Button'

const meta: Meta<typeof Modal> = {
  title: 'Components/Modal',
  component: Modal,
  tags: ['autodocs'],
  parameters: {
    backgrounds: { default: 'dark' },
    layout: 'centered',
  },
}

export default meta
type Story = StoryObj<typeof Modal>

export const Default: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    title: 'Confirm Action',
    children: <p className="text-text-secondary">Are you sure you want to proceed with this action?</p>,
  },
}

export const WithFormContent: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    title: 'Edit Profile',
    children: (
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-text-secondary mb-1">Name</label>
          <input className="w-full bg-background-dark border border-border rounded-lg px-3 py-2 text-text-primary" defaultValue="John Doe" />
        </div>
        <div>
          <label className="block text-sm text-text-secondary mb-1">Email</label>
          <input className="w-full bg-background-dark border border-border rounded-lg px-3 py-2 text-text-primary" defaultValue="john@example.com" />
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="ghost">Cancel</Button>
          <Button variant="primary">Save</Button>
        </div>
      </div>
    ),
  },
}

export const LongContent: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    title: 'Terms of Service',
    children: (
      <div className="text-text-secondary text-sm space-y-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <p key={i}>Section {i + 1}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        ))}
      </div>
    ),
  },
}
