import { describe, it, expect, vi, beforeEach } from 'vitest'

function createMockStore() {
  const store = new Map<number, Record<string, unknown>>()
  let nextId = 1

  return {
    add: vi.fn(async (_storeName: string, value: Record<string, unknown>) => {
      const entry = { ...value, id: nextId }
      store.set(nextId, entry)
      nextId++
      return entry.id
    }),
    get: vi.fn(async (_storeName: string, id: number) => store.get(id) ?? null),
    getAll: vi.fn(async (_storeName: string) => Array.from(store.values())),
    count: vi.fn(async (_storeName: string) => store.size),
    clear: vi.fn(async (_storeName: string) => { store.clear() }),
    delete: vi.fn(async (_storeName: string, id: number) => { store.delete(id) }),
    put: vi.fn(async (_storeName: string, value: Record<string, unknown>) => {
      store.set(value.id as number, value)
    }),
    transaction: vi.fn(),
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

describe('offlineQueue.enqueue', () => {
  it('adds an operation with correct shape', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineQueue } = await import('@/lib/offline/queue')

    await offlineQueue.enqueue({ type: 'create', table: 'tasks', data: { title: 'Test' } })

    expect(store.add).toHaveBeenCalledOnce()
    const addedValue = store.add.mock.calls[0][1] as Record<string, unknown>
    expect(addedValue).toMatchObject({
      type: 'create',
      table: 'tasks',
      data: { title: 'Test' },
      retryCount: 0,
    })
    expect(typeof addedValue.timestamp).toBe('number')
  })

  it('enqueues update operation', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineQueue } = await import('@/lib/offline/queue')
    await offlineQueue.enqueue({ type: 'update', table: 'courses', data: { id: '1', progress: 50 } })

    expect(store.add).toHaveBeenCalledOnce()
    const added = store.add.mock.calls[0][1] as Record<string, unknown>
    expect(added.type).toBe('update')
  })
})

describe('offlineQueue.getAll', () => {
  it('returns empty array for empty queue', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineQueue } = await import('@/lib/offline/queue')
    const items = await offlineQueue.getAll()
    expect(items).toEqual([])
  })

  it('returns all queued items', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineQueue } = await import('@/lib/offline/queue')

    await offlineQueue.enqueue({ type: 'create', table: 'tasks', data: { title: 'A' } })
    await offlineQueue.enqueue({ type: 'create', table: 'tasks', data: { title: 'B' } })

    const items = await offlineQueue.getAll()
    expect(items.length).toBe(2)
  })
})

describe('offlineQueue.getCount', () => {
  it('returns correct count after enqueue', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineQueue } = await import('@/lib/offline/queue')

    store.count.mockResolvedValue(3)
    const count = await offlineQueue.getCount()
    expect(count).toBe(3)
  })
})

describe('offlineQueue.clear', () => {
  it('clears all operations', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineQueue } = await import('@/lib/offline/queue')
    await offlineQueue.clear()
    expect(store.clear).toHaveBeenCalledWith('operations')
  })
})

describe('offlineQueue.remove', () => {
  it('removes an operation by id', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineQueue } = await import('@/lib/offline/queue')
    await offlineQueue.remove(1)
    expect(store.delete).toHaveBeenCalledWith('operations', 1)
  })
})

describe('offlineQueue.incrementRetry', () => {
  it('increments retryCount for an operation', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineQueue } = await import('@/lib/offline/queue')

    store.get.mockResolvedValueOnce({
      id: 1, retryCount: 0, type: 'create', table: 'tasks', data: {}, timestamp: Date.now(),
    })
    await offlineQueue.incrementRetry(1)

    expect(store.put).toHaveBeenCalled()
  })

  it('does nothing if operation not found', async () => {
    const store = createMockStore()
    const { openDB } = await import('idb')
    ;(openDB as ReturnType<typeof vi.fn>).mockResolvedValue(store)

    const { offlineQueue } = await import('@/lib/offline/queue')
    store.get.mockResolvedValueOnce(null)
    await offlineQueue.incrementRetry(999)
    expect(store.put).not.toHaveBeenCalled()
  })
})
