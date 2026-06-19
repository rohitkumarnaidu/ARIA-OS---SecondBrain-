import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Badge } from '@/components/ui/Badge'

describe('Badge', () => {
  it('renders with text', () => {
    render(<Badge>Active</Badge>)
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('renders all 6 variants', () => {
    const variants = ['default', 'success', 'warning', 'error', 'info', 'outline'] as const
    for (const variant of variants) {
      const { unmount } = render(<Badge variant={variant}>{variant}</Badge>)
      expect(screen.getByText(variant)).toBeInTheDocument()
      unmount()
    }
  })

  it('renders with icon as child', () => {
    render(<Badge><span data-testid="badge-icon">★</span>Featured</Badge>)
    expect(screen.getByTestId('badge-icon')).toBeInTheDocument()
    expect(screen.getByText('Featured')).toBeInTheDocument()
  })

  it('has pill shape (rounded-full)', () => {
    render(<Badge>Pill</Badge>)
    expect(screen.getByText('Pill')).toHaveClass('rounded-full')
  })

  it('merges custom className', () => {
    render(<Badge className="custom-badge">Custom</Badge>)
    expect(screen.getByText('Custom')).toHaveClass('custom-badge')
  })

  it('sets data-slot attribute', () => {
    render(<Badge>Slot Badge</Badge>)
    expect(screen.getByText('Slot Badge')).toHaveAttribute('data-slot', 'badge')
  })
})
