import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useCourseStore } from '@/lib/stores/courseStore'
import { courseService } from '@/lib/services/courses'

vi.mock('@/lib/services/courses', () => ({
  courseService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockCourse = {
  id: '1',
  user_id: 'user1',
  title: 'Test Course',
  platform: 'Coursera',
  completed_videos: 0,
  status: 'not_started' as const,
  created_at: '2026-01-01T00:00:00Z',
}

describe('courseStore', () => {
  beforeEach(() => {
    useCourseStore.setState(useCourseStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useCourseStore.getState()
    expect(state.items).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('fetch should load courses', async () => {
    vi.mocked(courseService.list).mockResolvedValue([mockCourse])
    await useCourseStore.getState().fetch()
    const state = useCourseStore.getState()
    expect(state.items).toHaveLength(1)
    expect(state.items[0].title).toBe('Test Course')
    expect(state.loading).toBe(false)
  })

  it('fetch should handle errors', async () => {
    vi.mocked(courseService.list).mockRejectedValue(new Error('Network error'))
    await useCourseStore.getState().fetch()
    expect(useCourseStore.getState().error).toBe('Network error')
    expect(useCourseStore.getState().loading).toBe(false)
  })

  it('getById should return the correct course', async () => {
    vi.mocked(courseService.list).mockResolvedValue([mockCourse])
    await useCourseStore.getState().fetch()
    const found = useCourseStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.title).toBe('Test Course')
  })

  it('create should add a course', async () => {
    vi.mocked(courseService.create).mockResolvedValue(mockCourse)
    await useCourseStore.getState().create({ title: 'Test Course', platform: 'Coursera' })
    expect(useCourseStore.getState().items).toHaveLength(1)
  })

  it('create should handle errors', async () => {
    vi.mocked(courseService.create).mockRejectedValue(new Error('Create failed'))
    await useCourseStore.getState().create({ title: 'Test Course', platform: 'Coursera' })
    expect(useCourseStore.getState().error).toBe('Create failed')
  })

  it('update should modify a course', async () => {
    vi.mocked(courseService.list).mockResolvedValue([mockCourse])
    vi.mocked(courseService.update).mockResolvedValue({ ...mockCourse, title: 'Updated' })
    await useCourseStore.getState().fetch()
    await useCourseStore.getState().update('1', { title: 'Updated' })
    expect(useCourseStore.getState().items[0].title).toBe('Updated')
  })

  it('update should handle errors', async () => {
    vi.mocked(courseService.update).mockRejectedValue(new Error('Update failed'))
    await useCourseStore.getState().update('1', { title: 'Updated' })
    expect(useCourseStore.getState().error).toBe('Update failed')
  })

  it('remove should delete a course', async () => {
    vi.mocked(courseService.list).mockResolvedValue([mockCourse])
    vi.mocked(courseService.delete).mockResolvedValue({ message: 'Deleted' })
    await useCourseStore.getState().fetch()
    await useCourseStore.getState().remove('1')
    expect(useCourseStore.getState().items).toHaveLength(0)
  })

  it('remove should handle errors', async () => {
    vi.mocked(courseService.delete).mockRejectedValue(new Error('Delete failed'))
    await useCourseStore.getState().remove('1')
    expect(useCourseStore.getState().error).toBe('Delete failed')
  })
})
