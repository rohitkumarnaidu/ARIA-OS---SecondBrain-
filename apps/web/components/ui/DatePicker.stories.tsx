import type { Meta, StoryObj } from '@storybook/react'
import { DatePicker } from './DatePicker'

const meta: Meta<typeof DatePicker> = {
  title: 'UI/DatePicker',
  component: DatePicker,
  tags: ['autodocs'],
  argTypes: {
    disabled: { control: 'boolean' },
    placeholder: { control: 'text' },
  },
}

export default meta
type Story = StoryObj<typeof DatePicker>

export const Default: Story = {
  args: { onChange: () => {}, placeholder: 'Pick a date' },
}

export const WithSelectedDate: Story = {
  args: { value: new Date(2026, 5, 15), onChange: () => {} },
}

export const Disabled: Story = {
  args: { value: new Date(2026, 5, 15), disabled: true },
}

export const CustomPlaceholder: Story = {
  args: { onChange: () => {}, placeholder: 'Select deadline...' },
}

export const WithDateRange: Story = {
  args: {
    value: new Date(2026, 5, 15),
    onChange: () => {},
    minDate: new Date(2026, 5, 1),
    maxDate: new Date(2026, 5, 30),
  },
}

export const WithoutOnChange: Story = {
  args: { value: new Date(2026, 5, 15) },
}
