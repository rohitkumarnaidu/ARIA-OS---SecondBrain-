import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/stores', () => ({
  useAcademicStore: vi.fn(() => ({
    subjects: [], marks: [], loading: false, error: null,
    fetchAll: vi.fn(), addSubject: vi.fn(), addMark: vi.fn(), deleteSubject: vi.fn(),
  })),
}))

vi.mock('@/lib/toast', () => ({
  showError: vi.fn(),
  showSuccess: vi.fn(),
}))

import AcademicsPage from '../../app/(dashboard)/academics/page'

describe('AcademicsPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<AcademicsPage />)
    expect(container).toBeTruthy()
  })
})
