import { openDB, type IDBPDatabase } from 'idb'

const DB_NAME = 'secondbrain-offline'
const DB_VERSION = 1

const STORE_NAMES = [
  'tasks',
  'habits',
  'habit_logs',
  'courses',
  'goals',
  'ideas',
  'income',
  'projects',
  'resources',
  'sleep_logs',
  'time_entries',
  'chat_messages',
  'sync_queue',
] as const

export type StoreName = (typeof STORE_NAMES)[number]

interface StoredRecord<T = unknown> {
  id: string
  data: T
  syncedAt: string | null
  lastModified: string
}

interface SyncQueueItem {
  id?: number
  table: StoreName
  operation: 'create' | 'update' | 'delete'
  recordId?: string
  data: unknown
  timestamp: number
  retryCount: number
  failed: boolean
}

let dbPromise: Promise<IDBPDatabase> | null = null

function getDb(): Promise<IDBPDatabase> {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        for (const name of STORE_NAMES) {
          if (!db.objectStoreNames.contains(name)) {
            if (name === 'sync_queue') {
              const store = db.createObjectStore(name, {
                keyPath: 'id',
                autoIncrement: true,
              })
              store.createIndex('by-timestamp', 'timestamp')
              store.createIndex('by-failed', 'failed')
            } else {
              const store = db.createObjectStore(name, { keyPath: 'id' })
              store.createIndex('by-synced-at', 'syncedAt')
              store.createIndex('by-last-modified', 'lastModified')
            }
          }
        }
      },
    })
  }
  return dbPromise
}

function isIndexedDBAvailable(): boolean {
  try {
    return typeof indexedDB !== 'undefined' && !!indexedDB
  } catch {
    return false
  }
}

export const offlineDb = {
  isAvailable: isIndexedDBAvailable(),

  async getAll<T>(storeName: StoreName): Promise<StoredRecord<T>[]> {
    if (!isIndexedDBAvailable()) return []
    try {
      const db = await getDb()
      return (await db.getAll(storeName)) as StoredRecord<T>[]
    } catch (err) {
      console.error(`[offlineDb] Failed to getAll from ${storeName}:`, err)
      return []
    }
  },

  async get<T>(storeName: StoreName, id: string): Promise<StoredRecord<T> | undefined> {
    if (!isIndexedDBAvailable()) return undefined
    try {
      const db = await getDb()
      return (await db.get(storeName, id)) as StoredRecord<T> | undefined
    } catch (err) {
      console.error(`[offlineDb] Failed to get ${id} from ${storeName}:`, err)
      return undefined
    }
  },

  async put<T>(
    storeName: StoreName,
    id: string,
    data: T,
    syncedAt: string | null = null,
  ): Promise<void> {
    if (!isIndexedDBAvailable()) return
    try {
      const db = await getDb()
      await db.put(storeName, {
        id,
        data,
        syncedAt,
        lastModified: new Date().toISOString(),
      } satisfies StoredRecord<T>)
    } catch (err) {
      console.error(`[offlineDb] Failed to put ${id} into ${storeName}:`, err)
    }
  },

  async putMany<T>(
    storeName: StoreName,
    records: Array<{ id: string; data: T }>,
    syncedAt: string | null = null,
  ): Promise<void> {
    if (!isIndexedDBAvailable()) return
    try {
      const db = await getDb()
      const tx = db.transaction(storeName, 'readwrite')
      const now = new Date().toISOString()
      for (const { id, data } of records) {
        tx.store.put({
          id,
          data,
          syncedAt,
          lastModified: now,
        } satisfies StoredRecord<T>)
      }
      await tx.done
    } catch (err) {
      console.error(`[offlineDb] Failed to putMany into ${storeName}:`, err)
    }
  },

  async remove(storeName: StoreName, id: string): Promise<void> {
    if (!isIndexedDBAvailable()) return
    try {
      const db = await getDb()
      await db.delete(storeName, id)
    } catch (err) {
      console.error(`[offlineDb] Failed to delete ${id} from ${storeName}:`, err)
    }
  },

  async clearStore(storeName: StoreName): Promise<void> {
    if (!isIndexedDBAvailable()) return
    try {
      const db = await getDb()
      await db.clear(storeName)
    } catch (err) {
      console.error(`[offlineDb] Failed to clear ${storeName}:`, err)
    }
  },

  async count(storeName: StoreName): Promise<number> {
    if (!isIndexedDBAvailable()) return 0
    try {
      const db = await getDb()
      return db.count(storeName)
    } catch {
      return 0
    }
  },

  async getLastSyncTime(storeName: StoreName): Promise<string | null> {
    if (!isIndexedDBAvailable()) return null
    try {
      const db = await getDb()
      const records = await db.getAll(storeName)
      let latest: string | null = null
      for (const r of records) {
        if (r.syncedAt && (!latest || r.syncedAt > latest)) {
          latest = r.syncedAt
        }
      }
      return latest
    } catch {
      return null
    }
  },

  async getAllLastSyncTime(): Promise<string | null> {
    if (!isIndexedDBAvailable()) return null
    let latest: string | null = null
    for (const name of STORE_NAMES) {
      if (name === 'sync_queue') continue
      const t = await this.getLastSyncTime(name)
      if (t && (!latest || t > latest)) {
        latest = t
      }
    }
    return latest
  },

  async getSyncQueueItems(): Promise<SyncQueueItem[]> {
    if (!isIndexedDBAvailable()) return []
    try {
      const db = await getDb()
      return (await db.getAll('sync_queue')) as SyncQueueItem[]
    } catch {
      return []
    }
  },

  async enqueueSync(
    table: StoreName,
    operation: SyncQueueItem['operation'],
    recordId: string | undefined,
    data: unknown,
  ): Promise<void> {
    if (!isIndexedDBAvailable()) return
    try {
      const db = await getDb()
      await db.add('sync_queue', {
        table,
        operation,
        recordId,
        data,
        timestamp: Date.now(),
        retryCount: 0,
        failed: false,
      })
    } catch (err) {
      console.error('[offlineDb] Failed to enqueue sync:', err)
    }
  },

  async dequeueSync(): Promise<SyncQueueItem | undefined> {
    if (!isIndexedDBAvailable()) return undefined
    try {
      const db = await getDb()
      const items = await db.getAllFromIndex('sync_queue', 'by-timestamp')
      const pending = items
        .filter((i) => !i.failed)
        .sort((a, b) => a.timestamp - b.timestamp)
      if (pending.length === 0) return undefined
      return pending[0]
    } catch {
      return undefined
    }
  },

  async removeSyncItem(id: number): Promise<void> {
    if (!isIndexedDBAvailable()) return
    try {
      const db = await getDb()
      await db.delete('sync_queue', id)
    } catch {
      // silent
    }
  },

  async updateSyncRetry(id: number): Promise<void> {
    if (!isIndexedDBAvailable()) return
    try {
      const db = await getDb()
      const item = await db.get('sync_queue', id)
      if (item) {
        item.retryCount++
        if (item.retryCount >= 3) {
          item.failed = true
        }
        await db.put('sync_queue', item)
      }
    } catch {
      // silent
    }
  },

  async getPendingSyncCount(): Promise<number> {
    if (!isIndexedDBAvailable()) return 0
    try {
      const db = await getDb()
      const all = await db.getAll('sync_queue')
      return all.filter((i) => !i.failed).length
    } catch {
      return 0
    }
  },

  async getFailedSyncCount(): Promise<number> {
    if (!isIndexedDBAvailable()) return 0
    try {
      const db = await getDb()
      const all = await db.getAll('sync_queue')
      return all.filter((i) => i.failed).length
    } catch {
      return 0
    }
  },

  async retryFailedSyncItems(): Promise<void> {
    if (!isIndexedDBAvailable()) return
    try {
      const db = await getDb()
      const all = await db.getAll('sync_queue')
      for (const item of all) {
        if (item.failed) {
          item.retryCount = 0
          item.failed = false
          await db.put('sync_queue', item)
        }
      }
    } catch {
      // silent
    }
  },

  async clearSyncQueue(): Promise<void> {
    if (!isIndexedDBAvailable()) return
    try {
      const db = await getDb()
      await db.clear('sync_queue')
    } catch {
      // silent
    }
  },

  async clearAllData(): Promise<void> {
    if (!isIndexedDBAvailable()) return
    for (const name of STORE_NAMES) {
      await this.clearStore(name)
    }
  },
}

export type { StoredRecord, SyncQueueItem }