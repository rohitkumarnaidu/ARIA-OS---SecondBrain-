import type { Meta, StoryObj } from '@storybook/react'
import { Calendar } from './Calendar'

const meta: Meta<typeof Calendar> = {
  title: 'UI/Calendar',
  component: Calendar,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof Calendar>

export const Default: Story = {
  args: { onChange: () => {} },
}

export const WithSelectedDate: Story = {
  args: { value: new Date(2026, 5, 15), onChange: () => {} },
}

export const WithMinMaxDates: Story = {
  args: {
    value: new Date(2026, 5, 15),
    onChange: () => {},
    minDate: new Date(2026, 5, 1),
    maxDate: new Date(2026, 5, 30),
  },
}

export const WithDisabledDates: Story = {
  args: {
    value: new Date(2026, 5, 10),
    onChange: () => {},
    disabledDates: [
      new Date(2026, 5, 5),
      new Date(2026, 5, 12),
      new Date(2026, 5, 18),
      new Date(2026, 5, 25),
    ],
  },
}

export const ReadOnly: Story = {
  args: { value: new Date(2026, 5, 15) },
}

export const EdgeOfMonth: Story = {
  args: { value: new Date(2026, 5, 1), onChange: () => {} },
}

export const EndOfMonth: Story = {
  args: { value: new Date(2026, 5, 30), onChange: () => {} },
}
