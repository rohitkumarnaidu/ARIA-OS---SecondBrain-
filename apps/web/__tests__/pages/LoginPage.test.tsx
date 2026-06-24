import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/components/ThreeBackground', () => ({
  default: () => <div data-testid="three-bg" />,
}))

vi.mock('@/lib/supabase', () => ({
  supabase: { auth: { signInWithOAuth: vi.fn() } },
}))

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: null, loading: false })),
}))

import LoginPage from '../../app/login/page'

describe('LoginPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<LoginPage />)
    expect(container).toBeTruthy()
  })
})
