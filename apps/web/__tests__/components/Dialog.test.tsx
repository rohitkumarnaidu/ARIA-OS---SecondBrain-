import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Dialog } from '@/components/ui/Dialog'

describe('Dialog', () => {
  it('renders when open={true}', () => {
    render(<Dialog open={true} onClose={vi.fn()} title="Test Dialog">Content</Dialog>)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Test Dialog')).toBeInTheDocument()
    expect(screen.getByText('Content')).toBeInTheDocument()
  })

  it('is hidden when open={false}', () => {
    render(<Dialog open={false} onClose={vi.fn()} title="Hidden">Content</Dialog>)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('closes on Escape key', async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()
    render(<Dialog open={true} onClose={onClose} title="Close Test">Content</Dialog>)
    await user.keyboard('{Escape}')
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('closes on backdrop click', async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()
    render(<Dialog open={true} onClose={onClose} title="Backdrop">Content</Dialog>)
    const backdrop = screen.getByRole('dialog').children[0]
    await user.click(backdrop)
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('renders all 5 sizes', () => {
    const sizes = ['sm', 'md', 'lg', 'xl', 'full'] as const
    for (const size of sizes) {
      const { unmount } = render(<Dialog open={true} onClose={vi.fn()} title={size} size={size}>Content</Dialog>)
      const dialog = screen.getByRole('dialog')
      expect(dialog).toBeInTheDocument()
      unmount()
    }
  })

  it('applies custom className via cn()', () => {
    render(<Dialog open={true} onClose={vi.fn()} title="Styled" className="custom-dialog">Content</Dialog>)
    const panel = screen.getByText('Styled').closest('.custom-dialog')
    expect(panel).toBeInTheDocument()
  })
})
