import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/stores', async (importOriginal) => {
  const mod = await importOriginal()
  return {
    ...mod,
    useProjectStore: vi.fn(() => ({
      items: [], loading: false, error: null,
      fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(),
    })),
  }
})

vi.mock('@/lib/toast', () => ({
  showError: vi.fn(),
  showSuccess: vi.fn(),
}))

import ProjectsPage from '../../app/(dashboard)/projects/page'

describe('ProjectsPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<ProjectsPage />)
    expect(container).toBeTruthy()
  })
})
