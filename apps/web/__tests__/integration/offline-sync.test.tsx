import { describe, it, expect, vi, beforeAll, afterAll, afterEach, beforeEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { server } from '@/__tests__/mocks/server'
import OfflinePage from '@/app/offline/page'
import OfflineBanner from '@/components/layout/OfflineBanner'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
beforeEach(() => { vi.mocked(useNetworkStatus).mockReturnValue({ isOnline: true }) })
afterEach(() => { server.resetHandlers(); vi.clearAllMocks() })
afterAll(() => server.close())

vi.mock('@/hooks/useNetworkStatus')

describe('Offline Sync Integration', () => {
  describe('OfflinePage', () => {
    it('renders offline page with title', () => {
      render(<OfflinePage />)
      expect(screen.getByText("You're Offline")).toBeInTheDocument()
    })

    it('renders offline icon', () => {
      const { container } = render(<OfflinePage />)
      const svg = container.querySelector('svg.lucide-wifi-off')
      expect(svg).toBeInTheDocument()
    })

    it('lists available offline features', () => {
      render(<OfflinePage />)
      expect(screen.getByText(/cached tasks and notes/i)).toBeInTheDocument()
      expect(screen.getByText(/previously loaded data/i)).toBeInTheDocument()
      expect(screen.getByText(/edit cached items/i)).toBeInTheDocument()
    })
  })

  describe('OfflineBanner', () => {
    it('shows banner when offline', () => {
      vi.mocked(useNetworkStatus).mockReturnValue({ isOnline: false })
      render(<OfflineBanner />)
      expect(screen.getByText('You are offline')).toBeInTheDocument()
      expect(screen.getByRole('alert')).toBeInTheDocument()
    })

    it('hides banner when online', () => {
      vi.mocked(useNetworkStatus).mockReturnValue({ isOnline: true })
      render(<OfflineBanner />)
      expect(screen.queryByText('You are offline')).not.toBeInTheDocument()
      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })

    it('has assertive aria-live for accessibility', () => {
      vi.mocked(useNetworkStatus).mockReturnValue({ isOnline: false })
      render(<OfflineBanner />)
      expect(screen.getByRole('alert')).toHaveAttribute('aria-live', 'assertive')
    })

    it('toggles visibility when network status changes', () => {
      const { rerender } = render(<OfflineBanner />)
      expect(screen.queryByText('You are offline')).not.toBeInTheDocument()

      vi.mocked(useNetworkStatus).mockReturnValue({ isOnline: false })
      rerender(<OfflineBanner />)
      expect(screen.getByText('You are offline')).toBeInTheDocument()

      vi.mocked(useNetworkStatus).mockReturnValue({ isOnline: true })
      rerender(<OfflineBanner />)
      expect(screen.queryByText('You are offline')).not.toBeInTheDocument()
    })
  })
})
