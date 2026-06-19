import { create } from 'zustand'
import type { AppNotification } from '@/lib/types'
import { notificationService } from '@/lib/services/notifications'
import { predictive } from '@/lib/ai'

interface NotificationStore {
  notifications: AppNotification[]
  panelOpen: boolean
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  generateNudges: () => Promise<void>
  setPanelOpen: (open: boolean) => void
  togglePanel: () => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  unreadCount: () => number
}

export const useNotificationStore = create<NotificationStore>((set, get) => ({
  notifications: [],
  panelOpen: false,
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await notificationService.list()
      set({ notifications: data, loading: false })
    } catch {
      set({ loading: false })
    }
  },

  generateNudges: async () => {
    try {
      const [tasks, habits, sleep] = await Promise.allSettled([
        predictive.taskCompletion(),
        predictive.habits(),
        predictive.sleep(),
      ])

      const localNudges: AppNotification[] = []

      if (tasks.status === 'fulfilled' && tasks.value.at_risk_count > 0) {
        localNudges.push({
          id: `nudge-tasks-${Date.now()}`,
          user_id: '',
          title: `${tasks.value.at_risk_count} task${tasks.value.at_risk_count !== 1 ? 's' : ''} at risk`,
          message: tasks.value.predictions.filter(p => p.probability < 40).slice(0, 3).map(p => p.title).join(', '),
          category: 'task',
          priority: 'high',
          read: false,
          action_url: '/dashboard/tasks',
          icon: 'alert-circle',
          created_at: new Date().toISOString(),
        })
      }

      if (habits.status === 'fulfilled' && habits.value.at_risk_count > 0) {
        localNudges.push({
          id: `nudge-habits-${Date.now()}`,
          user_id: '',
          title: `${habits.value.at_risk_count} habit${habits.value.at_risk_count !== 1 ? 's' : ''} slipping`,
          message: habits.value.predictions.filter(p => p.risk_level !== 'Low').slice(0, 3).map(p => `${p.habit_name} (${p.risk_level})`).join(', '),
          category: 'habit',
          priority: 'medium',
          read: false,
          action_url: '/dashboard/habits',
          icon: 'flame',
          created_at: new Date().toISOString(),
        })
      }

      if (sleep.status === 'fulfilled' && sleep.value.average_score > 0) {
        const s = sleep.value
        if (s.trend === 'declining') {
          localNudges.push({
            id: `nudge-sleep-${Date.now()}`,
            user_id: '',
            title: 'Sleep quality declining',
            message: s.recommendation,
            category: 'habit',
            priority: 'medium',
            read: false,
            action_url: '/dashboard/sleep',
            icon: 'moon',
            created_at: new Date().toISOString(),
          })
        }
      }

      if (localNudges.length > 0) {
        set(state => ({
          notifications: [...localNudges, ...state.notifications].slice(0, 50),
        }))
      }
    } catch {
      // Nudges are best-effort
    }
  },

  setPanelOpen: (open) => set({ panelOpen: open }),

  togglePanel: () => set((state) => ({ panelOpen: !state.panelOpen })),

  markAsRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n,
      ),
    })),

  markAllAsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
    })),

  unreadCount: () => get().notifications.filter((n) => !n.read).length,
}))
