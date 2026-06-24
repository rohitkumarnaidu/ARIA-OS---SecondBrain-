import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn().mockResolvedValue({}), post: vi.fn().mockResolvedValue({}) },
}))

import MonitoringPage from '../../app/(dashboard)/monitoring/page'

describe('MonitoringPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<MonitoringPage />)
    expect(container).toBeTruthy()
  })
})
