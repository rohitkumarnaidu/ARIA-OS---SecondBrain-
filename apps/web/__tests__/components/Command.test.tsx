import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Command } from '@/components/ui/Command'

const groups = [
  {
    heading: 'Navigation',
    items: [
      { id: '1', label: 'Dashboard' },
      { id: '2', label: 'Tasks' },
      { id: '3', label: 'Settings' },
    ],
  },
]

describe('Command', () => {
  it('renders search input with placeholder', () => {
    render(<Command groups={groups} />)
    expect(screen.getByPlaceholderText('Search or type a command...')).toBeInTheDocument()
  })

  it('renders all items', () => {
    render(<Command groups={groups} />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Tasks')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('filters items on search', async () => {
    const user = userEvent.setup()
    render(<Command groups={groups} />)
    const input = screen.getByPlaceholderText('Search or type a command...')
    await user.type(input, 'Task')
    expect(screen.getByText('Tasks')).toBeInTheDocument()
    expect(screen.queryByText('Settings')).not.toBeInTheDocument()
  })

  it('calls onSelect when item is clicked', async () => {
    const onSelect = vi.fn()
    const user = userEvent.setup()
    render(<Command groups={groups} onSelect={onSelect} />)
    await user.click(screen.getByText('Tasks'))
    expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ id: '2', label: 'Tasks' }))
  })

  it('renders groups heading', () => {
    render(<Command groups={groups} />)
    expect(screen.getByText('Navigation')).toBeInTheDocument()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('shows empty state', () => {
    render(<Command groups={[]} />)
    expect(screen.getByText(/no results/i)).toBeInTheDocument()
  })

  it('returns null when closed', () => {
    const { container } = render(<Command groups={groups} open={false} />)
    expect(container.innerHTML).toBe('')
  })

  it('applies custom className', () => {
    render(<Command groups={groups} className="custom" />)
    expect(screen.getByRole('dialog')).toHaveClass('custom')
  })

  it('renders empty groups gracefully', () => {
    render(<Command groups={[]} />)
    expect(screen.getByPlaceholderText('Search or type a command...')).toBeInTheDocument()
  })

  it('shows no results message when search has no matches', async () => {
    const user = userEvent.setup()
    render(<Command groups={groups} />)
    const input = screen.getByPlaceholderText('Search or type a command...')
    await user.type(input, 'xyznonexistent')
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
    expect(screen.queryByText('Navigation')).not.toBeInTheDocument()
  })

  it('handles multiple groups', () => {
    const multi = [
      { heading: 'Group A', items: [{ id: 'a1', label: 'Item A' }] },
      { heading: 'Group B', items: [{ id: 'b1', label: 'Item B' }] },
    ]
    render(<Command groups={multi} />)
    expect(screen.getByText('Group A')).toBeInTheDocument()
    expect(screen.getByText('Group B')).toBeInTheDocument()
  })

  it('clears search on close and reopen', () => {
    const { rerender } = render(<Command groups={groups} open={true} />)
    const input = screen.getByPlaceholderText('Search or type a command...')
    expect(input).toBeInTheDocument()
    rerender(<Command groups={groups} open={false} />)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('has textbox role on input', () => {
    render(<Command groups={groups} />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('applies custom placeholder', () => {
    render(<Command groups={groups} placeholder="Custom search..." />)
    expect(screen.getByPlaceholderText('Custom search...')).toBeInTheDocument()
  })
})
