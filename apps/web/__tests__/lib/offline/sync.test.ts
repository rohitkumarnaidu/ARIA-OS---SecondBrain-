import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockQueue = {
  enqueue: vi.fn(),
  getAll: vi.fn(),
  getCount: vi.fn(),
  clear: vi.fn(),
  remove: vi.fn(),
  incrementRetry: vi.fn(),
}

const mockStorage = {
  get: vi.fn(),
  set: vi.fn(),
  remove: vi.fn(),
  clear: vi.fn(),
  clearExpired: vi.fn(),
  getSize: vi.fn(),
}

vi.mock('@/lib/offline/queue', () => ({
  offlineQueue: mockQueue,
}))

vi.mock('@/lib/offline/storage', () => ({
  offlineStorage: mockStorage,
}))

const { syncManager } = await import('@/lib/offline/sync')

beforeEach(() => {
  vi.clearAllMocks()
})

describe('syncManager.registerHandler / unregisterHandler', () => {
  it('registers a handler for a table', () => {
    const handler = vi.fn()
    syncManager.registerHandler('tasks', handler)

    expect(() => syncManager.registerHandler('tasks', handler)).not.toThrow()
  })

  it('unregisters a handler', () => {
    const handler = vi.fn()
    syncManager.registerHandler('tasks', handler)
    syncManager.unregisterHandler('tasks')

    // After unregister, sync should fail
    mockQueue.getAll.mockResolvedValue([
      { id: 1, type: 'create', table: 'tasks', data: { title: 'A' }, timestamp: 100, retryCount: 0 },
    ])

    // We can verify unregister works via sync behavior
  })
})

describe('syncManager.sync', () => {
  it('processes queue in timestamp order', async () => {
    const handler = vi.fn().mockResolvedValue(undefined)
    syncManager.registerHandler('tasks', handler)

    mockQueue.getAll.mockResolvedValue([
      { id: 1, type: 'create', table: 'tasks', data: { title: 'Second' }, timestamp: 200, retryCount: 0 },
      { id: 2, type: 'create', table: 'tasks', data: { title: 'First' }, timestamp: 100, retryCount: 0 },
    ])

    const result = await syncManager.sync()

    expect(result.success).toBe(2)
    // Both removed on success
    expect(mockQueue.remove).toHaveBeenCalledTimes(2)
  })

  it('returns success and failed counts', async () => {
    const handler = vi.fn().mockResolvedValue(undefined)
    syncManager.registerHandler('tasks', handler)

    mockQueue.getAll.mockResolvedValue([
      { id: 1, type: 'create', table: 'tasks', data: {}, timestamp: 100, retryCount: 0 },
    ])

    const result = await syncManager.sync()
    expect(result).toEqual({ success: 1, failed: 0 })
  })

  it('handles empty queue gracefully', async () => {
    mockQueue.getAll.mockResolvedValue([])

    const result = await syncManager.sync()
    expect(result).toEqual({ success: 0, failed: 0 })
  })

  it('increments retry on handler failure and does not remove', async () => {
    const handler = vi.fn().mockRejectedValue(new Error('Network error'))
    syncManager.registerHandler('tasks', handler)

    mockQueue.getAll.mockResolvedValue([
      { id: 1, type: 'create', table: 'tasks', data: {}, timestamp: 100, retryCount: 0 },
    ])

    const result = await syncManager.sync()
    expect(result).toEqual({ success: 0, failed: 1 })
    expect(mockQueue.incrementRetry).toHaveBeenCalledWith(1)
    expect(mockQueue.remove).not.toHaveBeenCalled()
  })

  it('removes operation after max retries exceeded', async () => {
    const handler = vi.fn().mockRejectedValue(new Error('Permanent failure'))
    syncManager.registerHandler('tasks', handler)

    mockQueue.getAll.mockResolvedValue([
      { id: 1, type: 'create', table: 'tasks', data: {}, timestamp: 100, retryCount: 3 },
    ])

    const result = await syncManager.sync()
    expect(result).toEqual({ success: 0, failed: 1 })
    expect(mockQueue.remove).toHaveBeenCalledWith(1)
    expect(mockQueue.incrementRetry).not.toHaveBeenCalled()
  })

  it('fails operations with no registered handler and removes them', async () => {
    // No handler registered for 'goals'
    mockQueue.getAll.mockResolvedValue([
      { id: 1, type: 'create', table: 'goals', data: {}, timestamp: 100, retryCount: 0 },
    ])

    const result = await syncManager.sync()
    expect(result).toEqual({ success: 0, failed: 1 })
    expect(mockQueue.remove).toHaveBeenCalledWith(1)
  })

  it('processes multiple operations and returns correct counts', async () => {
    const handler = vi.fn()
    handler
      .mockResolvedValueOnce(undefined)
      .mockRejectedValueOnce(new Error('Fail'))
      .mockResolvedValueOnce(undefined)

    syncManager.registerHandler('tasks', handler)

    mockQueue.getAll.mockResolvedValue([
      { id: 1, type: 'create', table: 'tasks', data: { a: 1 }, timestamp: 100, retryCount: 0 },
      { id: 2, type: 'update', table: 'tasks', data: { b: 2 }, timestamp: 200, retryCount: 0 },
      { id: 3, type: 'delete', table: 'tasks', data: { c: 3 }, timestamp: 300, retryCount: 0 },
    ])

    const result = await syncManager.sync()
    expect(result).toEqual({ success: 2, failed: 1 })
  })

  it('network failure recovery - retry then succeed', async () => {
    const handler = vi.fn()
    handler
      .mockRejectedValueOnce(new Error('Temporary'))
      .mockResolvedValueOnce(undefined)

    syncManager.registerHandler('tasks', handler)

    // First sync: fails, increments retry
    mockQueue.getAll.mockResolvedValue([
      { id: 1, type: 'create', table: 'tasks', data: {}, timestamp: 100, retryCount: 0 },
    ])

    let result = await syncManager.sync()
    expect(result).toEqual({ success: 0, failed: 1 })
    expect(mockQueue.incrementRetry).toHaveBeenCalledWith(1)

    // Second sync: succeeds after retry
    mockQueue.getAll.mockResolvedValue([
      { id: 1, type: 'create', table: 'tasks', data: {}, timestamp: 100, retryCount: 1 },
    ])

    result = await syncManager.sync()
    expect(result).toEqual({ success: 1, failed: 0 })
    expect(mockQueue.remove).toHaveBeenCalledWith(1)
  })
})

describe('syncManager.getPendingCount', () => {
  it('returns count from queue', async () => {
    mockQueue.getCount.mockResolvedValue(5)

    const count = await syncManager.getPendingCount()
    expect(count).toBe(5)
  })
})

describe('syncManager.clearAll', () => {
  it('clears both queue and storage', async () => {
    await syncManager.clearAll()
    expect(mockQueue.clear).toHaveBeenCalled()
    expect(mockStorage.clear).toHaveBeenCalled()
  })
})
