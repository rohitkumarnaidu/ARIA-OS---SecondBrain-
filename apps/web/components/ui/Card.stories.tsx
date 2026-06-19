import type { Meta, StoryObj } from '@storybook/react'
import { Card } from './Card'

const meta: Meta<typeof Card> = {
  title: 'UI/Card',
  component: Card,
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['default', 'interactive', 'glass'] },
  },
}

export default meta
type Story = StoryObj<typeof Card>

export const Default: Story = {
  args: { variant: 'default', children: <div className="p-4">Default card content</div> },
}

export const Interactive: Story = {
  args: { variant: 'interactive', children: <div className="p-4">Hover me</div> },
}

export const Glass: Story = {
  args: { variant: 'default', children: <div className="p-4">Glass morphism card</div> },
}

export const WithCustomClass: Story = {
  args: { variant: 'default', className: 'max-w-md', children: <div className="p-4">Custom sized card with a longer description to demonstrate text wrapping behavior across multiple lines.</div> },
}
