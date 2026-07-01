import { api } from '@/lib/api'

const BASE = '/api/v1/skills'

export const skillService = {
  list: (params?: { category_id?: string; limit?: number; offset?: number }) =>
    api.get(`${BASE}/`, { params }),
  get: (id: string) => api.get(`${BASE}/${id}`),
  create: (data: Record<string, unknown>) => api.post(BASE, data),
  update: (id: string, data: Record<string, unknown>) => api.put(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete(`${BASE}/${id}`),

  categories: {
    list: (params?: { limit?: number; offset?: number }) =>
      api.get(`${BASE}/categories`, { params }),
    get: (id: string) => api.get(`${BASE}/categories/${id}`),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/categories`, data),
    update: (id: string, data: Record<string, unknown>) => api.put(`${BASE}/categories/${id}`, data),
    delete: (id: string) => api.delete(`${BASE}/categories/${id}`),
  },

  relationships: {
    list: (params?: { skill_id?: string; relationship_type?: string }) =>
      api.get(`${BASE}/relationships`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/relationships`, data),
    delete: (id: string) => api.delete(`${BASE}/relationships/${id}`),
  },

  tags: {
    list: (params?: { limit?: number; offset?: number }) =>
      api.get(`${BASE}/tags`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/tags`, data),
    delete: (id: string) => api.delete(`${BASE}/tags/${id}`),
    link: (skillId: string, tagId: string) =>
      api.post(`${BASE}/tags/link`, { skill_id: skillId, tag_id: tagId }),
  },

  userSkills: {
    list: (params?: { state?: string }) =>
      api.get(`${BASE}/user-skills`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/user-skills`, data),
    update: (id: string, data: Record<string, unknown>) =>
      api.put(`${BASE}/user-skills/${id}`, data),
    delete: (id: string) => api.delete(`${BASE}/user-skills/${id}`),
  },

  evidence: {
    list: (params?: { user_skill_id?: string }) =>
      api.get(`${BASE}/evidence`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/evidence`, data),
  },

  targets: {
    list: (params?: { status?: string }) =>
      api.get(`${BASE}/targets`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/targets`, data),
  },

  assessments: {
    list: (params?: { user_skill_id?: string }) =>
      api.get(`${BASE}/assessments`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/assessments`, data),
  },

  marketData: {
    list: (params?: { skill_id?: string }) =>
      api.get(`${BASE}/market-data`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/market-data`, data),
    update: (skillId: string, data: Record<string, unknown>) =>
      api.put(`${BASE}/market-data/${skillId}`, data),
  },

  income: {
    list: (params?: { skill_id?: string }) =>
      api.get(`${BASE}/income`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/income`, data),
  },

  certifications: {
    list: (params?: { skill_id?: string }) =>
      api.get(`${BASE}/certifications`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/certifications`, data),
    update: (id: string, data: Record<string, unknown>) =>
      api.put(`${BASE}/certifications/${id}`, data),
    delete: (id: string) => api.delete(`${BASE}/certifications/${id}`),
  },

  topics: {
    list: (params?: { skill_id?: string }) =>
      api.get(`${BASE}/topics`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/topics`, data),
    update: (id: string, data: Record<string, unknown>) =>
      api.put(`${BASE}/topics/${id}`, data),
    delete: (id: string) => api.delete(`${BASE}/topics/${id}`),
  },

  resources: {
    list: (params?: { skill_id?: string; resource_type?: string }) =>
      api.get(`${BASE}/resources`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/resources`, data),
    update: (id: string, data: Record<string, unknown>) =>
      api.put(`${BASE}/resources/${id}`, data),
    delete: (id: string) => api.delete(`${BASE}/resources/${id}`),
  },

  learningPaths: {
    list: (params?: { target_skill_id?: string }) =>
      api.get(`${BASE}/learning-paths`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/learning-paths`, data),
    update: (id: string, data: Record<string, unknown>) =>
      api.put(`${BASE}/learning-paths/${id}`, data),
    delete: (id: string) => api.delete(`${BASE}/learning-paths/${id}`),
  },

  recommendations: {
    list: (params?: { recommendation_type?: string }) =>
      api.get(`${BASE}/recommendations`, { params }),
    accept: (id: string) => api.put(`${BASE}/recommendations/${id}/accept`),
  },

  activity: {
    list: (params?: { activity_type?: string }) =>
      api.get(`${BASE}/activity`, { params }),
    log: (data: Record<string, unknown>) => api.post(`${BASE}/activity`, data),
  },

  externalMappings: {
    list: (params?: { skill_id?: string; system?: string }) =>
      api.get(`${BASE}/external-mappings`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/external-mappings`, data),
    update: (id: string, data: Record<string, unknown>) =>
      api.put(`${BASE}/external-mappings/${id}`, data),
    delete: (id: string) => api.delete(`${BASE}/external-mappings/${id}`),
  },

  roadmapDefinitions: {
    list: () => api.get(`${BASE}/roadmap-definitions`),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/roadmap-definitions`, data),
    update: (id: string, data: Record<string, unknown>) =>
      api.put(`${BASE}/roadmap-definitions/${id}`, data),
    delete: (id: string) => api.delete(`${BASE}/roadmap-definitions/${id}`),
  },

  forecasts: {
    list: (params?: { skill_id?: string }) =>
      api.get(`${BASE}/forecasts`, { params }),
    create: (data: Record<string, unknown>) => api.post(`${BASE}/forecasts`, data),
  },

  projectLinks: {
    create: (data: Record<string, unknown>) => api.post(`${BASE}/projects-link`, data),
    delete: (projectId: string, skillId: string) =>
      api.delete(`${BASE}/projects-link`, { params: { project_id: projectId, skill_id: skillId } }),
  },

  roadmapLinks: {
    create: (data: Record<string, unknown>) => api.post(`${BASE}/roadmaps-link`, data),
    delete: (roadmapId: string, skillId: string) =>
      api.delete(`${BASE}/roadmaps-link`, { params: { roadmap_id: roadmapId, skill_id: skillId } }),
  },

  opportunityLinks: {
    create: (data: Record<string, unknown>) => api.post(`${BASE}/opportunities-link`, data),
    delete: (opportunityId: string, skillId: string) =>
      api.delete(`${BASE}/opportunities-link`, { params: { opportunity_id: opportunityId, skill_id: skillId } }),
  },

  events: {
    create: (data: Record<string, unknown>) => api.post(`${BASE}/events`, data),
  },
}
