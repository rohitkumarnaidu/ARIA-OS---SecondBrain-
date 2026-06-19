import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Tabs } from '@/components/ui/Tabs'

const tabs = [
  { value: 'tab1', label: 'First Tab' },
  { value: 'tab2', label: 'Second Tab' },
  { value: 'tab3', label: 'Third Tab' },
]

describe('Tabs', () => {
  it('renders all tab labels', () => {
    render(<Tabs tabs={tabs} value="tab1" onChange={vi.fn()} />)
    expect(screen.getByText('First Tab')).toBeInTheDocument()
    expect(screen.getByText('Second Tab')).toBeInTheDocument()
    expect(screen.getByText('Third Tab')).toBeInTheDocument()
  })

  it('has role="tablist"', () => {
    render(<Tabs tabs={tabs} value="tab1" onChange={vi.fn()} />)
    expect(screen.getByRole('tablist')).toBeInTheDocument()
  })

  it('aria-selected reflects active tab', () => {
    render(<Tabs tabs={tabs} value="tab2" onChange={vi.fn()} />)
    const tabButtons = screen.getAllByRole('tab')
    expect(tabButtons[0]).toHaveAttribute('aria-selected', 'false')
    expect(tabButtons[1]).toHaveAttribute('aria-selected', 'true')
    expect(tabButtons[2]).toHaveAttribute('aria-selected', 'false')
  })

  it('onChange fires when clicking a tab', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Tabs tabs={tabs} value="tab1" onChange={onChange} />)
    await user.click(screen.getByText('Second Tab'))
    expect(onChange).toHaveBeenCalledWith('tab2')
  })

  it('arrow right keyboard navigation works', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Tabs tabs={tabs} value="tab1" onChange={onChange} />)
    const activeTab = screen.getByRole('tab', { name: 'First Tab' })
    activeTab.focus()
    await user.keyboard('{ArrowRight}')
    expect(onChange).toHaveBeenCalledWith('tab2')
  })

  it('arrow left keyboard navigation works', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<Tabs tabs={tabs} value="tab2" onChange={onChange} />)
    const activeTab = screen.getByRole('tab', { name: 'Second Tab' })
    activeTab.focus()
    await user.keyboard('{ArrowLeft}')
    expect(onChange).toHaveBeenCalledWith('tab1')
  })

  it('aria-controls links tab to panel', () => {
    render(<Tabs tabs={tabs} value="tab1" onChange={vi.fn()} />)
    const tab = screen.getByRole('tab', { name: 'First Tab' })
    expect(tab).toHaveAttribute('aria-controls', 'tabpanel-tab1')
  })
})
