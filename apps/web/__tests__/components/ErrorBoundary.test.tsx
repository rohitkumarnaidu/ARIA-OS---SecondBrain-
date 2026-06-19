import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'

describe('ErrorBoundary', () => {
  it('renders children when no error', () => {
    render(<ErrorBoundary><div>All good</div></ErrorBoundary>)
    expect(screen.getByText('All good')).toBeTruthy()
  })

  it('renders fallback on error', () => {
    const Throwing = () => { throw new Error('Boom') }
    render(<ErrorBoundary><Throwing /></ErrorBoundary>)
    expect(screen.getByText((content) => content.includes('failed to load'))).toBeTruthy()
  })
})
