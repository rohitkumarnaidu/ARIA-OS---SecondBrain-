import { describe, it, expect, beforeEach } from 'vitest'
import { useNotificationStore } from '@/lib/stores/notificationStore'

describe('notificationStore', () => {
  beforeEach(() => {
    useNotificationStore.setState(useNotificationStore.getInitialState())
  })

  it('initial state has mock notifications', () => {
    const { notifications, panelOpen } = useNotificationStore.getState()
    expect(notifications.length).toBeGreaterThan(0)
    expect(notifications.length).toBe(18)
    expect(panelOpen).toBe(false)
  })

  it('markAsRead updates a notification status', () => {
    const store = useNotificationStore.getState()
    const unread = store.notifications.find((n) => !n.read)
    expect(unread).toBeDefined()

    useNotificationStore.getState().markAsRead(unread!.id)
    const updated = useNotificationStore.getState().notifications.find((n) => n.id === unread!.id)
    expect(updated?.read).toBe(true)
  })

  it('markAllAsRead updates all unread notifications', () => {
    const beforeCount = useNotificationStore.getState().unreadCount()
    expect(beforeCount).toBeGreaterThan(0)

    useNotificationStore.getState().markAllAsRead()

    const after = useNotificationStore.getState()
    expect(after.notifications.every((n) => n.read)).toBe(true)
    expect(after.unreadCount()).toBe(0)
  })

  it('mock data has correct structure', () => {
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
