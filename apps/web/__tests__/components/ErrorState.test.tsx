import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ErrorState } from '@/components/ui/ErrorState'

describe('ErrorState', () => {
  it('renders default 500 error', () => {
    render(<ErrorState />)
    expect(screen.getByText('Server Error')).toBeTruthy()
  })

  it('renders 404 with resource name', () => {
    render(<ErrorState status={404} resource="task" />)
    expect(screen.getByText('Not Found')).toBeTruthy()
  })

  it('renders 429 rate limit display', () => {
    render(<ErrorState status={429} />)
    expect(screen.getByText('Rate Limited')).toBeTruthy()
  })

  it('renders 400 bad request', () => {
    render(<ErrorState status={400} />)
    expect(screen.getByText('Invalid Request')).toBeTruthy()
  })

  it('shows Try Again button for 500 with onRetry', () => {
    render(<ErrorState status={500} onRetry={() => {}} />)
    expect(screen.getByText('Try Again')).toBeTruthy()
  })

  it('calls onRetry when Try Again clicked', async () => {
    const user = userEvent.setup()
    const onRetry = vi.fn()
    render(<ErrorState status={500} onRetry={onRetry} />)
    await user.click(screen.getByText('Try Again'))
    expect(onRetry).toHaveBeenCalledOnce()
  })

  it('shows Go Back button for 404 with onGoBack', () => {
    render(<ErrorState status={404} onGoBack={() => {}} />)
    expect(screen.getByText('Go Back')).toBeTruthy()
  })

  it('shows Contact Support for 500', () => {
    render(<ErrorState status={500} />)
    expect(screen.getByText('Contact Support')).toBeTruthy()
  })

  it('shows ERROR_ status watermark in non-compact mode', () => {
    render(<ErrorState status={404} />)
    expect(screen.getByText('ERROR_404')).toBeTruthy()
  })

  it('hides watermark in compact mode', () => {
    render(<ErrorState status={404} compact />)
    expect(screen.queryByText('ERROR_404')).toBeNull()
  })

  it('accepts custom title and description', () => {
    render(<ErrorState title="Custom Error" description="Custom description" />)
    expect(screen.getByText('Custom Error')).toBeTruthy()
    expect(screen.getByText('Custom description')).toBeTruthy()
  })

  it('has role="alert"', () => {
    render(<ErrorState />)
    expect(screen.getByRole('alert')).toBeTruthy()
  })

  it('handles unknown status code', () => {
    render(<ErrorState status={999} />)
    expect(screen.getByRole('alert')).toBeTruthy()
  })

  it('renders long custom title and description', () => {
    const longTitle = 'E'.repeat(100)
    const longDesc = 'D'.repeat(200)
    render(<ErrorState title={longTitle} description={longDesc} />)
    expect(screen.getByText(longTitle)).toBeTruthy()
    expect(screen.getByText(longDesc)).toBeTruthy()
  })

  it('applies custom className', () => {
    const { container } = render(<ErrorState className="custom-error" />)
    expect(container.firstChild).toHaveClass('custom-error')
  })
})
