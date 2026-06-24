import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/stores', () => ({
  useRoadmapStore: vi.fn(() => ({
    milestones: [], loading: false, error: null,
    fetch: vi.fn(), add: vi.fn(), update: vi.fn(), remove: vi.fn(),
  })),
}))

vi.mock('@/lib/ai/hooks', () => ({
  useAIAgents: vi.fn(() => ({ agents: [], updateAgent: vi.fn() })),
  useAIAction: vi.fn(() => ({ execute: vi.fn(), isLoading: false })),
}))

vi.mock('@/components/ai', () => ({
  AIInsightCard: () => <div data-testid="ai-insight" />,
  ConfidenceBadge: () => <div data-testid="confidence-badge" />,
}))

import RoadmapPage from '../../app/(dashboard)/roadmap/page'

describe('RoadmapPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<RoadmapPage />)
    expect(container).toBeTruthy()
  })
})
