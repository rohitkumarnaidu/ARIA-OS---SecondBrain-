import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/stores', async (importOriginal) => {
  const mod = await importOriginal()
  return {
    ...mod,
    useReviewStore: vi.fn(() => ({
      items: [], latest: null, loading: false, error: null,
      fetch: vi.fn(), getLatest: vi.fn(),
    })),
  }
})

vi.mock('@/lib/ai/hooks', () => ({
  useAIAgents: vi.fn(() => ({ agents: [], updateAgent: vi.fn() })),
  useAIAction: vi.fn(() => ({ execute: vi.fn(), isLoading: false })),
}))

vi.mock('@/components/ai', () => ({
  AIInsightCard: () => <div data-testid="ai-insight" />,
  ThinkingIndicator: () => <div data-testid="thinking" />,
  ConfidenceBadge: () => <div data-testid="confidence-badge" />,
}))

import ReviewPage from '../../app/(dashboard)/review/page'

describe('ReviewPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<ReviewPage />)
    expect(container).toBeTruthy()
  })
})
