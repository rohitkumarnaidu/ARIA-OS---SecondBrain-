import type { Meta, StoryObj } from '@storybook/react'
import { Settings, User, LogOut } from 'lucide-react'
import { Popover } from './Popover'
import { Button } from './Button'

const meta = {
  title: 'UI/Popover',
  component: Popover,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
  argTypes: {
    side: { control: 'select', options: ['top', 'bottom', 'left', 'right'] },
    align: { control: 'select', options: ['start', 'center', 'end'] },
  },
} satisfies Meta<typeof Popover>

export default meta
type Story = StoryObj<typeof meta>

export const Bottom: Story = {
  args: {
    open: true,
    onOpenChange: () => {},
    side: 'bottom',
    align: 'center',
    trigger: <Button variant="primary" size="sm">Open Popover</Button>,
    children: (
      <div className="space-y-1">
        <p className="text-sm font-medium text-foreground">Account</p>
        <p className="text-xs text-text-secondary">Manage your account settings</p>
      </div>
    ),
  },
}

export const Top: Story = {
  args: {
    open: true,
    onOpenChange: () => {},
    side: 'top',
    align: 'center',
    trigger: <Button variant="primary" size="sm">Open Popover</Button>,
    children: (
      <p className="text-sm text-text-secondary font-body">Popover content displayed above the trigger.</p>
    ),
  },
}

export const Left: Story = {
  args: {
    open: true,
    onOpenChange: () => {},
    side: 'left',
    align: 'center',
    trigger: <Button variant="primary" size="sm">Open Popover</Button>,
    children: (
      <p className="text-sm text-text-secondary font-body">Popover content displayed to the left.</p>
    ),
  },
}

export const Right: Story = {
  args: {
    open: true,
    onOpenChange: () => {},
    side: 'right',
    align: 'center',
    trigger: <Button variant="primary" size="sm">Open Popover</Button>,
    children: (
      <p className="text-sm text-text-secondary font-body">Popover content displayed to the right.</p>
    ),
  },
}

export const AlignStart: Story = {
  args: {
    open: true,
    onOpenChange: () => {},
    side: 'bottom',
    align: 'start',
    trigger: <Button variant="primary" size="sm">Open Popover</Button>,
    children: (
      <p className="text-sm text-text-secondary font-body">Aligned to the start edge of the trigger.</p>
    ),
  },
}

export const AlignEnd: Story = {
  args: {
    open: true,
    onOpenChange: () => {},
    side: 'bottom',
    align: 'end',
    trigger: <Button variant="primary" size="sm">Open Popover</Button>,
    children: (
      <p className="text-sm text-text-secondary font-body">Aligned to the end edge of the trigger.</p>
    ),
  },
}

export const MenuPopover: Story = {
  args: {
    open: true,
    onOpenChange: () => {},
    side: 'bottom',
    align: 'end',
    trigger: <Button variant="ghost" size="sm"><Settings size={18} /></Button>,
    children: (
      <div className="space-y-1 -m-1">
        {[
          { icon: User, label: 'Profile' },
          { icon: Settings, label: 'Settings' },
          { icon: LogOut, label: 'Sign out' },
        ].map(({ icon: Icon, label }) => (
          <button
            key={label}
            className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-foreground hover:bg-background-elevated transition-colors"
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>
    ),
  },
}

export const RichContent: Story = {
  args: {
    open: true,
    onOpenChange: () => {},
    side: 'bottom',
    align: 'center',
    trigger: <Button variant="primary" size="sm">Notifications</Button>,
    children: (
      <div className="space-y-3 min-w-[240px]">
        <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Today</p>
        <div className="space-y-2">
          {[
            { title: 'Task completed', time: '2m ago' },
            { title: 'New comment on PR', time: '15m ago' },
            { title: 'Meeting reminder', time: '1h ago' },
          ].map((n, i) => (
            <div key={i} className="p-2 -mx-1 rounded-lg hover:bg-background-elevated transition-colors cursor-pointer">
              <p className="text-sm text-foreground">{n.title}</p>
              <p className="text-[11px] text-text-tertiary">{n.time}</p>
            </div>
          ))}
        </div>
      </div>
    ),
  },
}
