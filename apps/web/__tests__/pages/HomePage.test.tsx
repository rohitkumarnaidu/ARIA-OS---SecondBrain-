import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/components/ThreeBackground', () => ({
  default: () => <div data-testid="three-bg" />,
}))

vi.mock('@/lib/stores', () => ({
  useUserStore: vi.fn(() => ({ user: null, loading: false, error: null, signIn: vi.fn(), signOut: vi.fn(), fetchUser: vi.fn() })),
}))

import HomePage from '../../app/page'

describe('HomePage', () => {
  it('renders without crashing', () => {
    const { container } = render(<HomePage />)
    expect(container).toBeTruthy()
  })
})
