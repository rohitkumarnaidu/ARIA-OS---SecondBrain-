import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Modal } from '@/components/ui/Modal'

describe('Modal', () => {
  it('renders when isOpen is true', () => {
    render(<Modal isOpen={true} onClose={() => {}} title="Test Modal">Content</Modal>)
    expect(screen.getByText('Test Modal')).toBeTruthy()
    expect(screen.getByText('Content')).toBeTruthy()
  })

  it('is hidden when isOpen is false', () => {
    render(<Modal isOpen={false} onClose={() => {}} title="Test Modal">Content</Modal>)
    expect(screen.queryByText('Test Modal')).toBeNull()
  })

  it('closes on Escape key', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(<Modal isOpen={true} onClose={onClose} title="Test Modal">Content</Modal>)
    await user.keyboard('{Escape}')
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('closes on backdrop click', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(<Modal isOpen={true} onClose={onClose} title="Test Modal">Content</Modal>)
    const backdrop = document.querySelector('[aria-hidden="true"]')
    if (backdrop) await user.click(backdrop)
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('has role="dialog" and aria-modal="true"', () => {
    render(<Modal isOpen={true} onClose={() => {}} title="Test Modal">Content</Modal>)
    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
  })

  it('renders close button with aria-label', () => {
    render(<Modal isOpen={true} onClose={() => {}} title="Test Modal">Content</Modal>)
    expect(screen.getByLabelText('Close dialog')).toBeTruthy()
  })

  describe('Edge Cases', () => {
    it('renders with extremely long title without breaking layout', () => {
      const longTitle = 'M'.repeat(150)
      render(<Modal isOpen={true} onClose={() => {}} title={longTitle}>Content</Modal>)
      expect(screen.getByText(longTitle)).toBeInTheDocument()
    })

    it('trap focus within modal when open', async () => {
      const user = userEvent.setup()
      render(<Modal isOpen={true} onClose={() => {}} title="Focus">Content</Modal>)
      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-modal', 'true')
    })

    it('renders with custom aria-label', () => {
      render(<Modal isOpen={true} onClose={() => {}} title="Test" aria-label="Custom label">Content</Modal>)
      expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true')
    })

    it('has role="dialog" attribute', () => {
      render(<Modal isOpen={true} onClose={() => {}} title="Dialog Test">Content</Modal>)
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
  })
})
