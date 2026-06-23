import { api } from '@/lib/api'
import type {
  TaskCompletionForecast,
  HabitCompletionForecast,
  SleepInsight,
  SmartSlotResponse,
} from '@/lib/types'

interface CacheEntry<T> {
  data: T
  timestamp: number
  ttl: number
}

const inFlight = new Map<string, Promise<unknown>>()
const cache = new Map<string, CacheEntry<unknown>>()

const CACHE_TTL = {
  tasks: 5 * 60 * 1000,
  habits: 5 * 60 * 1000,
  sleep: 30 * 60 * 1000,
  slots: 60 * 60 * 1000,
}

function getCached<T>(key: string): T | null {
  const entry = cache.get(key)
  if (!entry) return null
  if (Date.now() - entry.timestamp > entry.ttl) {
    cache.delete(key)
    return null
  }
  return entry.data as T
}

function setCache<T>(key: string, data: T, ttl: number): void {
  cache.set(key, { data, timestamp: Date.now(), ttl })
}

async function dedupedFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number,
  fallback: () => Promise<T>,
): Promise<T> {
  const cached = getCached<T>(key)
  if (cached !== null) return cached

  if (typeof navigator !== 'undefined' && !navigator.onLine) {
    try {
      const result = await fallback()
      setCache(key, result, ttl)
      return result
    } catch {
      const stale = cache.get(key)?.data as T | undefined
      if (stale) return stale
      throw new Error('No prediction data available offline')
    }
  }

  if (inFlight.has(key)) {
    return inFlight.get(key) as Promise<T>
  }

  const promise = fetcher()
    .then((data) => {
      setCache(key, data, ttl)
      return data
    })
    .catch(async (err) => {
      try {
        const result = await fallback()
        setCache(key, result, ttl)
        return result
      } catch {
        const stale = cache.get(key)?.data as T | undefined
        if (stale) return stale
        throw err
      }
    })
    .finally(() => {
      inFlight.delete(key)
    })

  inFlight.set(key, promise)
  return promise
}

export const predictive = {
  async taskCompletion(): Promise<TaskCompletionForecast> {
    return dedupedFetch<TaskCompletionForecast>(
      'predictive:tasks',
      () => api.get<TaskCompletionForecast>('/api/v1/predictions/tasks'),
      CACHE_TTL.tasks,
      async () => ({
        total_pending: 0,
        high_completion: 0,
        at_risk_count: 0,
        predictions: [],
      }),
    )
  },

  async habits(): Promise<HabitCompletionForecast> {
    return dedupedFetch<HabitCompletionForecast>(
      'predictive:habits',
      () => api.get<HabitCompletionForecast>('/api/v1/predictions/habits'),
      CACHE_TTL.habits,
      async () => ({
        total_active: 0,
        at_risk_count: 0,
        predictions: [],
      }),
    )
  },

  async sleep(): Promise<SleepInsight> {
    return dedupedFetch<SleepInsight>(
      'predictive:sleep',
      () => api.get<SleepInsight>('/api/v1/predictions/sleep'),
      CACHE_TTL.sleep,
      async () => ({
        average_score: 0,
        average_duration: 0,
        trend: 'stable',
        recommendation: 'Track more sleep data for personalized insights.',
      }),
    )
  },

  async smartSlots(): Promise<SmartSlotResponse> {
    return dedupedFetch<SmartSlotResponse>(
      'predictive:slots',
      () => api.get<SmartSlotResponse>('/api/v1/predictions/slots'),
      CACHE_TTL.slots,
      async () => ({
        slots: [],
        best_hour: 9,
        best_day: 1,
      }),
    )
  },

  clearCache(): void {
    cache.clear()
  },

  invalidate(keys?: string[]): void {
    if (!keys) { cache.clear(); return }
    for (const key of keys) cache.delete(`predictive:${key}`)
  },
}
