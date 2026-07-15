import { api } from '@/lib/api/client'

const BASE = '/api/v1/learning'

export interface LearningProgress {
  tasks_created: number
  tasks_completed: number
  completion_rate: number
  courses_enrolled: number
  courses_completed: number
  active_habits: number
}

export interface ProductivityPatterns {
  total_tasks: number
  completed_tasks: number
  pending_tasks: number
  recent_completion_rate: number
  overall_completion_rate: number
  tasks_by_priority: Record<string, number>
}

export interface StudyHabits {
  total_courses: number
  courses_by_status: Record<string, number>
  active_habits: number
  habit_consistency: number
  best_streak: number
}

export interface PeakTimes {
  peak_hours: string[]
  deep_work_minutes_7d: number
  total_focus_minutes_7d: number
  deep_work_ratio: number
}

export interface LearningInsightsResponse {
  progress: LearningProgress
  productivity_patterns: ProductivityPatterns
  study_habits: StudyHabits
  peak_times: PeakTimes
  insights: string[]
  generated_at: string
}

export const learningService = {
  getInsights: (refresh = false) =>
    api.get<LearningInsightsResponse>(`${BASE}/insights`, {
      params: { refresh: refresh || undefined },
    }),
}
