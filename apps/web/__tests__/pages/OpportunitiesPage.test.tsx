import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/stores', async (importOriginal) => {
  const mod = await importOriginal()
  return {
    ...mod,
    useOpportunityStore: vi.fn(() => ({
      items: [], loading: false, error: null,
      fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(),
    })),
  }
})

vi.mock('@/lib/ai/hooks', () => ({
  useAIAgents: vi.fn(() => ({ agents: [], updateAgent: vi.fn() })),
  useAIAction: vi.fn(() => ({ execute: vi.fn(), isLoading: false })),
}))

vi.mock('@/components/ai', () => ({
  AIInsightCard: () => <div data-testid="ai-insight" />,
  ConfidenceBadge: () => <div data-testid="confidence-badge" />,
}))

vi.mock('@/components/opportunities/RadarScanner', () => ({
  RadarScanner: () => <div data-testid="radar-scanner" />,
}))

vi.mock('@/components/opportunities/MatchCard', () => ({
  MatchCard: () => <div data-testid="match-card" />,
}))

vi.mock('@/components/opportunities/SignalList', () => ({
  SignalList: () => <div data-testid="signal-list" />,
}))

vi.mock('@/components/opportunities/OpportunityDetail', () => ({
  OpportunityDetail: () => <div data-testid="opportunity-detail" />,
}))

vi.mock('@/components/opportunities/MatchTierPills', () => ({
  MatchTierPills: () => <div data-testid="match-tier-pills" />,
}))

import OpportunitiesPage from '../../app/(dashboard)/opportunities/page'

describe('OpportunitiesPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<OpportunitiesPage />)
    expect(container).toBeTruthy()
  })
})
