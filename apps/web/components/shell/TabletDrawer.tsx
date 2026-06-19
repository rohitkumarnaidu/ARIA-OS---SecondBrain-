'use client'

import { useEffect } from 'react'
import { Sidebar } from '@/components/layout'

interface TabletDrawerProps {
  open: boolean
  onClose: () => void
  onCommandCenter?: () => void
  onNewEntry?: () => void
}

export default function TabletDrawer({ open, onClose }: TabletDrawerProps) {
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

  if (!open) return null

  return (
    <>
      <div
        className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        className="fixed left-0 top-0 bottom-0 z-50 w-64 overflow-hidden bg-background-card border-r border-border shadow-2xl"
        role="dialog"
        aria-label="Navigation drawer"
        aria-modal="true"
      >
        <Sidebar />
      </div>
    </>
  )
}
