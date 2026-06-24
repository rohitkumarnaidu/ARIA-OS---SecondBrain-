import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useStreamingChat, useAIAgents, useAIAction } from '@/lib/ai/hooks'

vi.mock('@/lib/ai/client', () => {
  const sendMessageMock = vi.fn()
  const cancelMock = vi.fn()
  return {
    AIStreamClient: vi.fn(() => ({
      sendMessage: sendMessageMock,
      cancel: cancelMock,
      getCircuitBreakerState: () => 'closed',
      resetCircuitBreaker: vi.fn(),
    })),
    aiStream: {
      sendMessage: sendMessageMock,
      cancel: cancelMock,
      getCircuitBreakerState: () => 'closed',
      resetCircuitBreaker: vi.fn(),
    },
  }
})

describe('useStreamingChat', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('has correct initial state', () => {
    const { result } = renderHook(() => useStreamingChat())
    expect(result.current.messages).toEqual([])
    expect(result.current.isStreaming).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.connectionState).toBe('disconnected')
  })

  it('loads persisted messages from localStorage', () => {
    const existing = [{ role: 'user' as const, content: 'hello', timestamp: 100 }]
    localStorage.setItem('aria-chat-history', JSON.stringify(existing))
    const { result } = renderHook(() => useStreamingChat())
    expect(result.current.messages).toEqual(existing)
  })

  it('handles corrupted localStorage gracefully', () => {
    localStorage.setItem('aria-chat-history', 'not-json')
    const { result } = renderHook(() => useStreamingChat())
    expect(result.current.messages).toEqual([])
  })

  it('sendMessage adds user message and sets streaming state', async () => {
    const { result } = renderHook(() => useStreamingChat())

    const { aiStream } = await import('@/lib/ai/client')
    vi.mocked(aiStream.sendMessage).mockImplementation((_msg, _tid, onChunk, onDone, _onErr) => {
      onChunk('Hello from AI')
      onDone('Hello from AI')
      return Promise.resolve()
    })

    await act(async () => {
      result.current.sendMessage('Hi there')
      await vi.advanceTimersByTimeAsync(0)
    })

    expect(result.current.messages.length).toBe(2)
    expect(result.current.messages[0].role).toBe('user')
    expect(result.current.messages[0].content).toBe('Hi there')
    expect(result.current.messages[1].role).toBe('assistant')
    expect(result.current.messages[1].content).toBe('Hello from AI')
    expect(result.current.isStreaming).toBe(false)
  })

  it('sendMessage handles error state after exhausting retries', async () => {
    const { result } = renderHook(() => useStreamingChat())

    const { aiStream } = await import('@/lib/ai/client')
    const sendMock = vi.mocked(aiStream.sendMessage)

    // The hook retries 3 times internally via setTimeout(attemptSend, 1000 * retryCountRef.current)
    // Each call triggers onError, then the hook retries, then eventually gives up
    sendMock.mockImplementation((_msg, _tid, _onChunk, _onDone, onError) => {
      onError(new Error('AI is down'))
      return Promise.resolve()
    })

    await act(async () => {
      result.current.sendMessage('Hi')
      // Advance past retry 1 (1s), retry 2 (2s), retry 3 (3s) = 6s total
      await vi.advanceTimersByTimeAsync(7000)
    })

    expect(result.current.error).toBe('AI is down')
    expect(result.current.isStreaming).toBe(false)
  })

  it('clearMessages resets state and persists empty array', async () => {
    const { result } = renderHook(() => useStreamingChat())

    const { aiStream } = await import('@/lib/ai/client')
    vi.mocked(aiStream.sendMessage).mockImplementation((_msg, _tid, onChunk, onDone, _onErr) => {
      onChunk('hi')
      onDone('hi')
      return Promise.resolve()
    })

    await act(async () => {
      result.current.sendMessage('Hi')
      await vi.advanceTimersByTimeAsync(0)
    })

    expect(result.current.messages.length).toBeGreaterThan(0)

    act(() => {
      result.current.clearMessages()
    })

    expect(result.current.messages).toEqual([])
    expect(result.current.error).toBeNull()
    // After clearMessages, the effect re-runs and persists []
    expect(JSON.parse(localStorage.getItem('aria-chat-history') || '[]')).toEqual([])
  })

  it('cancelStream aborts and resets state', () => {
    const { result } = renderHook(() => useStreamingChat())

    act(() => {
      result.current.cancelStream()
    })

    expect(result.current.isStreaming).toBe(false)
    expect(result.current.connectionState).toBe('disconnected')
  })

  it('retry resets error and connection state', () => {
    const { result } = renderHook(() => useStreamingChat())
    act(() => {
      result.current.retry()
    })
    expect(result.current.error).toBeNull()
    expect(result.current.connectionState).toBe('disconnected')
  })
})

describe('useAIAgents', () => {
  it('returns all 8 agents with idle status', () => {
    const { result } = renderHook(() => useAIAgents())
    expect(result.current.agents.length).toBe(8)
    expect(result.current.agents.every(a => a.status === 'idle')).toBe(true)
  })

  it('updateAgent updates specific agent', () => {
    const { result } = renderHook(() => useAIAgents())
    act(() => {
      result.current.updateAgent('planner', { status: 'thinking', preview: 'Analyzing...' })
    })
    const planner = result.current.agents.find(a => a.agent_id === 'planner')
    expect(planner?.status).toBe('thinking')
    expect(planner?.preview).toBe('Analyzing...')
  })

  it('updateAgent does not modify other agents', () => {
    const { result } = renderHook(() => useAIAgents())
    act(() => {
      result.current.updateAgent('planner', { status: 'thinking' })
    })
    const memory = result.current.agents.find(a => a.agent_id === 'memory')
    expect(memory?.status).toBe('idle')
  })

  it('resetAgents resets all to idle', () => {
    const { result } = renderHook(() => useAIAgents())
    act(() => {
      result.current.updateAgent('planner', { status: 'thinking', preview: 'test', confidence: 0.5 })
      result.current.updateAgent('memory', { status: 'done' })
    })
    act(() => {
      result.current.resetAgents()
    })
    expect(result.current.agents.every(a => a.status === 'idle')).toBe(true)
    expect(result.current.agents.every(a => a.preview === undefined)).toBe(true)
    expect(result.current.agents.every(a => a.confidence === undefined)).toBe(true)
  })

  it('updateAgent with partial updates preserves other fields', () => {
    const { result } = renderHook(() => useAIAgents())
    act(() => {
      result.current.updateAgent('planner', { status: 'thinking' })
    })
    const planner = result.current.agents.find(a => a.agent_id === 'planner')
    expect(planner?.agent_name).toBe('Planner')
  })

  it('has correct agent names', () => {
    const { result } = renderHook(() => useAIAgents())
    const names = result.current.agents.map(a => a.agent_name)
    expect(names).toContain('Planner')
    expect(names).toContain('Memory')
    expect(names).toContain('Learning')
    expect(names).toContain('Daily Briefing')
    expect(names).toContain('Opportunity Radar')
    expect(names).toContain('Sleep Coach')
    expect(names).toContain('Nudge Engine')
    expect(names).toContain('Roadmap Optimizer')
  })
})

describe('useAIAction', () => {
  it('execute calls the wrapped action and returns result', async () => {
    const mockAction = vi.fn().mockResolvedValue('success')
    const { result } = renderHook(() => useAIAction(mockAction))

    let output: unknown
    await act(async () => {
      output = await result.current.execute('arg1', 'arg2')
    })

    expect(output).toBe('success')
    expect(mockAction).toHaveBeenCalledWith('arg1', 'arg2')
  })

  it('sets loading state during execution', async () => {
    const mockAction = vi.fn(async () => {
      await new Promise(r => setTimeout(r, 100))
      return 'done'
    })
    const { result } = renderHook(() => useAIAction(mockAction))

    let promise: Promise<unknown>
    act(() => {
      promise = result.current.execute()
    })
    expect(result.current.isLoading).toBe(true)

    await act(async () => {
      await promise
    })
    expect(result.current.isLoading).toBe(false)
  })

  it('sets error when action throws', async () => {
    const mockAction = vi.fn().mockRejectedValue(new Error('action failed'))
    const { result } = renderHook(() => useAIAction(mockAction))

    await act(async () => {
      try {
        await result.current.execute()
      } catch {
        // expected
      }
    })

    expect(result.current.error).toBe('action failed')
    expect(result.current.isLoading).toBe(false)
  })

  it('handles non-Error thrown values', async () => {
    const mockAction = vi.fn().mockRejectedValue('string error')
    const { result } = renderHook(() => useAIAction(mockAction))

    await act(async () => {
      try {
        await result.current.execute()
      } catch {
        // expected
      }
    })

    expect(result.current.error).toBe('AI action failed. Please try again.')
  })

  it('resets error on each execute call', async () => {
    const failOnce = vi.fn()
      .mockRejectedValueOnce(new Error('first fail'))
      .mockResolvedValueOnce('ok')

    const { result } = renderHook(() => useAIAction(failOnce))

    await act(async () => {
      try { await result.current.execute() } catch { /* expected */ }
    })
    expect(result.current.error).toBe('first fail')

    await act(async () => {
      await result.current.execute()
    })
    expect(result.current.error).toBeNull()
    expect(result.current.isLoading).toBe(false)
  })
})
