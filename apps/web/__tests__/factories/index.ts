import { faker } from '@faker-js/faker'

export interface Task {
  id: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  due_date: string | null
  user_id: string
  created_at: string
  updated_at: string
}

export interface User {
  id: string
  email: string
  display_name: string
  created_at: string
}

export interface Goal {
  id: string
  title: string
  description: string
  status: 'active' | 'completed' | 'archived'
  user_id: string
  created_at: string
}

export interface Course {
  id: string
  title: string
  progress: number
  status: 'not_started' | 'in_progress' | 'completed'
  user_id: string
  created_at: string
}

export interface Habit {
  id: string
  name: string
  frequency: 'daily' | 'weekly' | 'monthly'
  streak: number
  user_id: string
  created_at: string
}

export interface HabitLog {
  id: string
  habit_id: string
  date: string
  completed: boolean
  user_id: string
}

export interface SleepLog {
  id: string
  date: string
  duration_hours: number
  quality: number
  user_id: string
}

// --- Exported builders ---

export function buildTask(overrides: Partial<Task> = {}): Task {
  return {
    id: faker.string.uuid(),
    title: faker.lorem.sentence(4),
    description: faker.lorem.paragraph(),
    status: faker.helpers.arrayElement(['pending', 'in_progress', 'completed', 'cancelled']),
    priority: faker.helpers.arrayElement(['low', 'medium', 'high', 'urgent']),
    due_date: faker.helpers.maybe(() => faker.date.future().toISOString()) ?? null,
    user_id: faker.string.uuid(),
    created_at: faker.date.past().toISOString(),
    updated_at: faker.date.recent().toISOString(),
    ...overrides,
  }
}

export function buildUser(overrides: Partial<User> = {}): User {
  return {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    display_name: faker.person.fullName(),
    created_at: faker.date.past().toISOString(),
    ...overrides,
  }
}

export function buildGoal(overrides: Partial<Goal> = {}): Goal {
  return {
    id: faker.string.uuid(),
    title: faker.lorem.sentence(6),
    description: faker.lorem.paragraph(),
    status: faker.helpers.arrayElement(['active', 'completed', 'archived']),
    user_id: faker.string.uuid(),
    created_at: faker.date.past().toISOString(),
    ...overrides,
  }
}

export function buildCourse(overrides: Partial<Course> = {}): Course {
  return {
    id: faker.string.uuid(),
    title: faker.lorem.sentence(3),
    progress: faker.number.int({ min: 0, max: 100 }),
    status: faker.helpers.arrayElement(['not_started', 'in_progress', 'completed']),
    user_id: faker.string.uuid(),
    created_at: faker.date.past().toISOString(),
    ...overrides,
  }
}

export function buildHabit(overrides: Partial<Habit> = {}): Habit {
  return {
    id: faker.string.uuid(),
    name: faker.lorem.words(3),
    frequency: faker.helpers.arrayElement(['daily', 'weekly', 'monthly']),
    streak: faker.number.int({ min: 0, max: 365 }),
    user_id: faker.string.uuid(),
    created_at: faker.date.past().toISOString(),
    ...overrides,
  }
}

export function buildHabitLog(overrides: Partial<HabitLog> = {}): HabitLog {
  return {
    id: faker.string.uuid(),
    habit_id: faker.string.uuid(),
    date: faker.date.recent().toISOString().slice(0, 10),
    completed: faker.datatype.boolean(),
    user_id: faker.string.uuid(),
    ...overrides,
  }
}

export function buildSleepLog(overrides: Partial<SleepLog> = {}): SleepLog {
  return {
    id: faker.string.uuid(),
    date: faker.date.recent().toISOString().slice(0, 10),
    duration_hours: faker.number.float({ min: 4, max: 10, fractionDigits: 1 }),
    quality: faker.number.int({ min: 1, max: 5 }),
    user_id: faker.string.uuid(),
    ...overrides,
  }
}

export function buildList<T>(builder: () => T, count: number = 3): T[] {
  return Array.from({ length: count }, () => builder())
}
