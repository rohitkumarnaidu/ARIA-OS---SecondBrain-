import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Sheet } from '@/components/ui/Sheet'

describe('Sheet', () => {
  it('slides in from right when open', () => {
    render(<Sheet open={true} onClose={vi.fn()} title="Sheet Title">Content</Sheet>)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Sheet Title')).toBeInTheDocument()
    expect(screen.getByText('Content')).toBeInTheDocument()
  })

  it('hidden when closed', () => {
    render(<Sheet open={false} onClose={vi.fn()} title="Hidden">Content</Sheet>)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('backdrop click calls onClose', async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()
    render(<Sheet open={true} onClose={onClose} title="Backdrop">Content</Sheet>)
    // The backdrop is the first motion div inside the outer wrapper (before the dialog content)
    const dialog = screen.getByRole('dialog')
    const parent = dialog.parentElement
    const backdrop = parent?.children[0]
    if (backdrop) {
      await user.click(backdrop)
    }
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('renders without title', () => {
    render(<Sheet open={true} onClose={vi.fn()}>No Title</Sheet>)
    expect(screen.getByText('No Title')).toBeInTheDocument()
  })

  it('renders with title and close button', () => {
    render(<Sheet open={true} onClose={vi.fn()} title="Config">Content</Sheet>)
    expect(screen.getByText('Config')).toBeInTheDocument()
    expect(screen.getByLabelText('Close sheet')).toBeInTheDocument()
  })
})
