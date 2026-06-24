import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/lib/stores', () => ({
  useKnowledgeStore: vi.fn(() => ({
    nodes: [], edges: [], loading: false, error: null,
    fetch: vi.fn(),
  })),
}))

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/components/knowledge', () => ({
  KnowledgeGraph: () => <div data-testid="knowledge-graph" />,
  NodeDetail: () => <div data-testid="node-detail" />,
  KnowledgeSearch: () => <div data-testid="knowledge-search" />,
}))

import KnowledgePage from '../../app/(dashboard)/knowledge/page'

describe('KnowledgePage', () => {
  it('renders without crashing', () => {
    const { container } = render(<KnowledgePage />)
    expect(container).toBeTruthy()
  })
})
