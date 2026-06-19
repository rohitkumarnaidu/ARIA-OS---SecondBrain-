import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { Skeleton } from '@/components/ui/Skeleton'

describe('Skeleton', () => {
  it('renders text variant', () => {
    const { container } = render(<Skeleton variant="text" />)
    const el = container.firstChild as HTMLElement
    expect(el).toHaveClass('h-4')
    expect(el).toHaveClass('rounded')
    expect(el).toHaveAttribute('aria-hidden', 'true')
  })

  it('renders circle variant', () => {
    const { container } = render(<Skeleton variant="circle" />)
    const el = container.firstChild as HTMLElement
    expect(el).toHaveClass('w-10')
    expect(el).toHaveClass('h-10')
    expect(el).toHaveClass('rounded-full')
  })

  it('renders card variant', () => {
    const { container } = render(<Skeleton variant="card" />)
    const el = container.firstChild as HTMLElement
    expect(el).toHaveClass('h-32')
    expect(el).toHaveClass('rounded-xl')
  })

  it('configurable width/height via className', () => {
    const { container } = render(<Skeleton variant="text" className="w-64 h-8" />)
    const el = container.firstChild as HTMLElement
    expect(el).toHaveClass('w-64')
    expect(el).toHaveClass('h-8')
  })
})
