import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Drawer } from '@/components/ui/Drawer'

describe('Drawer', () => {
  it('renders when open={true}', () => {
    render(<Drawer open={true} onClose={vi.fn()} title="Drawer Title">Content</Drawer>)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Drawer Title')).toBeInTheDocument()
    expect(screen.getByText('Content')).toBeInTheDocument()
  })

  it('hidden when closed', () => {
    render(<Drawer open={false} onClose={vi.fn()} title="Hidden">Content</Drawer>)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('renders drag handle', () => {
    render(<Drawer open={true} onClose={vi.fn()} title="Drag">Content</Drawer>)
    const handle = screen.getByRole('dialog').querySelector('[class*="cursor-grab"]')
    expect(handle).toBeInTheDocument()
  })

  it('renders close button', () => {
    render(<Drawer open={true} onClose={vi.fn()} title="Closeable">Content</Drawer>)
    expect(screen.getByLabelText('Close drawer')).toBeInTheDocument()
  })

  it('renders without title', () => {
    render(<Drawer open={true} onClose={vi.fn()}>Content</Drawer>)
    expect(screen.getByText('Content')).toBeInTheDocument()
  })
})
