export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'
export type TaskCategory = 'study' | 'project' | 'habit' | 'personal' | 'income'
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled'

export interface Task {
  id: string
  user_id: string
  title: string
  description?: string
  priority: TaskPriority
  category: TaskCategory
  status: TaskStatus
  estimated_minutes?: number
  due_date?: string
  goal_id?: string
  project_id?: string
  completed_at?: string
  missed_count: number
  dependency_id?: string
  is_recurring: boolean
  recurring_frequency?: string
  created_at: string
  updated_at: string
}

export interface TaskFormData {
  title: string
  description?: string
  priority: TaskPriority
  category: TaskCategory
  estimated_minutes?: number
  due_date?: string
  goal_id?: string
  project_id?: string
  dependency_id?: string
  is_recurring: boolean
  recurring_frequency?: string
}
