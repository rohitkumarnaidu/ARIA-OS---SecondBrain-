import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useTaskStore } from '@/lib/stores/taskStore'
import { taskService } from '@/lib/services/tasks'

vi.mock('@/lib/services/tasks', () => ({
  taskService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    complete: vi.fn(),
  },
}))

const mockTask = {
  id: '1',
  user_id: 'user1',
  title: 'Test task',
  status: 'pending' as const,
  priority: 'medium' as const,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('taskStore', () => {
  beforeEach(() => {
    useTaskStore.setState(useTaskStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useTaskStore.getState()
    expect(state.tasks).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('fetchTasks should load tasks', async () => {
    vi.mocked(taskService.list).mockResolvedValue([mockTask])
    await useTaskStore.getState().fetchTasks()
    const state = useTaskStore.getState()
    expect(state.tasks).toHaveLength(1)
    expect(state.tasks[0].title).toBe('Test task')
    expect(state.loading).toBe(false)
  })

  it('fetchTasks should handle errors', async () => {
    vi.mocked(taskService.list).mockRejectedValue(new Error('Network error'))
    await useTaskStore.getState().fetchTasks()
    const state = useTaskStore.getState()
    expect(state.error).toBe('Network error')
    expect(state.loading).toBe(false)
  })

  it('getById should return the correct task', async () => {
    vi.mocked(taskService.list).mockResolvedValue([mockTask])
    await useTaskStore.getState().fetchTasks()
    const found = useTaskStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.title).toBe('Test task')
  })

  it('getById should return undefined for missing id', () => {
    const found = useTaskStore.getState().getById('nonexistent')
    expect(found).toBeUndefined()
  })

  it('addTask should create and prepend a task', async () => {
    vi.mocked(taskService.create).mockResolvedValue(mockTask)
    await useTaskStore.getState().addTask({ title: 'Test task' })
    expect(useTaskStore.getState().tasks).toHaveLength(1)
    expect(useTaskStore.getState().loading).toBe(false)
  })

  it('addTask should handle errors', async () => {
    vi.mocked(taskService.create).mockRejectedValue(new Error('Create failed'))
    await useTaskStore.getState().addTask({ title: 'Test task' })
    expect(useTaskStore.getState().error).toBe('Create failed')
    expect(useTaskStore.getState().loading).toBe(false)
  })

  it('updateTask should update an existing task', async () => {
    vi.mocked(taskService.list).mockResolvedValue([mockTask])
    vi.mocked(taskService.update).mockResolvedValue({ ...mockTask, title: 'Updated' })
    await useTaskStore.getState().fetchTasks()
    await useTaskStore.getState().updateTask('1', { title: 'Updated' })
    expect(useTaskStore.getState().tasks[0].title).toBe('Updated')
  })

  it('updateTask should handle errors', async () => {
    vi.mocked(taskService.update).mockRejectedValue(new Error('Update failed'))
    vi.mocked(taskService.list).mockResolvedValue([mockTask])
    await useTaskStore.getState().fetchTasks()
    await useTaskStore.getState().updateTask('1', { title: 'Updated' })
    expect(useTaskStore.getState().error).toBe('Update failed')
  })

  it('deleteTask should remove a task', async () => {
    vi.mocked(taskService.list).mockResolvedValue([mockTask])
    vi.mocked(taskService.delete).mockResolvedValue({ message: 'Deleted' })
    await useTaskStore.getState().fetchTasks()
    await useTaskStore.getState().deleteTask('1')
    expect(useTaskStore.getState().tasks).toHaveLength(0)
  })

  it('deleteTask should handle errors', async () => {
    vi.mocked(taskService.delete).mockRejectedValue(new Error('Delete failed'))
    await useTaskStore.getState().deleteTask('1')
    expect(useTaskStore.getState().error).toBe('Delete failed')
  })

  it('completeTask should mark a task as completed', async () => {
    vi.mocked(taskService.list).mockResolvedValue([mockTask])
    vi.mocked(taskService.complete).mockResolvedValue({ ...mockTask, status: 'completed' })
    await useTaskStore.getState().fetchTasks()
    await useTaskStore.getState().completeTask('1')
    const task = useTaskStore.getState().tasks[0]
    expect(task.status).toBe('completed')
  })

  it('completeTask should handle errors', async () => {
    vi.mocked(taskService.complete).mockRejectedValue(new Error('Complete failed'))
    await useTaskStore.getState().completeTask('1')
    expect(useTaskStore.getState().error).toBe('Complete failed')
  })
})
