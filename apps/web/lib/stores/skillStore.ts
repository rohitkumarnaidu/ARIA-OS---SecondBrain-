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

interface SkillStore {
  categories: SkillCategory[]
  skills: Skill[]
  userSkills: UserSkill[]
  loading: boolean
  error: string | null
  fetchCategories: () => Promise<void>
  fetchSkills: (categoryId?: string) => Promise<void>
  fetchUserSkills: (state?: string) => Promise<void>
  addUserSkill: (data: Record<string, unknown>) => Promise<void>
  updateUserSkill: (id: string, data: Record<string, unknown>) => Promise<void>
  deleteUserSkill: (id: string) => Promise<void>
}

export const useSkillStore = create<SkillStore>((set, get) => ({
  categories: [],
  skills: [],
  userSkills: [],
  loading: false,
  error: null,

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
}))
