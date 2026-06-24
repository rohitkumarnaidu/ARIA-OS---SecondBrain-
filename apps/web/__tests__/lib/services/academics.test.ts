import { describe, it, expect, vi, beforeEach } from 'vitest'
import { academicService } from '@/lib/services/academics'

const mockGet = vi.fn()
const mockPost = vi.fn()
const mockDelete = vi.fn()

vi.mock('@/lib/api', () => ({
  api: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('academicService', () => {
  describe('listSubjects', () => {
    it('returns subject list', async () => {
      const subjects = [{ id: '1', name: 'Math' }]
      mockGet.mockResolvedValueOnce(subjects)
      const result = await academicService.listSubjects()
      expect(result).toEqual(subjects)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/academics/subjects')
    })

    it('returns empty array when no subjects', async () => {
      mockGet.mockResolvedValueOnce([])
      const result = await academicService.listSubjects()
      expect(result).toEqual([])
    })
  })

  describe('createSubject', () => {
    it('creates and returns subject', async () => {
      const data = { name: 'Physics', code: 'PHY101' }
      const created = { id: '2', ...data }
      mockPost.mockResolvedValueOnce(created)
      const result = await academicService.createSubject(data)
      expect(result).toEqual(created)
      expect(mockPost).toHaveBeenCalledWith('/api/v1/academics/subjects', data)
    })

    it('handles validation error', async () => {
      const error = new Error('Validation failed')
      mockPost.mockRejectedValueOnce(error)
      await expect(academicService.createSubject({ name: '' })).rejects.toThrow('Validation failed')
    })
  })

  describe('deleteSubject', () => {
    it('deletes subject', async () => {
      mockDelete.mockResolvedValueOnce({ message: 'Deleted' })
      const result = await academicService.deleteSubject('1')
      expect(result).toEqual({ message: 'Deleted' })
      expect(mockDelete).toHaveBeenCalledWith('/api/v1/academics/subjects/1')
    })

    it('handles not found', async () => {
      mockDelete.mockRejectedValueOnce(new Error('Not found'))
      await expect(academicService.deleteSubject('999')).rejects.toThrow('Not found')
    })
  })

  describe('listMarks', () => {
    it('returns marks list', async () => {
      const marks = [{ id: '1', subject_id: '1', score: 85 }]
      mockGet.mockResolvedValueOnce(marks)
      const result = await academicService.listMarks()
      expect(result).toEqual(marks)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/academics/marks')
    })
  })

  describe('createMark', () => {
    it('creates and returns mark', async () => {
      const data = { subject_id: '1', score: 92, max_score: 100 }
      const created = { id: '3', ...data }
      mockPost.mockResolvedValueOnce(created)
      const result = await academicService.createMark(data)
      expect(result).toEqual(created)
      expect(mockPost).toHaveBeenCalledWith('/api/v1/academics/marks', data)
    })
  })

  describe('deleteMark', () => {
    it('deletes mark', async () => {
      mockDelete.mockResolvedValueOnce({ message: 'Deleted' })
      const result = await academicService.deleteMark('2')
      expect(result).toEqual({ message: 'Deleted' })
      expect(mockDelete).toHaveBeenCalledWith('/api/v1/academics/marks/2')
    })
  })
})
