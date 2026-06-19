'use client'

import { useEffect, useCallback } from 'react'
import { useResponsive } from '@/hooks/useResponsive'
import { useCommandCenter } from '@/hooks/useCommandCenter'
import { useNotificationStore } from '@/lib/stores/notificationStore'
import { CommandCenter } from '@/components/command-center'
import { NotificationPanel } from '@/components/notifications/NotificationPanel'
import { DesktopShell } from './DesktopShell'
import TabletShell from './TabletShell'
import { MobileShell } from './MobileShell'

interface ShellSelectorProps {
  children: React.ReactNode
  breadcrumb?: { label: string; active?: boolean }[]
  notificationCount?: number
  onCommandCenter?: () => void
  onNewEntry?: () => void
}

export default function ShellSelector({
  children,
  breadcrumb,
  notificationCount,
  onCommandCenter: externalOnCommandCenter,
  onNewEntry,
}: ShellSelectorProps) {
  const { breakpoint } = useResponsive()
  const { isOpen, open, close } = useCommandCenter()
  const setPanelOpen = useNotificationStore((s) => s.setPanelOpen)
  const fetchNotifications = useNotificationStore((s) => s.fetch)
  const generateNudges = useNotificationStore((s) => s.generateNudges)

  useEffect(() => {
    fetchNotifications()
    generateNudges()
  }, [fetchNotifications, generateNudges])

  const handleCommandCenter = useCallback(() => {
    externalOnCommandCenter?.()
    open()
  }, [externalOnCommandCenter, open])

  const handleNotificationOpen = useCallback(() => {
    setPanelOpen(true)
  }, [setPanelOpen])

  const shellProps = {
    breadcrumb,
    notificationCount,
    onCommandCenter: handleCommandCenter,
    onNewEntry,
    onNotificationOpen: handleNotificationOpen,
  }

  return (
    <>
      {breakpoint === 'desktop' && <DesktopShell {...shellProps}>{children}</DesktopShell>}
      {breakpoint === 'tablet' && <TabletShell {...shellProps}>{children}</TabletShell>}
      {breakpoint === 'mobile' && <MobileShell {...shellProps}>{children}</MobileShell>}
      <CommandCenter isOpen={isOpen} onClose={close} />
      <NotificationPanel />
    </>
  )
}
