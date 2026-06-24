import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/stores', () => ({
  useIncomeStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), remove: vi.fn(),
  })),
}))

import IncomePage from '../../app/(dashboard)/income/page'

describe('IncomePage', () => {
  it('renders without crashing', () => {
    const { container } = render(<IncomePage />)
    expect(container).toBeTruthy()
  })
})
