import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ChartContainer } from '@/components/ui/ChartContainer'

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactElement }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
}))

describe('ChartContainer', () => {
  it('renders children', () => {
    render(<ChartContainer><div data-testid="chart-child">Chart</div></ChartContainer>)
    expect(screen.getByTestId('chart-child')).toBeInTheDocument()
  })

  it('renders title and description', () => {
    render(
      <ChartContainer title="Revenue" description="Monthly revenue trend">
        <div>Chart</div>
      </ChartContainer>,
    )
    expect(screen.getByText('Revenue')).toBeInTheDocument()
    expect(screen.getByText('Monthly revenue trend')).toBeInTheDocument()
  })

  it('configurable height', () => {
    const { container } = render(<ChartContainer height={400}><div>Chart</div></ChartContainer>)
    const wrapper = container.querySelector('[style*="height"]')
    expect(wrapper).toBeInTheDocument()
    expect(wrapper?.outerHTML).toContain('height: 400px')
  })
})
