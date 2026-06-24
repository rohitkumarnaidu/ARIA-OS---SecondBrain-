import { describe, it, expect, vi, beforeEach } from 'vitest'
import { featureFlags } from '@/lib/utils/feature-flags'

const mockUserHash = 42

beforeEach(async () => {
  featureFlags.stopAutoRefresh()
  // Reset internal cache by refreshing with empty response
  vi.spyOn(globalThis, 'fetch').mockResolvedValue({
    ok: true,
    json: async () => ({ data: [] }),
  } as Response)
  await featureFlags.refresh()

  // Mock crypto.subtle.digest for deterministic hashing
  const subtleDigest = vi.spyOn(crypto.subtle, 'digest')
  subtleDigest.mockImplementation(async (_algo: string, _data: BufferSource) => {
    const hash = new Uint8Array(32)
    hash[0] = 0x2a // 42
    return hash.buffer as ArrayBuffer
  })
})

describe('isEnabled', () => {
  it('returns default value for missing flag', async () => {
    const result = await featureFlags.isEnabled('non_existent_flag', 'user1', true)
    expect(result).toBe(true)
  })

  it('returns false for a disabled flag', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: [{ key: 'test_flag', enabled: false, rollout_percentage: 0, user_segments: [], metadata: {}, updated_at: '' }],
      }),
    } as Response)
    await featureFlags.refresh()
    const result = await featureFlags.isEnabled('test_flag', 'user1')
    expect(result).toBe(false)
  })

  it('returns true when rollout_percentage is 100', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: [{ key: 'full_rollout', enabled: true, rollout_percentage: 100, user_segments: [], metadata: {}, updated_at: '' }],
      }),
    } as Response)
    await featureFlags.refresh()
    const result = await featureFlags.isEnabled('full_rollout', 'user1')
    expect(result).toBe(true)
  })

  it('returns true when user is in user_segments', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: [{ key: 'segment_flag', enabled: true, rollout_percentage: 0, user_segments: ['vip_user'], metadata: {}, updated_at: '' }],
      }),
    } as Response)
    await featureFlags.refresh()
    const result = await featureFlags.isEnabled('segment_flag', 'vip_user')
    expect(result).toBe(true)
  })

  it('returns false when user is not in rollout', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: [{ key: 'partial_flag', enabled: true, rollout_percentage: 0, user_segments: [], metadata: {}, updated_at: '' }],
      }),
    } as Response)
    await featureFlags.refresh()
    const result = await featureFlags.isEnabled('partial_flag', 'user1')
    // 0% rollout → false
    expect(result).toBe(false)
  })

  it('handles fetch failure gracefully', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('Network error'))
    // Should not throw
    await expect(featureFlags.refresh()).resolves.not.toThrow()
  })
})

describe('evaluate', () => {
  it('returns evaluation with key and enabled status', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: [{ key: 'test_flag', enabled: true, rollout_percentage: 50, user_segments: [], metadata: {}, updated_at: '' }],
      }),
    } as Response)
    await featureFlags.refresh()

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: false,
      status: 404,
    } as Response)

    const evalResult = await featureFlags.evaluate('test_flag', 'user1')
    expect(evalResult).toHaveProperty('key', 'test_flag')
    expect(evalResult).toHaveProperty('enabled')
    expect(evalResult).toHaveProperty('variant')
    expect(['control', 'treatment']).toContain(evalResult.variant)
  })
})

describe('auto refresh', () => {
  it('startAutoRefresh sets an interval', () => {
    const spy = vi.spyOn(globalThis, 'setInterval')
    featureFlags.startAutoRefresh()
    expect(spy).toHaveBeenCalled()
    featureFlags.stopAutoRefresh()
  })

  it('stopAutoRefresh clears the interval', () => {
    const spy = vi.spyOn(globalThis, 'clearInterval')
    featureFlags.startAutoRefresh()
    featureFlags.stopAutoRefresh()
    expect(spy).toHaveBeenCalled()
  })

  it('startAutoRefresh is idempotent', () => {
    const spy = vi.spyOn(globalThis, 'setInterval')
    featureFlags.startAutoRefresh()
    featureFlags.startAutoRefresh()
    expect(spy).toHaveBeenCalledTimes(1)
    featureFlags.stopAutoRefresh()
  })
})
