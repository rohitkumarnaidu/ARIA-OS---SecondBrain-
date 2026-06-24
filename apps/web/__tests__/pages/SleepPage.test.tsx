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
  useSleepStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), remove: vi.fn(),
  })),
}))

import SleepPage from '../../app/(dashboard)/sleep/page'

describe('SleepPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<SleepPage />)
    expect(container).toBeTruthy()
  })
})
