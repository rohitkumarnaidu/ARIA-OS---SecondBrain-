import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Avatar } from '@/components/ui/Avatar'

describe('Avatar', () => {
  it('renders initials for a name', () => {
    render(<Avatar name="John Doe" />)
    expect(screen.getByText('JD')).toBeInTheDocument()
  })

  it('renders single initial for single name', () => {
    render(<Avatar name="Admin" />)
    expect(screen.getByText('A')).toBeInTheDocument()
  })

  it('renders image when src is provided', () => {
    render(<Avatar name="John Doe" src="https://example.com/avatar.jpg" />)
    const img = document.querySelector('img')
    expect(img).toHaveAttribute('src', 'https://example.com/avatar.jpg')
  })

  it('falls back to initials on image error', () => {
    render(<Avatar name="Jane Doe" src="broken.jpg" />)
    const img = document.querySelector('img')!
    fireEvent.error(img)
    expect(screen.getByText('JD')).toBeInTheDocument()
  })

  it('renders all sizes', () => {
    const sizes = ['sm', 'md', 'lg', 'xl'] as const
    for (const size of sizes) {
      const { unmount } = render(<Avatar name="User" size={size} />)
      expect(screen.getByText('U')).toBeInTheDocument()
      unmount()
    }
  })

  it('renders status indicator', () => {
    render(<Avatar name="User" status="online" />)
    expect(screen.getByLabelText('online')).toBeInTheDocument()
  })

  it('renders with aria-label from alt prop', () => {
    render(<Avatar name="John Doe" alt="John's avatar" />)
    expect(screen.getByLabelText("John's avatar")).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<Avatar name="User" className="custom-class" />)
    expect(screen.getByLabelText('User')).toHaveClass('custom-class')
  })

  it('has data-slot attribute', () => {
    render(<Avatar name="User" />)
    expect(screen.getByLabelText('User')).toHaveAttribute('data-slot', 'avatar')
  })
})
