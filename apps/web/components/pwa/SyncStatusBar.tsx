'use client'

import { useEffect, useState, useCallback } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { WifiOff, CheckCircle2, AlertTriangle, RefreshCw, Loader2 } from 'lucide-react'
import { useOfflineStore, syncManager } from '@/lib/offline'

type SyncBarState = 'hidden' | 'offline' | 'syncing' | 'success' | 'error'

export function SyncStatusBar() {
  const [barState, setBarState] = useState<SyncBarState>('hidden')
  const [syncProgress, setSyncProgress] = useState({ current: 0, total: 0 })
  const [dismissed, setDismissed] = useState(false)
  const {
    isOnline,
    pendingMutations,
    syncInProgress,
    lastSyncError,
    failedMutations,
  } = useOfflineStore()

  useEffect(() => {
    if (pendingMutations === 0 && failedMutations === 0) return

    if (!isOnline) {
      setBarState('offline')
      setDismissed(false)
    }
  }, [isOnline, pendingMutations, failedMutations])

  useEffect(() => {
    if (!isOnline) {
      setBarState('offline')
      setDismissed(false)
      return
    }

    if (syncInProgress) {
      setBarState('syncing')
      setDismissed(false)
      return
    }

    if (lastSyncError) {
      setBarState('error')
      setDismissed(false)
      return
    }

    if (barState === 'syncing' && !syncInProgress) {
      setBarState('success')
      setDismissed(false)
      const timer = setTimeout(() => {
        setBarState('hidden')
        setDismissed(true)
      }, 3000)
      return () => clearTimeout(timer)
    }

    if (pendingMutations > 0 && isOnline && !syncInProgress) {
      setBarState('error')
      setDismissed(false)
      return
    }

    if (failedMutations > 0 && isOnline) {
      setBarState('error')
      setDismissed(false)
      return
    }

    if (!syncInProgress && !lastSyncError && pendingMutations === 0 && dismissed && barState === 'hidden') {
      return
    }
  }, [isOnline, syncInProgress, lastSyncError, pendingMutations, failedMutations, barState, dismissed])

  useEffect(() => {
    if (!syncInProgress) return
    const poll = async () => {
      const pending = await syncManager.getPendingMutationCount()
      const count = useOfflineStore.getState().pendingMutations
      setSyncProgress({ current: Math.max(0, count - pending), total: count })
    }
    const interval = setInterval(poll, 500)
    return () => clearInterval(interval)
  }, [syncInProgress])

  const handleRetry = useCallback(async () => {
    await syncManager.retryFailed()
    useOfflineStore.setState({ lastSyncError: null })
    const store = useOfflineStore.getState()
    if (store.isOnline) {
      useOfflineStore.setState({ syncInProgress: true })
      setTimeout(async () => {
        try {
          const result = await syncManager.processSyncQueue()
          await syncManager.syncAll()
          const count = await syncManager.getPendingMutationCount()
          useOfflineStore.setState({
            pendingMutations: count,
            failedMutations: await syncManager.getFailedMutationCount(),
            lastSyncError: result.failed > 0 ? `${result.failed} mutations still failing.` : null,
          })
        } catch {
          // silent
        } finally {
          useOfflineStore.setState({ syncInProgress: false })
        }
      }, 0)
    }
  }, [])

  return (
    <AnimatePresence>
      {barState !== 'hidden' && !dismissed && (
        <motion.div
          initial={{ y: 60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 60, opacity: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="fixed bottom-4 left-1/2 z-50 -translate-x-1/2"
        >
          <div className={[
            'flex items-center gap-3 rounded-xl border px-4 py-3 shadow-lg backdrop-blur-[20px]',
            barState === 'offline' && 'border-accent-warning/30 bg-background-card shadow-accent-warning/5',
            barState === 'syncing' && 'border-accent-primary/30 bg-background-card shadow-accent-primary/10',
            barState === 'success' && 'border-accent-neon/30 bg-background-card shadow-accent-neon/5',
            barState === 'error' && 'border-accent-danger/30 bg-background-card shadow-accent-danger/5',
          ].join(' ')}>
            {barState === 'offline' && (
              <>
                <WifiOff size={16} className="text-accent-warning shrink-0" />
                <span className="text-sm text-text-primary">
                  Offline &mdash; changes will sync when connected
                </span>
              </>
            )}
            {barState === 'syncing' && (
              <>
                <Loader2 size={16} className="animate-spin text-accent-primary shrink-0" />
                <span className="text-sm text-text-primary">
                  Syncing...
                  {syncProgress.total > 0 && (
                    <span className="text-text-secondary ml-1">
                      ({syncProgress.current}/{syncProgress.total} items)
                    </span>
                  )}
                </span>
              </>
            )}
            {barState === 'success' && (
              <>
                <CheckCircle2 size={16} className="text-accent-neon shrink-0" />
                <span className="text-sm text-text-primary">All synced</span>
              </>
            )}
            {barState === 'error' && (
              <>
                <AlertTriangle size={16} className="text-accent-danger shrink-0" />
                <span className="text-sm text-text-primary">
                  {lastSyncError
                    ? `Sync failed. ${failedMutations} items pending.`
                    : `${pendingMutations} changes pending sync`}
                </span>
                <button
                  onClick={handleRetry}
                  className="flex items-center gap-1 rounded-lg bg-accent-primary/10 px-2.5 py-1 text-xs font-medium text-accent-primary transition-colors hover:bg-accent-primary/20"
                >
                  <RefreshCw size={12} />
                  Retry
                </button>
              </>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}