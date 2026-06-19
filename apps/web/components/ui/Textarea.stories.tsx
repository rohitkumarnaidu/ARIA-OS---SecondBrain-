import type { Meta, StoryObj } from '@storybook/react'
import { Textarea } from './Textarea'

const meta: Meta<typeof Textarea> = {
  title: 'UI/Textarea',
  component: Textarea,
  tags: ['autodocs'],
  argTypes: {
    label: { control: 'text' },
    placeholder: { control: 'text' },
    error: { control: 'text' },
    helperText: { control: 'text' },
    maxLength: { control: 'number' },
    disabled: { control: 'boolean' },
    required: { control: 'boolean' },
  },
}

export default meta
type Story = StoryObj<typeof Textarea>

export const Default: Story = {
  args: {
    placeholder: 'Type your message here...',
  },
}

export const WithLabel: Story = {
  args: {
    label: 'Description',
    placeholder: 'Enter a description...',
  },
}

export const WithValue: Story = {
  args: {
    label: 'Notes',
    value: 'This is some pre-filled content in the textarea. It can be edited by the user.',
  },
}

export const Required: Story = {
  args: {
    label: 'Feedback',
    placeholder: 'Your feedback is required...',
    required: true,
  },
}

export const WithHelperText: Story = {
  args: {
    label: 'Bio',
    placeholder: 'Tell us about yourself...',
    helperText: 'This will be visible on your public profile.',
  },
}

export const WithError: Story = {
  args: {
    label: 'Email body',
    value: 'invalid content',
    error: 'This field contains invalid characters.',
  },
}

export const WithCharCount: Story = {
  args: {
    label: 'Tweet',
    placeholder: 'What is happening?',
    maxLength: 280,
    value: 'Halfway through my message...',
  },
}

export const CharCountNearLimit: Story = {
  args: {
    label: 'Short message',
    maxLength: 50,
    value: 'This is a message that is almost at the limit of allowed characters.',
  },
}

export const Disabled: Story = {
  args: {
    label: 'Read-only',
    value: 'This content cannot be edited.',
    disabled: true,
  },
}

export const Empty: Story = {
  args: {
    label: 'No content',
    placeholder: 'Nothing yet...',
  },
}
