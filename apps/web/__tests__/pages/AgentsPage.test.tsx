import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/lib/ai/orchestrator', () => ({
  orchestrator: {
    getPlan: vi.fn(() => null),
    on: vi.fn(() => vi.fn()),
  },
}))

import AgentsPage from '../../app/(dashboard)/agents/page'

describe('AgentsPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<AgentsPage />)
    expect(container).toBeTruthy()
  })
})
