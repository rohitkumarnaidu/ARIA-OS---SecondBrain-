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
})
