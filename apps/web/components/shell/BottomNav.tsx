'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Search, Sparkles, Bell, Menu } from 'lucide-react'

interface BottomNavProps {
  onSearchOpen: () => void
  onMenuToggle: () => void
  notificationCount?: number
}

export function BottomNav({ onSearchOpen, onMenuToggle, notificationCount = 0 }: BottomNavProps) {
  const pathname = usePathname()

  const isHomeActive = pathname === '/dashboard' || pathname === '/'
  const isAIActive = pathname.startsWith('/chat')

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 flex items-center justify-around px-2"
      style={{
        height: 64,
        background: 'rgba(53,52,56,0.9)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        borderTop: '1px solid rgba(70,70,79,0.2)',
        boxShadow: '0 -4px 20px rgba(99,102,241,0.2)',
        paddingBottom: 'env(safe-area-inset-bottom, 0px)',
      }}
      aria-label="Main navigation"
    >
      <Link
        href="/dashboard"
        className="flex flex-col items-center gap-1 min-w-[64px] min-h-[44px] justify-center rounded-xl transition-all"
        style={{ color: isHomeActive ? 'var(--accent-primary)' : 'var(--text-secondary)', background: isHomeActive ? 'color-mix(in srgb, var(--accent-primary) 15%, transparent)' : 'transparent' }}
        aria-label="Home"
        aria-current={isHomeActive ? 'page' : undefined}
      >
        <LayoutDashboard size={18} aria-hidden="true" />
        <span className="text-[11px]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
          Home
        </span>
      </Link>

      <button
        onClick={onSearchOpen}
        aria-label="Search"
        className="flex flex-col items-center gap-1 min-w-[64px] min-h-[44px] justify-center text-[var(--text-secondary)] hover:text-[var(--foreground)] transition-all"
      >
        <Search size={18} aria-hidden="true" />
        <span className="text-[11px]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
          Search
        </span>
      </button>

      <Link
        href="/chat"
        className="flex flex-col items-center gap-1 min-w-[64px] min-h-[44px] justify-center transition-all"
        style={{ color: isAIActive ? 'var(--accent-secondary)' : 'var(--text-secondary)' }}
        aria-label="AI Chat"
        aria-current={isAIActive ? 'page' : undefined}
      >
        <div className="relative">
          <Sparkles size={18} aria-hidden="true" />
          {isAIActive && (
            <div
              className="absolute inset-0 rounded-full opacity-30 blur-sm"
              style={{ background: 'var(--accent-neon)' }}
            />
          )}
        </div>
        <span className="text-[11px]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
          AI
        </span>
      </Link>

      <div
        className="flex flex-col items-center gap-1 min-w-[64px] min-h-[44px] justify-center text-[var(--text-secondary)] relative"
        role="status"
        aria-label={`${notificationCount > 0 ? `${notificationCount} notifications` : 'No notifications'}`}
      >
        <Bell size={18} aria-hidden="true" />
        <span className="text-[11px]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
          Alerts
        </span>
        {notificationCount > 0 && (
          <span
            className="absolute top-0.5 right-3 w-2 h-2 rounded-full"
            style={{ background: 'var(--accent-warning)', boxShadow: '0 0 8px var(--accent-glow-color-soft)' }}
          />
        )}
      </div>

      <button
        onClick={onMenuToggle}
        aria-label="Open navigation menu"
        className="flex flex-col items-center gap-1 min-w-[64px] min-h-[44px] justify-center text-[var(--text-secondary)] hover:text-[var(--foreground)] transition-all"
      >
        <Menu size={18} aria-hidden="true" />
        <span className="text-[11px]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
          Menu
        </span>
      </button>
    </nav>
  )
}
