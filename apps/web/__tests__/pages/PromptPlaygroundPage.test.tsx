import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/lib/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ total: 0, prompts: [], commits: [] }),
    post: vi.fn().mockResolvedValue({ rendered: '' }),
  },
}))

vi.mock('@/lib/toast', () => ({
  showSuccess: vi.fn(),
  showError: vi.fn(),
}))

import PromptPlaygroundPage from '../../app/(dashboard)/prompt-playground/page'

describe('PromptPlaygroundPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<PromptPlaygroundPage />)
    expect(container).toBeTruthy()
  })
})
