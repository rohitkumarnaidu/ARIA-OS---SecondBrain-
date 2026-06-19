import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BentoGrid, BentoCard } from '@/components/ui/BentoGrid'

describe('BentoGrid', () => {
  it('renders children in grid', () => {
    render(
      <BentoGrid>
        <BentoCard>Item 1</BentoCard>
        <BentoCard>Item 2</BentoCard>
      </BentoGrid>,
    )
    expect(screen.getByText('Item 1')).toBeInTheDocument()
    expect(screen.getByText('Item 2')).toBeInTheDocument()
  })

  it('BentoCard renders with correct span classes', () => {
    const { container } = render(
      <BentoGrid>
        <BentoCard span={2} className="test-span">Span 2</BentoCard>
      </BentoGrid>,
    )
    const card = screen.getByText('Span 2')
    expect(card).toHaveClass('bento-span-2')
  })

  it('responsive column counts', () => {
    const { container: c2 } = render(
      <BentoGrid cols={2}>
        <BentoCard>Col 2</BentoCard>
      </BentoGrid>,
    )
    const grid2 = screen.getByText('Col 2').parentElement
    expect(grid2).toHaveClass('md:grid-cols-2')

    const { unmount } = render(
      <BentoGrid cols={4}>
        <BentoCard>Col 4</BentoCard>
      </BentoGrid>,
    )
    const grid4 = screen.getByText('Col 4').parentElement
    expect(grid4).toHaveClass('lg:grid-cols-4')
    unmount()
  })

  it('custom className', () => {
    render(
      <BentoGrid className="custom-grid">
        <BentoCard>Item</BentoCard>
      </BentoGrid>,
    )
    const grid = screen.getByText('Item').parentElement
    expect(grid).toHaveClass('custom-grid')
  })
})
