import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LiveRegion } from '@/components/shared/LiveRegion'

describe('LiveRegion', () => {
  it('renders with polite politeness by default', () => {
    render(<LiveRegion message="New notification" />)
    const region = screen.getByRole('status')
    expect(region).toHaveAttribute('aria-live', 'polite')
    expect(region).toHaveTextContent('New notification')
  })

  it('renders with assertive politeness', () => {
    render(<LiveRegion message="Critical alert" politeness="assertive" />)
    const region = screen.getByRole('status')
    expect(region).toHaveAttribute('aria-live', 'assertive')
    expect(region).toHaveTextContent('Critical alert')
  })
})
