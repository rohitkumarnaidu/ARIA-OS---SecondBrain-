import { useState } from 'react'
import type { Meta, StoryObj } from '@storybook/react'
import { CourseFilters } from './CourseFilters'

const meta = {
  title: 'Courses/CourseFilters',
  component: CourseFilters,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof CourseFilters>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => {
    const [active, setActive] = useState('all')
    return <CourseFilters activeFilter={active} onFilterChange={setActive} />
  },
}

export const WithCounts: Story = {
  render: () => {
    const [active, setActive] = useState('all')
    return (
      <CourseFilters
        activeFilter={active}
        onFilterChange={setActive}
        counts={{ all: 10, in_progress: 4, not_started: 3, completed: 3 }}
      />
    )
  },
}
