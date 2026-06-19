import { z } from 'zod'

// ─── Validation error wrapper ──────────────────────────────────────────────

export interface ValidationResult<T> {
  success: boolean
  data?: T
  errors?: { path: string; message: string; code: string }[]
}

export function validateOrThrow<T>(schema: z.ZodSchema<T>, input: unknown): T {
  const result = schema.safeParse(input)
  if (!result.success) {
    const errors = result.error.issues.map(issue => ({
      path: issue.path.join('.'),
      message: issue.message,
      code: issue.code,
    }))
    throw new ValidationError('Validation failed', errors)
  }
  return result.data
}

export class ValidationError extends Error {
  public readonly errors: { path: string; message: string; code: string }[]
  constructor(message: string, errors: { path: string; message: string; code: string }[]) {
    super(message)
    this.name = 'ValidationError'
    this.errors = errors
  }
}

// ─── ISO datetime helpers ──────────────────────────────────────────────────

export const isoDatetime = z.string().datetime({ message: 'Must be ISO 8601 datetime' })
export const optionalIsoDatetime = isoDatetime.optional()

// ─── Task ──────────────────────────────────────────────────────────────────

export const taskCreateSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title too long'),
  description: z.string().max(5000, 'Description too long').optional(),
  priority: z.enum(['low', 'medium', 'high', 'urgent']).default('medium'),
  category: z.string().max(100).optional(),
  estimated_minutes: z.number().int().positive('Must be positive').max(1440).optional(),
  due_date: optionalIsoDatetime,
  is_recurring: z.boolean().default(false),
  recurring_frequency: z.enum(['daily', 'weekly', 'monthly']).optional(),
  course_id: z.string().uuid('Invalid course ID').optional(),
  goal_id: z.string().uuid('Invalid goal ID').optional(),
  project_id: z.string().uuid('Invalid project ID').optional(),
})

export const taskUpdateSchema = taskCreateSchema.partial()

// ─── Course ────────────────────────────────────────────────────────────────

export const courseCreateSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  platform: z.string().max(100),
  url: z.string().url('Invalid URL').optional().or(z.literal('')),
  total_videos: z.number().int().positive().optional(),
  deadline: optionalIsoDatetime,
  why_enrolled: z.string().max(2000).optional(),
})

// ─── Goal ──────────────────────────────────────────────────────────────────

export const goalCreateSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(5000).optional(),
  roadmap_type: z.enum(['career_skills', 'certification', 'fitness', 'academic', 'personal']),
  target_date: optionalIsoDatetime,
  hours_per_day: z.number().positive().max(24).optional(),
  days_per_week: z.number().int().min(1).max(7).optional(),
  intensity: z.enum(['low', 'medium', 'high']).default('medium'),
})

// ─── Habit ─────────────────────────────────────────────────────────────────

export const habitCreateSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  frequency: z.enum(['daily', 'weekly', 'monthly']),
  time_target_minutes: z.number().int().positive('Must be positive').max(1440, 'Max 24 hours'),
  is_active: z.boolean().default(true),
})

// ─── Sleep ─────────────────────────────────────────────────────────────────

export const sleepLogSchema = z
  .object({
    bedtime: isoDatetime,
    wake_time: isoDatetime,
    quality_rating: z.number().int().min(1, 'Min 1').max(5, 'Max 5'),
    duration_hours: z.number().positive('Must be positive').max(24, 'Max 24 hours'),
  })
  .refine(data => new Date(data.wake_time) > new Date(data.bedtime), {
    message: 'Wake time must be after bedtime',
    path: ['wake_time'],
  })

// ─── Idea ──────────────────────────────────────────────────────────────────

export const ideaCreateSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(5000).optional(),
  stage: z.enum(['raw', 'validating', 'building']).default('raw'),
})

// ─── Income ────────────────────────────────────────────────────────────────

export const incomeCreateSchema = z.object({
  source_type: z.string().min(1).max(100),
  amount: z.number().positive('Amount must be positive').max(999999.99),
  date: isoDatetime,
  description: z.string().max(1000).optional(),
  hourly_rate: z.number().positive().optional(),
  hours_worked: z.number().positive().optional(),
})

// ─── Project ───────────────────────────────────────────────────────────────

export const projectCreateSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(5000).optional(),
  phase: z.enum(['planning', 'active', 'review', 'completed']).default('planning'),
  live_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  repo_url: z.string().url('Invalid URL').optional().or(z.literal('')),
})

// ─── Resource ──────────────────────────────────────────────────────────────

export const resourceCreateSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  url: z.string().url('Invalid URL').optional().or(z.literal('')),
  resource_type: z.enum(['article', 'video', 'book', 'tool', 'other']).default('article'),
  tags: z
    .array(z.string().max(50, 'Tag too long'))
    .max(20, 'Max 20 tags')
    .default([]),
})

// ─── Chat ──────────────────────────────────────────────────────────────────

export const chatMessageSchema = z.object({
  message: z.string().min(1, 'Message is required').max(10000, 'Message too long'),
})

// ─── Time Entry ────────────────────────────────────────────────────────────

export const timeEntrySchema = z
  .object({
    start_time: isoDatetime,
    end_time: optionalIsoDatetime,
    duration_minutes: z.number().int().positive().max(1440).optional(),
    activity_type: z.enum(['deep_work', 'pomodoro', 'meeting', 'break', 'other']),
    description: z.string().max(500).optional(),
  })
  .refine(
    data => {
      if (!data.end_time) return true
      return new Date(data.end_time) > new Date(data.start_time)
    },
    { message: 'End time must be after start time', path: ['end_time'] },
  )
