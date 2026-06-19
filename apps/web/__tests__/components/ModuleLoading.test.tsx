import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ModuleLoading } from '@/components/shared/ModuleLoading'

describe('ModuleLoading', () => {
  it('renders with default label', () => {
    render(<ModuleLoading />)
    expect(screen.getByRole('status')).toBeTruthy()
  })

  it('renders with custom name', () => {
    render(<ModuleLoading name="Dashboard" />)
    expect(screen.getByText((content) => content.includes('Dashboard'))).toBeTruthy()
  })
})
