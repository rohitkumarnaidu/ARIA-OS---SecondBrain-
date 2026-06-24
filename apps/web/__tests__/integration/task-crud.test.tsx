import { describe, it, expect, vi, beforeAll, afterAll, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '@/__tests__/mocks/server'
import { buildTask, buildList } from '@/__tests__/factories'
import TasksPage from '@/app/(dashboard)/tasks/page'

const mockFetchTasks = vi.fn()
const mockAddTask = vi.fn()
const mockUpdateTask = vi.fn()
const mockDeleteTask = vi.fn()
const mockCompleteTask = vi.fn()
const mockPush = vi.fn()

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ user: { id: 'test-user', email: 'test@test.com' }, loading: false }),
}))

vi.mock('@/lib/stores/taskStore', () => ({
  useTaskStore: (selector?: (s: Record<string, unknown>) => unknown) => {
    const store = {
      tasks: [],
      loading: false,
      error: null,
      fetchTasks: mockFetchTasks,
      addTask: mockAddTask,
      updateTask: mockUpdateTask,
      deleteTask: mockDeleteTask,
      completeTask: mockCompleteTask,
    }
    return selector ? selector(store) : store
  },
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush, replace: vi.fn(), back: vi.fn(), forward: vi.fn(), refresh: vi.fn(), prefetch: vi.fn() }),
  usePathname: () => '/tasks',
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}))

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => { server.resetHandlers(); vi.clearAllMocks() })
afterAll(() => server.close())

describe('Task CRUD Integration', () => {
  it('renders tasks page header', async () => {
    mockFetchTasks.mockResolvedValue(undefined)
    render(<TasksPage />)
    await waitFor(() => {
      expect(screen.getByText('Tasks')).toBeInTheDocument()
    })
  })

  it('renders board and list view toggle', async () => {
    mockFetchTasks.mockResolvedValue(undefined)
    render(<TasksPage />)
    await waitFor(() => {
      expect(screen.getByRole('radio', { name: /board/i })).toBeInTheDocument()
      expect(screen.getByRole('radio', { name: /list/i })).toBeInTheDocument()
    })
  })

  it('renders all four kanban columns', async () => {
    mockFetchTasks.mockResolvedValue(undefined)
    render(<TasksPage />)
    await waitFor(() => {
      expect(screen.getAllByText('Backlog').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('In Progress').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Review').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Done').length).toBeGreaterThanOrEqual(1)
    })
  })

  it('renders Add Task button', async () => {
    mockFetchTasks.mockResolvedValue(undefined)
    render(<TasksPage />)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /add task/i })).toBeInTheDocument()
    })
  })

  it('shows empty column state with no tasks', async () => {
    mockFetchTasks.mockResolvedValue(undefined)
    render(<TasksPage />)
    await waitFor(() => {
      expect(screen.getAllByText('No tasks').length).toBeGreaterThanOrEqual(1)
    })
  })
})
