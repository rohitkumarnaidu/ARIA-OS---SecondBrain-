import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/lib/stores', () => ({
  useAutomationStore: vi.fn(() => ({
    automations: [], loading: false, error: null, running: false,
    fetch: vi.fn(() => Promise.resolve()),
    trigger: vi.fn(),
    toggle: vi.fn(),
  })),
}))

import AutomationPage from '../../app/(dashboard)/automation/page'

describe('AutomationPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<AutomationPage />)
    expect(container).toBeTruthy()
  })
})
