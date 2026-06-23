import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Pagination } from '@/components/ui/Pagination'

describe('Pagination', () => {
  it('renders page numbers', () => {
    render(<Pagination currentPage={1} totalPages={5} onPageChange={() => {}} />)
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
  })

  it('disables previous on first page', () => {
    render(<Pagination currentPage={1} totalPages={5} onPageChange={() => {}} />)
    expect(screen.getByLabelText('Previous page')).toBeDisabled()
  })

  it('disables next on last page', () => {
    render(<Pagination currentPage={5} totalPages={5} onPageChange={() => {}} />)
    expect(screen.getByLabelText('Next page')).toBeDisabled()
  })

  it('calls onPageChange on page click', async () => {
    const onPageChange = vi.fn()
    const user = userEvent.setup()
    render(<Pagination currentPage={1} totalPages={5} onPageChange={onPageChange} />)
    await user.click(screen.getByText('3'))
    expect(onPageChange).toHaveBeenCalledWith(3)
  })

  it('calls onPageChange on next click', async () => {
    const onPageChange = vi.fn()
    const user = userEvent.setup()
    render(<Pagination currentPage={2} totalPages={5} onPageChange={onPageChange} />)
    await user.click(screen.getByLabelText('Next page'))
    expect(onPageChange).toHaveBeenCalledWith(3)
  })

  it('calls onPageChange on previous click', async () => {
    const onPageChange = vi.fn()
    const user = userEvent.setup()
    render(<Pagination currentPage={3} totalPages={5} onPageChange={onPageChange} />)
    await user.click(screen.getByLabelText('Previous page'))
    expect(onPageChange).toHaveBeenCalledWith(2)
  })

  it('highlights current page', () => {
    render(<Pagination currentPage={3} totalPages={5} onPageChange={() => {}} />)
    const current = screen.getByText('3')
    expect(current).toHaveAttribute('aria-current', 'page')
  })

  it('applies custom className', () => {
    const { container } = render(<Pagination currentPage={1} totalPages={5} onPageChange={() => {}} className="custom" />)
    expect(screen.getByLabelText('Previous page').closest('nav')).toHaveClass('custom')
  })
})
