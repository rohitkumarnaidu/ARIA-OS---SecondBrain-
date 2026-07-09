// Shared enterprise — Second Brain OS
// Re-export all canonical types from a single entry point

export interface Task {
  id: string
  user_id: string
  title: string
  description?: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  due_date?: string
  tags?: string[]
  estimated_minutes?: number
  actual_minutes?: number
  is_recurring?: boolean
  recurrence_pattern?: string
  parent_task_id?: string
  order_index?: number
  created_at: string
  updated_at: string
}

export interface Course {
  id: string
  user_id: string
  name: string
  platform?: string
  url?: string
  total_lectures?: number
  completed_lectures?: number
  status: 'not_started' | 'in_progress' | 'completed' | 'dropped'
  deadline?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface Goal {
  id: string
  user_id: string
  title: string
  description?: string
  category: 'career' | 'health' | 'finance' | 'learning' | 'social' | 'personal'
  status: 'active' | 'achieved' | 'abandoned'
  target_date?: string
  milestones?: Milestone[]
  created_at: string
  updated_at: string
}

export interface Milestone {
  id: string
  goal_id: string
  title: string
  completed: boolean
  completed_at?: string
}

export interface Habit {
  id: string
  user_id: string
  name: string
  description?: string
  frequency: 'daily' | 'weekly' | 'monthly'
  target_count?: number
  streak: number
  longest_streak: number
  color?: string
  icon?: string
  created_at: string
  updated_at: string
}

export interface HabitLog {
  id: string
  habit_id: string
  user_id: string
  date: string
  count: number
  notes?: string
  created_at: string
}

export interface SleepLog {
  id: string
  user_id: string
  date: string
  bedtime: string
  wake_time: string
  duration_minutes: number
  quality_score?: number
  notes?: string
  created_at: string
}

export interface IncomeEntry {
  id: string
  user_id: string
  amount: number
  currency: string
  source: string
  category: string
  date: string
  hour?: number
  hourly_rate?: number
  notes?: string
  created_at: string
}

export interface Project {
  id: string
  user_id: string
  name: string
  description?: string
  status: 'idea' | 'active' | 'paused' | 'completed' | 'cancelled'
  phases?: ProjectPhase[]
  blockers?: string[]
  url?: string
  created_at: string
  updated_at: string
}

export interface ProjectPhase {
  id: string
  project_id: string
  name: string
  status: 'pending' | 'in_progress' | 'completed'
  order: number
}

export interface Idea {
  id: string
  user_id: string
  title: string
  description?: string
  stage: 'raw' | 'validating' | 'building' | 'launched' | 'archived'
  tags?: string[]
  created_at: string
  updated_at: string
}

export interface Resource {
  id: string
  user_id: string
  title: string
  url?: string
  type: 'article' | 'video' | 'book' | 'tool' | 'course' | 'other'
  tags?: string[]
  notes?: string
  created_at: string
  updated_at: string
}

export interface Opportunity {
  id: string
  user_id: string
  title: string
  description?: string
  category: 'internship' | 'job' | 'freelance' | 'scholarship' | 'hackathon' | 'other'
  url?: string
  match_score?: number
  status: 'new' | 'applied' | 'interviewing' | 'accepted' | 'rejected' | 'expired'
  deadline?: string
  created_at: string
  updated_at: string
}

export interface TimeEntry {
  id: string
  user_id: string
  start_time: string
  end_time?: string
  duration_minutes?: number
  category: 'deep_work' | 'meeting' | 'break' | 'admin' | 'learning' | 'other'
  description?: string
  tags?: string[]
  created_at: string
}

export interface Memory {
  id: string
  user_id: string
  type: 'preference' | 'pattern' | 'insight' | 'fact' | 'context'
  key: string
  value: unknown
  confidence: number
  expires_at?: string
  created_at: string
  updated_at: string
}

export interface Briefing {
  id: string
  user_id: string
  date: string
  content: BriefingContent
  generated_at: string
}

export interface BriefingContent {
  greeting: string
  focus_area: string
  today_schedule: BriefingSection[]
  reminders: string[]
  opportunities: string[]
  quote?: string
}

export interface BriefingSection {
  time?: string
  title: string
  description: string
  type: 'task' | 'habit' | 'course' | 'focus'
}

export interface ApiResponse<T> {
  data: T
  limit?: number
  offset?: number
  total?: number
}

export interface ApiError {
  detail: string
  error_code?: string
  request_id?: string
  timestamp?: string
}

export interface PaginationParams {
  limit?: number
  offset?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface UserProfile {
  id: string
  email: string
  name?: string
  avatar_url?: string
  preferences?: UserPreferences
  created_at: string
  updated_at: string
}

export interface UserPreferences {
  theme: 'dark' | 'light' | 'system'
  briefing_time?: string
  weekly_review_day?: number
  focus_duration_minutes?: number
  break_duration_minutes?: number
  notification_enabled: boolean
}
