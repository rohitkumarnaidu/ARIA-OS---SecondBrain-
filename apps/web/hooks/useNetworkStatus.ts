'use client'

import { useEffect, useState, useCallback } from 'react'
import { syncManager, useOfflineStore } from '@/lib/offline'

export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(true)
  const {
    setOnline,
    setPendingMutations,
    setSyncInProgress,
    setSyncError,
    setLastSyncAt,
  } = useOfflineStore.getState()

  const sync = useCallback(async () => {
    const store = useOfflineStore.getState()
    if (store.syncInProgress) return

    useOfflineStore.setState({ syncInProgress: true, lastSyncError: null })
    try {
      const pending = await syncManager.getPendingMutationCount()
      if (pending > 0) {
        const result = await syncManager.processSyncQueue()
        if (result.failed > 0) {
          useOfflineStore.setState({
            lastSyncError: `${result.failed} mutations failed after 3 retries.`,
          })
        }
      }
      await syncManager.syncAll()
      const lastSync = await syncManager.getLastSyncTime()
      const count = await syncManager.getPendingMutationCount()
      useOfflineStore.setState({
        lastSyncAt: lastSync,
        pendingMutations: count,
        failedMutations: await syncManager.getFailedMutationCount(),
      })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Sync failed'
      useOfflineStore.setState({ lastSyncError: message })
    } finally {
      useOfflineStore.setState({ syncInProgress: false })
    }
  }, [])

  useEffect(() => {
    setIsOnline(navigator.onLine)

    const handleOnline = async () => {
      setIsOnline(true)
      useOfflineStore.setState({ isOnline: true })
      const pending = await syncManager.getPendingMutationCount()
      if (pending > 0) {
        sync()
      }
    }

    const handleOffline = () => {
      setIsOnline(false)
      useOfflineStore.setState({ isOnline: false })
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [sync])

  return { isOnline, sync }
}