import { openDB, type IDBPDatabase } from 'idb'

interface QueuedOperation {
  id?: number
  type: 'create' | 'update' | 'delete'
  table: string
  data: unknown
  timestamp: number
  retryCount: number
}

const DB_NAME = 'aria-offline-queue'
const DB_VERSION = 1
const STORE_NAME = 'operations'

let dbPromise: Promise<IDBPDatabase> | null = null

async function getDb(): Promise<IDBPDatabase> {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          const store = db.createObjectStore(STORE_NAME, {
            keyPath: 'id',
            autoIncrement: true,
          })
          store.createIndex('by-timestamp', 'timestamp')
        }
      },
    })
  }
  return dbPromise
}

export const offlineQueue = {
  async enqueue(operation: Omit<QueuedOperation, 'id' | 'timestamp' | 'retryCount'>): Promise<void> {
    const db = await getDb()
    await db.add(STORE_NAME, {
      ...operation,
      timestamp: Date.now(),
      retryCount: 0,
    })
  },

  async dequeue(): Promise<QueuedOperation | undefined> {
    const db = await getDb()
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    const cursor = await store.openCursor(null, 'prev')
    if (cursor) {
      const operation = cursor.value
      await cursor.delete()
      return operation
    }
    return undefined
  },

  async getAll(): Promise<QueuedOperation[]> {
    const db = await getDb()
    return db.getAll(STORE_NAME)
  },

  async getCount(): Promise<number> {
    const db = await getDb()
    return db.count(STORE_NAME)
  },

  async clear(): Promise<void> {
    const db = await getDb()
    await db.clear(STORE_NAME)
  },

  async remove(id: number): Promise<void> {
    const db = await getDb()
    await db.delete(STORE_NAME, id)
  },

  async incrementRetry(id: number): Promise<void> {
    const db = await getDb()
    const operation = await db.get(STORE_NAME, id)
    if (operation) {
      operation.retryCount++
      await db.put(STORE_NAME, operation)
    }
  },
}
