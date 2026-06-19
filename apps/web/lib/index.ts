// Supabase
export { supabase, isUsingPlaceholders } from './supabase'
export { createSupabaseServerClient } from './supabase-server'

// Stores
export {
  useTaskStore,
  useCourseStore,
  useGoalStore,
  useHabitStore,
  useIdeaStore,
  useIncomeStore,
  useOpportunityStore,
  useProjectStore,
  useResourceStore,
  useSleepStore,
  useTimeStore,
  useChatStore,
  useBriefingStore,
  useReviewStore,
  useMemoryStore,
  useAnalyticsStore,
  useNotificationStore,
  useUserStore,
} from './stores'
export type { User } from './stores/userStore'

// Services
export {
  taskService,
  courseService,
  goalService,
  habitService,
  ideaService,
  incomeService,
  opportunityService,
  projectService,
  resourceService,
  sleepService,
  timeService,
  chatService,
  automationService,
  briefingService,
  reviewService,
  memoryService,
  analyticsService,
} from './services'

// Types
export type {
  Task, TaskCreate, TaskUpdate,
  Course, CourseCreate, CourseUpdate,
  Goal, GoalCreate, GoalUpdate,
  Habit, HabitCreate, HabitUpdate, HabitLog,
  Idea, IdeaCreate, IdeaUpdate,
  IncomeEntry, IncomeEntryCreate,
  Opportunity, OpportunityCreate, OpportunityUpdate,
  Project, ProjectCreate, ProjectUpdate,
  Resource, ResourceCreate, ResourceUpdate,
  SleepLog, SleepLogCreate,
  TimeEntry, TimeEntryCreate, TimeEntryUpdate,
  ChatMessage, ChatMessageCreate, Conversation,
  DailyBriefing, WeeklyReview,
  Memory, MemoryCreate,
  AppNotification,
  PaginatedResponse,
} from './types'

// API Client
export { api } from './api'
export type { RequestConfig } from './api'
export { useApiQuery, useApiMutation, useApiInfiniteQuery } from './api'

// Toast
export { showSuccess, showError, showInfo } from './toast'

// Query
export { QueryProvider } from './query'

// Utils
export { createLogger, trackEvent, trackPageView, measureAsync } from './utils'

// Web Vitals
export { reportWebVitals } from './web-vitals'
