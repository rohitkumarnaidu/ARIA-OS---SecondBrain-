import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LoadingScreen } from '@/components/ui/LoadingScreen'

describe('LoadingScreen', () => {
  it('renders page variant by default', () => {
    const { container } = render(<LoadingScreen />)
    expect(screen.getByRole('status')).toBeTruthy()
    expect(container.querySelectorAll('[role="status"]')).toHaveLength(1)
  })

  it('renders card variant', () => {
    render(<LoadingScreen variant="card" />)
    expect(screen.getByRole('status', { name: 'Loading card' })).toBeTruthy()
  })

  it('renders list variant with correct count', () => {
    const { container } = render(<LoadingScreen variant="list" count={3} />)
    expect(container.querySelectorAll('[role="row"]')).toHaveLength(0)
  })

  it('renders detail variant', () => {
    render(<LoadingScreen variant="detail" />)
    expect(screen.getByRole('status', { name: 'Loading detail' })).toBeTruthy()
  })

  it('accepts custom label', () => {
    render(<LoadingScreen variant="card" label="Custom loading label" />)
    expect(screen.getByRole('status', { name: 'Custom loading label' })).toBeTruthy()
  })
})
