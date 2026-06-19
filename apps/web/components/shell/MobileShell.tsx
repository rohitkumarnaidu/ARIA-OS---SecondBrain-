'use client'

import { useState, useCallback } from 'react'
import { BottomNav } from './BottomNav'
import { MobileDrawer } from './MobileDrawer'

interface MobileShellProps {
  children: React.ReactNode
  notificationCount?: number
  onCommandCenter?: () => void
}

export function MobileShell({ children, notificationCount = 0, onCommandCenter }: MobileShellProps) {
  const [drawerOpen, setDrawerOpen] = useState(false)

  const toggleDrawer = useCallback(() => {
    setDrawerOpen((v) => !v)
  }, [])

  const closeDrawer = useCallback(() => {
    setDrawerOpen(false)
  }, [])

  const handleSearchOpen = useCallback(() => {
    onCommandCenter?.()
  }, [onCommandCenter])

  return (
    <div
      className="flex flex-col min-h-screen pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)] pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)]"
    >
      <div className="flex-1 pt-4 pb-20">
        {children}
      </div>

      <BottomNav
        onSearchOpen={handleSearchOpen}
        onMenuToggle={toggleDrawer}
        notificationCount={notificationCount}
      />

      <MobileDrawer
        open={drawerOpen}
        onClose={closeDrawer}
      />
    </div>
  )
}
