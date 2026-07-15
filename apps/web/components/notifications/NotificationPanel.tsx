'use client'

import { useState, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bell,
  X,
  CheckSquare,
  BookOpen,
  Zap,
  Target,
  Repeat,
  Settings,
  Sparkles,
  AlertTriangle,
  ChevronDown,
  Check,
  ExternalLink,
} from 'lucide-react'
import { cn } from '@/components/ui/utils'
import { useNotificationStore } from '@/lib/stores/notificationStore'
import type { NotificationCategory, NotificationPriority } from '@/types/notifications'

const priorityColors: Record<NotificationPriority, string> = {
  high: 'var(--priority-urgent)',
  medium: 'var(--priority-high)',
  low: 'var(--accent-info)',
}

const categoryIcons: Record<NotificationCategory, React.ElementType> = {
  task: CheckSquare,
  learning: BookOpen,
  opportunity: Zap,
  goal: Target,
  habit: Repeat,
  system: Settings,
  ai: Sparkles,
  reminder: Bell,
  achievement: Sparkles,
  deadline_alert: AlertTriangle,
}

const categoryLabels: Record<NotificationCategory, string> = {
  task: 'Tasks',
  learning: 'Learning',
  opportunity: 'Opportunities',
  goal: 'Goals',
  habit: 'Habits',
  system: 'System',
  ai: 'AI Insights',
  reminder: 'Reminders',
  achievement: 'Achievements',
  deadline_alert: 'Deadline Alerts',
}

const categoryOrder: NotificationCategory[] = [
  'task',
  'learning',
  'opportunity',
  'goal',
  'habit',
  'system',
  'ai',
  'reminder',
  'achievement',
]

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  const weeks = Math.floor(days / 7)
  return `${weeks}w ago`
}

function groupByCategory(
  notifications: ReturnType<typeof useNotificationStore.getState>['notifications'],
): Map<NotificationCategory, ReturnType<typeof useNotificationStore.getState>['notifications']> {
  const map = new Map<NotificationCategory, typeof notifications>()
  for (const cat of categoryOrder) {
    const items = notifications.filter((n) => n.category === cat)
    if (items.length > 0) map.set(cat, items)
  }
  return map
}

function NotificationItem({
  notification,
  onMarkRead,
  index,
}: {
  notification: ReturnType<typeof useNotificationStore.getState>['notifications'][number]
  onMarkRead: (id: string) => void
  index: number
}): JSX.Element {
  const isUnread = !notification.read

  return (
    <motion.button
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.03, duration: 0.2, ease: 'easeOut' }}
      onClick={() => {
        if (isUnread) onMarkRead(notification.id)
        if (notification.action_url) {
          window.location.href = notification.action_url
        }
      }}
      className={cn(
        'group relative flex w-full items-start gap-3 px-4 py-3 text-left transition-all duration-150',
        'hover:bg-[var(--glass-light)] cursor-pointer',
        'focus-visible:outline-none focus-visible:bg-[var(--glass-light)] focus-visible:ring-1 focus-visible:ring-inset focus-visible:ring-[var(--accent-primary)]/30',
      )}
      aria-label={`${notification.title}: ${notification.message}`}
      role="button"
    >
      {/* Priority / Unread indicator */}
      <div className="absolute left-0 top-0 bottom-0 w-[3px] shrink-0" aria-hidden="true">
        {isUnread ? (
          <div className="h-full w-full" style={{ background: 'var(--accent-primary)' }} />
        ) : (
          <div className="h-full w-full" style={{ background: priorityColors[notification.priority] }} />
        )}
      </div>

      <div className="flex-1 min-w-0 pt-0.5">
        <p
          className={cn(
            'text-sm leading-snug truncate',
            isUnread ? 'font-medium text-[var(--text-primary)]' : 'text-[var(--text-secondary)]',
          )}
        >
          {notification.title}
        </p>
        <p className="text-xs text-[var(--text-secondary)] mt-0.5 line-clamp-2 leading-relaxed">
          {notification.message}
        </p>
        <div className="flex items-center gap-2 mt-1.5">
          <span className="text-[11px] text-[var(--text-tertiary)] font-mono">
            {relativeTime(notification.created_at)}
          </span>
          {notification.action_url && (
            <ExternalLink size={10} className="text-[var(--text-tertiary)] opacity-0 group-hover:opacity-100 transition-opacity" aria-hidden="true" />
          )}
        </div>
      </div>
    </motion.button>
  )
}

function CollapsibleSection({
  category,
  notifications,
  onMarkRead,
  initiallyOpen,
}: {
  category: NotificationCategory
  notifications: ReturnType<typeof useNotificationStore.getState>['notifications']
  onMarkRead: (id: string) => void
  initiallyOpen: boolean
}): JSX.Element {
  const [open, setOpen] = useState(initiallyOpen)
  const Icon = categoryIcons[category]
  const unreadInSection = notifications.filter((n) => !n.read).length

  return (
    <div className="border-b border-[var(--border)] last:border-b-0">
      <button
        onClick={() => setOpen((v) => !v)}
        className={cn(
          'flex w-full items-center gap-2 px-4 py-2.5 text-left transition-colors duration-150',
          'hover:bg-[var(--glass-light)]',
          'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-inset focus-visible:ring-[var(--accent-primary)]/30',
        )}
        aria-expanded={open}
        aria-controls={`section-${category}`}
      >
        <Icon size={14} className="text-[var(--accent-secondary)] shrink-0" aria-hidden="true" />
        <span className="text-xs font-medium text-[var(--text-secondary)] flex-1 uppercase tracking-wider">
          {categoryLabels[category]}
        </span>
        {unreadInSection > 0 && (
          <span
            className="flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full text-[10px] font-mono font-bold text-white"
            style={{ background: 'var(--accent-primary)' }}
          >
            {unreadInSection}
          </span>
        )}
        <motion.div
          animate={{ rotate: open ? 0 : -90 }}
          transition={{ duration: 0.2, ease: 'easeInOut' }}
        >
          <ChevronDown size={14} className="text-[var(--text-tertiary)]" aria-hidden="true" />
        </motion.div>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key={`content-${category}`}
            id={`section-${category}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="divide-y divide-[var(--border)]/50">
              {notifications.map((n, idx) => (
                <NotificationItem
                  key={n.id}
                  notification={n}
                  onMarkRead={onMarkRead}
                  index={idx}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export function NotificationPanel(): JSX.Element {
  const { notifications, panelOpen, setPanelOpen, markAsRead, markAllAsRead, unreadCount } =
    useNotificationStore()
  const totalUnread = unreadCount()
  const grouped = useMemo(() => groupByCategory(notifications), [notifications])

  const handleClose = useCallback(() => {
    setPanelOpen(false)
  }, [setPanelOpen])

  const handleMarkAllRead = useCallback(() => {
    markAllAsRead()
  }, [markAllAsRead])

  return (
    <AnimatePresence>
      {panelOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40"
            style={{ background: 'var(--glass-heavy)' }}
            onClick={handleClose}
            aria-hidden="true"
          />

          {/* Panel */}
          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed right-0 top-0 h-full w-[380px] max-w-[calc(100vw-32px)] z-50 flex flex-col"
            style={{
              background: 'var(--glass-heavy)',
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)',
              borderLeft: '1px solid var(--border)',
              boxShadow: '-8px 0 32px rgba(0,0,0,0.4)',
            }}
            role="dialog"
            aria-modal="true"
            aria-label="Notifications panel"
          >
            {/* Header */}
            <div
              className="flex items-center justify-between px-5 py-4 shrink-0"
              style={{ borderBottom: '1px solid var(--border)' }}
            >
              <div className="flex items-center gap-3">
                <Bell size={18} className="text-[var(--accent-primary)]" aria-hidden="true" />
                <h2 className="text-base font-display font-semibold text-[var(--text-primary)]">
                  Notifications
                </h2>
                {totalUnread > 0 && (
                  <span
                    className="flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full text-[10px] font-mono font-bold text-white"
                    style={{ background: 'var(--accent-primary)' }}
                  >
                    {totalUnread}
                  </span>
                )}
              </div>
              <button
                onClick={handleClose}
                className="flex items-center justify-center w-8 h-8 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--glass-light)] hover:text-[var(--text-primary)] transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--accent-primary)]"
                aria-label="Close notifications panel"
              >
                <X size={16} aria-hidden="true" />
              </button>
            </div>

            {/* Mark all read action */}
            {totalUnread > 0 && (
              <div className="flex items-center justify-between px-5 py-2 shrink-0">
                <span className="text-xs text-[var(--text-tertiary)] font-mono">
                  {totalUnread} unread
                </span>
                <button
                  onClick={handleMarkAllRead}
                  className="flex items-center gap-1.5 text-xs font-medium text-[var(--accent-primary)] hover:text-[var(--accent-secondary)] transition-colors focus-visible:outline-none focus-visible:underline"
                  aria-label="Mark all notifications as read"
                >
                  <Check size={12} aria-hidden="true" />
                  Mark all read
                </button>
              </div>
            )}

            {/* Body */}
            <div className="flex-1 overflow-y-auto" aria-live="polite" aria-atomic="true" role="region" aria-label="Notification list">
              {grouped.size === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center px-8">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center mb-4"
                    style={{ background: 'var(--glass-light)' }}
                  >
                    <Check size={20} className="text-[var(--accent-success)]" aria-hidden="true" />
                  </div>
                  <p className="text-sm font-medium text-[var(--text-primary)]">
                    All caught up!
                  </p>
                  <p className="text-xs text-[var(--text-tertiary)] mt-1">
                    You have no new notifications.
                  </p>
                </div>
              ) : (
                Array.from(grouped.entries()).map(([category, items]) => (
                  <CollapsibleSection
                    key={category}
                    category={category}
                    notifications={items}
                    onMarkRead={markAsRead}
                    initiallyOpen={items.some((n) => !n.read)}
                  />
                ))
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}
