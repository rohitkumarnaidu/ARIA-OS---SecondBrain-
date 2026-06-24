import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAutomationStore } from '@/lib/stores/automationStore'
import type { Automation } from '@/types/automation'

const mockList = vi.fn()
const mockTriggerBriefing = vi.fn()
const mockTriggerRadar = vi.fn()
const mockTriggerWeeklyReview = vi.fn()
const mockTriggerSleepAnalysis = vi.fn()
const mockTriggerBedtime = vi.fn()
const mockTriggerNudges = vi.fn()

vi.mock('@/lib/services/automation', () => ({
  automationService: {
    list: (...args: unknown[]) => mockList(...args),
    triggerBriefing: (...args: unknown[]) => mockTriggerBriefing(...args),
    triggerRadar: (...args: unknown[]) => mockTriggerRadar(...args),
    triggerWeeklyReview: (...args: unknown[]) => mockTriggerWeeklyReview(...args),
    triggerSleepAnalysis: (...args: unknown[]) => mockTriggerSleepAnalysis(...args),
    triggerBedtime: (...args: unknown[]) => mockTriggerBedtime(...args),
    triggerNudges: (...args: unknown[]) => mockTriggerNudges(...args),
  },
}))

const mockAutomation = (overrides: Partial<Automation> = {}): Automation => ({
  id: 'a1',
  name: 'Daily Briefing',
  description: 'Morning briefing',
  enabled: true,
  lastRun: null,
  ...overrides,
})

beforeEach(() => {
  vi.clearAllMocks()
  useAutomationStore.setState({ automations: [], loading: false, error: null, running: null })
})

describe('automationStore', () => {
  it('has correct initial state', () => {
    const s = useAutomationStore.getState()
    expect(s.automations).toEqual([])
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
    expect(s.running).toBeNull()
  })

  it('fetch loads automations', async () => {
    const items = [mockAutomation()]
    mockList.mockResolvedValueOnce(items)
    await useAutomationStore.getState().fetch()
    const s = useAutomationStore.getState()
    expect(s.automations).toEqual(items)
    expect(s.loading).toBe(false)
  })

  it('fetch sets error on failure', async () => {
    mockList.mockRejectedValueOnce(new Error('Offline'))
    await useAutomationStore.getState().fetch()
    expect(useAutomationStore.getState().error).toBe('Offline')
  })

  it('trigger runs briefing and updates lastRun', async () => {
    useAutomationStore.setState({ automations: [mockAutomation({ id: 'briefing' })] })
    mockTriggerBriefing.mockResolvedValueOnce({ message: 'Briefing sent' })
    await useAutomationStore.getState().trigger('briefing')
    const s = useAutomationStore.getState()
    expect(s.running).toBeNull()
    expect(s.automations[0].lastRun?.status).toBe('success')
    expect(s.automations[0].lastRun?.message).toBe('Briefing sent')
  })

  it('trigger sets lastRun error on failure', async () => {
    useAutomationStore.setState({ automations: [mockAutomation({ id: 'radar' })] })
    mockTriggerRadar.mockRejectedValueOnce(new Error('API timeout'))
    await useAutomationStore.getState().trigger('radar')
    expect(useAutomationStore.getState().automations[0].lastRun?.status).toBe('error')
    expect(useAutomationStore.getState().running).toBeNull()
  })

  it('trigger handles unknown automation id gracefully', async () => {
    useAutomationStore.setState({ automations: [mockAutomation({ id: 'unknown' })] })
    await useAutomationStore.getState().trigger('unknown')
    expect(useAutomationStore.getState().automations[0].lastRun).toBeNull()
  })

  it('toggle flips enabled flag', () => {
    useAutomationStore.setState({ automations: [mockAutomation({ id: 'a1', enabled: true })] })
    useAutomationStore.getState().toggle('a1')
    expect(useAutomationStore.getState().automations[0].enabled).toBe(false)
    useAutomationStore.getState().toggle('a1')
    expect(useAutomationStore.getState().automations[0].enabled).toBe(true)
  })
})
