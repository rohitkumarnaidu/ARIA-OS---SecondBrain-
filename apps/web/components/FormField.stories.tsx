import type { Meta, StoryObj } from '@storybook/react'
import { FormField } from './FormField'
import { Input } from '@/components/ui/Input'

const meta: Meta<typeof FormField> = {
  title: 'Components/FormField',
  component: FormField,
  tags: ['autodocs'],
  parameters: {
    backgrounds: { default: 'dark' },
    layout: 'centered',
  },
  argTypes: {
    layout: { control: 'select', options: ['vertical', 'horizontal'] },
    required: { control: 'boolean' },
  },
}

export default meta
type Story = StoryObj<typeof FormField>

export const Default: Story = {
  args: {
    label: 'Username',
    children: <Input placeholder="Enter username" />,
  },
}

export const Required: Story = {
  args: {
    label: 'Email',
    required: true,
    children: <Input placeholder="you@example.com" />,
  },
}

export const WithHelperText: Story = {
  args: {
    label: 'Password',
    helperText: 'Must be at least 8 characters',
    children: <Input type="password" placeholder="Enter password" />,
  },
}

export const WithError: Story = {
  args: {
    label: 'Email',
    error: 'Please enter a valid email address',
    children: <Input placeholder="you@example.com" defaultValue="invalid" />,
  },
}

export const WithCharacterCount: Story = {
  args: {
    label: 'Bio',
    characterCount: { current: 42, max: 160 },
    children: <Input placeholder="Tell us about yourself" defaultValue="Hello, I am a software engineer..." />,
  },
}

export const HorizontalLayout: Story = {
  args: {
    label: 'Full Name',
    layout: 'horizontal',
    children: <Input placeholder="John Doe" />,
  },
}

export const CharacterCountExceeded: Story = {
  args: {
    label: 'Tweet',
    characterCount: { current: 312, max: 280 },
    children: <Input placeholder="Your tweet..." defaultValue={Array(300).fill('a').join('')} />,
  },
}
