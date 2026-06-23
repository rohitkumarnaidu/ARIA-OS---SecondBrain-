import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Combobox } from '@/components/ui/Combobox'

const items = [
  { value: '1', label: 'React' },
  { value: '2', label: 'Vue' },
  { value: '3', label: 'Svelte' },
]

describe('Combobox', () => {
  it('renders trigger with placeholder', () => {
    render(<Combobox items={items} placeholder="Select framework" />)
    expect(screen.getByText('Select framework')).toBeInTheDocument()
  })

  it('renders selected value', () => {
    render(<Combobox items={items} value="1" />)
    expect(screen.getByText('React')).toBeInTheDocument()
  })

  it('opens popover on click', async () => {
    const user = userEvent.setup()
    render(<Combobox items={items} />)
    await user.click(screen.getByRole('combobox'))
    expect(screen.getByText('Vue')).toBeInTheDocument()
  })

  it('filters items on search', async () => {
    const user = userEvent.setup()
    render(<Combobox items={items} />)
    await user.click(screen.getByRole('combobox'))
    const input = screen.getByRole('textbox')
    await user.type(input, 'Svelte')
    expect(screen.getByText('Svelte')).toBeInTheDocument()
    expect(screen.queryByText('React')).not.toBeInTheDocument()
  })

  it('calls onChange when item is clicked', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Combobox items={items} onChange={onChange} />)
    await user.click(screen.getByRole('combobox'))
    const options = await screen.findAllByRole('option')
    fireEvent.click(options[1])
    expect(onChange).toHaveBeenCalledWith('2')
  })

  it('does not open when disabled', async () => {
    const user = userEvent.setup()
    render(<Combobox items={items} disabled />)
    await user.click(screen.getByRole('combobox'))
    expect(screen.queryByText('Vue')).not.toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<Combobox items={items} className="custom-class" />)
    expect(container.firstChild).toHaveClass('custom-class')
  })
})
