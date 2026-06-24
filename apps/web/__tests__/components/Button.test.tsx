import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '@/components/ui/Button'
import { Loader2 } from 'lucide-react'

describe('Button', () => {
  it('renders with default props', () => {
    render(<Button>Click me</Button>)
    const btn = screen.getByRole('button', { name: /click me/i })
    expect(btn).toBeInTheDocument()
    expect(btn).not.toBeDisabled()
    expect(btn).toHaveAttribute('data-slot', 'button')
  })

  it('renders with children as label', () => {
    render(<Button>Submit</Button>)
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument()
  })

  it('renders all 7 variants', () => {
    const variants = ['default', 'primary', 'secondary', 'destructive', 'outline', 'ghost', 'link'] as const
    for (const variant of variants) {
      const { container } = render(<Button variant={variant}>{variant}</Button>)
      expect(screen.getByRole('button', { name: variant })).toBeInTheDocument()
    }
  })

  it('renders all 3 sizes', () => {
    const sizes = ['sm', 'default', 'lg'] as const
    for (const size of sizes) {
      const { container } = render(<Button size={size}>{size}</Button>)
      expect(screen.getByRole('button', { name: size })).toBeInTheDocument()
    }
  })

  it('shows loading spinner when loading is true', () => {
    render(<Button loading>Loading</Button>)
    const btn = screen.getByRole('button', { name: /loading/i })
    expect(btn).toBeDisabled()
    expect(btn).toHaveAttribute('aria-busy', 'true')
  })

  it('disabled state prevents clicks', async () => {
    const onClick = vi.fn()
    render(<Button disabled onClick={onClick}>Disabled</Button>)
    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: /disabled/i }))
    expect(onClick).not.toHaveBeenCalled()
  })

  it('renders icon on the left by default', () => {
    render(<Button icon={<span data-testid="test-icon">*</span>}>Icon Button</Button>)
    expect(screen.getByTestId('test-icon')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /icon button/i })).toBeInTheDocument()
  })

  it('applies custom className via cn()', () => {
    render(<Button className="custom-class">Styled</Button>)
    expect(screen.getByRole('button', { name: /styled/i })).toHaveClass('custom-class')
  })

  it('sets aria-disabled when disabled', () => {
    render(<Button disabled>Aria Disabled</Button>)
    expect(screen.getByRole('button', { name: /aria disabled/i })).toHaveAttribute('aria-disabled', 'true')
  })

  it('forwards additional HTML attributes', () => {
    render(<Button data-testid="test-btn" type="submit">Submit Form</Button>)
    const btn = screen.getByTestId('test-btn')
    expect(btn).toHaveAttribute('type', 'submit')
  })

  describe('Edge Cases', () => {
    it('renders with extremely long text without breaking layout', () => {
      const longText = 'A'.repeat(200)
      render(<Button>{longText}</Button>)
      const btn = screen.getByRole('button')
      expect(btn).toBeInTheDocument()
      expect(btn.textContent).toBe(longText)
    })

    it('has accessible role and aria-disabled when disabled', () => {
      render(<Button disabled>Aria Disabled</Button>)
      const btn = screen.getByRole('button', { name: /aria disabled/i })
      expect(btn).toHaveAttribute('aria-disabled', 'true')
      expect(btn).not.toHaveAttribute('aria-busy')
    })

    it('supports keyboard Enter and Space activation', async () => {
      const onClick = vi.fn()
      const user = userEvent.setup()
      render(<Button onClick={onClick}>Keyboard</Button>)
      const btn = screen.getByRole('button', { name: /keyboard/i })
      btn.focus()
      await user.keyboard('{Enter}')
      expect(onClick).toHaveBeenCalledTimes(1)
      await user.keyboard(' ')
      expect(onClick).toHaveBeenCalledTimes(2)
    })

    it('loading state disables and shows aria-busy', () => {
      render(<Button loading>Loading State</Button>)
      const btn = screen.getByRole('button', { name: /loading state/i })
      expect(btn).toBeDisabled()
      expect(btn).toHaveAttribute('aria-busy', 'true')
    })
  })
})
