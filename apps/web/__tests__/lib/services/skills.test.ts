import { describe, it, expect, vi, beforeEach } from 'vitest'
import { skillService } from '@/lib/services/skills'

vi.mock('@/lib/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
}))

const { api } = require('@/lib/api')

describe('skillService', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('list calls GET /api/v1/skills/', async () => {
    api.get.mockResolvedValue([])
    const result = await skillService.list()
    expect(api.get).toHaveBeenCalledWith('/api/v1/skills/', { params: undefined })
    expect(result).toEqual([])
  })

  it('get calls GET /api/v1/skills/:id', async () => {
    api.get.mockResolvedValue({ skill_id: 's1' })
    const result = await skillService.get('s1')
    expect(api.get).toHaveBeenCalledWith('/api/v1/skills/s1')
    expect(result.skill_id).toBe('s1')
  })

  it('create calls POST /api/v1/skills/', async () => {
    api.post.mockResolvedValue({ skill_id: 'new' })
    const result = await skillService.create({ name: 'React' })
    expect(api.post).toHaveBeenCalledWith('/api/v1/skills', { name: 'React' })
    expect(result.skill_id).toBe('new')
  })

  it('categories.list calls GET /api/v1/skills/categories', async () => {
    api.get.mockResolvedValue([])
    await skillService.categories.list()
    expect(api.get).toHaveBeenCalledWith('/api/v1/skills/categories', { params: undefined })
  })

  it('userSkills.list calls GET /api/v1/skills/user-skills', async () => {
    api.get.mockResolvedValue([])
    await skillService.userSkills.list()
    expect(api.get).toHaveBeenCalledWith('/api/v1/skills/user-skills', { params: undefined })
  })

  it('evidence.create calls POST /api/v1/skills/evidence', async () => {
    api.post.mockResolvedValue({ evidence_id: 'ev-1' })
    await skillService.evidence.create({ title: 'Cert', signed_hash: 'abc', user_skill_id: 'us-1', collected_at: 0, user_id: 'u-1', source_type: 'certification' })
    expect(api.post).toHaveBeenCalledWith('/api/v1/skills/evidence', expect.any(Object))
  })

  it('recommendations.list calls GET /api/v1/skills/recommendations', async () => {
    api.get.mockResolvedValue([])
    await skillService.recommendations.list()
    expect(api.get).toHaveBeenCalledWith('/api/v1/skills/recommendations', { params: undefined })
  })

  it('activity.log calls POST /api/v1/skills/activity', async () => {
    api.post.mockResolvedValue({ activity_id: 'a-1' })
    await skillService.activity.log({ activity_type: 'skill_tree_viewed', user_id: 'u-1' })
    expect(api.post).toHaveBeenCalledWith('/api/v1/skills/activity', expect.any(Object))
  })

  it('delete calls DELETE /api/v1/skills/:id', async () => {
    api.delete.mockResolvedValue({ message: 'deleted' })
    await skillService.delete('s1')
    expect(api.delete).toHaveBeenCalledWith('/api/v1/skills/s1')
  })

  it('tags.link calls POST /api/v1/skills/tags/link', async () => {
    api.post.mockResolvedValue({ status: 'linked' })
    await skillService.tags.link('s1', 't1')
    expect(api.post).toHaveBeenCalledWith('/api/v1/skills/tags/link', { skill_id: 's1', tag_id: 't1' })
  })
})
