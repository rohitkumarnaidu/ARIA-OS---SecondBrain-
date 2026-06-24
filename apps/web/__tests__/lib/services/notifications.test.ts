import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { notificationService } from '@/lib/services/notifications'
import type { AppNotification } from '@/lib/types'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

const mockNotification = {
  id: 'notif-1',
  title: 'Test',
  message: 'Hello',
  category: 'task',
  priority: 'high',
  read: false,
  created_at: '2026-01-01',
} as AppNotification

describe('notificationService', () => {
  describe('list', () => {
    it('returns an array of notifications', async () => {
      mockedApi.get.mockResolvedValue([mockNotification])
      const result = await notificationService.list()
      expect(result).toEqual([mockNotification])
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/notifications')
    })
  })

  describe('markRead', () => {
    it('patches a notification as read', async () => {
      const updated = { ...mockNotification, read: true }
      mockedApi.patch.mockResolvedValue(updated)
      const result = await notificationService.markRead('notif-1')
      expect(result).toEqual(updated)
      expect(mockedApi.patch).toHaveBeenCalledWith('/api/v1/notifications/notif-1/read')
    })
  })

  describe('markAllRead', () => {
    it('posts to read-all endpoint', async () => {
      mockedApi.post.mockResolvedValue({ message: 'all marked read' })
      const result = await notificationService.markAllRead()
      expect(result).toEqual({ message: 'all marked read' })
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/notifications/read-all')
    })
  })
})
