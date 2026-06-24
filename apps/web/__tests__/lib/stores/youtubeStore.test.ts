import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useYoutubeStore } from '@/lib/stores/youtubeStore'

const mockList = vi.fn()
const mockCreate = vi.fn()
const mockUpdate = vi.fn()
const mockDelete = vi.fn()

vi.mock('@/lib/services/youtube', () => ({
  youtubeService: {
    list: (...args: unknown[]) => mockList(...args),
    create: (...args: unknown[]) => mockCreate(...args),
    update: (...args: unknown[]) => mockUpdate(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  useYoutubeStore.setState({ items: [], loading: false, error: null })
})

describe('youtubeStore', () => {
  it('has correct initial state', () => {
    const s = useYoutubeStore.getState()
    expect(s.items).toEqual([])
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
  })

  it('fetch loads videos', async () => {
    const items = [{ id: 'v1', title: 'React Tutorial', url: 'https://youtube.com/watch?v=abc' }]
    mockList.mockResolvedValueOnce(items)
    await useYoutubeStore.getState().fetch()
    expect(useYoutubeStore.getState().items).toEqual(items)
    expect(useYoutubeStore.getState().loading).toBe(false)
  })

  it('fetch sets error on failure', async () => {
    mockList.mockRejectedValueOnce(new Error('API unavailable'))
    await useYoutubeStore.getState().fetch()
    expect(useYoutubeStore.getState().error).toBe('API unavailable')
  })

  it('create prepends a video', async () => {
    const created = { id: 'v2', title: 'New Video', url: 'https://youtube.com/watch?v=xyz' }
    mockCreate.mockResolvedValueOnce(created)
    await useYoutubeStore.getState().create({ title: 'New Video', url: 'https://youtube.com/watch?v=xyz' })
    expect(useYoutubeStore.getState().items).toEqual([created])
  })

  it('create sets error on failure', async () => {
    mockCreate.mockRejectedValueOnce(new Error('Invalid URL'))
    await useYoutubeStore.getState().create({ title: '', url: '' })
    expect(useYoutubeStore.getState().error).toBe('Invalid URL')
  })

  it('update replaces video in place', async () => {
    useYoutubeStore.setState({ items: [{ id: 'v1', title: 'Old Title', url: 'https://youtube.com/watch?v=abc' }] })
    const updated = { id: 'v1', title: 'Updated Title', url: 'https://youtube.com/watch?v=abc' }
    mockUpdate.mockResolvedValueOnce(updated)
    await useYoutubeStore.getState().update('v1', { title: 'Updated Title' })
    expect(useYoutubeStore.getState().items).toEqual([updated])
  })

  it('update sets error on failure', async () => {
    useYoutubeStore.setState({ items: [{ id: 'v1', title: 'Old', url: '' }] })
    mockUpdate.mockRejectedValueOnce(new Error('Not found'))
    await useYoutubeStore.getState().update('v1', { title: 'New' })
    expect(useYoutubeStore.getState().error).toBe('Not found')
  })

  it('remove filters out deleted video', async () => {
    useYoutubeStore.setState({ items: [{ id: 'v1', title: 'A', url: '' }, { id: 'v2', title: 'B', url: '' }] })
    mockDelete.mockResolvedValueOnce({})
    await useYoutubeStore.getState().remove('v1')
    expect(useYoutubeStore.getState().items).toEqual([{ id: 'v2', title: 'B', url: '' }])
  })

  it('remove sets error on failure', async () => {
    mockDelete.mockRejectedValueOnce(new Error('Delete failed'))
    await useYoutubeStore.getState().remove('x')
    expect(useYoutubeStore.getState().error).toBe('Delete failed')
  })
})
