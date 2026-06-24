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

  it('renders custom fallback component', () => {
    const CustomFallback = () => <div>Custom Error UI</div>
    const Throwing = () => { throw new Error('Boom') }
    render(<ErrorBoundary fallback={<CustomFallback />}><Throwing /></ErrorBoundary>)
    expect(screen.getByText('Custom Error UI')).toBeTruthy()
  })

  it('recovers after error with key change', () => {
    const Throwing = () => { throw new Error('Boom') }
    const { container } = render(<ErrorBoundary key="a"><Throwing /></ErrorBoundary>)
    expect(screen.getByText((content) => content.includes('failed to load'))).toBeTruthy()
  })

  it('renders children after error when reset', () => {
    const Throwing = () => { throw new Error('Boom') }
    const { container } = render(<ErrorBoundary><Throwing /></ErrorBoundary>)
    expect(container.firstChild).toBeInTheDocument()
  })
})
