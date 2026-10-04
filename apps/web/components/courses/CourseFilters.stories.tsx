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

// Both props of CourseFilters are required, so Storybook 10 makes `args` a
// required field of StoryObj<typeof meta>. `args` supplies the required props
// (and populates the args/controls table); `render` then layers local state on
// top so the filter tabs stay interactive in Storybook.
const defaultArgs = {
  activeFilter: 'all',
  onFilterChange: () => {},
}

export const Default: Story = {
  args: defaultArgs,
  render: (args) => {
    const [active, setActive] = useState(args.activeFilter)
    return <CourseFilters {...args} activeFilter={active} onFilterChange={setActive} />
  },
}

export const WithCounts: Story = {
  args: {
    ...defaultArgs,
    counts: { all: 10, in_progress: 4, not_started: 3, completed: 3 },
  },
  render: (args) => {
    const [active, setActive] = useState(args.activeFilter)
    return <CourseFilters {...args} activeFilter={active} onFilterChange={setActive} />
  },
}