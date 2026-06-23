'use client'

import { useEffect, useState, useCallback } from 'react'
import { Download } from 'lucide-react'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export function PWAInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [showPrompt, setShowPrompt] = useState(false)

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_PWA_ENABLED !== 'true') return

    const handler = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e as BeforeInstallPromptEvent)
      setShowPrompt(true)
    }

    window.addEventListener('beforeinstallprompt', handler)

    return () => window.removeEventListener('beforeinstallprompt', handler)
  }, [])

  const handleInstall = useCallback(async () => {
    if (!deferredPrompt) return
    deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice
    if (outcome === 'accepted') setShowPrompt(false)
    setDeferredPrompt(null)
  }, [deferredPrompt])

  const handleDismiss = useCallback(() => {
    setShowPrompt(false)
    setDeferredPrompt(null)
  }, [])

  if (!showPrompt) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex items-center gap-3 rounded-xl border border-accent-primary/30 bg-background-card px-4 py-3 shadow-lg shadow-accent-primary/10">
      <div className="flex-shrink-0 rounded-lg bg-accent-primary/10 p-2">
        <Download className="h-5 w-5 text-accent-primary" />
      </div>
      <div className="flex flex-col">
        <p className="text-sm font-medium text-text-primary">Install ARIA OS</p>
        <p className="text-xs text-text-secondary">Add to your home screen for quick access</p>
      </div>
      <div className="flex items-center gap-2 ml-2">
        <button
          onClick={handleInstall}
          className="rounded-lg bg-accent-primary px-3 py-1.5 text-xs font-medium text-white hover:bg-accent-secondary transition-colors"
        >
          Install
        </button>
        <button
          onClick={handleDismiss}
          className="rounded-lg px-2 py-1.5 text-xs text-text-secondary hover:text-text-primary transition-colors"
        >
          Not now
        </button>
      </div>
    </div>
  )
}
