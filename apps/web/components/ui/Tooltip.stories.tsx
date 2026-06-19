import type { Meta, StoryObj } from '@storybook/react'
import { Tooltip } from './Tooltip'
import { Button } from './Button'

const meta: Meta<typeof Tooltip> = {
  title: 'UI/Tooltip',
  component: Tooltip,
  tags: ['autodocs'],
  argTypes: {
    side: { control: 'select', options: ['top', 'bottom', 'left', 'right'] },
    delay: { control: 'number' },
    hideDelay: { control: 'number' },
  },
}

export default meta
type Story = StoryObj<typeof Tooltip>

export const Top: Story = {
  args: {
    content: 'Tooltip on top',
    side: 'top',
    children: <Button variant="secondary">Hover me (top)</Button>,
  },
}

export const Bottom: Story = {
  args: {
    content: 'Tooltip on bottom',
    side: 'bottom',
    children: <Button variant="secondary">Hover me (bottom)</Button>,
  },
}

export const Left: Story = {
  args: {
    content: 'Tooltip on left',
    side: 'left',
    children: <Button variant="secondary">Hover me (left)</Button>,
  },
}

export const Right: Story = {
  args: {
    content: 'Tooltip on right',
    side: 'right',
    children: <Button variant="secondary">Hover me (right)</Button>,
  },
}

export const Immediate: Story = {
  args: {
    content: 'Appears instantly',
    delay: 0,
    children: <Button variant="secondary">No delay</Button>,
  },
}

export const SlowDelay: Story = {
  args: {
    content: 'Takes 1 second',
    delay: 1000,
    children: <Button variant="secondary">1s delay</Button>,
  },
}

export const RichContent: Story = {
  args: {
    content: (
      <div className="space-y-1">
        <p className="font-semibold">Details</p>
        <p className="text-xs opacity-70">Extra information here</p>
      </div>
    ),
    children: <Button variant="secondary">Rich tooltip</Button>,
  },
}
