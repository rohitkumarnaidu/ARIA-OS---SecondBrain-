import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

import OfflinePage from '../../app/offline/page'

describe('OfflinePage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('renders without crashing', () => {
    const { container } = render(<OfflinePage />)
    expect(container).toBeTruthy()
  })

  it('shows offline message', () => {
    render(<OfflinePage />)
    expect(screen.getByText("You're Offline")).toBeInTheDocument()
  })

  it('shows offline description', () => {
    render(<OfflinePage />)
    expect(
      screen.getByText(/Some features may be unavailable/)
    ).toBeInTheDocument()
  })

  it('shows quick links to cached pages', () => {
    render(<OfflinePage />)

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Tasks')).toBeInTheDocument()
    expect(screen.getByText('Habits')).toBeInTheDocument()
    expect(screen.getByText('Courses')).toBeInTheDocument()
  })

  it('shows Try Again button', () => {
    render(<OfflinePage />)
    expect(screen.getByText('Try Again')).toBeInTheDocument()
  })

  it('displays last sync time from localStorage', () => {
    const syncTime = '2026-07-09T10:30:00'
    localStorage.setItem('aria-last-sync', syncTime)
    render(<OfflinePage />)
    expect(screen.getByText(/Last synced/)).toBeInTheDocument()
  })
})
