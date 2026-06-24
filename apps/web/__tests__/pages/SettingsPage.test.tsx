import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/components/settings/SettingsPage', () => ({
  SettingsPage: () => <div data-testid="settings-page" />,
}))

import SettingsPageRoute from '../../app/(dashboard)/settings/page'

describe('SettingsPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<SettingsPageRoute />)
    expect(container).toBeTruthy()
  })
})
