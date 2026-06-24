import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useRoadmapStore } from '@/lib/stores/roadmapStore'

const mockList = vi.fn()
const mockCreate = vi.fn()
const mockUpdate = vi.fn()
const mockDelete = vi.fn()

vi.mock('@/lib/services/roadmap', () => ({
  roadmapService: {
    list: (...args: unknown[]) => mockList(...args),
    create: (...args: unknown[]) => mockCreate(...args),
    update: (...args: unknown[]) => mockUpdate(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  useRoadmapStore.setState({ milestones: [], loading: false, error: null })
})

describe('roadmapStore', () => {
  it('has correct initial state', () => {
    const s = useRoadmapStore.getState()
    expect(s.milestones).toEqual([])
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
  })

  it('fetch loads milestones', async () => {
    const items = [{ id: 'm1', skill: 'React', category: 'Frontend', targetDate: '2026-03-01', progress: 50, status: 'in_progress' }]
    mockList.mockResolvedValueOnce(items)
    await useRoadmapStore.getState().fetch()
    expect(useRoadmapStore.getState().milestones).toEqual(items)
    expect(useRoadmapStore.getState().loading).toBe(false)
  })

  it('fetch sets error on failure', async () => {
    mockList.mockRejectedValueOnce(new Error('Network error'))
    await useRoadmapStore.getState().fetch()
    expect(useRoadmapStore.getState().error).toBe('Network error')
  })

  it('add prepends a milestone', async () => {
    const created = { id: 'm2', skill: 'Python', category: 'Backend', targetDate: '2026-04-01', progress: 0, status: 'not_started' as const }
    mockCreate.mockResolvedValueOnce(created)
    await useRoadmapStore.getState().add({ skill: 'Python' })
    expect(useRoadmapStore.getState().milestones).toEqual([created])
  })

  it('add sets error on failure', async () => {
    mockCreate.mockRejectedValueOnce(new Error('Validation failed'))
    await useRoadmapStore.getState().add({ skill: '' })
    expect(useRoadmapStore.getState().error).toBe('Validation failed')
  })

  it('update merges partial data into milestone', async () => {
    const existing = { id: 'm1', skill: 'React', category: 'Frontend', targetDate: '2026-03-01', progress: 50, status: 'in_progress' as const }
    useRoadmapStore.setState({ milestones: [existing] })
    mockUpdate.mockResolvedValueOnce({ progress: 80, status: 'completed' })
    await useRoadmapStore.getState().update('m1', { progress: 80, status: 'completed' })
    const m = useRoadmapStore.getState().milestones[0]
    expect(m.progress).toBe(80)
    expect(m.status).toBe('completed')
    expect(m.skill).toBe('React')
  })

  it('update sets error on failure', async () => {
    useRoadmapStore.setState({ milestones: [{ id: 'm1', skill: 'React', category: '', targetDate: '', progress: 0, status: 'not_started' }] })
    mockUpdate.mockRejectedValueOnce(new Error('Not found'))
    await useRoadmapStore.getState().update('m1', { progress: 100 })
    expect(useRoadmapStore.getState().error).toBe('Not found')
  })

  it('remove filters out deleted milestone', async () => {
    useRoadmapStore.setState({
      milestones: [
        { id: 'm1', skill: 'React', category: '', targetDate: '', progress: 0, status: 'not_started' },
        { id: 'm2', skill: 'Python', category: '', targetDate: '', progress: 0, status: 'not_started' },
      ],
    })
    mockDelete.mockResolvedValueOnce({})
    await useRoadmapStore.getState().remove('m1')
    expect(useRoadmapStore.getState().milestones).toEqual([
      { id: 'm2', skill: 'Python', category: '', targetDate: '', progress: 0, status: 'not_started' },
    ])
  })

  it('remove sets error on failure', async () => {
    mockDelete.mockRejectedValueOnce(new Error('Delete failed'))
    await useRoadmapStore.getState().remove('x')
    expect(useRoadmapStore.getState().error).toBe('Delete failed')
  })
})
