import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1', name: 'Test User' }, loading: false })),
}))

vi.mock('@/lib/stores', () => ({
  useTaskStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetchTasks: vi.fn(), getById: vi.fn(),
    addTask: vi.fn(), updateTask: vi.fn(),
    deleteTask: vi.fn(), completeTask: vi.fn(),
  })),
  useGoalStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(),
  })),
  useHabitStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(), log: vi.fn(),
  })),
  useCourseStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(),
  })),
  useSleepStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), remove: vi.fn(),
  })),
  useBriefingStore: vi.fn(() => ({
    today: null, loading: false, error: null, getToday: vi.fn(),
  })),
  useReviewStore: vi.fn(() => ({
    items: [], latest: null, loading: false, error: null,
    fetch: vi.fn(), getLatest: vi.fn(),
  })),
  useProjectStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(),
  })),
  useMemoryStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), remove: vi.fn(), update: vi.fn(),
  })),
  useOpportunityStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(),
  })),
  useTimeStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(), stop: vi.fn(),
  })),
  useChatStore: vi.fn(() => ({
    messages: [], loading: false, error: null,
    sendMessage: vi.fn(), fetchMessages: vi.fn(),
  })),
  useUserStore: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

import DashboardPage from '../../app/(dashboard)/dashboard/page'

describe('DashboardPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<DashboardPage />)
    expect(container).toBeTruthy()
  })
})
