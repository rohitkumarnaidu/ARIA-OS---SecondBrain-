import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PageHeader } from '@/components/ui/PageHeader'

describe('PageHeader', () => {
  it('renders title', () => {
    render(<PageHeader title="Dashboard" />)
    expect(screen.getByText('Dashboard')).toBeTruthy()
  })

  it('renders description', () => {
    render(<PageHeader title="Dashboard" description="Your at-a-glance overview" />)
    expect(screen.getByText('Your at-a-glance overview')).toBeTruthy()
  })

  it('renders breadcrumb nav', () => {
    render(<PageHeader title="Tasks" breadcrumb={[{ label: 'Home' }, { label: 'Tasks' }]} />)
    expect(screen.getByRole('navigation', { name: 'Breadcrumb' })).toBeTruthy()
    expect(screen.getByText('Home')).toBeTruthy()
    expect(screen.getAllByText('Tasks').length).toBeGreaterThanOrEqual(1)
  })

  it('marks last breadcrumb as current page', () => {
    render(<PageHeader title="Tasks" breadcrumb={[{ label: 'Home' }, { label: 'Tasks' }]} />)
    const items = screen.getAllByText('Tasks')
    const breadcrumbItem = items.find(item => item.getAttribute('aria-current') === 'page')
    expect(breadcrumbItem).toBeTruthy()
  })

  it('renders breadcrumb with href on non-last items', () => {
    render(<PageHeader title="Tasks" breadcrumb={[{ label: 'Home', href: '/' }, { label: 'Tasks' }]} />)
    const link = screen.getByText('Home')
    expect(link.tagName).toBe('A')
    expect(link).toHaveAttribute('href', '/')
  })

  it('renders actions slot', () => {
    render(<PageHeader title="Tasks" actions={<button>Add Task</button>} />)
    expect(screen.getByText('Add Task')).toBeTruthy()
  })

  it('applies custom className', () => {
    const { container } = render(<PageHeader title="Test" className="custom-class" />)
    expect(container.firstElementChild).toHaveClass('custom-class')
  })
})
