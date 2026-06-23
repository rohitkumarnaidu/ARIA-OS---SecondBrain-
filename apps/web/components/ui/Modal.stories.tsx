import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Modal } from './Modal'
import { Button } from '@/components/ui/Button'

const meta: Meta<typeof Modal> = {
  title: 'UI/Modal',
  component: Modal,
  tags: ['autodocs'],
  parameters: {
    backgrounds: { default: 'dark' },
    layout: 'centered',
  },
  argTypes: {
    size: { control: 'select', options: ['sm', 'md', 'lg', 'xl', 'full'] },
  },
}

export default meta
type Story = StoryObj<typeof Modal>

export const Default: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    title: 'Dialog Title',
    size: 'md',
    children: <p className="text-text-secondary">This is the modal body content. It supports any React children.</p>,
  },
}

export const Small: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    title: 'Confirm',
    size: 'sm',
    children: (
      <div className="space-y-4">
        <p className="text-text-secondary">Are you sure?</p>
        <div className="flex justify-end gap-2">
          <Button variant="ghost">Cancel</Button>
          <Button variant="destructive">Delete</Button>
        </div>
      </div>
    ),
  },
}

export const Large: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    title: 'Form Details',
    size: 'lg',
    children: (
      <div className="space-y-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i}>
            <label className="block text-sm text-text-secondary mb-1">Field {i + 1}</label>
            <input className="w-full bg-background-dark border border-border rounded-lg px-3 py-2 text-text-primary" placeholder={`Field ${i + 1}`} />
          </div>
        ))}
      </div>
    ),
  },
}

export const ExtraLarge: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    title: 'Extended Settings',
    size: 'xl',
    children: (
      <div className="grid grid-cols-2 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i}>
            <label className="block text-sm text-text-secondary mb-1">Setting {i + 1}</label>
            <input className="w-full bg-background-dark border border-border rounded-lg px-3 py-2 text-text-primary" />
          </div>
        ))}
      </div>
    ),
  },
}

export const Fullscreen: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    title: 'Fullscreen View',
    size: 'full',
    children: (
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 9 }).map((_, i) => (
          <div key={i} className="h-32 rounded-lg bg-background-elevated flex items-center justify-center text-text-secondary">Panel {i + 1}</div>
        ))}
      </div>
    ),
  },
}

export const LongContentScroll: Story = {
  args: {
    isOpen: true,
    onClose: () => {},
    title: 'Terms & Conditions',
    size: 'lg',
    children: (
      <div className="text-text-secondary text-sm space-y-4">
        {Array.from({ length: 15 }).map((_, i) => (
          <p key={i}>Section {i + 1}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
        ))}
      </div>
    ),
  },
}
