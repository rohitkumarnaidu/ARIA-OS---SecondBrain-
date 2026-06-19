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
})
