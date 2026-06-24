import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { GhostHint } from '@/components/ai/GhostHint'

describe('GhostHint', () => {
  it('renders hint text', () => {
    render(<GhostHint text="Try asking about your tasks" state="visible" />)
    expect(screen.getByText('Try asking about your tasks')).toBeTruthy()
  })

  it('shows keyboard hint in visible state', () => {
    render(<GhostHint text="Hint" state="visible" />)
    expect(screen.getByText((content) => content.includes('Tab'))).toBeTruthy()
  })

  it('shows accepted state text', () => {
    render(<GhostHint text="Hint" state="filled" />)
    expect(screen.getByText('Accepted')).toBeTruthy()
  })

  it('does not render when state is hidden', () => {
    const { container } = render(<GhostHint text="Hint" state="hidden" />)
    expect(container.firstElementChild).toBeNull()
  })

  it('applies line-through decoration in filled state', () => {
    render(<GhostHint text="Completed" state="filled" />)
    const span = screen.getByText('Completed')
    expect(span.className).toContain('line-through')
  })

  it('renders empty text string', () => {
    const { container } = render(<GhostHint text="" state="visible" />)
    const spans = container.querySelectorAll('span.italic')
    expect(spans.length).toBeGreaterThan(0)
  })

  it('renders very long hint text', () => {
    const long = 'A'.repeat(200)
    render(<GhostHint text={long} state="visible" />)
    expect(screen.getByText(long)).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<GhostHint text="Hint" state="visible" className="custom-ghost" />)
    expect(container.firstChild).toHaveClass('custom-ghost')
  })

  it('has aria-live region when visible', () => {
    render(<GhostHint text="Hint" state="visible" />)
    const region = screen.getByText('Hint').closest('[aria-live]')
    expect(region).toBeInTheDocument()
  })
})
