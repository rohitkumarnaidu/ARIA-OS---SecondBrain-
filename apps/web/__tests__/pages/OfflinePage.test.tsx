import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'

import OfflinePage from '../../app/offline/page'

describe('OfflinePage', () => {
  it('renders without crashing', () => {
    const { container } = render(<OfflinePage />)
    expect(container).toBeTruthy()
  })
})
