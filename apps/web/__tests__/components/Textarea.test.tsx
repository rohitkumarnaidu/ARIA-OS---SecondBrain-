import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Textarea } from '@/components/ui/Textarea'

describe('Textarea', () => {
  it('renders with placeholder', () => {
    render(<Textarea placeholder="Enter description" />)
    expect(screen.getByPlaceholderText('Enter description')).toBeInTheDocument()
  })

  it('renders with label', () => {
    render(<Textarea label="Description" />)
    expect(screen.getByText('Description')).toBeInTheDocument()
  })

  it('calls onChange when typing', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Textarea onChange={onChange} />)
    await user.type(screen.getByRole('textbox'), 'hello')
    expect(onChange).toHaveBeenCalled()
  })

  it('shows error message', () => {
    render(<Textarea error="Field is required" />)
    expect(screen.getByText('Field is required')).toBeInTheDocument()
  })

  it('shows character count when label is present', () => {
    render(<Textarea maxLength={500} value="Hello" onChange={() => {}} label="Bio" />)
    expect(screen.getByText('5/500')).toBeInTheDocument()
  })

  it('disables textarea', () => {
    render(<Textarea disabled />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  it('applies custom className', () => {
    render(<Textarea className="custom-class" />)
    expect(screen.getByRole('textbox')).toHaveClass('custom-class')
  })
})
