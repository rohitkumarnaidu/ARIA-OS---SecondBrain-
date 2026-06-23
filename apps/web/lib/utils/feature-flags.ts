interface FeatureFlag {
  key: string
  enabled: boolean
  rollout_percentage: number
  user_segments: string[]
  metadata: Record<string, unknown>
  updated_at: string
}

interface FlagEvaluation {
  key: string
  enabled: boolean
  variant: 'control' | 'treatment'
}

const API_BASE = '/api/v1/feature-flags'

async function getUserBucket(userId: string, key: string): Promise<number> {
  const input = `${userId}:${key}`
  const enc = new TextEncoder()
  const hash = await crypto.subtle.digest('SHA-256', enc.encode(input))
  const hex = Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
  return parseInt(hex.slice(0, 8), 16) % 100
}

class FeatureFlagClient {
  private cache: Map<string, FeatureFlag> = new Map()
  private evaluationCache: Map<string, FlagEvaluation> = new Map()
  private refreshInterval: number
  private refreshTimer: ReturnType<typeof setInterval> | null = null

  constructor(refreshIntervalMs = 60000) {
    this.refreshInterval = refreshIntervalMs
  }

  startAutoRefresh(): void {
    if (this.refreshTimer) return
    this.refreshTimer = setInterval(() => this.refresh(), this.refreshInterval)
  }

  stopAutoRefresh(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
      this.refreshTimer = null
    }
  }

  async refresh(): Promise<void> {
    try {
      const res = await fetch(API_BASE)
      if (!res.ok) return
      const body = await res.json()
      this.cache.clear()
      this.evaluationCache.clear()
      for (const flag of body.data ?? []) {
        this.cache.set(flag.key, flag)
      }
    } catch {
      // Silent fail — use cached values
    }
  }

  async isEnabled(key: string, userId?: string, defaultVal = false): Promise<boolean> {
    const flag = this.cache.get(key)
    if (!flag) return defaultVal
    if (!flag.enabled) return false
    if (flag.rollout_percentage >= 100) return true
    if (!userId) return flag.rollout_percentage > 0
    if (flag.user_segments?.includes(userId)) return true
    return (await getUserBucket(userId, key)) < flag.rollout_percentage
  }

  async getVariant(key: string, userId: string, defaultVal: 'control' | 'treatment' = 'control'): Promise<'control' | 'treatment'> {
    const flag = this.cache.get(key)
    if (!flag || !flag.enabled) return defaultVal
    if (flag.rollout_percentage >= 100) return 'treatment'
    if (flag.user_segments?.includes(userId)) return 'treatment'
    return (await getUserBucket(userId, key)) < flag.rollout_percentage ? 'treatment' : 'control'
  }

  async evaluate(key: string, userId: string): Promise<FlagEvaluation> {
    try {
      const res = await fetch(`${API_BASE}/${encodeURIComponent(key)}/evaluate`)
      if (res.ok) {
        const eval_ = await res.json()
        this.evaluationCache.set(key, eval_)
        return eval_
      }
    } catch {
      // Fall through
    }
    return {
      key,
      enabled: await this.isEnabled(key, userId),
      variant: await this.getVariant(key, userId),
    }
  }
}

export const featureFlags = new FeatureFlagClient()
export type { FeatureFlag, FlagEvaluation }
