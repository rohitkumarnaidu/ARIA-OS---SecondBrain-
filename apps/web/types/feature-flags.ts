export interface FeatureFlag {
  key: string
  name: string
  description: string
  enabled: boolean
  rollout_percentage: number
  user_segments: string[]
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface FeatureFlagCreate {
  key: string
  name: string
  description: string
  enabled: boolean
  rollout_percentage: number
  user_segments: string[]
  metadata?: Record<string, unknown>
}

export interface FeatureFlagUpdate {
  enabled?: boolean
  rollout_percentage?: number
  user_segments?: string[]
  metadata?: Record<string, unknown>
}

export interface EvaluateResult {
  key: string
  enabled: boolean
  variant: string
}
