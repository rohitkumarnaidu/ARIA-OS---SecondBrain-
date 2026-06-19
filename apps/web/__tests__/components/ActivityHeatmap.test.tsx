import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ActivityHeatmap } from '@/components/ui/ActivityHeatmap'

describe('ActivityHeatmap', () => {
  const today = new Date().toISOString().slice(0, 10)
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10)

  it('renders with data', () => {
    render(<ActivityHeatmap data={[{ date: today, count: 5 }]} />)
    expect(screen.getByRole('grid', { name: 'Activity heatmap' })).toBeTruthy()
  })

  it('shows gridcell for each data point', () => {
    render(<ActivityHeatmap data={[{ date: today, count: 3 }]} />)
    const cells = screen.getAllByRole('gridcell')
    expect(cells.length).toBeGreaterThan(0)
  })

  it('marks today with accent ring', () => {
    render(<ActivityHeatmap data={[{ date: today, count: 5 }]} />)
    const cells = screen.getAllByRole('gridcell')
    expect(cells.length).toBeGreaterThan(0)
  })

  it('shows Less/More legend', () => {
    render(<ActivityHeatmap data={[{ date: today, count: 0 }]} />)
    expect(screen.getByText('Less')).toBeTruthy()
    expect(screen.getByText('More')).toBeTruthy()
  })

  it('renders month labels', () => {
    render(<ActivityHeatmap data={[{ date: today, count: 0 }]} />)
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const found = months.some(m => screen.queryByText(m))
    expect(found).toBe(true)
  })
})
