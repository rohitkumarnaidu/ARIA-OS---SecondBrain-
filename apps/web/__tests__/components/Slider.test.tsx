import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Slider } from '@/components/ui/Slider'

describe('Slider', () => {
  it('renders with default value', () => {
    render(<Slider value={50} onChange={() => {}} />)
    const slider = screen.getByRole('slider')
    expect(slider).toBeInTheDocument()
  })

  it('renders with min/max labels', () => {
    render(<Slider value={50} onChange={() => {}} min={0} max={100} />)
    expect(screen.getByText('0')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
  })

  it('disables slider', () => {
    render(<Slider value={50} onChange={() => {}} disabled />)
    expect(screen.getByRole('slider')).toBeDisabled()
  })

  it('applies custom className', () => {
    render(<Slider value={50} onChange={() => {}} className="custom-class" />)
    expect(screen.getByRole('slider').closest('div')).toHaveClass('custom-class')
  })

  it('displays current value in tooltip on hover', async () => {
    const user = userEvent.setup()
    render(<Slider value={75} onChange={() => {}} />)
    const slider = screen.getByRole('slider')
    await user.hover(slider.closest('div')!)
    expect(screen.getByText('75')).toBeInTheDocument()
  })
})
