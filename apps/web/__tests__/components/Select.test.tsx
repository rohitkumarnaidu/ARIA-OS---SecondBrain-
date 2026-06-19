import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Select } from '@/components/ui/Select'

const options = [
  { value: 'react', label: 'React' },
  { value: 'vue', label: 'Vue' },
  { value: 'angular', label: 'Angular' },
  { value: 'svelte', label: 'Svelte' },
]

describe('Select', () => {
  it('renders with placeholder', () => {
    render(<Select options={options} onChange={vi.fn()} placeholder="Pick a framework" />)
    expect(screen.getByText('Pick a framework')).toBeInTheDocument()
  })

  it('opens dropdown on click', () => {
    render(<Select options={options} onChange={vi.fn()} />)
    fireEvent.click(screen.getByRole('combobox'))
    expect(screen.getByRole('listbox')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
  })

  it('shows filtered options when typing', () => {
    render(<Select options={options} onChange={vi.fn()} />)
    fireEvent.click(screen.getByRole('combobox'))
    expect(screen.getByRole('listbox')).toBeInTheDocument()

    const searchInput = screen.getByLabelText('Search options')
    fireEvent.change(searchInput, { target: { value: 'Re' } })

    expect(screen.getByText('React')).toBeInTheDocument()
  })

  it('onChange fires with selected value', () => {
    const onChange = vi.fn()
    render(<Select options={options} onChange={onChange} />)
    fireEvent.click(screen.getByRole('combobox'))
    fireEvent.click(screen.getByText('Vue'))
    expect(onChange).toHaveBeenCalledWith('vue')
  })

  it('aria-expanded reflects open state', () => {
    render(<Select options={options} onChange={vi.fn()} />)
    const combobox = screen.getByRole('combobox')
    expect(combobox).toHaveAttribute('aria-expanded', 'false')
    fireEvent.click(combobox)
    expect(combobox).toHaveAttribute('aria-expanded', 'true')
  })

  it('keyboard navigation with arrow down and enter', () => {
    const onChange = vi.fn()
    render(<Select options={options} onChange={onChange} />)
    const combobox = screen.getByRole('combobox')

    fireEvent.keyDown(combobox, { key: 'ArrowDown' })
    expect(screen.getByRole('listbox')).toBeInTheDocument()

    fireEvent.keyDown(combobox, { key: 'ArrowDown' })
    fireEvent.keyDown(combobox, { key: 'Enter' })
    expect(onChange).toHaveBeenCalledWith('react')
  })
})
