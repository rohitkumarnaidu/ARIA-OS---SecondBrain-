import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/ai/hooks/useAnalytics', () => ({
  useAnalytics: vi.fn(() => ({
    stats: null, timeline: [], loading: false, error: null,
    fetchStats: vi.fn(), fetchTimeline: vi.fn(),
  })),
}))

import AnalyticsPage from '../../app/(dashboard)/analytics/page'

describe('AnalyticsPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<AnalyticsPage />)
    expect(container).toBeTruthy()
  })
})
