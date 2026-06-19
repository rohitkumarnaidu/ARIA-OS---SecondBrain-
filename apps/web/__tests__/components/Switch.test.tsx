import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Switch } from '@/components/ui/Switch'

describe('Switch', () => {
  it('toggles on click', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Switch checked={false} onChange={onChange} />)
    await user.click(screen.getByRole('switch'))
    expect(onChange).toHaveBeenCalledWith(true)
  })

  it('shows checked state visually', () => {
    render(<Switch checked={true} onChange={vi.fn()} />)
    expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'true')
  })

  it('shows unchecked state visually', () => {
    render(<Switch checked={false} onChange={vi.fn()} />)
    expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'false')
  })

  it('onChange fires with new value', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Switch checked={true} onChange={onChange} />)
    await user.click(screen.getByRole('switch'))
    expect(onChange).toHaveBeenCalledWith(false)
  })

  it('disabled prop prevents interaction', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Switch checked={false} onChange={onChange} disabled />)
    await user.click(screen.getByRole('switch'))
    expect(onChange).not.toHaveBeenCalled()
    expect(screen.getByRole('switch')).toBeDisabled()
  })

  it('renders label text', () => {
    render(<Switch checked={false} onChange={vi.fn()} label="Dark Mode" />)
    expect(screen.getByText('Dark Mode')).toBeInTheDocument()
  })
})
