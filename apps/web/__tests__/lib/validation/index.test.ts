import { describe, it, expect } from 'vitest'
import {
  taskCreateSchema,
  taskUpdateSchema,
  courseCreateSchema,
  goalCreateSchema,
  habitCreateSchema,
  sleepLogSchema,
  ideaCreateSchema,
  incomeCreateSchema,
  projectCreateSchema,
  resourceCreateSchema,
  chatMessageSchema,
  timeEntrySchema,
  validateOrThrow,
  ValidationError,
} from '@/lib/validation/index'

function expectValid<T>(schema: import('zod').ZodSchema<T>, input: unknown): T {
  const result = schema.safeParse(input)
  expect(result.success, `Expected valid: ${JSON.stringify(input)}`).toBe(true)
  return (result as { success: true; data: T }).data
}

function expectInvalid<T>(schema: import('zod').ZodSchema<T>, input: unknown, expectedMsg?: string) {
  const result = schema.safeParse(input)
  expect(result.success, `Expected invalid: ${JSON.stringify(input)}`).toBe(false)
  if (expectedMsg && !result.success) {
    const messages = result.error.issues.map(i => i.message)
    expect(messages.some(m => m.includes(expectedMsg))).toBe(true)
  }
}

describe('validation utilities', () => {
  describe('validateOrThrow', () => {
    it('returns parsed data on success', () => {
      const result = validateOrThrow(taskCreateSchema, { title: 'Test' })
      expect(result.title).toBe('Test')
      expect(result.priority).toBe('medium')
    })

    it('throws ValidationError on failure', () => {
      expect(() => validateOrThrow(taskCreateSchema, {})).toThrow(ValidationError)
    })

    it('ValidationError has structured errors', () => {
      try {
        validateOrThrow(taskCreateSchema, {})
      } catch (e) {
        expect(e).toBeInstanceOf(ValidationError)
        expect((e as ValidationError).errors).toBeInstanceOf(Array)
        expect((e as ValidationError).errors[0]).toHaveProperty('path')
        expect((e as ValidationError).errors[0]).toHaveProperty('message')
        expect((e as ValidationError).errors[0]).toHaveProperty('code')
      }
    })
  })
})

describe('taskCreateSchema', () => {
  it('validates a minimal task', () => {
    const data = expectValid(taskCreateSchema, { title: 'Buy groceries' })
    expect(data.title).toBe('Buy groceries')
  })

  it('applies defaults for optional fields', () => {
    const data = expectValid(taskCreateSchema, { title: 'Task' })
    expect(data.priority).toBe('medium')
    expect(data.is_recurring).toBe(false)
  })

  it('validates full task', () => {
    const data = expectValid(taskCreateSchema, {
      title: 'Complete project',
      description: 'Finish the report',
      priority: 'high',
      category: 'work',
      estimated_minutes: 60,
      due_date: '2026-07-01T00:00:00Z',
      is_recurring: true,
      recurring_frequency: 'weekly',
      course_id: '550e8400-e29b-41d4-a716-446655440000',
      goal_id: '550e8400-e29b-41d4-a716-446655440001',
      project_id: '550e8400-e29b-41d4-a716-446655440002',
    })
    expect(data.priority).toBe('high')
    expect(data.estimated_minutes).toBe(60)
    expect(data.is_recurring).toBe(true)
  })

  it('rejects empty title', () => {
    expectInvalid(taskCreateSchema, { title: '' }, 'required')
  })

  it('rejects title over 200 chars', () => {
    expectInvalid(taskCreateSchema, { title: 'x'.repeat(201) }, 'long')
  })

  it('rejects invalid priority', () => {
    expectInvalid(taskCreateSchema, { title: 'Task', priority: 'critical' })
  })

  it('rejects negative estimated_minutes', () => {
    expectInvalid(taskCreateSchema, { title: 'Task', estimated_minutes: -1 })
  })

  it('rejects invalid UUID for course_id', () => {
    expectInvalid(taskCreateSchema, { title: 'Task', course_id: 'not-a-uuid' })
  })

  it('rejects estimated_minutes > 1440', () => {
    expectInvalid(taskCreateSchema, { title: 'Task', estimated_minutes: 9999 })
  })
})

describe('taskUpdateSchema', () => {
  it('allows partial updates', () => {
    const data = expectValid(taskUpdateSchema, { title: 'Updated' })
    expect(data.title).toBe('Updated')
  })

  it('allows empty object (no fields)', () => {
    expectValid(taskUpdateSchema, {})
  })

  it('validates partial fields', () => {
    expectInvalid(taskUpdateSchema, { title: '' }, 'required')
  })
})

describe('courseCreateSchema', () => {
  it('validates minimal course', () => {
    const data = expectValid(courseCreateSchema, { title: 'React Course', platform: 'Udemy' })
    expect(data.title).toBe('React Course')
  })

  it('validates course with URL', () => {
    expectValid(courseCreateSchema, { title: 'Course', platform: 'Coursera', url: 'https://example.com' })
  })

  it('allows empty URL string', () => {
    expectValid(courseCreateSchema, { title: 'Course', platform: 'Coursera', url: '' })
  })

  it('rejects invalid URL', () => {
    expectInvalid(courseCreateSchema, { title: 'Course', platform: 'Coursera', url: 'not-a-url' })
  })

  it('rejects empty title', () => {
    expectInvalid(courseCreateSchema, { title: '', platform: 'Udemy' }, 'required')
  })
})

describe('goalCreateSchema', () => {
  it('validates a complete goal', () => {
    const data = expectValid(goalCreateSchema, {
      title: 'Learn TypeScript',
      roadmap_type: 'career_skills',
    })
    expect(data.intensity).toBe('medium')
  })

  it('rejects invalid roadmap_type', () => {
    expectInvalid(goalCreateSchema, { title: 'Goal', roadmap_type: 'invalid' })
  })

  it('rejects hours_per_day > 24', () => {
    expectInvalid(goalCreateSchema, { title: 'Goal', roadmap_type: 'career_skills', hours_per_day: 25 })
  })

  it('rejects days_per_week > 7', () => {
    expectInvalid(goalCreateSchema, { title: 'Goal', roadmap_type: 'career_skills', days_per_week: 8 })
  })
})

describe('habitCreateSchema', () => {
  it('validates a habit', () => {
    const data = expectValid(habitCreateSchema, { name: 'Read', frequency: 'daily', time_target_minutes: 30 })
    expect(data.is_active).toBe(true)
  })

  it('rejects empty name', () => {
    expectInvalid(habitCreateSchema, { name: '', frequency: 'daily', time_target_minutes: 30 }, 'required')
  })

  it('rejects invalid frequency', () => {
    expectInvalid(habitCreateSchema, { name: 'Read', frequency: 'yearly', time_target_minutes: 30 })
  })

  it('rejects time > 1440', () => {
    expectInvalid(habitCreateSchema, { name: 'Read', frequency: 'daily', time_target_minutes: 9999 })
  })
})

describe('sleepLogSchema', () => {
  it('validates a sleep log', () => {
    expectValid(sleepLogSchema, {
      bedtime: '2026-06-23T23:00:00Z',
      wake_time: '2026-06-24T07:00:00Z',
      quality_rating: 3,
      duration_hours: 8,
    })
  })

  it('rejects wake_time before bedtime', () => {
    expectInvalid(sleepLogSchema, {
      bedtime: '2026-06-24T07:00:00Z',
      wake_time: '2026-06-23T23:00:00Z',
      quality_rating: 3,
      duration_hours: 8,
    }, 'after bedtime')
  })

  it('rejects quality_rating > 5', () => {
    expectInvalid(sleepLogSchema, {
      bedtime: '2026-06-23T23:00:00Z',
      wake_time: '2026-06-24T07:00:00Z',
      quality_rating: 6,
      duration_hours: 8,
    })
  })

  it('rejects negative duration', () => {
    expectInvalid(sleepLogSchema, {
      bedtime: '2026-06-23T23:00:00Z',
      wake_time: '2026-06-24T07:00:00Z',
      quality_rating: 3,
      duration_hours: -1,
    })
  })
})

describe('ideaCreateSchema', () => {
  it('validates an idea', () => {
    const data = expectValid(ideaCreateSchema, { title: 'New App Idea' })
    expect(data.stage).toBe('raw')
  })

  it('rejects empty title', () => {
    expectInvalid(ideaCreateSchema, { title: '' }, 'required')
  })

  it('rejects invalid stage', () => {
    expectInvalid(ideaCreateSchema, { title: 'Idea', stage: 'done' })
  })
})

describe('incomeCreateSchema', () => {
  it('validates income entry', () => {
    expectValid(incomeCreateSchema, {
      source_type: 'Freelance',
      amount: 500,
      date: '2026-06-24T00:00:00Z',
    })
  })

  it('rejects negative amount', () => {
    expectInvalid(incomeCreateSchema, {
      source_type: 'Freelance',
      amount: -10,
      date: '2026-06-24T00:00:00Z',
    })
  })

  it('rejects empty source_type', () => {
    expectInvalid(incomeCreateSchema, {
      source_type: '',
      amount: 100,
      date: '2026-06-24T00:00:00Z',
    })
  })
})

describe('projectCreateSchema', () => {
  it('validates a project', () => {
    const data = expectValid(projectCreateSchema, { title: 'Build App' })
    expect(data.phase).toBe('planning')
  })

  it('allows optional URLs', () => {
    expectValid(projectCreateSchema, {
      title: 'Build App',
      live_url: 'https://example.com',
      repo_url: 'https://github.com/user/repo',
    })
  })

  it('rejects invalid URLs', () => {
    expectInvalid(projectCreateSchema, { title: 'Build App', live_url: 'not-a-url' })
  })
})

describe('resourceCreateSchema', () => {
  it('validates a resource', () => {
    const data = expectValid(resourceCreateSchema, { title: 'React Docs' })
    expect(data.resource_type).toBe('article')
    expect(data.tags).toEqual([])
  })

  it('validates with tags', () => {
    expectValid(resourceCreateSchema, {
      title: 'React Docs',
      resource_type: 'article',
      tags: ['react', 'frontend'],
    })
  })

  it('rejects tags over 50 chars', () => {
    expectInvalid(resourceCreateSchema, {
      title: 'Resource',
      tags: ['x'.repeat(51)],
    }, 'long')
  })

  it('rejects more than 20 tags', () => {
    expectInvalid(resourceCreateSchema, {
      title: 'Resource',
      tags: Array.from({ length: 21 }, (_, i) => `tag${i}`),
    }, '20')
  })
})

describe('chatMessageSchema', () => {
  it('validates a chat message', () => {
    expectValid(chatMessageSchema, { message: 'Hello ARIA' })
  })

  it('rejects empty message', () => {
    expectInvalid(chatMessageSchema, { message: '' }, 'required')
  })

  it('rejects message over 10000 chars', () => {
    expectInvalid(chatMessageSchema, { message: 'x'.repeat(10001) }, 'long')
  })
})

describe('timeEntrySchema', () => {
  it('validates a minimal time entry', () => {
    expectValid(timeEntrySchema, {
      start_time: '2026-06-24T10:00:00Z',
      activity_type: 'deep_work',
    })
  })

  it('validates with end_time', () => {
    expectValid(timeEntrySchema, {
      start_time: '2026-06-24T10:00:00Z',
      end_time: '2026-06-24T11:00:00Z',
      activity_type: 'deep_work',
    })
  })

  it('rejects end_time before start_time', () => {
    expectInvalid(timeEntrySchema, {
      start_time: '2026-06-24T11:00:00Z',
      end_time: '2026-06-24T10:00:00Z',
      activity_type: 'deep_work',
    }, 'after')
  })

  it('rejects invalid activity_type', () => {
    expectInvalid(timeEntrySchema, {
      start_time: '2026-06-24T10:00:00Z',
      activity_type: 'invalid',
    })
  })

  it('rejects duration_minutes > 1440', () => {
    expectInvalid(timeEntrySchema, {
      start_time: '2026-06-24T10:00:00Z',
      activity_type: 'deep_work',
      duration_minutes: 9999,
    })
  })
})
