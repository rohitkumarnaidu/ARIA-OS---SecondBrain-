import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/stores', () => ({
  useGoalStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(),
  })),
}))

import GoalsPage from '../../app/(dashboard)/goals/page'

describe('GoalsPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<GoalsPage />)
    expect(container).toBeTruthy()
  })
})
