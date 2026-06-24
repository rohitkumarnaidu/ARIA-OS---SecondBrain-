import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/stores', () => ({
  useTaskStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetchTasks: vi.fn(), getById: vi.fn(),
    addTask: vi.fn(), updateTask: vi.fn(),
    deleteTask: vi.fn(), completeTask: vi.fn(),
  })),
}))

import TasksPage from '../../app/(dashboard)/tasks/page'

describe('TasksPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<TasksPage />)
    expect(container).toBeTruthy()
  })
})
