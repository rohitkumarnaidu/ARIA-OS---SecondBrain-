import { describe, it, expect, vi, beforeAll, afterAll, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { server } from '@/__tests__/mocks/server'
import Sidebar from '@/components/layout/Sidebar'

const mockPathname = '/dashboard'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn(), forward: vi.fn(), refresh: vi.fn(), prefetch: vi.fn() }),
  usePathname: () => mockPathname,
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
  default: {},
}))

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => { server.resetHandlers(); vi.clearAllMocks() })
afterAll(() => server.close())

describe('Navigation Flow Integration', () => {
  it('renders sidebar with logo', () => {
    render(<Sidebar />)
    expect(screen.getByText('Second Brain OS')).toBeInTheDocument()
  })

  it('renders all navigation links', () => {
    render(<Sidebar />)
    const navNames = [
      'Dashboard', 'Tasks', 'Courses', 'YouTube', 'Resources',
      'Ideas', 'Goals', 'Opportunities', 'Income', 'Projects',
      'Academics', 'Habits', 'Sleep', 'Time', 'Chat', 'Automation',
    ]
    for (const name of navNames) {
      expect(screen.getByText(name)).toBeInTheDocument()
    }
  })

  it('marks active route with aria-current="page"', () => {
    render(<Sidebar />)
    const dashboardLink = screen.getByText('Dashboard').closest('a')
    expect(dashboardLink).toHaveAttribute('aria-current', 'page')
  })

  it('other routes do not have aria-current', () => {
    render(<Sidebar />)
    const tasksLink = screen.getByText('Tasks').closest('a')
    expect(tasksLink).not.toHaveAttribute('aria-current')
  })

  it('renders navigation role and aria-label', () => {
    render(<Sidebar />)
    expect(screen.getByRole('navigation', { name: /main navigation/i })).toBeInTheDocument()
    expect(screen.getByRole('navigation', { name: /module navigation/i })).toBeInTheDocument()
  })

  it('all nav items have accessible link text', () => {
    render(<Sidebar />)
    const links = screen.getAllByRole('link')
    links.forEach(link => {
      expect(link).toHaveAttribute('href')
      expect(link.textContent?.trim()).toBeTruthy()
    })
  })

  it('nav links have correct href attributes', () => {
    render(<Sidebar />)
    const expectedHrefs = [
      '/dashboard', '/tasks', '/courses', '/youtube', '/resources',
      '/ideas', '/goals', '/opportunities', '/income', '/projects',
      '/academics', '/habits', '/sleep', '/time', '/chat', '/automation',
    ]
    const links = screen.getAllByRole('link')
    for (const href of expectedHrefs) {
      expect(links.some(l => l.getAttribute('href') === href)).toBe(true)
    }
  })

  it('has accessible focusable elements', () => {
    render(<Sidebar />)
    const links = screen.getAllByRole('link')
    links.forEach(link => {
      expect(link).toHaveAttribute('href')
    })
  })
})
