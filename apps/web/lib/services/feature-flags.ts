import { api } from '@/lib/api'
import type { FeatureFlag, FeatureFlagCreate, FeatureFlagUpdate, EvaluateResult } from '@/types/feature-flags'

const BASE = '/api/v1/feature-flags'

export const featureFlagService = {
  list: () => api.get<{ data: FeatureFlag[] }>(BASE),

  get: (key: string) => api.get<FeatureFlag>(`${BASE}/${encodeURIComponent(key)}`),

  evaluate: (key: string) => api.get<EvaluateResult>(`${BASE}/${encodeURIComponent(key)}/evaluate`),

  create: (data: FeatureFlagCreate) => api.post<FeatureFlag>(BASE, data),

  update: (key: string, data: FeatureFlagUpdate) =>
    api.put<FeatureFlag>(`${BASE}/${encodeURIComponent(key)}`, data),

  delete: (key: string) => api.delete<void>(`${BASE}/${encodeURIComponent(key)}`),
}
