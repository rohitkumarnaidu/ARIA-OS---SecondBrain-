import type {
  Task as CanonicalTask,
  TaskStatus as CanonicalTaskStatus,
  TaskPriority as CanonicalTaskPriority,
} from '@/lib/types'

export type TaskCategory = 'study' | 'project' | 'habit' | 'personal' | 'income'
export type { CanonicalTask as Task }
export type { CanonicalTaskStatus as TaskStatus }
export type { CanonicalTaskPriority as TaskPriority }

export interface TaskFormData {
  title: string
  description?: string
  priority: CanonicalTaskPriority
  category: TaskCategory
  estimated_minutes?: number
  due_date?: string
  goal_id?: string
  project_id?: string
  dependency_id?: string
  is_recurring: boolean
  recurring_frequency?: string
}
