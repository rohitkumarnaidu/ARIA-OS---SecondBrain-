import type { Meta, StoryObj } from '@storybook/react'
import { HabitCalendar } from './HabitCalendar'

const today = new Date()
const year = today.getFullYear()
const month = today.getMonth() + 1

const completions = new Set([
  `${year}-${String(month).padStart(2, '0')}-01`,
  `${year}-${String(month).padStart(2, '0')}-02`,
  `${year}-${String(month).padStart(2, '0')}-05`,
  `${year}-${String(month).padStart(2, '0')}-08`,
  `${year}-${String(month).padStart(2, '0')}-10`,
  `${year}-${String(month).padStart(2, '0')}-12`,
])

const meta = {
  title: 'Habits/HabitCalendar',
  component: HabitCalendar,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof HabitCalendar>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: { year, month, completions },
}

export const Empty: Story = {
  args: { year, month, completions: new Set() },
}

export const Loading: Story = {
  args: { year, month, completions: new Set(), loading: true },
}

export const FullMonth: Story = {
  args: {
    year,
    month,
    completions: new Set(
      Array.from({ length: 28 }).map(
        (_, i) => `${year}-${String(month).padStart(2, '0')}-${String(i + 1).padStart(2, '0')}`,
      ),
    ),
  },
}
