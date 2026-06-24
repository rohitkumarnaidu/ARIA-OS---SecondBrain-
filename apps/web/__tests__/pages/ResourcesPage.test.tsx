import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/components/resources/ResourceGrid', () => ({
  ResourceGrid: () => <div data-testid="resource-grid" />,
}))

vi.mock('@/components/resources/ResourceFilters', () => ({
  ResourceFilters: () => <div data-testid="resource-filters" />,
}))

import ResourcesPage from '../../app/(dashboard)/resources/page'

describe('ResourcesPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<ResourcesPage />)
    expect(container).toBeTruthy()
  })
})
