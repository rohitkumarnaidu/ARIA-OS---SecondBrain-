import { describe, it, expect } from 'vitest'

describe('@/lib/services barrel exports', () => {
  const expectedExports = [
    'taskService',
    'courseService',
    'goalService',
    'habitService',
    'ideaService',
    'incomeService',
    'opportunityService',
    'projectService',
    'resourceService',
    'sleepService',
    'timeService',
    'chatService',
    'automationService',
    'briefingService',
    'reviewService',
    'memoryService',
    'analyticsService',
    'roadmapService',
    'knowledgeService',
    'notificationService',
    'academicService',
    'youtubeService',
    'nudgeService',
    'skillService',
    'featureFlagService',
    'learningService',
  ]

  it('exports all expected services', async () => {
    const mod = await import('@/lib/services')
    for (const name of expectedExports) {
      expect(mod).toHaveProperty(name)
    }
    expect(Object.keys(mod).length).toBe(expectedExports.length)
  }, 60000)
})
