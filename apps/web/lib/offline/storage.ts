import { openDB, type IDBPDatabase } from 'idb'

interface CacheEntry<T = unknown> {
  key: string
  data: T
  timestamp: number
  ttl: number // milliseconds
}

const DB_NAME = 'aria-offline-cache'
const DB_VERSION = 1
const STORE_NAME = 'cache'

let dbPromise: Promise<IDBPDatabase> | null = null

async function getDb(): Promise<IDBPDatabase> {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          const store = db.createObjectStore(STORE_NAME, { keyPath: 'key' })
          store.createIndex('by-timestamp', 'timestamp')
        }
      },
    })
  }
  return dbPromise
}

export const offlineStorage = {
  async get<T>(key: string): Promise<T | null> {
    const db = await getDb()
    const entry = await db.get(STORE_NAME, key)
    if (!entry) return null

    const isExpired = Date.now() - entry.timestamp > entry.ttl
    if (isExpired) {
      await db.delete(STORE_NAME, key)
      return null
    }

    return entry.data as T
  },

  async set<T>(key: string, data: T, ttl = 5 * 60 * 1000): Promise<void> {
    const db = await getDb()
    await db.put(STORE_NAME, {
      key,
      data,
      timestamp: Date.now(),
      ttl,
    })
  },

  async remove(key: string): Promise<void> {
    const db = await getDb()
    await db.delete(STORE_NAME, key)
  },

  async clear(): Promise<void> {
    const db = await getDb()
    await db.clear(STORE_NAME)
  },

  async clearExpired(): Promise<number> {
    const db = await getDb()
    const all = await db.getAll(STORE_NAME)
    let cleared = 0
    for (const entry of all) {
      if (Date.now() - entry.timestamp > entry.ttl) {
        await db.delete(STORE_NAME, entry.key)
        cleared++
      }
    }
    return cleared
  },

  async getSize(): Promise<number> {
    const db = await getDb()
    return db.count(STORE_NAME)
  },
}
