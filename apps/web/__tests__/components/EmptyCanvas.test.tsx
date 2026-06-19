import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EmptyCanvas } from '@/components/ui/EmptyCanvas'

describe('EmptyCanvas', () => {
  it('renders title and description', () => {
    render(<EmptyCanvas title="No items" description="Get started by adding your first item." />)
    expect(screen.getByText('No items')).toBeTruthy()
    expect(screen.getByText('Get started by adding your first item.')).toBeTruthy()
  })

  it('renders badge text', () => {
    render(<EmptyCanvas title="No items" description="..." badge="NEW" />)
    expect(screen.getByText('NEW')).toBeTruthy()
  })

  it('renders primary action button', () => {
    render(<EmptyCanvas title="No items" description="..." actions={[{ label: 'Create', primary: true }]} />)
    expect(screen.getByText('Create')).toBeTruthy()
  })

  it('calls onClick when primary action clicked', async () => {
    const user = userEvent.setup()
    let clicked = false
    render(<EmptyCanvas title="No items" description="..." actions={[{ label: 'Create', primary: true, onClick: () => { clicked = true } }]} />)
    await user.click(screen.getByText('Create'))
    expect(clicked).toBe(true)
  })

  it('renders secondary action button', () => {
    render(<EmptyCanvas title="No items" description="..." actions={[{ label: 'Cancel', primary: false }]} />)
    expect(screen.getByText('Cancel')).toBeTruthy()
  })

  it('renders multiple actions', () => {
    render(<EmptyCanvas title="No items" description="..." actions={[{ label: 'Create', primary: true }, { label: 'Import', primary: false }]} />)
    expect(screen.getByText('Create')).toBeTruthy()
    expect(screen.getByText('Import')).toBeTruthy()
  })

  it('shows CANVAS_AREA watermark', () => {
    render(<EmptyCanvas title="No items" description="..." />)
    expect(screen.getByText('CANVAS_AREA')).toBeTruthy()
  })
})
