'use client'

import { useEffect, useState, useCallback } from 'react'
import { Serwist } from '@serwist/window'
import { toast } from 'sonner'

export function PWAStatus() {
  const [isOnline, setIsOnline] = useState(true)
  const [updateAvailable, setUpdateAvailable] = useState(false)
  const [swInstance, setSwInstance] = useState<Serwist | null>(null)

  const handleUpdate = useCallback(() => {
    swInstance?.messageSkipWaiting()
    setUpdateAvailable(false)
    setTimeout(() => window.location.reload(), 500)
  }, [swInstance])

  useEffect(() => {
    setIsOnline(navigator.onLine)
    const onOnline = () => setIsOnline(true)
    const onOffline = () => {
      setIsOnline(false)
      toast.info('You are offline — using cached content')
    }
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [])

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_PWA_ENABLED !== 'true') return
    if (!('serviceWorker' in navigator)) return

    const sw = new Serwist('/sw.js')
    setSwInstance(sw)

    sw.addEventListener('waiting', () => {
      setUpdateAvailable(true)
      toast('A new version is available', {
        action: { label: 'Update', onClick: handleUpdate },
        duration: Infinity,
      })
    })

    sw.register({ immediate: true })

    return () => {
      swInstance?.messageSkipWaiting()
    }
  }, [handleUpdate])

  if (process.env.NEXT_PUBLIC_PWA_ENABLED !== 'true') return null

  return (
    <>
      {updateAvailable && (
        <div className="fixed bottom-4 right-4 z-50 flex items-center gap-3 rounded-xl border border-accent-primary/30 bg-background-card px-4 py-3 shadow-lg shadow-accent-primary/10">
          <div className="flex-shrink-0">
            <div className="h-2 w-2 animate-pulse rounded-full bg-accent-neon" />
          </div>
          <div className="flex flex-col">
            <p className="text-sm font-medium text-text-primary">Update available</p>
            <button
              onClick={handleUpdate}
              className="text-left text-xs text-accent-primary hover:underline"
            >
              Refresh to update
            </button>
          </div>
        </div>
      )}
      {!isOnline && (
        <div className="fixed bottom-4 left-4 z-50 rounded-xl border border-accent-warning/30 bg-background-card px-4 py-3 shadow-lg">
          <p className="text-sm text-accent-warning">You are offline</p>
        </div>
      )}
    </>
  )
}
