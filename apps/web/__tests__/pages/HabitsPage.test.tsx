import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/hooks', () => ({
  usePredictions: vi.fn(() => ({
    habits: [], sleep: null, loading: false,
  })),
}))

vi.mock('@/lib/stores', () => ({
  useHabitStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(), log: vi.fn(),
  })),
}))

import HabitsPage from '../../app/(dashboard)/habits/page'

describe('HabitsPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<HabitsPage />)
    expect(container).toBeTruthy()
  })
})
