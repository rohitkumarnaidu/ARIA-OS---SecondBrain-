import { offlineQueue } from './queue'
import { offlineStorage } from './storage'

type SyncHandler = (operation: { type: 'create' | 'update' | 'delete'; table: string; data: unknown }) => Promise<void>

const syncHandlers = new Map<string, SyncHandler>()

export const syncManager = {
  registerHandler(table: string, handler: SyncHandler): void {
    syncHandlers.set(table, handler)
  },

  unregisterHandler(table: string): void {
    syncHandlers.delete(table)
  },

  async sync(): Promise<{ success: number; failed: number }> {
    let success = 0
    let failed = 0

    const operations = await offlineQueue.getAll()
    operations.sort((a, b) => a.timestamp - b.timestamp)

    for (const op of operations) {
      const handler = syncHandlers.get(op.table)
      if (!handler) {
        failed++
        if (op.id !== undefined) await offlineQueue.remove(op.id)
        continue
      }

      try {
        await handler({ type: op.type, table: op.table, data: op.data })
        if (op.id !== undefined) await offlineQueue.remove(op.id)
        success++
      } catch {
        if (op.retryCount >= 3) {
          if (op.id !== undefined) await offlineQueue.remove(op.id)
          failed++
        } else {
          if (op.id !== undefined) await offlineQueue.incrementRetry(op.id)
          failed++
        }
      }
    }

    return { success, failed }
  },

  async getPendingCount(): Promise<number> {
    return offlineQueue.getCount()
  },

  async clearAll(): Promise<void> {
    await offlineQueue.clear()
    await offlineStorage.clear()
  },
}

// Auto-sync when online
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    syncManager.sync()
  })
}
