import { describe, it, expect, vi, beforeEach } from 'vitest'

type Entry = { key: string; data: unknown; timestamp: number; ttl: number }

function createMockStore() {
  const store = new Map<string, Entry>()

  return {
    get: vi.fn(async (_storeName: string, key: string) => store.get(key) ?? null),
    put: vi.fn(async (_storeName: string, entry: Entry) => { store.set(entry.key, entry) }),
    delete: vi.fn(async (_storeName: string, key: string) => { store.delete(key) }),
    clear: vi.fn(async (_storeName: string) => { store.clear() }),
    getAll: vi.fn(async (_storeName: string) => Array.from(store.values())),
    count: vi.fn(async (_storeName: string) => store.size),
    add: vi.fn(),
    objectStoreNames: { contains: vi.fn().mockReturnValue(true) },
  }
}

vi.mock('idb', () => ({
  openDB: vi.fn(),
}))

beforeEach(async () => {
  vi.clearAllMocks()
  vi.resetModules()
})

describe('offlineStorage.set', () => {
  it('stores data with default TTL of 5 minutes', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineStorage } = await import('@/lib/offline/storage')
    await offlineStorage.set('key1', { hello: 'world' })

    expect(store.put).toHaveBeenCalledOnce()
    const entry = store.put.mock.calls[0][1] as Entry
    expect(entry.key).toBe('key1')
    expect(entry.data).toEqual({ hello: 'world' })
    expect(entry.ttl).toBe(5 * 60 * 1000)
    expect(typeof entry.timestamp).toBe('number')
  })

  it('stores data with custom TTL', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineStorage } = await import('@/lib/offline/storage')
    await offlineStorage.set('key2', 'value', 1000)

    const entry = store.put.mock.calls[0][1] as Entry
    expect(entry.ttl).toBe(1000)
  })
})

describe('offlineStorage.get', () => {
  it('returns stored data when key exists and not expired', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)
    store.get.mockResolvedValueOnce({
      key: 'key1', data: { message: 'hello' }, timestamp: Date.now(), ttl: 60000,
    })

    const { offlineStorage } = await import('@/lib/offline/storage')
    const result = await offlineStorage.get<{ message: string }>('key1')
    expect(result).toEqual({ message: 'hello' })
  })

  it('returns null for non-existent key', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineStorage } = await import('@/lib/offline/storage')
    const result = await offlineStorage.get('nonexistent')
    expect(result).toBeNull()
  })

  it('returns null and deletes expired entry', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)
    store.get.mockResolvedValueOnce({
      key: 'expired', data: 'old', timestamp: Date.now() - 100000, ttl: 100,
    })

    const { offlineStorage } = await import('@/lib/offline/storage')
    const result = await offlineStorage.get('expired')
    expect(result).toBeNull()
    expect(store.delete).toHaveBeenCalledWith('cache', 'expired')
  })

  it('returns data when within TTL', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)
    store.get.mockResolvedValueOnce({
      key: 'fresh', data: 'still valid', timestamp: Date.now() - 500, ttl: 60000,
    })

    const { offlineStorage } = await import('@/lib/offline/storage')
    const result = await offlineStorage.get<string>('fresh')
    expect(result).toBe('still valid')
  })
})

describe('offlineStorage.remove', () => {
  it('removes an entry by key', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineStorage } = await import('@/lib/offline/storage')
    await offlineStorage.remove('key1')
    expect(store.delete).toHaveBeenCalledWith('cache', 'key1')
  })
})

describe('offlineStorage.clear', () => {
  it('clears all entries', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineStorage } = await import('@/lib/offline/storage')
    await offlineStorage.clear()
    expect(store.clear).toHaveBeenCalledWith('cache')
  })
})

describe('offlineStorage.clearExpired', () => {
  it('removes expired entries and returns count', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)
    const now = Date.now()
    store.getAll.mockResolvedValueOnce([
      { key: 'fresh', data: 'a', timestamp: now, ttl: 60000 },
      { key: 'stale', data: 'b', timestamp: now - 100000, ttl: 100 },
      { key: 'expired', data: 'c', timestamp: now - 50000, ttl: 1000 },
    ])

    const { offlineStorage } = await import('@/lib/offline/storage')
    const count = await offlineStorage.clearExpired()
    expect(count).toBe(2)
    expect(store.delete).toHaveBeenCalledWith('cache', 'stale')
    expect(store.delete).toHaveBeenCalledWith('cache', 'expired')
    expect(store.delete).not.toHaveBeenCalledWith('cache', 'fresh')
  })
})

describe('offlineStorage.getSize', () => {
  it('returns number of cached entries', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)
    store.count.mockResolvedValue(3)

    const { offlineStorage } = await import('@/lib/offline/storage')
    const count = await offlineStorage.getSize()
    expect(count).toBe(3)
  })
})
