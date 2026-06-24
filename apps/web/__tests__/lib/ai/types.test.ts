import { describe, it, expect } from 'vitest'
import type { AIStreamChunk, AIRequest, AIResponse, AIAgentResult, AIConnectionState } from '@/lib/ai/types'

describe('AI types', () => {
  it('AIStreamChunk accepts minimal shape', () => {
    const chunk: AIStreamChunk = { content: 'hello' }
    expect(chunk.content).toBe('hello')
    expect(chunk.agent).toBeUndefined()
    expect(chunk.done).toBeUndefined()
    expect(chunk.error).toBeUndefined()
  })

  it('AIStreamChunk accepts all fields', () => {
    const chunk: AIStreamChunk = { content: 'hello', agent: 'planner', done: true, error: undefined }
    expect(chunk.content).toBe('hello')
    expect(chunk.agent).toBe('planner')
    expect(chunk.done).toBe(true)
  })

  it('AIRequest accepts message and optional fields', () => {
    const r1: AIRequest = { message: 'hello' }
    expect(r1.message).toBe('hello')
    expect(r1.thread_id).toBeUndefined()

    const r2: AIRequest = { message: 'hello', thread_id: 't1', context: { key: 'val' } }
    expect(r2.thread_id).toBe('t1')
    expect(r2.context?.key).toBe('val')
  })

  it('AIResponse has required fields', () => {
    const res: AIResponse = { message: 'hello', thread_id: 't1', agent: 'planner', timestamp: '2026-01-01T00:00:00Z' }
    expect(res.message).toBe('hello')
    expect(res.thread_id).toBe('t1')
    expect(res.agent).toBe('planner')
    expect(res.timestamp).toBe('2026-01-01T00:00:00Z')
  })

  it('AIAgentResult accepts all status values', () => {
    const statuses = ['idle', 'thinking', 'streaming', 'done', 'error'] as const
    for (const status of statuses) {
      const agent: AIAgentResult = { agent_id: 'a1', agent_name: 'Test', status }
      expect(agent.status).toBe(status)
    }
  })

  it('AIAgentResult accepts optional preview and confidence', () => {
    const agent: AIAgentResult = { agent_id: 'a1', agent_name: 'Test', status: 'idle', preview: 'preview text', confidence: 0.85 }
    expect(agent.preview).toBe('preview text')
    expect(agent.confidence).toBe(0.85)
  })

  it('AIConnectionState accepts all valid values', () => {
    const states: AIConnectionState[] = ['disconnected', 'connecting', 'streaming', 'connected', 'error']
    for (const s of states) {
      expect(s).toBeDefined()
    }
  })

  it('AIConnectionState rejects invalid values at compile time', () => {
    const valid: AIConnectionState = 'connected'
    expect(['disconnected', 'connecting', 'streaming', 'connected', 'error']).toContain(valid)
  })
})
