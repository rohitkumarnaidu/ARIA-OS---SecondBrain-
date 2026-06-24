import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { opportunityService } from '@/lib/services/opportunities'
import type { Opportunity, OpportunityCreate, OpportunityUpdate } from '@/lib/types'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

const mock = { id: 'opp-1', title: 'Internship', company: 'Acme', match_score: 85 } as Opportunity
const mockCreate = { title: 'New Opp', company: 'Beta' } as OpportunityCreate
const mockUpdate = { match_score: 90 } as OpportunityUpdate

describe('opportunityService', () => {
  describe('list', () => {
    it('returns array', async () => {
      mockedApi.get.mockResolvedValue([mock])
      const result = await opportunityService.list()
      expect(result).toEqual([mock])
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/opportunities')
    })
  })

  describe('get', () => {
    it('returns single', async () => {
      mockedApi.get.mockResolvedValue(mock)
      const result = await opportunityService.get('opp-1')
      expect(result).toEqual(mock)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/opportunities/opp-1')
    })
  })

  describe('create', () => {
    it('creates and returns', async () => {
      mockedApi.post.mockResolvedValue(mock)
      const result = await opportunityService.create(mockCreate)
      expect(result).toEqual(mock)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/opportunities', mockCreate)
    })
  })

  describe('update', () => {
    it('updates and returns', async () => {
      mockedApi.put.mockResolvedValue(mock)
      const result = await opportunityService.update('opp-1', mockUpdate)
      expect(result).toEqual(mock)
      expect(mockedApi.put).toHaveBeenCalledWith('/api/v1/opportunities/opp-1', mockUpdate)
    })
  })

  describe('delete', () => {
    it('deletes and returns message', async () => {
      mockedApi.delete.mockResolvedValue({ message: 'deleted' })
      const result = await opportunityService.delete('opp-1')
      expect(result).toEqual({ message: 'deleted' })
      expect(mockedApi.delete).toHaveBeenCalledWith('/api/v1/opportunities/opp-1')
    })
  })
})
