import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Input } from '@/components/ui/Input'

describe('Input', () => {
  it('renders with label and input', () => {
    render(<Input label="Name" />)
    expect(screen.getByLabelText('Name')).toBeTruthy()
  })

  it('shows required asterisk when required', () => {
    render(<Input label="Email" required />)
    expect(screen.getByText('*')).toBeTruthy()
  })

  it('displays error message with role="alert"', () => {
    render(<Input label="Name" error="This field is required" />)
    expect(screen.getByRole('alert')).toHaveTextContent('This field is required')
  })

  it('sets aria-invalid when error is present', () => {
    render(<Input label="Name" error="Error" />)
    expect(screen.getByLabelText('Name')).toHaveAttribute('aria-invalid', 'true')
  })

  it('displays helper text when no error', () => {
    render(<Input label="Name" helperText="Enter your full name" />)
    expect(screen.getByText('Enter your full name')).toBeTruthy()
  })

  it('does not show helper text when error is present', () => {
    render(<Input label="Name" error="Error" helperText="Hidden helper" />)
    expect(screen.queryByText('Hidden helper')).toBeNull()
  })

  it('forwards ref to input element', () => {
    const ref = { current: null }
    render(<Input ref={ref} />)
    expect(ref.current).toBeInstanceOf(HTMLInputElement)
  })

  it('applies aria-describedby for error', () => {
    render(<Input label="Name" error="Error" />)
    const input = screen.getByLabelText('Name')
    const errorId = input.getAttribute('aria-describedby')
    expect(errorId).toBeTruthy()
    expect(document.getElementById(errorId!)).toHaveTextContent('Error')
  })
})
