import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@/__tests__/test-utils'
import { DropdownMenu } from '@/components/ui/DropdownMenu'

describe('DropdownMenu', () => {
  const freshItems = () => [
    { label: 'Edit', onClick: vi.fn() },
    { label: 'Duplicate', onClick: vi.fn() },
    { label: 'divider', divider: true, onClick: vi.fn() },
    { label: 'Delete', onClick: vi.fn(), disabled: true },
  ]

  it('opens on trigger click', () => {
    render(<DropdownMenu trigger={<button>Menu</button>} items={freshItems()} />)
    fireEvent.click(screen.getByText('Menu'))
    expect(screen.getByRole('menu')).toBeInTheDocument()
  })

  it('renders menu items when open', () => {
    render(<DropdownMenu trigger={<button>Menu</button>} items={freshItems()} />)
    fireEvent.click(screen.getByText('Menu'))
    expect(screen.getByText('Edit')).toBeInTheDocument()
    expect(screen.getByText('Duplicate')).toBeInTheDocument()
    expect(screen.getByText('Delete')).toBeInTheDocument()
  })

  it('click item fires onClick handler', () => {
    const onClick = vi.fn()
    render(<DropdownMenu trigger={<button>Menu</button>} items={[{ label: 'Save', onClick }]} />)
    fireEvent.click(screen.getByText('Menu'))
    fireEvent.click(screen.getByText('Save'))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('disabled item does not fire onClick', () => {
    const onClick = vi.fn()
    render(<DropdownMenu trigger={<button>Menu</button>} items={[{ label: 'Delete', onClick, disabled: true }]} />)
    fireEvent.click(screen.getByText('Menu'))
    fireEvent.click(screen.getByText('Delete'))
    expect(onClick).not.toHaveBeenCalled()
  })

  it('renders divider', () => {
    render(<DropdownMenu trigger={<button>Menu</button>} items={[{ label: 'A', divider: true }]} />)
    fireEvent.click(screen.getByText('Menu'))
    expect(screen.getByRole('menu')).toBeInTheDocument()
  })
})
