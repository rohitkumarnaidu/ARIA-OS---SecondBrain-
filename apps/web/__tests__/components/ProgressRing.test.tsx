import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ProgressRing } from '@/components/ui/ProgressRing'

describe('ProgressRing', () => {
  it('renders SVG circle', () => {
    const { container } = render(<ProgressRing progress={50} />)
    expect(container.querySelector('svg')).toBeInTheDocument()
    expect(container.querySelector('circle')).toBeInTheDocument()
  })

  it('shows progress percentage visually', () => {
    render(<ProgressRing progress={75} />)
    const el = screen.getByRole('progressbar')
    expect(el).toHaveAttribute('aria-valuenow', '75')
    expect(el).toHaveAttribute('aria-valuemin', '0')
    expect(el).toHaveAttribute('aria-valuemax', '100')
  })

  it('renders center children', () => {
    render(<ProgressRing progress={50}><span>50%</span></ProgressRing>)
    expect(screen.getByText('50%')).toBeInTheDocument()
  })

  it('configurable size and strokeWidth', () => {
    const { container } = render(<ProgressRing progress={30} size={200} strokeWidth={12} />)
    const svg = container.querySelector('svg')
    expect(svg).toHaveAttribute('width', '200')
    expect(svg).toHaveAttribute('height', '200')
  })
})
