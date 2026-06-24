import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/components/youtube-vault/YouTubeVault', () => ({
  YouTubeVault: () => <div data-testid="youtube-vault" />,
}))

import YouTubeVaultPage from '../../app/(dashboard)/youtube-vault/page'

describe('YouTubeVaultPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<YouTubeVaultPage />)
    expect(container).toBeTruthy()
  })
})
