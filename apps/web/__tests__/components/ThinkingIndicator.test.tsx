import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ThinkingIndicator } from '@/components/ai/ThinkingIndicator'

describe('ThinkingIndicator', () => {
  it('returns null in idle state', () => {
    const { container } = render(<ThinkingIndicator state="idle" />)
    expect(container.innerHTML).toBe('')
  })

  it('renders in thinking state with dots', () => {
    render(<ThinkingIndicator state="thinking" messages={['Processing...', 'Almost done...']} />)
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByText('Processing...')).toBeInTheDocument()
  })

  it('renders in complete state', () => {
    render(<ThinkingIndicator state="complete" />)
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByLabelText('Complete')).toBeInTheDocument()
  })

  it('renders in error state', () => {
    render(<ThinkingIndicator state="error" />)
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByLabelText('Error')).toBeInTheDocument()
  })

  it('renders in cancelled state', () => {
    render(<ThinkingIndicator state="cancelled" />)
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByLabelText('Cancelled')).toBeInTheDocument()
  })
})
