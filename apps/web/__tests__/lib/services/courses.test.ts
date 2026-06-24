import { describe, it, expect, vi, beforeEach } from 'vitest'
import { courseService } from '@/lib/services/courses'

const mockGet = vi.fn()
const mockPost = vi.fn()
const mockPut = vi.fn()
const mockDelete = vi.fn()

vi.mock('@/lib/api', () => ({
  api: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
    put: (...args: unknown[]) => mockPut(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('courseService', () => {
  describe('list', () => {
    it('returns course list', async () => {
      const courses = [{ id: '1', title: 'CS 101', status: 'in_progress' }]
      mockGet.mockResolvedValueOnce(courses)
      const result = await courseService.list()
      expect(result).toEqual(courses)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/courses')
    })

    it('returns empty array when no courses', async () => {
      mockGet.mockResolvedValueOnce([])
      const result = await courseService.list()
      expect(result).toEqual([])
    })
  })

  describe('get', () => {
    it('returns a single course', async () => {
      const course = { id: '1', title: 'CS 101', status: 'in_progress' }
      mockGet.mockResolvedValueOnce(course)
      const result = await courseService.get('1')
      expect(result).toEqual(course)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/courses/1')
    })

    it('returns null when not found', async () => {
      mockGet.mockResolvedValueOnce(null)
      const result = await courseService.get('999')
      expect(result).toBeNull()
    })
  })

  describe('create', () => {
    it('creates and returns course', async () => {
      const data = { title: 'Math 201', code: 'MATH201' }
      const created = { id: '2', ...data, status: 'not_started' }
      mockPost.mockResolvedValueOnce(created)
      const result = await courseService.create(data)
      expect(result).toEqual(created)
      expect(mockPost).toHaveBeenCalledWith('/api/v1/courses', data)
    })

    it('handles validation error', async () => {
      mockPost.mockRejectedValueOnce(new Error('Validation failed'))
      await expect(courseService.create({ title: '' })).rejects.toThrow('Validation failed')
    })
  })

  describe('update', () => {
    it('updates and returns course', async () => {
      const data = { status: 'completed' }
      const updated = { id: '1', title: 'CS 101', status: 'completed' }
      mockPut.mockResolvedValueOnce(updated)
      const result = await courseService.update('1', data)
      expect(result).toEqual(updated)
      expect(mockPut).toHaveBeenCalledWith('/api/v1/courses/1', data)
    })

    it('handles not found on update', async () => {
      mockPut.mockRejectedValueOnce(new Error('Course not found'))
      await expect(courseService.update('999', { title: 'Nope' })).rejects.toThrow('Course not found')
    })
  })

  describe('delete', () => {
    it('deletes course', async () => {
      mockDelete.mockResolvedValueOnce({ message: 'Deleted' })
      const result = await courseService.delete('1')
      expect(result).toEqual({ message: 'Deleted' })
      expect(mockDelete).toHaveBeenCalledWith('/api/v1/courses/1')
    })

    it('handles not found on delete', async () => {
      mockDelete.mockRejectedValueOnce(new Error('Not found'))
      await expect(courseService.delete('999')).rejects.toThrow('Not found')
    })
  })
})
