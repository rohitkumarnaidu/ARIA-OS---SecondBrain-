import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { taskService } from '@/lib/services/tasks'
import type { Task, TaskCreate, TaskUpdate } from '@/lib/types'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

const mockTask = { id: 't-1', title: 'Write tests', status: 'pending', priority: 'high' } as Task
const mockCreate = { title: 'New task', status: 'pending', priority: 'medium' } as TaskCreate
const mockUpdate = { priority: 'low' } as TaskUpdate

describe('taskService', () => {
  describe('list', () => {
    it('returns an array of tasks', async () => {
      mockedApi.get.mockResolvedValue([mockTask])
      const result = await taskService.list()
      expect(result).toEqual([mockTask])
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/tasks')
    })
  })

  describe('get', () => {
    it('returns a single task', async () => {
      mockedApi.get.mockResolvedValue(mockTask)
      const result = await taskService.get('t-1')
      expect(result).toEqual(mockTask)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/tasks/t-1')
    })
  })

  describe('create', () => {
    it('creates and returns a task', async () => {
      mockedApi.post.mockResolvedValue(mockTask)
      const result = await taskService.create(mockCreate)
      expect(result).toEqual(mockTask)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/tasks', mockCreate)
    })
  })

  describe('update', () => {
    it('updates and returns the task', async () => {
      mockedApi.put.mockResolvedValue(mockTask)
      const result = await taskService.update('t-1', mockUpdate)
      expect(result).toEqual(mockTask)
      expect(mockedApi.put).toHaveBeenCalledWith('/api/v1/tasks/t-1', mockUpdate)
    })
  })

  describe('delete', () => {
    it('deletes and returns a message', async () => {
      mockedApi.delete.mockResolvedValue({ message: 'deleted' })
      const result = await taskService.delete('t-1')
      expect(result).toEqual({ message: 'deleted' })
      expect(mockedApi.delete).toHaveBeenCalledWith('/api/v1/tasks/t-1')
    })
  })

  describe('complete', () => {
    it('posts to complete endpoint and returns the updated task', async () => {
      const completed = { ...mockTask, status: 'completed' }
      mockedApi.post.mockResolvedValue(completed)
      const result = await taskService.complete('t-1')
      expect(result).toEqual(completed)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/tasks/t-1/complete')
    })
  })
})
