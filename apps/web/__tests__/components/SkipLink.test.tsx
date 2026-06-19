import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SkipLink } from '@/components/layout/SkipLink'

describe('SkipLink', () => {
  it('renders skip link', () => {
    render(<SkipLink />)
    const link = screen.getByText('Skip to main content')
    expect(link).toBeTruthy()
    expect(link.tagName).toBe('A')
  })

  it('links to main content by default', () => {
    render(<SkipLink />)
    expect(screen.getByText('Skip to main content')).toHaveAttribute('href', '#main-content')
  })
})
