import { api } from '@/lib/api'
import type { Opportunity, OpportunityCreate, OpportunityUpdate } from '@/lib/types'

const BASE = '/api/v1/opportunities'

export const opportunityService = {
  list: () => api.get<Opportunity[]>(BASE),
  get: (id: string) => api.get<Opportunity>(`${BASE}/${id}`),
  create: (data: OpportunityCreate) => api.post<Opportunity>(BASE, data),
  update: (id: string, data: OpportunityUpdate) => api.put<Opportunity>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
