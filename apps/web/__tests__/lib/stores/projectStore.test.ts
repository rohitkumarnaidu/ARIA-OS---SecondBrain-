import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useProjectStore } from '@/lib/stores/projectStore'
import { projectService } from '@/lib/services/projects'

vi.mock('@/lib/services/projects', () => ({
  projectService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockProject = {
  id: '1',
  user_id: 'user1',
  title: 'Test Project',
  phase: 'planning',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('projectStore', () => {
  beforeEach(() => {
    useProjectStore.setState(useProjectStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useProjectStore.getState()
    expect(state.items).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('fetch should load projects', async () => {
    vi.mocked(projectService.list).mockResolvedValue([mockProject])
    await useProjectStore.getState().fetch()
    const state = useProjectStore.getState()
    expect(state.items).toHaveLength(1)
    expect(state.items[0].title).toBe('Test Project')
    expect(state.loading).toBe(false)
  })

  it('fetch should handle errors', async () => {
    vi.mocked(projectService.list).mockRejectedValue(new Error('Network error'))
    await useProjectStore.getState().fetch()
    expect(useProjectStore.getState().error).toBe('Network error')
    expect(useProjectStore.getState().loading).toBe(false)
  })

  it('getById should return the correct project', async () => {
    vi.mocked(projectService.list).mockResolvedValue([mockProject])
    await useProjectStore.getState().fetch()
    const found = useProjectStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.title).toBe('Test Project')
  })

  it('create should add a project', async () => {
    vi.mocked(projectService.create).mockResolvedValue(mockProject)
    await useProjectStore.getState().create({ title: 'Test Project' })
    expect(useProjectStore.getState().items).toHaveLength(1)
  })

  it('create should handle errors', async () => {
    vi.mocked(projectService.create).mockRejectedValue(new Error('Create failed'))
    await useProjectStore.getState().create({ title: 'Test Project' })
    expect(useProjectStore.getState().error).toBe('Create failed')
  })

  it('update should modify a project', async () => {
    vi.mocked(projectService.list).mockResolvedValue([mockProject])
    vi.mocked(projectService.update).mockResolvedValue({ ...mockProject, title: 'Updated' })
    await useProjectStore.getState().fetch()
    await useProjectStore.getState().update('1', { title: 'Updated' })
    expect(useProjectStore.getState().items[0].title).toBe('Updated')
  })

  it('update should handle errors', async () => {
    vi.mocked(projectService.update).mockRejectedValue(new Error('Update failed'))
    await useProjectStore.getState().update('1', { title: 'Updated' })
    expect(useProjectStore.getState().error).toBe('Update failed')
  })

  it('remove should delete a project', async () => {
    vi.mocked(projectService.list).mockResolvedValue([mockProject])
    vi.mocked(projectService.delete).mockResolvedValue({ message: 'Deleted' })
    await useProjectStore.getState().fetch()
    await useProjectStore.getState().remove('1')
    expect(useProjectStore.getState().items).toHaveLength(0)
  })

  it('remove should handle errors', async () => {
    vi.mocked(projectService.delete).mockRejectedValue(new Error('Delete failed'))
    await useProjectStore.getState().remove('1')
    expect(useProjectStore.getState().error).toBe('Delete failed')
  })
})
