import type { Meta, StoryObj } from '@storybook/react'
import { Sheet } from './Sheet'
import { Button } from './Button'

const meta = {
  title: 'UI/Sheet',
  component: Sheet,
  parameters: { layout: 'fullscreen' },
  tags: ['autodocs'],
  argTypes: {
    width: { control: 'select', options: ['sm', 'md', 'lg'] },
  },
} satisfies Meta<typeof Sheet>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Notifications',
    children: (
      <div className="space-y-4">
        {[
          { title: 'Task completed', desc: 'You completed "Review PR #42"', time: '2m ago' },
          { title: 'New message', desc: 'Alice sent you a message', time: '15m ago' },
          { title: 'Reminder', desc: 'Weekly review is due tomorrow', time: '1h ago' },
        ].map((item, i) => (
          <div key={i} className="p-3 rounded-lg bg-background-elevated border border-border">
            <p className="text-sm font-medium text-foreground">{item.title}</p>
            <p className="text-xs text-text-secondary mt-0.5">{item.desc}</p>
            <p className="text-[11px] text-text-tertiary mt-1">{item.time}</p>
          </div>
        ))}
      </div>
    ),
    width: 'md',
  },
}

export const SmallWidth: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Sheet',
    children: <p className="text-sm text-text-secondary font-body">A narrow sheet for compact panels.</p>,
    width: 'sm',
  },
}

export const LargeWidth: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Settings',
    children: (
      <div className="space-y-6">
        {['Profile', 'Account', 'Notifications', 'Privacy', 'Appearance'].map((section) => (
          <div key={section} className="p-3 rounded-lg bg-background-elevated border border-border">
            <p className="text-sm font-medium text-foreground">{section}</p>
            <p className="text-xs text-text-secondary mt-1">Configuration options for {section.toLowerCase()}.</p>
          </div>
        ))}
      </div>
    ),
    width: 'lg',
  },
}

export const WithoutTitle: Story = {
  args: {
    open: true,
    onClose: () => {},
    children: (
      <p className="text-sm text-text-secondary font-body">A sheet panel without a header title.</p>
    ),
    width: 'md',
  },
}

export const WithActions: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Filter Options',
    children: (
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">Status</label>
          <div className="space-y-2">
            {['All', 'Active', 'Completed', 'Archived'].map((s) => (
              <label key={s} className="flex items-center gap-2 text-sm text-text-secondary cursor-pointer">
                <input type="radio" name="status" className="accent-accent-primary" />
                {s}
              </label>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-3 pt-4 border-t border-border">
          <Button variant="ghost" size="sm" onClick={() => {}}>Reset</Button>
          <Button variant="primary" size="sm" onClick={() => {}}>Apply</Button>
        </div>
      </div>
    ),
    width: 'sm',
  },
}
