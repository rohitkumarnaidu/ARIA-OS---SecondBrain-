'use client'

import DesktopSidebar from './DesktopSidebar'
import { TopNav } from './TopNav'

interface DesktopShellProps {
  children: React.ReactNode
  breadcrumb?: { label: string; active?: boolean }[]
  notificationCount?: number
  onCommandCenter?: () => void
  onNewEntry?: () => void
  onNotificationOpen?: () => void
}

export function DesktopShell({
  children,
  breadcrumb,
  notificationCount = 0,
  onCommandCenter,
  onNewEntry,
  onNotificationOpen,
}: DesktopShellProps) {
  return (
    <div className="flex h-screen overflow-hidden w-full bg-background">
      {/* Desktop Sidebar — always visible ≥1024px (enforced by ShellSelector) */}
      <div className="hidden lg:flex h-full shrink-0">
        <DesktopSidebar
          onCommandCenter={onCommandCenter}
          onNewEntry={onNewEntry}
        />
      </div>

      {/* Main content area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopNav
          onSearchOpen={onCommandCenter}
          breadcrumb={breadcrumb}
          notificationCount={notificationCount}
          onNotificationOpen={onNotificationOpen}
        />
        <main
          id="main-content"
          className="flex-1 overflow-y-auto px-6 py-6"
          tabIndex={-1}
        >
          {children}
        </main>
      </div>

      {/* AI Dock — right sidebar, visible ≥768px */}
      <div
        className="hidden md:flex flex-col shrink-0 w-12 items-center pt-6 gap-4 border-l border-border"
        style={{ background: 'var(--background)' }}
        role="complementary"
        aria-label="AI dock"
      />
    </div>
  )
}
