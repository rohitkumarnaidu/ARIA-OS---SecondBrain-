import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest'
import { render, screen, cleanup, act, fireEvent } from '@testing-library/react'
import { Tooltip } from '@/components/ui/Tooltip'

afterEach(() => {
  cleanup()
  vi.useRealTimers()
})

describe('Tooltip', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
  })

  it('shows on hover after delay', () => {
    render(
      <Tooltip content="Tooltip content" delay={300}>
        <button>Hover me</button>
      </Tooltip>,
    )
    fireEvent.mouseEnter(screen.getByText('Hover me'))
    act(() => { vi.advanceTimersByTime(300) })
    expect(screen.getByRole('tooltip')).toBeInTheDocument()
    expect(screen.getByText('Tooltip content')).toBeInTheDocument()
  })

  it('hides on mouse leave after hide delay', () => {
    render(
      <Tooltip content="Tooltip content" delay={100} hideDelay={200}>
        <button>Hover me</button>
      </Tooltip>,
    )
    const trigger = screen.getByText('Hover me')
    fireEvent.mouseEnter(trigger)
    act(() => { vi.advanceTimersByTime(100) })
    expect(screen.getByRole('tooltip')).toBeInTheDocument()

    fireEvent.mouseLeave(trigger)
    act(() => { vi.advanceTimersByTime(200) })
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()
  })

  it('shows on focus and hides on blur', () => {
    render(
      <Tooltip content="Focus tooltip">
        <button>Focus me</button>
      </Tooltip>,
    )
    const trigger = screen.getByText('Focus me')
    fireEvent.focus(trigger)
    act(() => { vi.advanceTimersByTime(0) })
    expect(screen.getByRole('tooltip')).toBeInTheDocument()

    fireEvent.blur(trigger)
    act(() => { vi.advanceTimersByTime(100) })
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()
  })

  it('renders with side prop', () => {
    vi.useRealTimers()
    render(
      <Tooltip content="Side tooltip" side="bottom">
        <button>Hover me</button>
      </Tooltip>,
    )
    expect(screen.getByText('Hover me')).toBeInTheDocument()
  })
})
