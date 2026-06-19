import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ModuleError } from '@/components/shared/ModuleError'

describe('ModuleError', () => {
  it('renders error message', () => {
    render(<ModuleError error={new Error('Something broke')} reset={() => {}} />)
    expect(screen.getByText(/Failed to load/)).toBeTruthy()
  })

  it('shows retry button and calls reset on click', async () => {
    const user = userEvent.setup()
    const reset = vi.fn()
    render(<ModuleError error={new Error('Boom')} reset={reset} />)
    await user.click(screen.getByText('Try again'))
    expect(reset).toHaveBeenCalledOnce()
  })

  it('renders with custom page name', () => {
    render(<ModuleError error={new Error('Boom')} reset={() => {}} name="dashboard" />)
    expect(screen.getByText((content) => content.includes('dashboard'))).toBeTruthy()
  })
})
