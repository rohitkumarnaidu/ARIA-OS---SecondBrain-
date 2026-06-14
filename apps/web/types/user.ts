export interface User {
  id: string
  email: string
  name?: string
  avatar_url?: string
  college?: string
  year?: number
  skills?: string[]
  bio?: string
  created_at: string
  updated_at: string
}

export interface UserProfile extends User {
  daily_routine?: DailyRoutine
  opportunity_preferences?: OpportunityPreferences
}

export interface DailyRoutine {
  wake_time?: string
  sleep_time?: string
  focus_hours?: string
  break_times?: string[]
}

export interface OpportunityPreferences {
  categories?: string[]
  locations?: string[]
  job_types?: string[]
}
