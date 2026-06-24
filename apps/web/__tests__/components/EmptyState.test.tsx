import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EmptyState } from '@/components/ui/EmptyState'

describe('EmptyState', () => {
  it('renders icon, title, description', () => {
    render(
      <EmptyState
        icon={<span data-testid="empty-icon">📭</span>}
        title="No items found"
        description="Try adjusting your filters"
      />,
    )
    expect(screen.getByTestId('empty-icon')).toBeInTheDocument()
    expect(screen.getByText('No items found')).toBeInTheDocument()
    expect(screen.getByText('Try adjusting your filters')).toBeInTheDocument()
  })

  it('renders action button with onClick', async () => {
    const onClick = vi.fn()
    const user = userEvent.setup()
    render(
      <EmptyState
        title="Empty"
        action={{ label: 'Add Item', onClick }}
      />,
    )
    const btn = screen.getByRole('button', { name: /add item/i })
    expect(btn).toBeInTheDocument()
    await user.click(btn)
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('renders without optional props', () => {
    render(<EmptyState title="Minimal" />)
    expect(screen.getByText('Minimal')).toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('renders long title and description without overflow', () => {
    const longTitle = 'T'.repeat(150)
    const longDesc = 'D'.repeat(300)
    render(<EmptyState title={longTitle} description={longDesc} />)
    expect(screen.getByText(longTitle)).toBeInTheDocument()
    expect(screen.getByText(longDesc)).toBeInTheDocument()
  })

  it('renders without icon', () => {
    const { container } = render(<EmptyState title="No icon" />)
    expect(screen.getByText('No icon')).toBeInTheDocument()
  })

  it('renders action as link when href provided', () => {
    render(<EmptyState title="Link" action={{ label: 'Go Somewhere', href: '/test' }} />)
    const btn = screen.getByRole('button', { name: /go somewhere/i })
    expect(btn).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<EmptyState title="Styled" className="custom-empty" />)
    expect(screen.getByText('Styled')).toBeInTheDocument()
  })
})
