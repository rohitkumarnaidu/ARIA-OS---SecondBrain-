import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SuggestionChips } from '@/components/ai/SuggestionChips'

describe('SuggestionChips', () => {
  const suggestions = [
    { id: '1', label: 'What are my tasks?', icon: 'list' as const },
    { id: '2', label: 'Analyze my week', icon: 'chart' as const },
    { id: '3', label: 'Suggest goals', icon: 'goal' as const },
  ]

  it('renders all suggestions', () => {
    render(<SuggestionChips suggestions={suggestions} onSelect={() => {}} />)
    expect(screen.getByText('What are my tasks?')).toBeTruthy()
    expect(screen.getByText('Analyze my week')).toBeTruthy()
    expect(screen.getByText('Suggest goals')).toBeTruthy()
  })

  it('calls onSelect with id when chip clicked', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    render(<SuggestionChips suggestions={suggestions} onSelect={onSelect} />)
    await user.click(screen.getByText('What are my tasks?'))
    expect(onSelect).toHaveBeenCalledWith('1')
  })

  it('renders nothing when suggestions empty', () => {
    const { container } = render(<SuggestionChips suggestions={[]} onSelect={() => {}} />)
    expect(container.firstElementChild).toBeNull()
  })
})
