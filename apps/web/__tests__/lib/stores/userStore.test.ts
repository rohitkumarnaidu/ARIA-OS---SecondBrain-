import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useUserStore } from '@/lib/stores/userStore'

const mockSignInWithOAuth = vi.fn()
const mockSignOut = vi.fn()
const mockGetUser = vi.fn()
const mockFromSelect = vi.fn()

vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      signInWithOAuth: (...args: unknown[]) => mockSignInWithOAuth(...args),
      signOut: (...args: unknown[]) => mockSignOut(...args),
      getUser: (...args: unknown[]) => mockGetUser(...args),
    },
    from: () => ({
      select: (...args: unknown[]) => ({
        eq: (...args2: unknown[]) => ({
          single: (...args3: unknown[]) => mockFromSelect(...args3),
        }),
      }),
    }),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  useUserStore.setState({ user: null, loading: false, error: null })
})

describe('userStore', () => {
  it('has correct initial state', () => {
    const s = useUserStore.getState()
    expect(s.user).toBeNull()
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
  })

  it('signIn calls google OAuth', async () => {
    mockSignInWithOAuth.mockResolvedValueOnce({ error: null })
    await useUserStore.getState().signIn()
    expect(mockSignInWithOAuth).toHaveBeenCalledWith({
      provider: 'google',
      options: { redirectTo: expect.stringContaining('/dashboard') },
    })
    expect(useUserStore.getState().loading).toBe(false)
  })

  it('signIn sets error on failure', async () => {
    mockSignInWithOAuth.mockResolvedValueOnce({ error: new Error('OAuth failed') })
    await useUserStore.getState().signIn()
    expect(useUserStore.getState().error).toBe('OAuth failed')
  })

  it('signIn sets generic error on thrown exception', async () => {
    mockSignInWithOAuth.mockRejectedValueOnce(new Error('Network error'))
    await useUserStore.getState().signIn()
    expect(useUserStore.getState().error).toBe('Network error')
  })

  it('signOut clears user', async () => {
    useUserStore.setState({ user: { id: 'u1', email: 'test@test.com' } })
    mockSignOut.mockResolvedValueOnce({ error: null })
    await useUserStore.getState().signOut()
    expect(useUserStore.getState().user).toBeNull()
    expect(useUserStore.getState().loading).toBe(false)
  })

  it('signOut sets error on failure', async () => {
    mockSignOut.mockResolvedValueOnce({ error: new Error('Sign out failed') })
    await useUserStore.getState().signOut()
    expect(useUserStore.getState().error).toBe('Sign out failed')
  })

  it('fetchUser loads user from supabase', async () => {
    const supabaseUser = { id: 'u1', email: 'test@test.com' }
    const profile = { id: 'u1', name: 'Test User', college: 'MIT' }
    mockGetUser.mockResolvedValueOnce({ data: { user: supabaseUser } })
    mockFromSelect.mockResolvedValueOnce({ data: profile, error: null })
    await useUserStore.getState().fetchUser()
    expect(useUserStore.getState().user).toEqual(profile)
    expect(useUserStore.getState().loading).toBe(false)
  })

  it('fetchUser falls back to auth user when no profile', async () => {
    mockGetUser.mockResolvedValueOnce({ data: { user: { id: 'u2', email: 'guest@test.com' } } })
    mockFromSelect.mockResolvedValueOnce({ data: null, error: null })
    await useUserStore.getState().fetchUser()
    expect(useUserStore.getState().user).toEqual({ id: 'u2', email: 'guest@test.com' })
  })

  it('fetchUser sets user null when no auth user', async () => {
    mockGetUser.mockResolvedValueOnce({ data: { user: null } })
    await useUserStore.getState().fetchUser()
    expect(useUserStore.getState().user).toBeNull()
    expect(useUserStore.getState().loading).toBe(false)
  })

  it('fetchUser sets error on failure', async () => {
    mockGetUser.mockRejectedValueOnce(new Error('Unauthorized'))
    await useUserStore.getState().fetchUser()
    expect(useUserStore.getState().error).toBe('Unauthorized')
  })
})
