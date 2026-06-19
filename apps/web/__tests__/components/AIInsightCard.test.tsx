import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AIInsightCard } from '@/components/ai/AIInsightCard'

describe('AIInsightCard', () => {
  it('renders title and description', () => {
    render(<AIInsightCard type="insight" title="AI Insight" description="Your productivity is up 20%" />)
    expect(screen.getByText('AI Insight')).toBeTruthy()
    expect(screen.getByText('Your productivity is up 20%')).toBeTruthy()
  })

  it('renders action button and calls onClick', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<AIInsightCard type="insight" title="Insight" description="Desc" action={{ label: 'View', onClick }} />)
    await user.click(screen.getByText('View'))
    expect(onClick).toHaveBeenCalledOnce()
  })
})
