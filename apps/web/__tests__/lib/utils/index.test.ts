import { describe, it, expect } from 'vitest'
import * as utilsIndex from '@/lib/utils/index'

describe('utils barrel exports', () => {
  it('exports createLogger', () => {
    expect(utilsIndex.createLogger).toBeDefined()
    expect(typeof utilsIndex.createLogger).toBe('function')
  })

  it('exports trackEvent', () => {
    expect(utilsIndex.trackEvent).toBeDefined()
    expect(typeof utilsIndex.trackEvent).toBe('function')
  })

  it('exports trackPageView', () => {
    expect(utilsIndex.trackPageView).toBeDefined()
    expect(typeof utilsIndex.trackPageView).toBe('function')
  })

  it('exports measureAsync', () => {
    expect(utilsIndex.measureAsync).toBeDefined()
    expect(typeof utilsIndex.measureAsync).toBe('function')
  })

  it('has exactly 4 named exports', () => {
    const keys = Object.keys(utilsIndex).sort()
    expect(keys).toEqual(['createLogger', 'measureAsync', 'trackEvent', 'trackPageView'])
  })

  it('all exports are functions', () => {
    for (const [key, value] of Object.entries(utilsIndex)) {
      expect(typeof value, `${key} should be a function`).toBe('function')
    }
  })
})
