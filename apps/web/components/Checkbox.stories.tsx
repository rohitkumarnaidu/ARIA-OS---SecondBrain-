import type { Meta, StoryObj } from '@storybook/react'
import { Checkbox } from './Checkbox'

const meta: Meta<typeof Checkbox> = {
  title: 'Components/Checkbox',
  component: Checkbox,
  tags: ['autodocs'],
  parameters: {
    backgrounds: { default: 'dark' },
    layout: 'centered',
  },
  argTypes: {
    size: { control: 'select', options: ['sm', 'md'] },
    checked: { control: 'boolean' },
    disabled: { control: 'boolean' },
    indeterminate: { control: 'boolean' },
    error: { control: 'boolean' },
  },
}

export default meta
type Story = StoryObj<typeof Checkbox>

export const Unchecked: Story = {
  args: { label: 'Remember me' },
}

export const Checked: Story = {
  args: { label: 'Accept terms', checked: true },
}

export const Indeterminate: Story = {
  args: { label: 'Select all', indeterminate: true },
}

export const WithError: Story = {
  args: { label: 'I agree', error: true },
}

export const Disabled: Story = {
  args: { label: 'Disabled option', disabled: true },
}

export const Sm: Story = {
  args: { label: 'Compact', size: 'sm', checked: true },
}
