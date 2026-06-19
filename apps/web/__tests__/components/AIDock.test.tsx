import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AIDock } from '@/components/ai/AIDock'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => '/',
}))

describe('AIDock', () => {
  it('renders ARIA dock', () => {
    const { container } = render(<AIDock />)
    expect(container.firstElementChild).toBeTruthy()
  })
})
