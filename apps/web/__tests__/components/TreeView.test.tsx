import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TreeView } from '@/components/ui/TreeView'

const items = [
  {
    id: '1', label: 'Documents',
    children: [
      { id: '1-1', label: 'Work' },
      { id: '1-2', label: 'Personal' },
    ],
  },
  { id: '2', label: 'Images' },
]

describe('TreeView', () => {
  it('renders top-level items', () => {
    render(<TreeView items={items} />)
    expect(screen.getByText('Documents')).toBeInTheDocument()
    expect(screen.getByText('Images')).toBeInTheDocument()
  })

  it('expands children on click', async () => {
    const user = userEvent.setup()
    render(<TreeView items={items} />)
    await user.click(screen.getByText('Documents'))
    expect(screen.getByText('Work')).toBeInTheDocument()
  })

  it('calls onSelect when leaf clicked', async () => {
    const onSelect = vi.fn()
    const user = userEvent.setup()
    render(<TreeView items={items} onSelect={onSelect} />)
    await user.click(screen.getByText('Documents'))
    await user.click(screen.getByText('Work'))
    expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ id: '1-1', label: 'Work' }))
  })

  it('applies custom className', () => {
    const { container } = render(<TreeView items={items} className="custom" />)
    expect(container.firstChild).toHaveClass('custom')
  })

  it('renders empty items gracefully', () => {
    const { container } = render(<TreeView items={[]} />)
    expect(container.firstChild).toBeInTheDocument()
  })

  it('renders single item without children', () => {
    render(<TreeView items={[{ id: '1', label: 'Solo' }]} />)
    expect(screen.getByText('Solo')).toBeInTheDocument()
  })

  it('expands collapsed nodes on click', async () => {
    const user = userEvent.setup()
    render(<TreeView items={items} />)
    expect(screen.queryByText('Work')).not.toBeInTheDocument()
    await user.click(screen.getByText('Documents'))
    expect(screen.getByText('Work')).toBeInTheDocument()
  })

  it('does not call onSelect when expanding parent', async () => {
    const onSelect = vi.fn()
    const user = userEvent.setup()
    render(<TreeView items={items} onSelect={onSelect} />)
    await user.click(screen.getByText('Documents'))
    expect(screen.getByText('Work')).toBeInTheDocument()
  })

  it('has tree role', () => {
    render(<TreeView items={items} />)
    expect(screen.getByRole('tree')).toBeInTheDocument()
  })

  it('renders deeply nested children', () => {
    const deep = [
      { id: '1', label: 'Root', children: [{ id: '2', label: 'Level 1', children: [{ id: '3', label: 'Level 2' }] }] },
    ]
    render(<TreeView items={deep} />)
    expect(screen.getByText('Root')).toBeInTheDocument()
  })
})
