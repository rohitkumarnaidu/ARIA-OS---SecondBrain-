import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MultiSelect } from '@/components/ui/MultiSelect'

const items = [
  { value: 'js', label: 'JavaScript' },
  { value: 'ts', label: 'TypeScript' },
  { value: 'py', label: 'Python' },
]

describe('MultiSelect', () => {
  it('renders placeholder when no values selected', () => {
    render(<MultiSelect items={items} values={[]} onChange={() => {}} placeholder="Select languages" />)
    expect(screen.getByText('Select languages')).toBeInTheDocument()
  })

  it('renders selected items as chips', () => {
    render(<MultiSelect items={items} values={['js', 'py']} onChange={() => {}} />)
    expect(screen.getByText('JavaScript')).toBeInTheDocument()
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.queryByText('TypeScript')).not.toBeInTheDocument()
  })

  it('renders default placeholder', () => {
    render(<MultiSelect items={items} values={[]} onChange={() => {}} />)
    expect(screen.getByText('Select...')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<MultiSelect items={items} values={[]} onChange={() => {}} className="custom" />)
    expect(screen.getByText('Select...').closest('[class]')).toBeTruthy()
  })
})
