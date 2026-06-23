import { describe, it, expect, vi } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Toggle } from '@/components/ui/Toggle'

describe('Toggle', () => {
  it('renders unchecked by default', () => {
    render(<Toggle checked={false} onChange={() => {}} />)
    const btn = screen.getByRole('switch')
    expect(btn).toHaveAttribute('aria-checked', 'false')
  })

  it('renders checked state', () => {
    render(<Toggle checked={true} onChange={() => {}} />)
    expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'true')
  })

  it('calls onChange when clicked', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Toggle checked={false} onChange={onChange} />)
    await user.click(screen.getByRole('switch'))
    expect(onChange).toHaveBeenCalledWith(true)
  })

  it('does not call onChange when disabled', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Toggle checked={false} onChange={onChange} disabled />)
    await user.click(screen.getByRole('switch'))
    expect(onChange).not.toHaveBeenCalled()
  })

  it('renders label when provided', () => {
    render(<Toggle checked={false} onChange={() => {}} label="Dark Mode" />)
    expect(screen.getByText('Dark Mode')).toBeInTheDocument()
  })

  it('renders all sizes', () => {
    const sizes = ['sm', 'md'] as const
    for (const size of sizes) {
      cleanup()
      render(<Toggle checked={false} onChange={() => {}} size={size} />)
      expect(screen.getByRole('switch')).toBeInTheDocument()
    }
    cleanup()
  })

  it('applies custom className', () => {
    render(<Toggle checked={false} onChange={() => {}} className="custom-class" />)
    expect(screen.getByRole('switch').closest('label')).toHaveClass('custom-class')
  })

  it('handles keyboard Enter', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Toggle checked={false} onChange={onChange} />)
    const btn = screen.getByRole('switch')
    btn.focus()
    await user.keyboard('{Enter}')
    expect(onChange).toHaveBeenCalledWith(true)
  })

  it('handles keyboard Space', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Toggle checked={false} onChange={onChange} />)
    const btn = screen.getByRole('switch')
    btn.focus()
    await user.keyboard(' ')
    expect(onChange).toHaveBeenCalledWith(true)
  })
})
