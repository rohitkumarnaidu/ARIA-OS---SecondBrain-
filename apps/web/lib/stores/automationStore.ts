import { create } from 'zustand'
import { automationService } from '@/lib/services'
import type { Automation } from '@/types/automation'

interface AutomationStore {
  automations: Automation[]
  loading: boolean
  error: string | null
  running: string | null
  fetch: () => Promise<void>
  trigger: (id: string) => Promise<void>
  toggle: (id: string) => void
}

const tempId = () => `auto-${Date.now()}`

export const useAutomationStore = create<AutomationStore>((set, get) => ({
  automations: [],
  loading: false,
  error: null,
  running: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const automations = await automationService.list()
      set({ automations, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load automations'
      set({ error: message, loading: false })
    }
  },

  trigger: async (id) => {
    set({ running: id, error: null })
    try {
      const triggerMap: Record<string, () => Promise<any>> = {
        briefing: automationService.triggerBriefing,
        radar: automationService.triggerRadar,
        weekly: automationService.triggerWeeklyReview,
        sleep_analysis: automationService.triggerSleepAnalysis,
        sleep_bedtime: automationService.triggerBedtime,
        nudges: automationService.triggerNudges,
      }
      const fn = triggerMap[id]
      if (fn) {
        const result = await fn()
        set((state) => ({
          automations: state.automations.map(a =>
            a.id === id ? { ...a, lastRun: { status: 'success' as const, duration: 1, timestamp: new Date().toISOString(), message: result.message } } : a
          ),
        }))
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Automation failed'
      set((state) => ({
        automations: state.automations.map(a =>
          a.id === id ? { ...a, lastRun: { status: 'error' as const, duration: 1, timestamp: new Date().toISOString(), message } } : a
        ),
      }))
    } finally {
      set({ running: null })
    }
  },

  toggle: (id) => {
    set((state) => ({
      automations: state.automations.map(a =>
        a.id === id ? { ...a, enabled: !a.enabled } : a
      ),
    }))
  },
}))
