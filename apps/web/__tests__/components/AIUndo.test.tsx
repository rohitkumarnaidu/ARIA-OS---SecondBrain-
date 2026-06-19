import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { AIUndo } from '@/components/ai/AIUndo'

afterEach(() => {
  vi.useRealTimers()
})

describe('AIUndo', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  it('renders message text', () => {
    render(<AIUndo message="Action completed" onUndo={vi.fn()} onExpired={vi.fn()} />)
    expect(screen.getByText('Action completed')).toBeInTheDocument()
  })

  it('shows undo button', () => {
    render(<AIUndo message="Action completed" onUndo={vi.fn()} onExpired={vi.fn()} />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.getByText('Undo')).toBeInTheDocument()
  })

  it('calls onUndo when undo clicked', () => {
    const onUndo = vi.fn()
    const onExpired = vi.fn()
    render(<AIUndo message="Action completed" onUndo={onUndo} onExpired={onExpired} />)
    screen.getByText('Undo').click()
    expect(onUndo).toHaveBeenCalledTimes(1)
    expect(onExpired).not.toHaveBeenCalled()
  })

  it('calls onExpired after duration', () => {
    const onUndo = vi.fn()
    const onExpired = vi.fn()
    render(<AIUndo message="Action completed" onUndo={onUndo} onExpired={onExpired} duration={5000} />)
    act(() => { vi.advanceTimersByTime(5000) })
    expect(onExpired).toHaveBeenCalledTimes(1)
    expect(onUndo).not.toHaveBeenCalled()
  })
})
