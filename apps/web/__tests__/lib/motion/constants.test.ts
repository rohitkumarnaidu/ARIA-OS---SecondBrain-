import { describe, it, expect } from 'vitest'
import { DURATION, MOTION_DURATION, EASING, STAGGER } from '@/lib/motion/constants'

describe('DURATION', () => {
  it('has all presets as numbers within expected range', () => {
    expect(DURATION.fast).toBe(150)
    expect(DURATION.normal).toBe(200)
    expect(DURATION.slow).toBe(300)
    expect(DURATION.slower).toBe(500)
    expect(DURATION.slowest).toBe(1000)
  })

  it('all values are positive numbers', () => {
    for (const val of Object.values(DURATION)) {
      expect(typeof val).toBe('number')
      expect(val).toBeGreaterThan(0)
    }
  })

  it('values are in ascending order', () => {
    const values = Object.values(DURATION)
    for (let i = 1; i < values.length; i++) {
      expect(values[i]).toBeGreaterThan(values[i - 1])
    }
  })
})

describe('MOTION_DURATION', () => {
  it('has all presets as numbers within expected range', () => {
    expect(MOTION_DURATION.fast).toBe(0.15)
    expect(MOTION_DURATION.normal).toBe(0.2)
    expect(MOTION_DURATION.slow).toBe(0.3)
    expect(MOTION_DURATION.slower).toBe(0.5)
    expect(MOTION_DURATION.slowest).toBe(1)
  })

  it('all values are between 0 and 2', () => {
    for (const val of Object.values(MOTION_DURATION)) {
      expect(typeof val).toBe('number')
      expect(val).toBeGreaterThan(0)
      expect(val).toBeLessThanOrEqual(2)
    }
  })
})

describe('EASING', () => {
  it('has all easing presets as arrays of length 4', () => {
    for (const [key, val] of Object.entries(EASING)) {
      expect(Array.isArray(val), `${key} should be an array`).toBe(true)
      expect(val).toHaveLength(4)
      for (const num of val) {
        expect(typeof num).toBe('number')
      }
    }
  })

  it('has expected easing curves', () => {
    expect(EASING.default).toEqual([0.4, 0, 0.2, 1])
    expect(EASING.in).toEqual([0.4, 0, 1, 1])
    expect(EASING.out).toEqual([0, 0, 0.2, 1])
    expect(EASING.bounce).toEqual([0.68, -0.55, 0.265, 1.55])
    expect(EASING.elastic).toEqual([0.68, -0.6, 0.32, 1.6])
    expect(EASING.smooth).toEqual([0.16, 1, 0.3, 1])
  })
})

describe('STAGGER', () => {
  it('has stagger presets with staggerChildren and delayChildren', () => {
    expect(STAGGER.fast).toEqual({ staggerChildren: 0.04, delayChildren: 0.05 })
    expect(STAGGER.normal).toEqual({ staggerChildren: 0.08, delayChildren: 0.1 })
    expect(STAGGER.slow).toEqual({ staggerChildren: 0.12, delayChildren: 0.15 })
  })

  it('stagger values increase with speed', () => {
    expect(STAGGER.fast.staggerChildren).toBeLessThan(STAGGER.normal.staggerChildren)
    expect(STAGGER.normal.staggerChildren).toBeLessThan(STAGGER.slow.staggerChildren)
  })
})
