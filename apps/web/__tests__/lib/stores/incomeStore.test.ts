import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useIncomeStore } from '@/lib/stores/incomeStore'
import { incomeService } from '@/lib/services/income'

vi.mock('@/lib/services/income', () => ({
  incomeService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockIncome = {
  id: '1',
  user_id: 'user1',
  source_type: 'freelance',
  amount: 500,
  date: '2026-01-01',
  created_at: '2026-01-01T00:00:00Z',
}

describe('incomeStore', () => {
  beforeEach(() => {
    useIncomeStore.setState(useIncomeStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useIncomeStore.getState()
    expect(state.items).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('fetch should load income entries', async () => {
    vi.mocked(incomeService.list).mockResolvedValue([mockIncome])
    await useIncomeStore.getState().fetch()
    const state = useIncomeStore.getState()
    expect(state.items).toHaveLength(1)
    expect(state.items[0].amount).toBe(500)
    expect(state.loading).toBe(false)
  })

  it('fetch should handle errors', async () => {
    vi.mocked(incomeService.list).mockRejectedValue(new Error('Network error'))
    await useIncomeStore.getState().fetch()
    expect(useIncomeStore.getState().error).toBe('Network error')
  })

  it('getById should return the correct entry', async () => {
    vi.mocked(incomeService.list).mockResolvedValue([mockIncome])
    await useIncomeStore.getState().fetch()
    const found = useIncomeStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.source_type).toBe('freelance')
  })

  it('create should add an income entry', async () => {
    vi.mocked(incomeService.create).mockResolvedValue(mockIncome)
    await useIncomeStore.getState().create({ source_type: 'freelance', amount: 500 })
    expect(useIncomeStore.getState().items).toHaveLength(1)
  })

  it('create should handle errors', async () => {
    vi.mocked(incomeService.create).mockRejectedValue(new Error('Create failed'))
    await useIncomeStore.getState().create({ source_type: 'freelance', amount: 500 })
    expect(useIncomeStore.getState().error).toBe('Create failed')
  })

  it('update should modify an income entry', async () => {
    vi.mocked(incomeService.list).mockResolvedValue([mockIncome])
    vi.mocked(incomeService.update).mockResolvedValue({ ...mockIncome, amount: 600 })
    await useIncomeStore.getState().fetch()
    await useIncomeStore.getState().update('1', { amount: 600 })
    expect(useIncomeStore.getState().items[0].amount).toBe(600)
  })

  it('update should handle errors', async () => {
    vi.mocked(incomeService.update).mockRejectedValue(new Error('Update failed'))
    await useIncomeStore.getState().update('1', { amount: 600 })
    expect(useIncomeStore.getState().error).toBe('Update failed')
  })

  it('remove should delete an income entry', async () => {
    vi.mocked(incomeService.list).mockResolvedValue([mockIncome])
    vi.mocked(incomeService.delete).mockResolvedValue({ message: 'Deleted' })
    await useIncomeStore.getState().fetch()
    await useIncomeStore.getState().remove('1')
    expect(useIncomeStore.getState().items).toHaveLength(0)
  })

  it('remove should handle errors', async () => {
    vi.mocked(incomeService.delete).mockRejectedValue(new Error('Delete failed'))
    await useIncomeStore.getState().remove('1')
    expect(useIncomeStore.getState().error).toBe('Delete failed')
  })
})
