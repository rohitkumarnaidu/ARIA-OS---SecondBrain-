import { describe, it, expect } from 'vitest'
import { computeSentiment } from '@/lib/ai/sentiment'

describe('computeSentiment', () => {
  it('returns null when no signals present', () => {
    const result = computeSentiment({ taskAtRisk: 0, habitAtRisk: 0, sleepTrend: 'stable', avgSleepScore: 80 })
    expect(result).toBeNull()
  })

  it('returns null with exactly boundary values', () => {
    const result = computeSentiment({ taskAtRisk: 3, habitAtRisk: 2, sleepTrend: 'improving', avgSleepScore: 60 })
    expect(result).toBeNull()
  })

  it('returns low severity with task overload only', () => {
    const result = computeSentiment({ taskAtRisk: 5, habitAtRisk: 0, sleepTrend: 'stable', avgSleepScore: 80 })
    expect(result).toEqual({
      level: 'low',
      message: expect.stringContaining('quick wins'),
      signals: ['task-overload'],
    })
  })

  it('returns low severity with habit slip only', () => {
    const result = computeSentiment({ taskAtRisk: 0, habitAtRisk: 3, sleepTrend: 'stable', avgSleepScore: 80 })
    expect(result).toEqual({
      level: 'low',
      message: expect.stringContaining('quick wins'),
      signals: ['habit-slip'],
    })
  })

  it('returns medium severity with two signals', () => {
    const result = computeSentiment({ taskAtRisk: 5, habitAtRisk: 3, sleepTrend: 'stable', avgSleepScore: 80 })
    expect(result).toEqual({
      level: 'medium',
      message: expect.stringContaining('momentum'),
      signals: ['task-overload', 'habit-slip'],
    })
  })

  it('returns medium severity with sleep decline + poor sleep combo', () => {
    const result = computeSentiment({ taskAtRisk: 0, habitAtRisk: 0, sleepTrend: 'declining', avgSleepScore: 50 })
    expect(result).toEqual({
      level: 'medium',
      message: expect.stringContaining('attention'),
      signals: ['sleep-decline', 'poor-sleep'],
    })
  })

  it('returns high severity with three or more signals', () => {
    const result = computeSentiment({ taskAtRisk: 5, habitAtRisk: 3, sleepTrend: 'declining', avgSleepScore: 50 })
    expect(result).toEqual({
      level: 'high',
      message: expect.stringContaining('heavy'),
      signals: ['task-overload', 'habit-slip', 'sleep-decline', 'poor-sleep'],
    })
  })

  it('returns high severity with exactly three signals', () => {
    const result = computeSentiment({ taskAtRisk: 5, habitAtRisk: 3, sleepTrend: 'declining', avgSleepScore: 80 })
    expect(result).toEqual({
      level: 'high',
      message: expect.stringContaining('heavy'),
      signals: ['task-overload', 'habit-slip', 'sleep-decline'],
    })
  })

  it('does not include poor-sleep signal when avgSleepScore is 0', () => {
    const result = computeSentiment({ taskAtRisk: 0, habitAtRisk: 0, sleepTrend: 'declining', avgSleepScore: 0 })
    expect(result).toEqual({
      level: 'low',
      message: expect.any(String),
      signals: ['sleep-decline'],
    })
  })

  it('does not flag poor-sleep when avgSleepScore equals 60 exactly', () => {
    const result = computeSentiment({ taskAtRisk: 0, habitAtRisk: 0, sleepTrend: 'stable', avgSleepScore: 60 })
    expect(result).toBeNull()
  })

  it('handles all signals simultaneously', () => {
    const result = computeSentiment({ taskAtRisk: 10, habitAtRisk: 5, sleepTrend: 'declining', avgSleepScore: 40 })
    expect(result?.level).toBe('high')
    expect(result?.signals).toContain('task-overload')
    expect(result?.signals).toContain('habit-slip')
    expect(result?.signals).toContain('sleep-decline')
    expect(result?.signals).toContain('poor-sleep')
  })
})
