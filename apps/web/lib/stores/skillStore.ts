import { create } from 'zustand'
import { skillService } from '@/lib/services/skills'

export interface SkillCategory {
  category_id: string
  name: string
  slug: string
  description: string
  parent_category_id?: string
  sort_order: number
  level: number
  is_active: boolean
}

export interface Skill {
  skill_id: string
  category_id: string
  name: string
  slug: string
  description: string
  level_min: number
  level_max: number
  aliases: string[]
  skill_health?: number
  is_deprecated: boolean
  created_at: number
  updated_at: number
}

export interface UserSkill {
  user_skill_id: string
  skill_id: string
  level: number
  state: string
  confidence_score: number
  evidence_score: number
  is_emerging: boolean
  is_stale: boolean
  created_at: number
  updated_at: number
}

export interface SkillEvidence {
  evidence_id: string
  user_skill_id: string
  evidence_type: string
  title: string
  description: string
  source_url?: string
  source_type: string
  confidence_delta: number
  occurred_at: number
  created_at: number
}

export interface SkillTarget {
  target_id: string
  user_skill_id: string
  target_level: number
  target_date: number
  status: string
  notes?: string
  created_at: number
  updated_at: number
}

export interface SkillAssessment {
  assessment_id: string
  user_skill_id: string
  assessor: string
  level_before: number
  level_after: number
  confidence_score: number
  assessment_type: string
  notes?: string
  assessed_at: number
}

export interface SkillMarketData {
  skill_id: string
  demand_trend?: string
  salary_range_min?: number
  salary_range_max?: number
  job_posting_count?: number
  growth_rate?: number
  remote_friendly?: number
  source_updated_at: number
}

export interface SkillIncomeData {
  income_id: string
  skill_id: string
  project_name?: string
  amount: number
  currency: string
  hourly_rate?: number
  hours_worked?: number
  income_date: number
  notes?: string
}

export interface SkillCertification {
  certification_id: string
  skill_id: string
  name: string
  issuer: string
  description?: string
  url?: string
  cost?: number
  duration_hours?: number
  is_verified: boolean
}

export interface SkillTopic {
  topic_id: string
  skill_id: string
  name: string
  description?: string
  weight: number
  order_index: number
}

export interface SkillResource {
  resource_id: string
  skill_id: string
  title: string
  url?: string
  resource_type: string
  difficulty?: string
  duration_minutes?: number
  is_free: boolean
  rating?: number
  notes?: string
}

export interface SkillLearningPath {
  path_id: string
  target_skill_id: string
  name: string
  description?: string
  estimated_days: number
  difficulty: string
  steps: unknown
  is_active: boolean
}

export interface SkillAIRecommendation {
  recommendation_id: string
  user_skill_id?: string
  recommendation_type: string
  title: string
  description: string
  priority_score: number
  is_accepted: boolean
}

export interface SkillActivityLog {
  activity_id: string
  user_skill_id?: string
  activity_type: string
  description: string
  metadata?: unknown
  created_at: number
}

export interface SkillExternalMapping {
  mapping_id: string
  skill_id: string
  external_system: string
  external_id: string
  external_name: string
  external_url?: string
  confidence: number
}

export interface SkillRoadmapDefinition {
  roadmap_id: string
  name: string
  description?: string
  target_role?: string
  stages: unknown
  is_active: boolean
}

export interface SkillForecast {
  forecast_id: string
  skill_id: string
  forecast_date: number
  metric: string
  predicted_value: number
  confidence_interval_lower?: number
  confidence_interval_upper?: number
  model_name: string
}

interface SkillStore {
  categories: SkillCategory[]
  skills: Skill[]
  userSkills: UserSkill[]
  evidence: SkillEvidence[]
  targets: SkillTarget[]
  assessments: SkillAssessment[]
  marketData: SkillMarketData[]
  income: SkillIncomeData[]
  certifications: SkillCertification[]
  topics: SkillTopic[]
  resources: SkillResource[]
  learningPaths: SkillLearningPath[]
  recommendations: SkillAIRecommendation[]
  activity: SkillActivityLog[]
  externalMappings: SkillExternalMapping[]
  roadmapDefinitions: SkillRoadmapDefinition[]
  forecasts: SkillForecast[]
  loading: boolean
  error: string | null
  selectedSkillId: string | null
  setSelectedSkillId: (id: string | null) => void
  fetchCategories: () => Promise<void>
  fetchSkills: (categoryId?: string) => Promise<void>
  createSkill: (data: Record<string, unknown>) => Promise<void>
  updateSkill: (id: string, data: Record<string, unknown>) => Promise<void>
  deleteSkill: (id: string) => Promise<void>
  fetchUserSkills: (state?: string) => Promise<void>
  addUserSkill: (data: Record<string, unknown>) => Promise<void>
  updateUserSkill: (id: string, data: Record<string, unknown>) => Promise<void>
  deleteUserSkill: (id: string) => Promise<void>
  fetchEvidence: (userSkillId?: string) => Promise<void>
  addEvidence: (data: Record<string, unknown>) => Promise<void>
  fetchTargets: (status?: string) => Promise<void>
  addTarget: (data: Record<string, unknown>) => Promise<void>
  fetchAssessments: (userSkillId?: string) => Promise<void>
  addAssessment: (data: Record<string, unknown>) => Promise<void>
  fetchMarketData: (skillId?: string) => Promise<void>
  addMarketData: (data: Record<string, unknown>) => Promise<void>
  updateMarketData: (skillId: string, data: Record<string, unknown>) => Promise<void>
  fetchIncome: (skillId?: string) => Promise<void>
  addIncome: (data: Record<string, unknown>) => Promise<void>
  fetchCertifications: (skillId?: string) => Promise<void>
  addCertification: (data: Record<string, unknown>) => Promise<void>
  updateCertification: (id: string, data: Record<string, unknown>) => Promise<void>
  deleteCertification: (id: string) => Promise<void>
  fetchTopics: (skillId?: string) => Promise<void>
  addTopic: (data: Record<string, unknown>) => Promise<void>
  updateTopic: (id: string, data: Record<string, unknown>) => Promise<void>
  deleteTopic: (id: string) => Promise<void>
  fetchResources: (skillId?: string) => Promise<void>
  addResource: (data: Record<string, unknown>) => Promise<void>
  updateResource: (id: string, data: Record<string, unknown>) => Promise<void>
  deleteResource: (id: string) => Promise<void>
  fetchLearningPaths: (targetSkillId?: string) => Promise<void>
  addLearningPath: (data: Record<string, unknown>) => Promise<void>
  updateLearningPath: (id: string, data: Record<string, unknown>) => Promise<void>
  deleteLearningPath: (id: string) => Promise<void>
  fetchRecommendations: (type?: string) => Promise<void>
  acceptRecommendation: (id: string) => Promise<void>
  fetchActivity: (type?: string) => Promise<void>
  logActivity: (data: Record<string, unknown>) => Promise<void>
  fetchExternalMappings: (skillId?: string) => Promise<void>
  addExternalMapping: (data: Record<string, unknown>) => Promise<void>
  updateExternalMapping: (id: string, data: Record<string, unknown>) => Promise<void>
  deleteExternalMapping: (id: string) => Promise<void>
  fetchRoadmapDefinitions: () => Promise<void>
  addRoadmapDefinition: (data: Record<string, unknown>) => Promise<void>
  updateRoadmapDefinition: (id: string, data: Record<string, unknown>) => Promise<void>
  deleteRoadmapDefinition: (id: string) => Promise<void>
  fetchForecasts: (skillId?: string) => Promise<void>
  addForecast: (data: Record<string, unknown>) => Promise<void>
}

export const useSkillStore = create<SkillStore>((set, get) => ({
  categories: [],
  skills: [],
  userSkills: [],
  evidence: [],
  targets: [],
  assessments: [],
  marketData: [],
  income: [],
  certifications: [],
  topics: [],
  resources: [],
  learningPaths: [],
  recommendations: [],
  activity: [],
  externalMappings: [],
  roadmapDefinitions: [],
  forecasts: [],
  loading: false,
  error: null,
  selectedSkillId: null,

  setSelectedSkillId: (id) => set({ selectedSkillId: id }),

  fetchCategories: async () => {
    set({ loading: true, error: null })
    try {
      const data = await skillService.categories.list()
      set({ categories: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load categories'
      set({ error: message, loading: false })
    }
  },

  fetchSkills: async (categoryId) => {
    set({ loading: true, error: null })
    try {
      const data = await skillService.list({ category_id: categoryId })
      set({ skills: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load skills'
      set({ error: message, loading: false })
    }
  },

  createSkill: async (data) => {
    try {
      const created = await skillService.create(data)
      set({ skills: [...get().skills, created] })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create skill'
      set({ error: message })
    }
  },

  updateSkill: async (id, data) => {
    try {
      const updated = await skillService.update(id, data)
      set({ skills: get().skills.map(s => s.skill_id === id ? { ...s, ...updated } : s) })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update skill'
      set({ error: message })
    }
  },

  deleteSkill: async (id) => {
    try {
      await skillService.delete(id)
      set({ skills: get().skills.filter(s => s.skill_id !== id) })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete skill'
      set({ error: message })
    }
  },

  fetchUserSkills: async (state) => {
    set({ loading: true, error: null })
    try {
      const data = await skillService.userSkills.list({ state })
      set({ userSkills: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load user skills'
      set({ error: message, loading: false })
    }
  },

  addUserSkill: async (data) => {
    try {
      const created = await skillService.userSkills.create(data)
      set({ userSkills: [created, ...get().userSkills] })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to add skill'
      set({ error: message })
    }
  },

  updateUserSkill: async (id, data) => {
    try {
      const updated = await skillService.userSkills.update(id, data)
      set({ userSkills: get().userSkills.map(s => s.user_skill_id === id ? { ...s, ...updated } : s) })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update skill'
      set({ error: message })
    }
  },

  deleteUserSkill: async (id) => {
    try {
      await skillService.userSkills.delete(id)
      set({ userSkills: get().userSkills.filter(s => s.user_skill_id !== id) })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete skill'
      set({ error: message })
    }
  },

  fetchEvidence: async (userSkillId) => {
    try {
      const data = await skillService.evidence.list({ user_skill_id: userSkillId })
      set({ evidence: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load evidence' })
    }
  },

  addEvidence: async (data) => {
    try {
      const created = await skillService.evidence.create(data)
      set({ evidence: [created, ...get().evidence] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add evidence' })
    }
  },

  fetchTargets: async (status) => {
    try {
      const data = await skillService.targets.list({ status })
      set({ targets: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load targets' })
    }
  },

  addTarget: async (data) => {
    try {
      const created = await skillService.targets.create(data)
      set({ targets: [created, ...get().targets] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add target' })
    }
  },

  fetchAssessments: async (userSkillId) => {
    try {
      const data = await skillService.assessments.list({ user_skill_id: userSkillId })
      set({ assessments: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load assessments' })
    }
  },

  addAssessment: async (data) => {
    try {
      const created = await skillService.assessments.create(data)
      set({ assessments: [created, ...get().assessments] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add assessment' })
    }
  },

  fetchMarketData: async (skillId) => {
    try {
      const data = await skillService.marketData.list({ skill_id: skillId })
      set({ marketData: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load market data' })
    }
  },

  addMarketData: async (data) => {
    try {
      const created = await skillService.marketData.create(data)
      set({ marketData: [...get().marketData, created] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add market data' })
    }
  },

  updateMarketData: async (skillId, data) => {
    try {
      const updated = await skillService.marketData.update(skillId, data)
      set({ marketData: get().marketData.map(m => m.skill_id === skillId ? { ...m, ...updated } : m) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to update market data' })
    }
  },

  fetchIncome: async (skillId) => {
    try {
      const data = await skillService.income.list({ skill_id: skillId })
      set({ income: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load income data' })
    }
  },

  addIncome: async (data) => {
    try {
      const created = await skillService.income.create(data)
      set({ income: [created, ...get().income] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add income data' })
    }
  },

  fetchCertifications: async (skillId) => {
    try {
      const data = await skillService.certifications.list({ skill_id: skillId })
      set({ certifications: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load certifications' })
    }
  },

  addCertification: async (data) => {
    try {
      const created = await skillService.certifications.create(data)
      set({ certifications: [...get().certifications, created] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add certification' })
    }
  },

  updateCertification: async (id, data) => {
    try {
      const updated = await skillService.certifications.update(id, data)
      set({ certifications: get().certifications.map(c => c.certification_id === id ? { ...c, ...updated } : c) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to update certification' })
    }
  },

  deleteCertification: async (id) => {
    try {
      await skillService.certifications.delete(id)
      set({ certifications: get().certifications.filter(c => c.certification_id !== id) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to delete certification' })
    }
  },

  fetchTopics: async (skillId) => {
    try {
      const data = await skillService.topics.list({ skill_id: skillId })
      set({ topics: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load topics' })
    }
  },

  addTopic: async (data) => {
    try {
      const created = await skillService.topics.create(data)
      set({ topics: [...get().topics, created] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add topic' })
    }
  },

  updateTopic: async (id, data) => {
    try {
      const updated = await skillService.topics.update(id, data)
      set({ topics: get().topics.map(t => t.topic_id === id ? { ...t, ...updated } : t) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to update topic' })
    }
  },

  deleteTopic: async (id) => {
    try {
      await skillService.topics.delete(id)
      set({ topics: get().topics.filter(t => t.topic_id !== id) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to delete topic' })
    }
  },

  fetchResources: async (skillId) => {
    try {
      const data = await skillService.resources.list({ skill_id: skillId })
      set({ resources: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load resources' })
    }
  },

  addResource: async (data) => {
    try {
      const created = await skillService.resources.create(data)
      set({ resources: [...get().resources, created] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add resource' })
    }
  },

  updateResource: async (id, data) => {
    try {
      const updated = await skillService.resources.update(id, data)
      set({ resources: get().resources.map(r => r.resource_id === id ? { ...r, ...updated } : r) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to update resource' })
    }
  },

  deleteResource: async (id) => {
    try {
      await skillService.resources.delete(id)
      set({ resources: get().resources.filter(r => r.resource_id !== id) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to delete resource' })
    }
  },

  fetchLearningPaths: async (targetSkillId) => {
    try {
      const data = await skillService.learningPaths.list({ target_skill_id: targetSkillId })
      set({ learningPaths: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load learning paths' })
    }
  },

  addLearningPath: async (data) => {
    try {
      const created = await skillService.learningPaths.create(data)
      set({ learningPaths: [...get().learningPaths, created] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add learning path' })
    }
  },

  updateLearningPath: async (id, data) => {
    try {
      const updated = await skillService.learningPaths.update(id, data)
      set({ learningPaths: get().learningPaths.map(p => p.path_id === id ? { ...p, ...updated } : p) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to update learning path' })
    }
  },

  deleteLearningPath: async (id) => {
    try {
      await skillService.learningPaths.delete(id)
      set({ learningPaths: get().learningPaths.filter(p => p.path_id !== id) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to delete learning path' })
    }
  },

  fetchRecommendations: async (type) => {
    try {
      const data = await skillService.recommendations.list({ recommendation_type: type })
      set({ recommendations: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load recommendations' })
    }
  },

  acceptRecommendation: async (id) => {
    try {
      await skillService.recommendations.accept(id)
      set({ recommendations: get().recommendations.map(r => r.recommendation_id === id ? { ...r, is_accepted: true } : r) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to accept recommendation' })
    }
  },

  fetchActivity: async (type) => {
    try {
      const data = await skillService.activity.list({ activity_type: type })
      set({ activity: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load activity' })
    }
  },

  logActivity: async (data) => {
    try {
      const created = await skillService.activity.log(data)
      set({ activity: [created, ...get().activity] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to log activity' })
    }
  },

  fetchExternalMappings: async (skillId) => {
    try {
      const data = await skillService.externalMappings.list({ skill_id: skillId })
      set({ externalMappings: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load external mappings' })
    }
  },

  addExternalMapping: async (data) => {
    try {
      const created = await skillService.externalMappings.create(data)
      set({ externalMappings: [...get().externalMappings, created] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add external mapping' })
    }
  },

  updateExternalMapping: async (id, data) => {
    try {
      const updated = await skillService.externalMappings.update(id, data)
      set({ externalMappings: get().externalMappings.map(m => m.mapping_id === id ? { ...m, ...updated } : m) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to update external mapping' })
    }
  },

  deleteExternalMapping: async (id) => {
    try {
      await skillService.externalMappings.delete(id)
      set({ externalMappings: get().externalMappings.filter(m => m.mapping_id !== id) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to delete external mapping' })
    }
  },

  fetchRoadmapDefinitions: async () => {
    try {
      const data = await skillService.roadmapDefinitions.list()
      set({ roadmapDefinitions: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load roadmap definitions' })
    }
  },

  addRoadmapDefinition: async (data) => {
    try {
      const created = await skillService.roadmapDefinitions.create(data)
      set({ roadmapDefinitions: [...get().roadmapDefinitions, created] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add roadmap definition' })
    }
  },

  updateRoadmapDefinition: async (id, data) => {
    try {
      const updated = await skillService.roadmapDefinitions.update(id, data)
      set({ roadmapDefinitions: get().roadmapDefinitions.map(d => d.roadmap_id === id ? { ...d, ...updated } : d) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to update roadmap definition' })
    }
  },

  deleteRoadmapDefinition: async (id) => {
    try {
      await skillService.roadmapDefinitions.delete(id)
      set({ roadmapDefinitions: get().roadmapDefinitions.filter(d => d.roadmap_id !== id) })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to delete roadmap definition' })
    }
  },

  fetchForecasts: async (skillId) => {
    try {
      const data = await skillService.forecasts.list({ skill_id: skillId })
      set({ forecasts: data })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to load forecasts' })
    }
  },

  addForecast: async (data) => {
    try {
      const created = await skillService.forecasts.create(data)
      set({ forecasts: [...get().forecasts, created] })
    } catch (err: unknown) {
      set({ error: err instanceof Error ? err.message : 'Failed to add forecast' })
    }
  },
}))
