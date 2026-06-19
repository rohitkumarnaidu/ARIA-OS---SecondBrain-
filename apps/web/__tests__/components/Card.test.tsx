import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter, CardDescription } from '@/components/ui/Card'

describe('Card', () => {
  it('renders children', () => {
    render(<Card><p>Card content</p></Card>)
    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('renders title from CardHeader / CardTitle', () => {
    render(
      <Card>
        <CardHeader><CardTitle>My Title</CardTitle></CardHeader>
      </Card>,
    )
    expect(screen.getByRole('heading', { name: /my title/i })).toBeInTheDocument()
  })

  it('renders description from CardDescription', () => {
    render(
      <Card>
        <CardDescription>Card description text</CardDescription>
      </Card>,
    )
    expect(screen.getByText('Card description text')).toBeInTheDocument()
  })

  it('interactive variant renders with cursor-pointer class', () => {
    const { container } = render(<Card variant="interactive"><p>Interactive</p></Card>)
    expect(screen.getByText('Interactive').parentElement).toHaveClass('cursor-pointer')
  })

  it('compact variant renders with smaller padding', () => {
    const { container } = render(<Card variant="compact"><p>Compact</p></Card>)
    const card = screen.getByText('Compact').parentElement
    expect(card).toHaveClass('p-3')
    expect(card).toHaveClass('text-sm')
  })

  it('merges custom className', () => {
    render(<Card className="my-custom-class"><p>Custom</p></Card>)
    const card = screen.getByText('Custom').parentElement
    expect(card).toHaveClass('my-custom-class')
  })

  it('renders CardFooter with data-slot attribute', () => {
    render(
      <Card>
        <CardFooter>Footer content</CardFooter>
      </Card>,
    )
    const footer = screen.getByText('Footer content').closest('[data-slot="card-footer"]')
    expect(footer).toBeInTheDocument()
  })
})
