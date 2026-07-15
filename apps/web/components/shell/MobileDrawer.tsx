'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import type { LucideIcon } from 'lucide-react'
import { X, LayoutDashboard, CheckSquare, BookOpen, Youtube, FileText, Lightbulb, Target, Radar, Wallet, FolderKanban, GraduationCap, Moon, Clock, MessageCircle, Zap, Flag, Bell, Brain } from 'lucide-react'
import { clsx } from 'clsx'

interface MobileDrawerProps {
  open: boolean
  onClose: () => void
}

const workspaceItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Tasks', href: '/tasks', icon: CheckSquare },
  { name: 'Courses', href: '/courses', icon: BookOpen },
  { name: 'YouTube', href: '/youtube', icon: Youtube },
  { name: 'Resources', href: '/resources', icon: FileText },
  { name: 'Ideas', href: '/ideas', icon: Lightbulb },
  { name: 'Goals', href: '/goals', icon: Target },
]

const trackingItems = [
  { name: 'Opportunities', href: '/opportunities', icon: Radar },
  { name: 'Income', href: '/income', icon: Wallet },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Academics', href: '/academics', icon: GraduationCap },
  { name: 'Habits', href: '/habits', icon: Moon },
  { name: 'Sleep', href: '/sleep', icon: Moon },
  { name: 'Time', href: '/time', icon: Clock },
]

const systemItems = [
  { name: 'Chat', href: '/chat', icon: MessageCircle },
  { name: 'Automation', href: '/automation', icon: Zap },
  { name: 'Learning Insights', href: '/learning', icon: Brain },
  { name: 'Feature Flags', href: '/flags', icon: Flag },
]

function NavSection({ title, items, pathname, onItemClick }: { title: string; items: { name: string; href: string; icon: LucideIcon }[]; pathname: string; onItemClick: () => void }) {
  return (
    <div className="mb-6">
      <p
        className="text-[10px] uppercase tracking-widest px-3 mb-2"
        style={{ color: 'rgba(148,163,184,0.5)', fontFamily: 'JetBrains Mono, monospace' }}
      >
        {title}
      </p>
      <ul className="space-y-0.5">
        {items.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                onClick={onItemClick}
                className={clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors min-h-[44px] text-sm font-medium',
                  isActive
                    ? 'text-[var(--primary-foreground)]'
                    : 'text-[var(--text-tertiary)] hover:text-[var(--foreground)]',
                )}
                style={isActive ? { background: 'rgba(99,102,241,0.15)' } : undefined}
                aria-current={isActive ? 'page' : undefined}
                tabIndex={0}
              >
                <Icon size={20} aria-hidden="true" />
                {item.name}
              </Link>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

export function MobileDrawer({ open, onClose }: MobileDrawerProps) {
  const pathname = usePathname()
  const panelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  useEffect(() => {
    if (!open) return

    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, onClose])

  useEffect(() => {
    if (!open) return

    const panel = panelRef.current
    if (!panel) return

    const handleFocusTrap = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return
      const focusable = panel.querySelectorAll<HTMLElement>(
        'a[href], button, [tabindex]:not([tabindex="-1"])',
      )
      if (focusable.length === 0) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault()
          last.focus()
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault()
          first.focus()
        }
      }
    }

    panel.addEventListener('keydown', handleFocusTrap)
    return () => panel.removeEventListener('keydown', handleFocusTrap)
  }, [open])

  useEffect(() => {
    if (open) {
      const panel = panelRef.current
      if (panel) {
        const firstFocusable = panel.querySelector<HTMLElement>(
          'a[href], button, [tabindex]:not([tabindex="-1"])',
        )
        firstFocusable?.focus()
      }
    }
  }, [open])

  return (
    <>
      <div
        className="fixed inset-0 z-40"
        style={{
          background: 'rgba(10,11,15,0.7)',
          backdropFilter: 'blur(2px)',
          WebkitBackdropFilter: 'blur(2px)',
          opacity: open ? 1 : 0,
          pointerEvents: open ? 'auto' : 'none',
          transition: 'opacity 200ms ease-in-out',
        }}
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        ref={panelRef}
        id="navigation-drawer"
        className="fixed left-0 top-0 bottom-0 z-50 overflow-y-auto"
        style={{
          width: 256,
          maxWidth: '80vw',
          background: 'var(--surface-primary)',
          borderRight: '1px solid rgba(70,70,79,0.2)',
          transform: open ? 'translateX(0)' : 'translateX(-100%)',
          transition: 'transform 250ms ease-in-out',
        }}
        role="dialog"
        aria-modal="true"
        aria-label="Navigation drawer"
      >
        <div className="p-4 pb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold" style={{ fontFamily: 'Syne, sans-serif', color: 'var(--primary-foreground)' }}>
              ARIA OS
            </h2>
            <button
              onClick={onClose}
              className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg text-[var(--text-tertiary)] hover:text-[var(--foreground)] hover:bg-[var(--glass-light)] transition-all"
              aria-label="Close navigation menu"
            >
              <X size={20} aria-hidden="true" />
            </button>
          </div>

          <nav aria-label="Main navigation">
            <NavSection title="Workspace" items={workspaceItems} pathname={pathname} onItemClick={onClose} />
            <NavSection title="Tracking" items={trackingItems} pathname={pathname} onItemClick={onClose} />
            <NavSection title="System" items={systemItems} pathname={pathname} onItemClick={onClose} />
          </nav>
        </div>
      </div>
    </>
  )
}
