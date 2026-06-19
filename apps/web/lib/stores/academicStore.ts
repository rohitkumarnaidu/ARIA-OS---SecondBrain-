import { create } from 'zustand'
import { academicService } from '@/lib/services'
import type { Subject, SubjectCreate, Mark, MarkCreate } from '@/lib/types'

interface AcademicStore {
  subjects: Subject[]
  marks: Mark[]
  loading: boolean
  error: string | null
  fetchAll: () => Promise<void>
  addSubject: (data: SubjectCreate) => Promise<void>
  addMark: (data: MarkCreate) => Promise<void>
  deleteSubject: (id: string) => Promise<void>
}

export const useAcademicStore = create<AcademicStore>((set, get) => ({
  subjects: [],
  marks: [],
  loading: false,
  error: null,

  fetchAll: async () => {
    set({ loading: true, error: null })
    try {
      const [subjects, marks] = await Promise.all([
        academicService.listSubjects(),
        academicService.listMarks(),
      ])
      set({ subjects, marks, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load academic data'
      set({ error: message, loading: false })
    }
  },

  addSubject: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await academicService.createSubject(data)
      set({ subjects: [created, ...get().subjects], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to add subject'
      set({ error: message, loading: false })
    }
  },

  addMark: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await academicService.createMark(data)
      set({ marks: [created, ...get().marks], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to add mark'
      set({ error: message, loading: false })
    }
  },

  deleteSubject: async (id) => {
    set({ loading: true, error: null })
    try {
      await academicService.deleteSubject(id)
      set({ subjects: get().subjects.filter(s => s.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete subject'
      set({ error: message, loading: false })
    }
  },
}))
