import { api } from '@/lib/api'
import type { Automation } from '@/types/automation'

const BASE = '/api/v1/automation'

const defaultAutomations: Automation[] = [
  {
    id: 'briefing', name: 'Daily Briefing',
    description: 'Generate your morning briefing with top tasks, goals, and ARIA pick',
    schedule: '7:00 AM daily', scheduleHour: 7, icon: 'Zap', enabled: true,
    lastRun: null,
  },
  {
    id: 'radar', name: 'Opportunity Radar',
    description: 'Scan for internships, hackathons, open source, and freelance opportunities',
    schedule: '6:00 AM daily', scheduleHour: 6, icon: 'Target', enabled: true,
    lastRun: null,
  },
  {
    id: 'weekly', name: 'Weekly Review',
    description: 'Get a summary of your week: tasks completed, courses progress, income',
    schedule: 'Sunday 8:00 PM', scheduleHour: 20, icon: 'Clock', enabled: true,
    lastRun: null,
  },
  {
    id: 'sleep_analysis', name: 'Sleep Analysis',
    description: 'Analyze last night sleep quality and get personalized recommendations',
    schedule: 'On-demand', scheduleHour: -1, icon: 'Moon', enabled: true,
    lastRun: null,
  },
  {
    id: 'sleep_bedtime', name: 'Bedtime Suggestion',
    description: 'Get AI-suggested bedtime based on your recent sleep patterns',
    schedule: '10:30 PM daily', scheduleHour: 22, icon: 'Moon', enabled: true,
    lastRun: null,
  },
  {
    id: 'nudges', name: 'Course & Habit Nudges',
    description: 'Check course progress and habit streaks, generate motivational nudges',
    schedule: '6:00 PM daily', scheduleHour: 18, icon: 'Bell', enabled: true,
    lastRun: null,
  },
]

export const automationService = {
  list: () => Promise.resolve(defaultAutomations),
  triggerBriefing: () => api.post<{ message: string }>(`${BASE}/trigger/briefing`),
  triggerRadar: () => api.post<{ message: string }>(`${BASE}/trigger/radar`),
  triggerWeeklyReview: () => api.post<{ message: string }>(`${BASE}/trigger/weekly-review`),
  triggerSleepAnalysis: () => api.post<{ message: string }>(`${BASE}/trigger/sleep-analysis`),
  triggerBedtime: () => api.post<{ message: string }>(`${BASE}/trigger/sleep-bedtime`),
  triggerNudges: () => api.post<{ message: string }>(`${BASE}/trigger/nudges`),
}
