import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/stores/taskStore', () => ({
  useTaskStore: vi.fn(() => ({
    tasks: [], loading: false, error: null,
    fetchTasks: vi.fn(), getById: vi.fn(),
    addTask: vi.fn(), updateTask: vi.fn(),
    deleteTask: vi.fn(), completeTask: vi.fn(),
  })),
}))

vi.mock('@/lib/services', () => ({
  taskService: {
    get: vi.fn().mockResolvedValue({ id: '1', title: 'Test Task', status: 'pending', priority: 'medium', tags: [] }),
    list: vi.fn().mockResolvedValue([]),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    complete: vi.fn(),
  },
}))

import TaskDetailPage from '../../app/(dashboard)/tasks/[id]/page'

describe('TaskDetailPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<TaskDetailPage />)
    expect(container).toBeTruthy()
  })
})
