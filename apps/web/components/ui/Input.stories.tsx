import type { Meta, StoryObj } from '@storybook/react'
import { Input } from './Input'

const meta: Meta<typeof Input> = {
  title: 'UI/Input',
  component: Input,
  tags: ['autodocs'],
  argTypes: {
    placeholder: { control: 'text' },
    disabled: { control: 'boolean' },
    error: { control: 'text' },
  },
}

export default meta
type Story = StoryObj<typeof Input>

export const Default: Story = {
  args: { placeholder: 'Enter text...' },
}

export const WithValue: Story = {
  args: { placeholder: 'Enter text...', defaultValue: 'Some value' },
}

export const Disabled: Story = {
  args: { placeholder: 'Disabled input', disabled: true },
}

export const WithError: Story = {
  args: { placeholder: 'Enter text...', error: 'This field is required' },
}

export const WithLabel: Story = {
  args: { placeholder: 'Enter email', 'aria-label': 'Email address' },
}
