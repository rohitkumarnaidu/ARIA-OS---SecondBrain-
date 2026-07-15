import type { Meta, StoryObj } from '@storybook/react'
import { CourseCard } from './CourseCard'
import type { Course } from '@/lib/types'

const mockCourse: Course = {
  id: '1',
  user_id: 'user-1',
  title: 'Advanced Machine Learning',
  platform: 'Coursera',
  url: 'https://coursera.org/learn/ml',
  total_videos: 24,
  completed_videos: 12,
  deadline: '2026-09-01T00:00:00Z',
  why_enrolled: 'Deepen ML knowledge for research',
  status: 'in_progress',
  daily_minutes_needed: 45,
  created_at: '2026-01-15T00:00:00Z',
}

const meta = {
  title: 'Courses/CourseCard',
  component: CourseCard,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof CourseCard>

export default meta
type Story = StoryObj<typeof meta>

export const InProgress: Story = {
  args: { course: { ...mockCourse, status: 'in_progress' } },
}

export const Completed: Story = {
  args: { course: { ...mockCourse, status: 'completed', completed_videos: 24 } },
}

export const NotStarted: Story = {
  args: { course: { ...mockCourse, status: 'not_started', completed_videos: 0 } },
}
