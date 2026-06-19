import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { Spinner } from '@/components/ui/Spinner'

describe('Spinner', () => {
  it('renders with default size', () => {
    const { container } = render(<Spinner />)
    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
    expect(svg).toHaveAttribute('aria-hidden', 'true')
  })

  it('renders with custom size', () => {
    const { container } = render(<Spinner size={32} />)
    const svg = container.querySelector('svg')
    expect(svg).toHaveAttribute('width', '32')
    expect(svg).toHaveAttribute('height', '32')
  })

  it('applies custom className', () => {
    const { container } = render(<Spinner className="custom-spinner" />)
    const svg = container.querySelector('svg')
    expect(svg).toHaveClass('custom-spinner')
  })
})
