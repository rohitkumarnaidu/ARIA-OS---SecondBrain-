import { describe, it, expect, vi, beforeEach } from 'vitest'
import { automationService } from '@/lib/services/automation'

const mockGet = vi.fn()
const mockPost = vi.fn()

vi.mock('@/lib/api', () => ({
  api: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('automationService', () => {
  describe('list', () => {
    it('returns automation list', async () => {
      const automations = [{ id: '1', trigger: 'daily_briefing', enabled: true }]
      mockGet.mockResolvedValueOnce(automations)
      const result = await automationService.list()
      expect(result).toEqual(automations)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/automation')
    })

    it('returns empty array when no automations', async () => {
      mockGet.mockResolvedValueOnce([])
      const result = await automationService.list()
      expect(result).toEqual([])
    })
  })

  describe('triggerBriefing', () => {
    it('triggers briefing generation', async () => {
      mockPost.mockResolvedValueOnce({ message: 'Briefing triggered' })
      const result = await automationService.triggerBriefing()
      expect(result).toEqual({ message: 'Briefing triggered' })
      expect(mockPost).toHaveBeenCalledWith('/api/v1/automation/trigger/briefing')
    })

    it('handles failure', async () => {
      mockPost.mockRejectedValueOnce(new Error('AI unavailable'))
      await expect(automationService.triggerBriefing()).rejects.toThrow('AI unavailable')
    })
  })

  describe('triggerRadar', () => {
    it('triggers opportunity radar', async () => {
      mockPost.mockResolvedValueOnce({ message: 'Radar scan complete' })
      const result = await automationService.triggerRadar()
      expect(result).toEqual({ message: 'Radar scan complete' })
      expect(mockPost).toHaveBeenCalledWith('/api/v1/automation/trigger/radar')
    })
  })

  describe('triggerWeeklyReview', () => {
    it('triggers weekly review', async () => {
      mockPost.mockResolvedValueOnce({ message: 'Weekly review generated' })
      const result = await automationService.triggerWeeklyReview()
      expect(result).toEqual({ message: 'Weekly review generated' })
      expect(mockPost).toHaveBeenCalledWith('/api/v1/automation/trigger/weekly-review')
    })
  })

  describe('triggerSleepAnalysis', () => {
    it('triggers sleep analysis', async () => {
      mockPost.mockResolvedValueOnce({ message: 'Sleep analysis complete' })
      const result = await automationService.triggerSleepAnalysis()
      expect(result).toEqual({ message: 'Sleep analysis complete' })
      expect(mockPost).toHaveBeenCalledWith('/api/v1/automation/trigger/sleep-analysis')
    })
  })

  describe('triggerBedtime', () => {
    it('triggers bedtime wind-down', async () => {
      mockPost.mockResolvedValueOnce({ message: 'Bedtime wind-down started' })
      const result = await automationService.triggerBedtime()
      expect(result).toEqual({ message: 'Bedtime wind-down started' })
      expect(mockPost).toHaveBeenCalledWith('/api/v1/automation/trigger/sleep-bedtime')
    })
  })

  describe('triggerNudges', () => {
    it('triggers nudges', async () => {
      mockPost.mockResolvedValueOnce({ message: 'Nudges sent' })
      const result = await automationService.triggerNudges()
      expect(result).toEqual({ message: 'Nudges sent' })
      expect(mockPost).toHaveBeenCalledWith('/api/v1/automation/trigger/nudges')
    })
  })
})
