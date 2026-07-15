// ============================================================================
// ARIA OS — Shared TypeScript Database Interfaces
// Auto-generated. Do not edit manually.
// ============================================================================

// ── Utility ──────────────────────────────────────────────────────────────────
export type UUID = string
export type Timestamp = string // ISO 8601

// ── Tasks ───────────────────────────────────────────────────────────────────
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled'
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface Task {
  id: UUID
  user_id: UUID
  title: string
  description?: string
  status: TaskStatus
  priority: TaskPriority
  category?: string
  due_date?: Timestamp
  estimated_minutes?: number
  actual_minutes?: number
  completed_at?: Timestamp
  goal_id?: UUID
  project_id?: UUID
  dependency_id?: UUID
  is_recurring?: boolean
  recurring_frequency?: string
  missed_count?: number
  tags?: string[]
  dependencies?: UUID[]
  created_at: Timestamp
  updated_at: Timestamp
}

export interface TaskCreate {
  title: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
  category?: string
  due_date?: Timestamp
  estimated_minutes?: number
  goal_id?: UUID
  project_id?: UUID
  dependency_id?: UUID
  is_recurring?: boolean
  recurring_frequency?: string
  tags?: string[]
  dependencies?: UUID[]
}

export interface TaskUpdate extends Partial<TaskCreate> {
  completed_at?: Timestamp
  status?: TaskStatus
}

// ── Courses ─────────────────────────────────────────────────────────────────
export type CourseStatus = 'not_started' | 'in_progress' | 'completed' | 'dropped' | 'abandoned'

export interface Course {
  id: UUID
  user_id: UUID
  title: string
  platform: string
  url?: string
  total_videos?: number
  completed_videos: number
  deadline?: Timestamp
  why_enrolled?: string
  status: CourseStatus
  daily_minutes_needed?: number
  created_at: Timestamp
  updated_at?: Timestamp
}

export interface CourseCreate {
  title: string
  platform: string
  url?: string
  total_videos?: number
  deadline?: Timestamp
  why_enrolled?: string
}

export interface CourseUpdate extends Partial<CourseCreate> {
  completed_videos?: number
  status?: CourseStatus
}

// ── Goals ───────────────────────────────────────────────────────────────────
export type GoalStatus = 'active' | 'paused' | 'completed' | 'abandoned'
export type GoalCategory = 'career' | 'academic' | 'health' | 'finance' | 'personal' | 'skill'

export interface Goal {
  id: UUID
  user_id: UUID
  title: string
  description?: string
  category?: GoalCategory
  status: GoalStatus
  roadmap_type?: string
  target_date?: Timestamp
  hours_per_day?: number
  days_per_week?: number
  intensity?: string
  progress: number
  milestones?: GoalMilestone[]
  nodes?: unknown[] // Roadmap flow nodes (type refined at runtime)
  created_at: Timestamp
  updated_at?: Timestamp
}

export interface GoalMilestone {
  id: UUID
  goal_id: UUID
  title: string
  completed: boolean
  due_date?: Timestamp
}

export interface GoalCreate {
  title: string
  description?: string
  category?: GoalCategory
  roadmap_type?: string
  status?: GoalStatus
  target_date?: Timestamp
  hours_per_day?: number
  days_per_week?: number
  intensity?: string
  progress?: number
  nodes?: unknown[] // Roadmap flow nodes (type refined at runtime)
}

export interface GoalUpdate extends Partial<GoalCreate> {}

// ── Habits ──────────────────────────────────────────────────────────────────
export type HabitFrequency = 'daily' | 'weekly' | 'weekdays' | 'weekends' | 'custom'
export type HabitTimeOfDay = 'morning' | 'afternoon' | 'evening' | 'any'

export interface Habit {
  id: UUID
  user_id: UUID
  name: string
  frequency: HabitFrequency
  custom_days?: number[]
  time_target_minutes?: number
  goal_id?: UUID
  is_active: boolean
  current_streak: number
  best_streak: number
  consistency_percentage: number
  created_at: Timestamp
}

export interface HabitLog {
  id: UUID
  user_id: UUID
  habit_id: UUID
  date: string
  completed: boolean
  note?: string
  created_at: Timestamp
}

export interface HabitCreate {
  name: string
  frequency?: HabitFrequency
  custom_days?: number[]
  time_target_minutes?: number
}

export interface HabitUpdate {
  name?: string
  frequency?: HabitFrequency
  custom_days?: number[]
  time_target_minutes?: number
  is_active?: boolean
}

// ── Sleep Wind-Down ─────────────────────────────────────────────────────────
export interface WindDownStep {
  time?: string
  action: string
  duration_minutes?: number
  reason?: string
}

export interface WindDownData {
  available: boolean
  message?: string
  suggested_bedtime?: string
  suggested_wake_time?: string
  wind_down_routine?: WindDownStep[]
  recommendations?: string[]
  sleep_analysis?: string
}

// ── Sleep ───────────────────────────────────────────────────────────────────
export interface SleepLog {
  id: UUID
  user_id: UUID
  bedtime: Timestamp
  wake_time: Timestamp
  quality_rating: number
  duration_hours: number
  sleep_score: number
  sleep_debt: number
  created_at: Timestamp
}

export interface SleepLogCreate {
  bedtime: string
  wake_time: string
  quality_rating: number
}

// ── Income ──────────────────────────────────────────────────────────────────
export interface IncomeEntry {
  id: UUID
  user_id: UUID
  source_type: string
  amount: number
  platform?: string
  description?: string
  date: string
  hours_spent?: number
  effective_hourly_rate?: number
  created_at: Timestamp
}

export interface IncomeEntryCreate {
  source_type: string
  amount: number
  platform?: string
  description?: string
  date?: string
  hours_spent?: number
  effective_hourly_rate?: number
}

// ── Projects ────────────────────────────────────────────────────────────────
export type ProjectStatus = 'planning' | 'active' | 'paused' | 'completed' | 'cancelled'

export interface Project {
  id: UUID
  user_id: UUID
  title: string
  description?: string
  phase: string
  phases?: ProjectPhase[]
  blockers?: string[]
  github_url?: string
  live_url?: string
  next_action?: string
  blocker?: string
  start_date?: Timestamp
  target_date?: Timestamp
  completed_date?: Timestamp
  created_at: Timestamp
  updated_at: Timestamp
}

export interface ProjectPhase {
  id: UUID
  name: string
  status: 'pending' | 'in_progress' | 'completed'
  order: number
}

export interface ProjectCreate {
  title: string
  description?: string
  phase?: string
  github_url?: string
  live_url?: string
  next_action?: string
  blocker?: string
  start_date?: Timestamp
  target_date?: Timestamp
}

export interface ProjectUpdate extends Partial<ProjectCreate> {
  phases?: ProjectPhase[]
  blockers?: string[]
}

// ── Ideas ───────────────────────────────────────────────────────────────────
export interface Idea {
  id: UUID
  user_id: UUID
  title: string
  description?: string
  status: string
  market_research?: string
  competitors?: string
  feasibility_notes?: string
  validation_plan?: string
  created_at: Timestamp
}

export interface IdeaCreate {
  title: string
  description?: string
  status?: string
}

export interface IdeaUpdate {
  title?: string
  description?: string
  status?: string
}

// ── Resources ───────────────────────────────────────────────────────────────
export type ResourceType = 'article' | 'video' | 'book' | 'course' | 'tool' | 'podcast' | 'other'

export interface Resource {
  id: UUID
  user_id: UUID
  title: string
  url?: string
  resource_type: string
  tags?: string[]
  notes?: string
  is_archived: boolean
  created_at: Timestamp
  updated_at: Timestamp
}

export interface ResourceCreate {
  title: string
  url?: string
  resource_type: string
  tags?: string[]
  notes?: string
  is_archived?: boolean
}

export interface ResourceUpdate extends Partial<ResourceCreate> {}

// ── Opportunities ──────────────────────────────────────────────────────────
export type OpportunityType = 'internship' | 'job' | 'scholarship' | 'competition' | 'grant' | 'other'
export type OpportunityStatus = 'saved' | 'applied' | 'interviewing' | 'offered' | 'accepted' | 'rejected'

export interface Opportunity {
  id: UUID
  user_id: UUID
  title: string
  company?: string
  url: string
  opportunity_type: string
  status: OpportunityStatus
  match_score?: number
  deadline?: Timestamp
  notes?: string
  created_at: Timestamp
  updated_at: Timestamp
}

export interface OpportunityCreate {
  title: string
  company?: string
  url: string
  opportunity_type: string
  status?: OpportunityStatus
  match_score?: number
  deadline?: Timestamp
  notes?: string
}

export interface OpportunityUpdate extends Partial<OpportunityCreate> {}

// ── Time Entries ────────────────────────────────────────────────────────────
export interface TimeEntry {
  id: UUID
  user_id: UUID
  task_id?: UUID
  description?: string
  start_time: Timestamp
  end_time?: Timestamp
  duration_minutes?: number
  is_deep_work: boolean
  category: string
  created_at: Timestamp
}

export interface TimeEntryCreate {
  task_id?: UUID
  description?: string
  start_time: Timestamp
  end_time?: Timestamp
  duration_minutes?: number
  is_deep_work?: boolean
  category?: string
}

export interface TimeEntryUpdate {
  description?: string
  end_time?: Timestamp
  duration_minutes?: number
  is_deep_work?: boolean
  category?: string
}

// ── Chat Messages ──────────────────────────────────────────────────────────
export type MessageRole = 'user' | 'assistant' | 'system' | 'agent'
export type MessageStatus = 'sending' | 'sent' | 'streaming' | 'complete' | 'error'

export interface ChatMessage {
  id: UUID
  user_id: UUID
  conversation_id: UUID
  role: MessageRole
  content: string
  agent_id?: string
  metadata?: Record<string, unknown>
  status: MessageStatus
  created_at: Timestamp
}

export interface Conversation {
  id: UUID
  user_id: UUID
  title: string
  agent_id?: string
  messages?: ChatMessage[]
  created_at: Timestamp
  updated_at: Timestamp
}

export interface ChatMessageCreate {
  conversation_id: UUID
  role: MessageRole
  content: string
  agent_id?: string
}

// ── Daily Briefings ────────────────────────────────────────────────────────
export interface DailyBriefing {
  id: UUID
  user_id: UUID
  date: string // YYYY-MM-DD
  title: string
  summary: string
  tasks_count: number
  habits_streak: number
  sleep_score?: number
  weather?: string
  top_priority?: string
  ai_insight?: string
  generated_by?: string
  read: boolean
  created_at: Timestamp
}

// ── Weekly Reviews ──────────────────────────────────────────────────────────
export interface WeeklyReview {
  id: UUID
  user_id: UUID
  week_start: string // YYYY-MM-DD
  week_end: string // YYYY-MM-DD
  summary: string
  tasks_completed: number
  tasks_added: number
  habits_consistency: number
  focus_hours: number
  highlights: string[]
  challenges: string[]
  next_week_focus: string[]
  ai_insights?: string
  mood_trend?: string
  generated_by?: string
  created_at: Timestamp
}

// ── Memory ──────────────────────────────────────────────────────────────────
export type MemoryType = 'preference' | 'pattern' | 'fact' | 'context' | 'learning'
export type MemoryImportance = 'low' | 'medium' | 'high' | 'critical'

export interface Memory {
  id: UUID
  user_id: UUID
  type: MemoryType
  key: string
  value: unknown
  importance: MemoryImportance
  tags?: string[]
  expires_at?: Timestamp
  created_at: Timestamp
  updated_at: Timestamp
}

export interface MemoryCreate {
  type: MemoryType
  key: string
  value: unknown
  importance?: MemoryImportance
  tags?: string[]
  expires_at?: Timestamp
}

export interface MemoryUpdate {
  type?: MemoryType
  key?: string
  value?: unknown
  importance?: MemoryImportance
  tags?: string[]
  expires_at?: Timestamp
}

// ── Learning Progress ──────────────────────────────────────────────────────
export interface LearningProgress {
  id: UUID
  user_id: UUID
  date: string // YYYY-MM-DD
  subject: string
  hours_studied: number
  topics_covered: string[]
  confidence_score?: number
  notes?: string
  created_at: Timestamp
}

// ── User ────────────────────────────────────────────────────────────────────
export type ThemeMode = 'dark' | 'light'
export type AccentColor = 'indigo' | 'emerald' | 'amber' | 'rose' | 'sky' | 'purple'

export interface User {
  id: UUID
  email: string
  name?: string
  avatar_url?: string
  preferences?: UserPreferences
  created_at: Timestamp
  updated_at: Timestamp
}

export interface UserPreferences {
  theme: ThemeMode
  accent: AccentColor
  high_contrast: boolean
  reduced_motion: boolean
  notifications_enabled: boolean
  weekly_review_day: 'sunday' | 'monday'
  briefing_time: string // HH:mm format
  focus_duration: number // minutes
}

// ── Nudges ───────────────────────────────────────────────────────────────────
export type NudgeType = 'course' | 'habit' | 'task'
export type NudgeSeverity = 'info' | 'warning' | 'critical'

export interface NudgeEntry {
  id: UUID
  user_id: UUID
  type: NudgeType
  severity: NudgeSeverity
  title: string
  message: string
  priority: string
  category: string
  read: boolean
  action_url?: string
  icon?: string
  created_at: Timestamp
}

// ── Notifications ───────────────────────────────────────────────────────────
export type NotificationCategory = 'task' | 'habit' | 'ai' | 'system' | 'reminder' | 'achievement' | 'learning' | 'opportunity' | 'goal' | 'deadline_alert'
export type NotificationPriority = 'low' | 'medium' | 'high'

export interface AppNotification {
  id: UUID
  user_id: UUID
  title: string
  message: string
  category: NotificationCategory
  priority: NotificationPriority
  read: boolean
  action_url?: string
  icon?: string
  created_at: Timestamp
}

// ── Academics ────────────────────────────────────────────────────────────────
export interface Subject {
  id: UUID
  user_id: UUID
  name: string
  code?: string
  credits?: number
  semester?: string
  exam_date?: string
  target_marks?: number
  created_at: Timestamp
}

export interface SubjectCreate {
  name: string
  code?: string
  credits?: number
  semester?: string
  exam_date?: string
  target_marks?: number
}

export interface Mark {
  id: UUID
  user_id: UUID
  subject_id: UUID
  exam_type: string
  marks_obtained: number
  max_marks: number
  date: string
  created_at: Timestamp
}

export interface MarkCreate {
  subject_id: UUID
  exam_type: string
  marks_obtained: number
  max_marks: number
  date: string
}

// ── YouTube ──────────────────────────────────────────────────────────────────
export interface Video {
  id: UUID
  user_id: UUID
  url: string
  title: string
  thumbnail_url?: string
  ai_summary?: string
  status: string
  created_at: Timestamp
}

export interface VideoCreate {
  url: string
  title: string
  thumbnail_url?: string
  status?: string
}

export interface VideoUpdate {
  title?: string
  url?: string
  thumbnail_url?: string
  ai_summary?: string
  status?: string
}

// ── API Response Wrappers ────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  data: T[]
  count: number
  limit: number
  offset: number
}

export interface ApiError {
  detail: string
  error_code: string
  request_id: UUID
  timestamp: Timestamp
}

// ── Predictions ───────────────────────────────────────────────────────────
export interface CompletionPrediction {
  task_id: string
  title: string
  probability: number
  confidence: string
  due_date?: string
  recommendation: string
}

export interface TaskCompletionForecast {
  total_pending: number
  high_completion: number
  at_risk_count: number
  predictions: CompletionPrediction[]
}

export interface StreakPrediction {
  habit_id: string
  habit_name: string
  current_streak: number
  risk_level: string
  risk_probability: number
  recommendation: string
}

export interface HabitCompletionForecast {
  total_active: number
  at_risk_count: number
  predictions: StreakPrediction[]
}

export interface BedtimePrediction {
  optimal_bedtime: string
  optimal_wake: string
  expected_score: number
  confidence: string
  based_on_sessions: number
}

export interface SleepInsight {
  average_score: number
  average_duration: number
  trend: string
  recommendation: string
  bedtime_prediction?: BedtimePrediction
}

export interface SmartSlot {
  hour: number
  day_of_week: number
  productivity_score: number
  task_count: number
  completion_rate: number
}

export interface SmartSlotResponse {
  slots: SmartSlot[]
  best_hour: number
  best_day: number
}
