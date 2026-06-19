'use client'

import { useState } from 'react'
import { TopNav } from '@/components/shell/TopNav'
import TabletDrawer from './TabletDrawer'

interface TabletShellProps {
  children: React.ReactNode
  breadcrumb?: { label: string; active?: boolean }[]
  notificationCount?: number
  onCommandCenter?: () => void
  onNewEntry?: () => void
  onNotificationOpen?: () => void
}

export default function TabletShell({
  children,
  breadcrumb,
  notificationCount = 0,
  onCommandCenter,
  onNewEntry,
  onNotificationOpen,
}: TabletShellProps) {
  const [drawerOpen, setDrawerOpen] = useState(false)

  const handleClose = () => setDrawerOpen(false)

  return (
    <div className="flex flex-col flex-1 min-w-0 h-screen overflow-hidden">
      <TopNav
        breadcrumb={breadcrumb}
        notificationCount={notificationCount}
        onSearchOpen={onCommandCenter}
        onMenuToggle={() => setDrawerOpen((v) => !v)}
        menuOpen={drawerOpen}
        onNotificationOpen={onNotificationOpen}
      />

      <TabletDrawer
        open={drawerOpen}
        onClose={handleClose}
        onCommandCenter={() => {
          setDrawerOpen(false)
          onCommandCenter?.()
        }}
        onNewEntry={() => {
          setDrawerOpen(false)
          onNewEntry?.()
        }}
      />

      <main
        id="main-content"
        className="flex-1 overflow-y-auto pt-16 px-6 pb-6"
        tabIndex={-1}
      >
        {children}
      </main>
    </div>
  )
}
