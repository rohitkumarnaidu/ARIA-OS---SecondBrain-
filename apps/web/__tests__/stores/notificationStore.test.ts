import { describe, it, expect, beforeEach } from 'vitest'
import { useNotificationStore } from '@/lib/stores/notificationStore'
import type { AppNotification } from '@/lib/types'

const mockNotifications: AppNotification[] = Array.from({ length: 18 }, (_, i) => ({
  id: `mock-${i}`,
  user_id: 'test-user',
  title: `Notification ${i}`,
  message: `Message ${i}`,
  category: i % 3 === 0 ? 'task' : i % 3 === 1 ? 'habit' : 'system',
  priority: i < 6 ? 'high' : i < 12 ? 'medium' : 'low',
  read: i >= 9,
  createdAt: new Date(Date.now() - i * 3600000).toISOString(),
  created_at: new Date(Date.now() - i * 3600000).toISOString(),
}))

describe('notificationStore', () => {
  beforeEach(() => {
    useNotificationStore.setState(useNotificationStore.getInitialState())
  })

  it('initial state has empty notifications', () => {
    const { notifications, panelOpen } = useNotificationStore.getState()
    expect(notifications).toEqual([])
    expect(panelOpen).toBe(false)
  })

  it('markAsRead updates a notification status', () => {
    useNotificationStore.setState({ notifications: mockNotifications })
    const store = useNotificationStore.getState()
    const unread = store.notifications.find((n) => !n.read)
    expect(unread).toBeDefined()

    useNotificationStore.getState().markAsRead(unread!.id)
    const updated = useNotificationStore.getState().notifications.find((n) => n.id === unread!.id)
    expect(updated?.read).toBe(true)
  })

  it('markAllAsRead updates all unread notifications', () => {
    useNotificationStore.setState({ notifications: mockNotifications })
    const beforeCount = useNotificationStore.getState().unreadCount()
    expect(beforeCount).toBeGreaterThan(0)

    useNotificationStore.getState().markAllAsRead()

    const after = useNotificationStore.getState()
    expect(after.notifications.every((n) => n.read)).toBe(true)
    expect(after.unreadCount()).toBe(0)
  })

  it('mock data has correct structure', () => {
    useNotificationStore.setState({ notifications: mockNotifications })
    const { notifications } = useNotificationStore.getState()
    for (const n of notifications) {
      expect(n).toHaveProperty('id')
      expect(n).toHaveProperty('title')
      expect(n).toHaveProperty('message')
      expect(n).toHaveProperty('category')
      expect(n).toHaveProperty('priority')
      expect(n).toHaveProperty('read')
      expect(n).toHaveProperty('createdAt')
    }
  })

  it('toggles panel state', () => {
    expect(useNotificationStore.getState().panelOpen).toBe(false)
    useNotificationStore.getState().togglePanel()
    expect(useNotificationStore.getState().panelOpen).toBe(true)
    useNotificationStore.getState().togglePanel()
    expect(useNotificationStore.getState().panelOpen).toBe(false)
  })
})
