import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Timeline } from '@/components/ui/Timeline'

const items = [
  { id: '1', title: 'Step 1', description: 'First step', date: 'Jan 1', status: 'completed' as const },
  { id: '2', title: 'Step 2', description: 'Second step', date: 'Jan 5', status: 'current' as const },
  { id: '3', title: 'Step 3', description: 'Third step', date: 'Jan 10', status: 'upcoming' as const },
  { id: '4', title: 'Step 4', description: 'Skipped step', date: 'Jan 15', status: 'skipped' as const },
]

describe('Timeline', () => {
  it('renders all items', () => {
    render(<Timeline items={items} />)
    expect(screen.getByText('Step 1')).toBeInTheDocument()
    expect(screen.getByText('Step 2')).toBeInTheDocument()
    expect(screen.getByText('Step 3')).toBeInTheDocument()
    expect(screen.getByText('Step 4')).toBeInTheDocument()
  })

  it('renders date labels', () => {
    render(<Timeline items={items} />)
    expect(screen.getByText('Jan 1')).toBeInTheDocument()
    expect(screen.getByText('Jan 5')).toBeInTheDocument()
    expect(screen.getByText('Jan 10')).toBeInTheDocument()
  })

  it('renders descriptions', () => {
    render(<Timeline items={items} />)
    expect(screen.getByText('First step')).toBeInTheDocument()
    expect(screen.getByText('Second step')).toBeInTheDocument()
  })

  it('returns null for empty items', () => {
    const { container } = render(<Timeline items={[]} />)
    expect(container.innerHTML).toBe('')
  })
})
