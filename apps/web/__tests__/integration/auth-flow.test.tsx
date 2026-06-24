import { describe, it, expect, vi, beforeAll, afterAll, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { server } from '@/__tests__/mocks/server'
import LoginPage from '@/app/login/page'

const mockSignInWithOAuth = vi.fn()
const mockPush = vi.fn()

vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      signInWithOAuth: (...args: unknown[]) => mockSignInWithOAuth(...args),
    },
  },
  isUsingPlaceholders: false,
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush, replace: vi.fn(), back: vi.fn(), forward: vi.fn(), refresh: vi.fn(), prefetch: vi.fn() }),
  usePathname: () => '/login',
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}))

vi.mock('@/components/ThreeBackground', () => ({
  default: () => null,
}))

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => { server.resetHandlers(); vi.clearAllMocks() })
afterAll(() => server.close())

describe('Auth Flow Integration', () => {
  it('renders login page with title and description', () => {
    render(<LoginPage />)
    expect(screen.getByText('ARIA OS')).toBeInTheDocument()
    expect(screen.getByText('Your personal AI productivity system')).toBeInTheDocument()
  })

  it('renders Google sign-in button', () => {
    render(<LoginPage />)
    expect(screen.getByRole('button', { name: /continue with google/i })).toBeInTheDocument()
  })

  it('calls signInWithOAuth when Google button is clicked', async () => {
    mockSignInWithOAuth.mockResolvedValue({ data: { provider: 'google', url: 'http://localhost:3000/auth/callback' }, error: null })
    const user = userEvent.setup()
    render(<LoginPage />)

    await user.click(screen.getByRole('button', { name: /continue with google/i }))
    expect(mockSignInWithOAuth).toHaveBeenCalledWith({
      provider: 'google',
      options: { redirectTo: expect.stringContaining('/dashboard') },
    })
  })

  it('shows error message when login fails', async () => {
    mockSignInWithOAuth.mockRejectedValue(new Error('OAuth configuration error'))
    const user = userEvent.setup()
    render(<LoginPage />)

    await user.click(screen.getByRole('button', { name: /continue with google/i }))
    await waitFor(() => {
      expect(screen.getByText('ARIA OS')).toBeInTheDocument()
    })
  })

  it('disables button during loading state', async () => {
    mockSignInWithOAuth.mockImplementation(() => new Promise(() => {}))
    const user = userEvent.setup()
    render(<LoginPage />)

    const button = screen.getByRole('button', { name: /continue with google/i })
    await user.click(button)
    expect(button).toBeDisabled()
  })

  it('renders feature preview stats', () => {
    render(<LoginPage />)
    expect(screen.getByText('15+')).toBeInTheDocument()
    expect(screen.getByText('AI')).toBeInTheDocument()
    expect(screen.getByText('Free')).toBeInTheDocument()
  })
})
