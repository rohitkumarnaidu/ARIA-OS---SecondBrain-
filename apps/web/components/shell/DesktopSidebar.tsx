'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx } from 'clsx'
import {
  LayoutDashboard, CheckSquare, BookOpen, Youtube,
  FileText, Lightbulb, Target, Radar, Wallet,
  FolderKanban, GraduationCap, Moon, Clock, MessageCircle, Zap, Terminal,
  Plus, ChevronRight, PanelLeftClose, PanelLeftOpen,
} from 'lucide-react'

const navGroups = [
  {
    label: 'Workspace',
    items: [
      { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
      { label: 'Tasks', href: '/tasks', icon: CheckSquare },
      { label: 'Courses', href: '/courses', icon: BookOpen },
      { label: 'YouTube', href: '/youtube', icon: Youtube },
      { label: 'Resources', href: '/resources', icon: FileText },
      { label: 'Ideas', href: '/ideas', icon: Lightbulb },
      { label: 'Goals', href: '/goals', icon: Target },
    ],
  },
  {
    label: 'Tracking',
    items: [
      { label: 'Opportunities', href: '/opportunities', icon: Radar },
      { label: 'Income', href: '/income', icon: Wallet },
      { label: 'Projects', href: '/projects', icon: FolderKanban },
      { label: 'Academics', href: '/academics', icon: GraduationCap },
      { label: 'Habits', href: '/habits', icon: Moon },
      { label: 'Sleep', href: '/sleep', icon: Moon },
      { label: 'Time', href: '/time', icon: Clock },
    ],
  },
  {
    label: 'System',
    items: [
      { label: 'Chat', href: '/chat', icon: MessageCircle },
      { label: 'Automation', href: '/automation', icon: Zap },
    ],
  },
] as const

interface DesktopSidebarProps {
  onCommandCenter?: () => void
  onNewEntry?: () => void
}

const SIDEBAR_BG = 'var(--sidebar)'
const SIDEBAR_TEXT_SEC = 'var(--sidebar-foreground)'
const SIDEBAR_PRIMARY = 'var(--sidebar-primary)'
const SIDEBAR_PRIMARY_FG = 'var(--sidebar-primary-foreground)'
const SIDEBAR_ACCENT = 'var(--sidebar-accent)'
const SIDEBAR_ACCENT_FG = 'var(--sidebar-accent-foreground)'
const SIDEBAR_BORDER = 'var(--sidebar-border)'
const BORDER_COLOR = 'var(--border)'

export default function DesktopSidebar({ onCommandCenter, onNewEntry }: DesktopSidebarProps) {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  useEffect(() => {
    try {
      const saved = localStorage.getItem('sidebar-collapsed')
      if (saved === 'true') setCollapsed(true)
    } catch { /* ignore */ }
  }, [])

  const toggleCollapsed = useCallback(() => {
    setCollapsed(v => {
      const next = !v
      try { localStorage.setItem('sidebar-collapsed', String(next)) } catch { /* ignore */ }
      return next
    })
  }, [])

  return (
    <aside
      id="main-navigation"
      className="flex flex-col h-full shrink-0 border-r overflow-hidden transition-[width] duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]"
      style={{
        width: collapsed ? 56 : 240,
        background: SIDEBAR_BG,
        borderColor: SIDEBAR_BORDER,
      }}
      role="navigation"
      aria-label="Main navigation"
    >
      {/* Brand Header */}
      <div className={clsx('flex items-center shrink-0', collapsed ? 'justify-center px-2 pt-5 pb-6' : 'gap-3 px-4 pt-6 pb-8')}>
        <div
          className="flex items-center justify-center h-10 w-10 rounded-xl shrink-0"
          style={{
            background: `linear-gradient(125deg, ${SIDEBAR_PRIMARY_FG} 0%, var(--aria-indigo-200) 100%)`,
            boxShadow: `0 0 16px ${SIDEBAR_BORDER}`,
          }}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="M10 2L13.5 7.5H17L14 11.5L15.5 17L10 14L4.5 17L6 11.5L3 7.5H6.5L10 2Z" fill="var(--aria-indigo-dark)" />
          </svg>
        </div>
        {!collapsed && (
          <div className="flex flex-col">
            <span
              className="text-sm font-bold tracking-tight leading-tight"
              style={{ fontFamily: 'Syne, sans-serif', color: SIDEBAR_ACCENT_FG }}
            >
              Second Brain OS
            </span>
            <span
              className="text-[11px] tracking-[0.12px]"
              style={{ fontFamily: 'JetBrains Mono, monospace', color: 'var(--sidebar-foreground)' }}
            >
              v2.4.0-stable
            </span>
          </div>
        )}
      </div>

      {/* New Entry CTA */}
      <div className={clsx('shrink-0', collapsed ? 'px-2 pb-5' : 'px-4 pb-6')}>
        <button
          onClick={onNewEntry}
          className={clsx(
            'flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90 active:scale-[0.98] min-h-button',
            collapsed ? 'w-10 mx-auto' : 'w-full',
          )}
          style={{
            background: SIDEBAR_PRIMARY_FG,
            color: 'var(--aria-indigo-dark)',
            boxShadow: `0 0 7.5px var(--accent-glow-color)`,
            fontFamily: 'DM Sans, sans-serif',
          }}
          aria-label="Create new entry"
        >
          <Plus size={14} aria-hidden="true" />
          {!collapsed && <span>New Entry</span>}
        </button>
      </div>

      {/* Divider */}
      <div className={clsx('shrink-0', collapsed ? 'px-2 pb-3' : 'px-4 pb-4')}>
        <div style={{ height: 1, background: SIDEBAR_BORDER }} />
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto no-scrollbar" style={{ padding: collapsed ? '0 4px 8px' : '0 8px 16px' }}>
        {navGroups.map((group) => (
          <div key={group.label} className={clsx('space-y-0.5', collapsed && 'flex flex-col items-center')}>
            {!collapsed && (
              <div className="pt-4 pb-1 px-3">
                <span
                  className="text-[10px] tracking-[0.8px] uppercase"
                  style={{ fontFamily: 'JetBrains Mono, monospace', color: SIDEBAR_TEXT_SEC, opacity: 0.6 }}
                >
                  {group.label}
                </span>
              </div>
            )}
            {/* Command Center entry in System section */}
            {group.label === 'System' && (
              <button
                onClick={onCommandCenter}
                className={clsx(
                  'flex items-center rounded-lg text-sm transition-all group min-h-touch',
                  collapsed ? 'justify-center w-10 mx-auto px-0 py-2.5' : 'w-full gap-3 px-3 py-2.5',
                )}
                style={{
                  color: SIDEBAR_TEXT_SEC,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = `color-mix(in oklab, ${SIDEBAR_ACCENT} 50%, transparent)`
                  e.currentTarget.style.color = SIDEBAR_ACCENT_FG
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = SIDEBAR_TEXT_SEC
                }}
                aria-label="Open command center"
              >
                <span style={{ color: SIDEBAR_TEXT_SEC, opacity: 0.7 }}>
                  <Terminal size={16} aria-hidden="true" />
                </span>
                {!collapsed && (
                  <>
                    <span style={{ fontFamily: 'DM Sans, sans-serif' }}>Command Center</span>
                    <span
                      className="ml-auto text-[10px] tracking-[0.5px] px-1.5 py-0.5 rounded"
                      style={{
                        fontFamily: 'JetBrains Mono, monospace',
                        background: 'rgba(70,70,79,0.4)',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      ⌘K
                    </span>
                  </>
                )}
              </button>
            )}
            {group.items.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={clsx(
                    'flex items-center rounded-lg text-sm transition-all group min-h-touch',
                    collapsed ? 'justify-center w-10 mx-auto px-0 py-2.5' : 'gap-3 px-3 py-2.5',
                  )}
                  style={{
                    color: isActive ? SIDEBAR_PRIMARY_FG : SIDEBAR_TEXT_SEC,
                    background: isActive ? `color-mix(in oklab, ${SIDEBAR_PRIMARY} 15%, transparent)` : 'transparent',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = `color-mix(in oklab, ${SIDEBAR_ACCENT} 50%, transparent)`
                      e.currentTarget.style.color = SIDEBAR_ACCENT_FG
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'transparent'
                      e.currentTarget.style.color = SIDEBAR_TEXT_SEC
                    }
                  }}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <span style={{ color: isActive ? SIDEBAR_PRIMARY : SIDEBAR_TEXT_SEC, opacity: 0.7 }}>
                    <Icon size={16} aria-hidden="true" />
                  </span>
                  {!collapsed && <span style={{ fontFamily: 'DM Sans, sans-serif' }}>{item.label}</span>}
                  {isActive && !collapsed && (
                    <div
                      className="ml-auto w-1 h-4 rounded-full shrink-0"
                      style={{ background: SIDEBAR_PRIMARY, boxShadow: `0 0 6px ${SIDEBAR_PRIMARY}` }}
                    />
                  )}
                </Link>
              )
            })}
          </div>
        ))}
      </div>

      {/* Toggle Collapse Button */}
      <div className="shrink-0 px-2 pb-1">
        <button
          onClick={toggleCollapsed}
          className={clsx(
            'flex items-center justify-center w-full py-2 rounded-lg transition-all group min-h-touch',
            collapsed ? 'mx-auto w-10' : 'w-full',
          )}
          style={{ color: SIDEBAR_TEXT_SEC }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = `color-mix(in oklab, ${SIDEBAR_ACCENT} 50%, transparent)`
            e.currentTarget.style.color = SIDEBAR_ACCENT_FG
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent'
            e.currentTarget.style.color = SIDEBAR_TEXT_SEC
          }}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <PanelLeftOpen size={16} aria-hidden="true" /> : <PanelLeftClose size={16} aria-hidden="true" />}
        </button>
      </div>

      {/* User Profile Footer */}
      <div className="shrink-0 border-t" style={{ borderColor: SIDEBAR_BORDER }}>
        <button
          className={clsx(
            'flex items-center rounded-lg transition-all group min-h-touch',
            collapsed ? 'justify-center w-full px-0 py-3' : 'gap-3 px-4 py-3',
          )}
          style={{ color: SIDEBAR_TEXT_SEC }}
          aria-label="User settings"
        >
          <div className={clsx('w-8 h-8 rounded-full shrink-0 overflow-hidden', collapsed ? '' : '')} style={{ border: `1px solid ${SIDEBAR_BORDER}` }}>
            <div
              className="w-full h-full flex items-center justify-center text-xs font-bold"
              style={{
                background: `linear-gradient(135deg, ${SIDEBAR_PRIMARY}, var(--aria-indigo-500))`,
                color: SIDEBAR_PRIMARY_FG,
                fontFamily: 'Syne, sans-serif',
              }}
            >
              AS
            </div>
          </div>
          {!collapsed && (
            <>
              <div className="flex flex-col items-start min-w-0 flex-1">
                <span className="text-sm font-medium truncate w-full" style={{ fontFamily: 'DM Sans, sans-serif', color: SIDEBAR_ACCENT_FG }}>
                  Alex Stevens
                </span>
                <span className="text-[11px] truncate w-full" style={{ fontFamily: 'JetBrains Mono, monospace', color: SIDEBAR_TEXT_SEC }}>
                  alex@aria.os
                </span>
              </div>
              <ChevronRight size={14} style={{ color: SIDEBAR_TEXT_SEC, opacity: 0.6 }} aria-hidden="true" />
            </>
          )}
        </button>
      </div>
    </aside>
  )
}
