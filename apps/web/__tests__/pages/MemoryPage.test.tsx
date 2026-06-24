import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/lib/stores', () => ({
  useMemoryStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), remove: vi.fn(), update: vi.fn(),
  })),
}))

import MemoryPage from '../../app/(dashboard)/memory/page'

describe('MemoryPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<MemoryPage />)
    expect(container).toBeTruthy()
  })
})
