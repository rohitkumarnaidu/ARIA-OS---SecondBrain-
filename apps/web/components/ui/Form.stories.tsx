import type { Meta, StoryObj } from '@storybook/react'
import { FormField, FormLabel, FormControl, FormMessage, FormDescription } from './Form'
import { Input } from './Input'

const meta: Meta<typeof FormField> = {
  title: 'UI/Form',
  component: FormField,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof FormField>

export const Default: Story = {
  render: () => (
    <div className="w-80">
      <FormField name="email">
        <FormLabel>Email</FormLabel>
        <FormControl>
          <Input type="email" placeholder="you@example.com" />
        </FormControl>
        <FormDescription>We'll never share your email.</FormDescription>
      </FormField>
    </div>
  ),
}

export const WithLabel: Story = {
  render: () => (
    <div className="w-80">
      <FormField name="fullname">
        <FormLabel>Full Name</FormLabel>
        <FormControl>
          <Input placeholder="John Doe" />
        </FormControl>
      </FormField>
    </div>
  ),
}

export const WithError: Story = {
  render: () => (
    <div className="w-80">
      <FormField name="password" error="Password must be at least 8 characters">
        <FormLabel>Password</FormLabel>
        <FormControl>
          <Input type="password" placeholder="Enter password" />
        </FormControl>
        <FormMessage />
      </FormField>
    </div>
  ),
}

export const WithHelper: Story = {
  render: () => (
    <div className="w-80">
      <FormField name="username">
        <FormLabel>Username</FormLabel>
        <FormControl>
          <Input placeholder="your_handle" />
        </FormControl>
        <FormDescription>Must be 3-20 characters, letters and numbers only.</FormDescription>
      </FormField>
    </div>
  ),
}

export const CustomMessage: Story = {
  render: () => (
    <div className="w-80">
      <FormField name="bio">
        <FormLabel>Bio</FormLabel>
        <FormControl>
          <Input placeholder="Tell us about yourself" />
        </FormControl>
        <FormMessage>This field is optional</FormMessage>
      </FormField>
    </div>
  ),
}

export const MultipleFields: Story = {
  render: () => (
    <div className="w-80 space-y-4">
      <FormField name="email">
        <FormLabel>Email</FormLabel>
        <FormControl>
          <Input type="email" placeholder="you@example.com" />
        </FormControl>
      </FormField>
      <FormField name="password" error="Too short">
        <FormLabel>Password</FormLabel>
        <FormControl>
          <Input type="password" placeholder="••••••••" />
        </FormControl>
        <FormMessage />
      </FormField>
    </div>
  ),
}
