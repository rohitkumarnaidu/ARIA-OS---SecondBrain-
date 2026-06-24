import { describe, it, expect } from 'vitest'
import * as ai from '@/lib/ai'

describe('ai barrel exports', () => {
  it('exports runtime values', () => {
    expect(ai).toHaveProperty('AIStreamClient')
    expect(ai).toHaveProperty('aiStream')
    expect(ai).toHaveProperty('predictive')
    expect(ai).toHaveProperty('computeSentiment')
    expect(ai).toHaveProperty('parseCommand')
    expect(ai).toHaveProperty('resolveNavigation')
    expect(ai).toHaveProperty('orchestrator')
  })

  it('aiStream is an AIStreamClient instance', () => {
    expect(ai.aiStream.constructor.name).toBe('AIStreamClient')
    expect(typeof ai.aiStream.sendMessage).toBe('function')
    expect(typeof ai.aiStream.cancel).toBe('function')
    expect(typeof ai.aiStream.getCircuitBreakerState).toBe('function')
  })

  it('predictive has expected methods', () => {
    expect(typeof ai.predictive.taskCompletion).toBe('function')
    expect(typeof ai.predictive.habits).toBe('function')
    expect(typeof ai.predictive.sleep).toBe('function')
    expect(typeof ai.predictive.smartSlots).toBe('function')
    expect(typeof ai.predictive.clearCache).toBe('function')
    expect(typeof ai.predictive.invalidate).toBe('function')
  })

  it('computeSentiment is a function', () => {
    expect(typeof ai.computeSentiment).toBe('function')
  })

  it('parseCommand is a function', () => {
    expect(typeof ai.parseCommand).toBe('function')
  })

  it('resolveNavigation is a function', () => {
    expect(typeof ai.resolveNavigation).toBe('function')
  })

  it('orchestrator is an Orchestrator instance', () => {
    expect(ai.orchestrator.constructor.name).toBe('Orchestrator')
    expect(typeof ai.orchestrator.plan).toBe('function')
    expect(typeof ai.orchestrator.execute).toBe('function')
    expect(typeof ai.orchestrator.confirm).toBe('function')
    expect(typeof ai.orchestrator.reject).toBe('function')
  })

  it('exports type-only symbols (compile-time check)', () => {
    // At runtime these are undefined since they're type exports,
    // but we can still verify they don't collide with value exports
    expect((ai as any).AIStreamChunk).toBeUndefined()
    expect((ai as any).AIRequest).toBeUndefined()
    expect((ai as any).AIResponse).toBeUndefined()
    expect((ai as any).AIAgentResult).toBeUndefined()
    expect((ai as any).AIConnectionState).toBeUndefined()
  })
})
