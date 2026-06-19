'use client'

import { useState, useMemo, useCallback } from 'react'
import { Search, Bell, Menu, X, Check, ExternalLink } from 'lucide-react'
import { usePathname } from 'next/navigation'
import { isToday, isYesterday } from 'date-fns'
import { NotificationBadge } from '@/components/notifications/NotificationBadge'
import { useNotificationStore } from '@/lib/stores/notificationStore'
import { motion, AnimatePresence } from 'framer-motion'

const routeLabels: Record<string, string> = {
  dashboard: 'Home',
  tasks: 'Tasks',
  courses: 'Courses',
  goals: 'Goals',
  habits: 'Habits',
  sleep: 'Sleep',
  time: 'Time',
  income: 'Income',
  projects: 'Projects',
  ideas: 'Ideas',
  resources: 'Resources',
  opportunities: 'Opportunities',
  academics: 'Academics',
  knowledge: 'Knowledge Vault',
  chat: 'Chat',
  automation: 'Automation',
}

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return `${Math.floor(days / 7)}w ago`
}

function useBreadcrumb() {
  const pathname = usePathname()
  return useMemo(() => {
    const segments = pathname.split('/').filter(Boolean)
    const items: { label: string; active?: boolean }[] = []
    items.push({ label: 'Home' })
    const maxLevels = 3
    let count = 0
    for (const segment of segments) {
      if (count >= maxLevels - 1) break
      count++
      const isId = /^[0-9a-f]{8,}$/i.test(segment) || segment.length > 30
      const label = isId ? 'Detail' : (routeLabels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1))
      items.push({ label })
    }
    if (items.length > 0) items[items.length - 1].active = true
    return items
  }, [pathname])
}

interface TopNavProps {
  onSearchOpen?: () => void
  onMenuToggle?: () => void
  menuOpen?: boolean
  breadcrumb?: { label: string; active?: boolean }[]
  notificationCount?: number
  onNotificationOpen?: () => void
}

export function TopNav({
  onSearchOpen = () => {},
  onMenuToggle,
  menuOpen,
  breadcrumb: breadcrumbProp,
}: TopNavProps) {
  const autoBreadcrumb = useBreadcrumb()
  const breadcrumb = breadcrumbProp ?? autoBreadcrumb
  const [notifOpen, setNotifOpen] = useState(false)
  const notifications = useNotificationStore(s => s.notifications)
  const markAsRead = useNotificationStore(s => s.markAsRead)
  const markAllAsRead = useNotificationStore(s => s.markAllAsRead)
  const setPanelOpen = useNotificationStore(s => s.setPanelOpen)
  const unreadCount = useMemo(() => notifications.filter(n => !n.read).length, [notifications])

  const todayNotifs = useMemo(
    () => notifications.filter(n => isToday(new Date(n.created_at))),
    [notifications],
  )
  const yesterdayNotifs = useMemo(
    () => notifications.filter(n => isYesterday(new Date(n.created_at))),
    [notifications],
  )

  const handleNotifClick = useCallback(() => {
    setNotifOpen(v => !v)
  }, [])

  const handleViewAll = useCallback(() => {
    setNotifOpen(false)
    setPanelOpen(true)
  }, [setPanelOpen])

  const handleMarkAllRead = useCallback(() => {
    markAllAsRead()
  }, [markAllAsRead])

  const handleBackdropClick = useCallback(() => {
    setNotifOpen(false)
  }, [])

  const isTruncatable = breadcrumb.length > 2

  return (
    <header
      className="h-16 shrink-0 flex items-center justify-between px-4 gap-4 z-30 relative"
      style={{
        background: 'rgba(19,19,23,0.8)',
        backdropFilter: 'blur(6px)',
        WebkitBackdropFilter: 'blur(6px)',
        borderBottom: '1px solid rgba(70,70,79,0.2)',
      }}
      role="banner"
    >
      {/* Left: Menu toggle (tablet) + Breadcrumb */}
      <div className="flex items-center gap-3 min-w-0 flex-1">
        {onMenuToggle && (
          <button
            onClick={onMenuToggle}
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={menuOpen}
            aria-controls="navigation-drawer"
            className="flex lg:hidden items-center justify-center w-9 h-9 rounded-full text-[var(--text-secondary)] hover:bg-[var(--glass-medium)] hover:text-[var(--foreground)] transition-all shrink-0 min-h-touch min-w-touch"
          >
            {menuOpen ? <X size={18} aria-hidden="true" /> : <Menu size={18} aria-hidden="true" />}
          </button>
        )}

        {breadcrumb.length > 0 && (
          <nav className="flex items-center gap-2 text-sm min-w-0" aria-label="Breadcrumb">
            {breadcrumb.map((crumb, i) => {
              const showOnMd = !isTruncatable || i === 0 || i === breadcrumb.length - 1
              const hidden = isTruncatable && !showOnMd
              return (
                <span key={i} className="flex items-center gap-2 min-w-0">
                  {i > 0 && (
                    <svg width="4" height="7" viewBox="0 0 4 7" fill="none" className="shrink-0" aria-hidden="true">
                      <path d="M1 1L3.5 3.5L1 6" stroke="var(--text-secondary)" strokeWidth="1" strokeLinecap="round" />
                    </svg>
                  )}
                  {hidden ? (
                    <span className="hidden md:block text-[var(--text-tertiary)] px-0.5" aria-hidden="true">...</span>
                  ) : (
                    <span
                      className={`truncate ${crumb.active ? 'text-[var(--primary-foreground)]' : 'text-[var(--text-secondary)]'}`}
                      style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 13 }}
                    >
                      {crumb.label}
                    </span>
                  )}
                </span>
              )
            })}
          </nav>
        )}
      </div>

      {/* Right: Search + Notifications + Avatar */}
      <div className="flex items-center gap-2 shrink-0">
        {/* Search pill */}
        <button
          onClick={onSearchOpen}
          aria-label="Open search"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-[var(--text-secondary)] hover:text-[var(--foreground)] transition-all min-h-button"
          style={{ background: 'rgba(70,70,79,0.15)', border: '1px solid rgba(70,70,79,0.2)' }}
        >
          <Search size={14} aria-hidden="true" />
          <span className="text-[13px] hidden sm:block" style={{ fontFamily: 'DM Sans, sans-serif' }}>
            Search...
          </span>
          <span
            className="text-[10px] px-1.5 py-0.5 rounded hidden md:block"
            style={{
              fontFamily: 'JetBrains Mono, monospace',
              background: 'rgba(70,70,79,0.4)',
              color: 'var(--text-secondary)',
            }}
          >
            ⌘K
          </span>
        </button>

        {/* Vertical divider */}
        <div className="h-6 w-px mx-1 shrink-0" style={{ background: 'rgba(70,70,79,0.3)' }} aria-hidden="true" />

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={handleNotifClick}
            aria-label={`${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}`}
            aria-expanded={notifOpen}
            aria-haspopup="dialog"
            className="relative flex items-center justify-center w-9 h-9 rounded-full text-[var(--text-secondary)] hover:bg-[var(--glass-medium)] hover:text-[var(--foreground)] transition-all min-h-touch min-w-touch"
          >
            <Bell size={16} aria-hidden="true" />
            <NotificationBadge count={unreadCount} />
          </button>

          <AnimatePresence>
            {notifOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={handleBackdropClick} aria-hidden="true" />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -8 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -8 }}
                  transition={{ duration: 0.15, ease: 'easeOut' }}
                  className="absolute right-0 top-full mt-2 z-50 w-[320px] rounded-xl overflow-hidden"
                  style={{
                    background: 'var(--glass-heavy)',
                    backdropFilter: 'blur(20px)',
                    WebkitBackdropFilter: 'blur(20px)',
                    border: '1px solid var(--border)',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                  }}
                  role="dialog"
                  aria-modal="true"
                  aria-label="Notifications"
                >
                  <div className="max-h-[480px] overflow-y-auto">
                    {todayNotifs.length === 0 && yesterdayNotifs.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-10 text-center px-6">
                        <div
                          className="w-10 h-10 rounded-full flex items-center justify-center mb-3"
                          style={{ background: 'var(--glass-light)' }}
                        >
                          <Check size={16} className="text-[var(--accent-success)]" aria-hidden="true" />
                        </div>
                        <p className="text-sm font-medium text-[var(--text-primary)]">All caught up!</p>
                        <p className="text-xs text-[var(--text-tertiary)] mt-1">No new notifications.</p>
                      </div>
                    ) : (
                      <>
                        {todayNotifs.length > 0 && (
                          <div>
                            <div className="px-4 py-2 text-[11px] font-mono font-medium uppercase tracking-wider text-[var(--text-tertiary)] bg-[var(--glass-light)]">
                              Today
                            </div>
                            {todayNotifs.map(n => (
                              <button
                                key={n.id}
                                onClick={() => { if (!n.read) markAsRead(n.id) }}
                                className="group relative flex w-full items-start gap-3 px-4 py-3 text-left transition-all duration-150 hover:bg-[var(--glass-light)] cursor-pointer"
                                aria-label={`${n.title}: ${n.message}`}
                              >
                                {!n.read && (
                                  <div className="absolute left-0 top-0 bottom-0 w-[3px] shrink-0" aria-hidden="true">
                                    <div className="h-full w-full" style={{ background: 'var(--accent-primary)' }} />
                                  </div>
                                )}
                                <div className="flex-1 min-w-0 pt-0.5">
                                  <p className={`text-sm leading-snug truncate ${!n.read ? 'font-medium text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}`}>
                                    {n.title}
                                  </p>
                                  <p className="text-xs text-[var(--text-secondary)] mt-0.5 line-clamp-2 leading-relaxed">
                                    {n.message}
                                  </p>
                                  <span className="text-[11px] text-[var(--text-tertiary)] font-mono mt-1 block">
                                    {relativeTime(n.created_at)}
                                  </span>
                                </div>
                              </button>
                            ))}
                          </div>
                        )}
                        {yesterdayNotifs.length > 0 && (
                          <div>
                            <div className="px-4 py-2 text-[11px] font-mono font-medium uppercase tracking-wider text-[var(--text-tertiary)] bg-[var(--glass-light)] border-t border-[var(--border)]">
                              Yesterday
                            </div>
                            {yesterdayNotifs.map(n => (
                              <button
                                key={n.id}
                                onClick={() => { if (!n.read) markAsRead(n.id) }}
                                className="group relative flex w-full items-start gap-3 px-4 py-3 text-left transition-all duration-150 hover:bg-[var(--glass-light)] cursor-pointer"
                                aria-label={`${n.title}: ${n.message}`}
                              >
                                {!n.read && (
                                  <div className="absolute left-0 top-0 bottom-0 w-[3px] shrink-0" aria-hidden="true">
                                    <div className="h-full w-full" style={{ background: 'var(--accent-primary)' }} />
                                  </div>
                                )}
                                <div className="flex-1 min-w-0 pt-0.5">
                                  <p className={`text-sm leading-snug truncate ${!n.read ? 'font-medium text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}`}>
                                    {n.title}
                                  </p>
                                  <p className="text-xs text-[var(--text-secondary)] mt-0.5 line-clamp-2 leading-relaxed">
                                    {n.message}
                                  </p>
                                  <span className="text-[11px] text-[var(--text-tertiary)] font-mono mt-1 block">
                                    {relativeTime(n.created_at)}
                                  </span>
                                </div>
                              </button>
                            ))}
                          </div>
                        )}
                      </>
                    )}
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between px-4 py-2.5 border-t border-[var(--border)] bg-[var(--glass-light)]">
                    {unreadCount > 0 ? (
                      <button
                        onClick={handleMarkAllRead}
                        className="flex items-center gap-1.5 text-xs font-medium text-[var(--accent-primary)] hover:text-[var(--accent-secondary)] transition-colors"
                        aria-label="Mark all notifications as read"
                      >
                        <Check size={12} aria-hidden="true" />
                        Mark all read
                      </button>
                    ) : (
                      <span />
                    )}
                    <button
                      onClick={handleViewAll}
                      className="flex items-center gap-1.5 text-xs font-medium text-[var(--accent-primary)] hover:text-[var(--accent-secondary)] transition-colors"
                    >
                      <ExternalLink size={12} aria-hidden="true" />
                      View all
                    </button>
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>

        {/* User avatar */}
        <button
          aria-label="User menu"
          className="w-8 h-8 rounded-full overflow-hidden border border-[rgba(70,70,79,0.5)] hover:border-[rgba(99,102,241,0.5)] transition-all shrink-0"
        >
          <div
            className="w-full h-full flex items-center justify-center text-xs font-bold"
            style={{ background: 'linear-gradient(135deg, var(--accent-primary), var(--chart-3))', color: 'var(--primary-foreground)', fontFamily: 'Syne, sans-serif' }}
          >
            AS
          </div>
        </button>
      </div>
    </header>
  )
}
