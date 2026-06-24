import { describe, it, expect, vi, beforeEach } from 'vitest'
import { measureAsync } from '@/lib/utils/performance'

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('measureAsync', () => {
  it('returns the resolved value of the function', async () => {
    const result = await measureAsync('test', async () => 'hello')
    expect(result).toBe('hello')
  })

  it('returns the resolved numeric value', async () => {
    const result = await measureAsync('test', async () => 42)
    expect(result).toBe(42)
  })

  it('re-throws errors from the function', async () => {
    await expect(
      measureAsync('test', async () => { throw new Error('fail') })
    ).rejects.toThrow('fail')
  })

  it('calls the function exactly once', async () => {
    const fn = vi.fn().mockResolvedValue('done')
    await measureAsync('test', fn)
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('measures duration using performance.now', async () => {
    const spy = vi.spyOn(performance, 'now')
    await measureAsync('test', async () => 'ok')
    expect(spy).toHaveBeenCalledTimes(2)
  })

  it('handles async functions that take time to resolve', async () => {
    const result = await measureAsync('test', async () => {
      await new Promise(r => setTimeout(r, 5))
      return 'slow'
    })
    expect(result).toBe('slow')
  }, 10000)

  it('does not modify the return type', async () => {
    const obj = { a: 1, b: 'two' }
    const result = await measureAsync('test', async () => obj)
    expect(result).toEqual(obj)
  })
})
