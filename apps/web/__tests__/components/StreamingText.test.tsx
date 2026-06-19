import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest'
import { render, cleanup, act } from '@testing-library/react'
import { StreamingText } from '@/components/ai/StreamingText'

beforeEach(() => {
  vi.useFakeTimers({ shouldAdvanceTime: true })
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
})

describe('StreamingText', () => {
  it('renders text when not streaming', () => {
    const { container } = render(<StreamingText text="Hello" isStreaming={false} />)
    expect(container.textContent).toBe('Hello')
  })

  it('renders text when streaming', () => {
    const { container } = render(<StreamingText text="Hello" isStreaming={true} speed={30} />)
    expect(container.textContent).toBe('Hello')
  })

  it('shows complete state when streaming ends', () => {
    const { container } = render(<StreamingText text="Done" isStreaming={false} />)
    expect(container.textContent).toBe('Done')
  })

  it('renders with custom className', () => {
    const { container } = render(<StreamingText text="Test" isStreaming={false} className="custom-stream" />)
    expect(container.textContent).toBe('Test')
  })
})
