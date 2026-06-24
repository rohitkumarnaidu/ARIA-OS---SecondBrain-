import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/stores', () => ({
  useBriefingStore: vi.fn(() => ({
    today: null, loading: false, error: null, getToday: vi.fn(),
  })),
}))

import BriefingPage from '../../app/(dashboard)/briefing/page'

describe('BriefingPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<BriefingPage />)
    expect(container).toBeTruthy()
  })
})
