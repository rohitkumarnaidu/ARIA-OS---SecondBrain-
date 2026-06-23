import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DatePicker } from '@/components/ui/DatePicker'

describe('DatePicker', () => {
  it('renders with placeholder', () => {
    render(<DatePicker value={undefined} onChange={() => {}} />)
    expect(screen.getByText('Pick a date')).toBeInTheDocument()
  })

  it('renders selected date formatted', () => {
    render(<DatePicker value={new Date(2026, 5, 15)} onChange={() => {}} />)
    expect(screen.getByText('Jun 15, 2026')).toBeInTheDocument()
  })

  it('disables input', () => {
    render(<DatePicker value={undefined} onChange={() => {}} disabled />)
    const btn = screen.getByRole('button')
    expect(btn).toBeDisabled()
  })

  it('applies custom className', () => {
    render(<DatePicker value={undefined} onChange={() => {}} className="custom" />)
    expect(screen.getByText('Pick a date').closest('[class]')).toBeTruthy()
  })

  it('renders custom placeholder', () => {
    render(<DatePicker value={undefined} onChange={() => {}} placeholder="Select date" />)
    expect(screen.getByText('Select date')).toBeInTheDocument()
  })
})
