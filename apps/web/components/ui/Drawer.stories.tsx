import type { Meta, StoryObj } from '@storybook/react'
import { Drawer } from './Drawer'
import { Button } from './Button'

const meta = {
  title: 'UI/Drawer',
  component: Drawer,
  parameters: { layout: 'fullscreen' },
  tags: ['autodocs'],
} satisfies Meta<typeof Drawer>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Task Details',
    children: (
      <div className="space-y-4">
        <p className="text-sm text-text-secondary font-body">Review the PR for the new dashboard feature. Make sure all tests pass and the UI matches the design spec.</p>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded-full text-[11px] font-mono bg-accent-primary/10 text-accent-secondary border border-accent-primary/20">High Priority</span>
          <span className="px-2 py-0.5 rounded-full text-[11px] font-mono bg-accent-warning/10 text-accent-warning border border-accent-warning/20">In Progress</span>
        </div>
        <Button variant="primary" size="sm" onClick={() => {}}>Mark Complete</Button>
      </div>
    ),
  },
}

export const WithoutTitle: Story = {
  args: {
    open: true,
    onClose: () => {},
    children: (
      <p className="text-sm text-text-secondary font-body">A drawer without a title header.</p>
    ),
  },
}

export const ScrollingContent: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Release Notes v2.4.0',
    children: (
      <div className="space-y-6">
        {Array.from({ length: 20 }).map((_, i) => (
          <div key={i}>
            <h3 className="text-sm font-medium text-foreground mb-1">Feature #{i + 1}</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            </p>
          </div>
        ))}
      </div>
    ),
  },
}

export const CustomSnapPoints: Story = {
  args: {
    open: true,
    onClose: () => {},
    title: 'Draggable Drawer',
    children: (
      <p className="text-sm text-text-secondary font-body">
        Drag the handle to resize this drawer. It snaps to predefined heights (50%, 75%, 100%).
      </p>
    ),
    snapPoints: [50, 75, 100],
  },
}
