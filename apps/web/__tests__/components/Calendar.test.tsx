import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Calendar } from '@/components/ui/Calendar'

describe('Calendar', () => {
  it('renders month/year header', () => {
    const date = new Date(2026, 5, 15)
    render(<Calendar value={date} onChange={() => {}} />)
    expect(screen.getByText(/2026/)).toBeInTheDocument()
  })

  it('renders day grid with selected day', () => {
    const date = new Date(2026, 5, 15)
    render(<Calendar value={date} onChange={() => {}} />)
    expect(screen.getByText('15')).toBeInTheDocument()
  })

  it('calls onChange when a day is clicked', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Calendar value={new Date(2026, 5, 15)} onChange={onChange} />)
    await user.click(screen.getByText('15'))
    expect(onChange).toHaveBeenCalled()
  })

  it('navigates months', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Calendar value={new Date(2026, 5, 15)} onChange={onChange} />)
    const nextBtn = screen.getByLabelText('Next month')
    await user.click(nextBtn)
    expect(onChange).toHaveBeenCalledWith(expect.any(Date))
  })

  it('renders with min/max dates', () => {
    render(
      <Calendar
        value={new Date(2026, 5, 15)}
        onChange={() => {}}
        minDate={new Date(2026, 5, 1)}
        maxDate={new Date(2026, 5, 30)}
      />
    )
    expect(screen.getByText('15')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<Calendar value={new Date()} onChange={() => {}} className="custom" />)
    expect(container.firstChild).toHaveClass('custom')
  })
})
