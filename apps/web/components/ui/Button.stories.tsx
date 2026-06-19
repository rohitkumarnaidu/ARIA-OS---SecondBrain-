import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['primary', 'secondary', 'ghost', 'danger'] },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
  },
}

export default meta
type Story = StoryObj<typeof Button>

export const Primary: Story = {
  args: { variant: 'primary', children: 'Primary Button', size: 'default' },
}

export const Secondary: Story = {
  args: { variant: 'secondary', children: 'Secondary Button', size: 'default' },
}

export const Ghost: Story = {
  args: { variant: 'ghost', children: 'Ghost Button', size: 'default' },
}

export const Danger: Story = {
  args: { variant: 'destructive', children: 'Delete', size: 'default' },
}

export const Small: Story = {
  args: { variant: 'primary', children: 'Small', size: 'sm' },
}

export const Large: Story = {
  args: { variant: 'primary', children: 'Large', size: 'lg' },
}

export const Loading: Story = {
  args: { variant: 'primary', children: 'Loading...', loading: true, size: 'default' },
}
