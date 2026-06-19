export type AutomationId = 'briefing' | 'radar' | 'weekly' | 'sleep_analysis' | 'sleep_bedtime' | 'nudges'
export type RunStatus = 'pending' | 'running' | 'success' | 'error'

export interface Automation {
  id: AutomationId
  name: string
  description: string
  schedule: string
  scheduleHour: number
  icon: string
  enabled: boolean
  lastRun: {
    status: RunStatus
    duration: number
    timestamp: string
  } | null
}

export interface AutomationResult {
  status: 'success' | 'error'
  message: string
  duration: number
  details?: Record<string, unknown>
}
