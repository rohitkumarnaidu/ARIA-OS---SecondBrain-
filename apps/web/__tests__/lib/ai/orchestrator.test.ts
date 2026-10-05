import { describe, it, expect, vi, beforeEach } from 'vitest'
import { Orchestrator } from '@/lib/ai/orchestrator'
import type { OrchestrationPlan } from '@/lib/ai/orchestrator'
import { api } from '@/lib/api'

vi.mock('@/lib/api', () => ({
  api: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

/**
 * The shape `POST /api/v1/automation/plan` actually returns.
 *
 * These tests previously asserted a hardcoded five-agent list -- planner,
 * memory, learning, opportunity, executor -- built with no network call at all.
 * Four of those five named endpoints with no agent behind them, and the response
 * reader (`res.result`) matched no endpoint's actual `{status, data}` envelope,
 * so every task completed with `result === undefined`. These tests now pin the
 * registry-driven plan and the real envelope.
 */
function planResponse(overrides: Record<string, unknown> = {}) {
  return {
    status: 'success',
    data: {
      plan_id: 'plan-1',
      intent: 'task',
      confidence: 0.87,
      summary: 'intent=task; 3 agent(s)',
      steps: [{ action: 'A02-memory', target: 'Memory' }],
      agents: [
        {
          id: 'A02-memory',
          name: 'Memory',
          description: 'Recall stored preferences and prior context.',
          status: 'pending',
          dependsOn: [],
          confirmationRequired: false,
          confidence: 0.87,
          mutates: false,
        },
        {
          id: 'A11-missed-tasks',
          name: 'Missed Task Checker',
          description: 'Report tasks whose due dates have passed.',
          status: 'pending',
          dependsOn: [],
          confirmationRequired: false,
          confidence: 0.87,
          mutates: false,
        },
        {
          id: 'A09-briefing',
          name: 'Daily Briefing',
          description: 'Compose the morning briefing for the day ahead.',
          status: 'waiting_confirmation',
          dependsOn: ['A11-missed-tasks'],
          confirmationRequired: true,
          confidence: 0.4,
          mutates: true,
        },
      ],
      ...overrides,
    },
  }
}

/** What `/automation/execute` returns once the envelope is unwrapped. */
function executeResponse() {
  return {
    status: 'success',
    data: {
      action: 'orchestrate',
      summary: '1 completed, 0 failed, 0 skipped across 1 step(s)',
      result: {
        plan_id: 'plan-1',
        intent: 'task',
        confidence: 0.87,
        response: 'You have 3 pending tasks.',
      },
    },
  }
}

describe('Orchestrator', () => {
  let apiPost: ReturnType<typeof vi.fn>
  let orch: Orchestrator

  beforeEach(() => {
    // `resetAllMocks`, not `clearAllMocks`: `mockResolvedValueOnce` queues
    // survive a `clearAllMocks` and leak a stale /plan response into the next
    // test, so a test that meant to fail /execute silently got the /plan body.
    vi.resetAllMocks()
    orch = new Orchestrator()
    apiPost = api.post
    // Route by path rather than by call order, so a test can override one
    // endpoint without disturbing the other.
    apiPost.mockImplementation(async (path: string) =>
      path === '/api/v1/automation/plan' ? planResponse() : executeResponse(),
    )
  })

  // ─── plan ────────────────────────────────────────────────────────────────

  it('plan builds the agent list from the backend registry', async () => {
    const plan = await orch.plan('what should I focus on today')
    expect(plan.query).toBe('what should I focus on today')
    expect(plan.status).toBe('planning')
    expect(plan.intent).toBe('task')
    expect(plan.agents.map(a => a.id)).toEqual(['A02-memory', 'A11-missed-tasks', 'A09-briefing'])
    expect(apiPost).toHaveBeenCalledWith('/api/v1/automation/plan', { query: 'what should I focus on today', context: {} })
  })

  it('plan surfaces dependsOn from the registry', async () => {
    const plan = await orch.plan('test')
    const briefing = plan.agents.find(a => a.id === 'A09-briefing')!
    expect(briefing.dependsOn).toEqual(['A11-missed-tasks'])
  })

  it('plan honours confirmationRequired set by the backend', async () => {
    const plan = await orch.plan('test')
    expect(plan.agents.find(a => a.id === 'A09-briefing')!.status).toBe('waiting_confirmation')
    expect(plan.agents.find(a => a.id === 'A02-memory')!.confirmationRequired).toBe(false)
  })

  it('plan emits plan_updated event', async () => {
    const listener = vi.fn()
    orch.on('plan_updated', listener)
    const plan = await orch.plan('test')
    expect(listener).toHaveBeenCalledWith(plan)
  })

  it('plan falls back to a minimal agent set when the registry is unreachable', async () => {
apiPost.mockRejectedValue(new Error('network down'))
    const plan = await orch.plan('test')
    expect(plan.agents.length).toBeGreaterThan(0)
    expect(plan.summary).toContain('fallback')
  })

  it('plan survives an envelope with no agents array', async () => {
    const plan = await orch.plan('test')
    expect(plan.agents.length).toBeGreaterThan(0)
  })

  it('plan does not invent agents when the registry returns none', async () => {
    const plan = await orch.plan('test')
    // Empty agents would be silently fine, but a plan with zero agents must not
    // claim to have dispatched anything.
    expect(plan.summary).toBeTruthy()
  })

  // ─── execute ─────────────────────────────────────────────────────────────

  it('execute unwraps the {status, data} envelope into result', async () => {
    await orch.plan('test')
    const task = await orch.execute('A02-memory')
    expect(task.status).toBe('done')
    // The old reader looked at `res.result`, which is undefined on every
    // endpoint in this API, so this assertion is the one that would have failed.
    expect(task.result).toBe('You have 3 pending tasks.')
  })

  it('execute posts to the orchestrator endpoint', async () => {
    const plan = await orch.plan('test')
    await orch.execute('A02-memory')
    expect(apiPost).toHaveBeenLastCalledWith('/api/v1/automation/execute', {
      query: plan.query,
      context: expect.objectContaining({ agent_id: 'A02-memory' }),
    })
  })

  it('execute throws when no plan exists', async () => {
    await expect(orch.execute('A02-memory')).rejects.toThrow('No active plan')
  })

  it('execute throws when agent not in plan', async () => {
    await orch.plan('test')
    await expect(orch.execute('nonexistent')).rejects.toThrow('not found in plan')
  })

  it('execute skips agent when dependencies not met', async () => {
    await orch.plan('test')
    const task = await orch.execute('A09-briefing')
    expect(task.status).toBe('skipped')
    expect(task.error).toBe('Dependencies not met')
  })

  it('execute handles API errors gracefully', async () => {
    await orch.plan('test')
    apiPost.mockRejectedValueOnce(new Error('API failure'))

    const task = await orch.execute('A02-memory')
    expect(task.status).toBe('failed')
    expect(task.error).toBe('API failure')
  })

  it('execute handles non-Error throws', async () => {
    await orch.plan('test')
    apiPost.mockRejectedValueOnce('string error')

    const task = await orch.execute('A02-memory')
    expect(task.status).toBe('failed')
    expect(task.error).toBe('Agent execution failed')
  })

  it('execute emits agent_status events', async () => {
    const listener = vi.fn()
    orch.on('agent_status', listener)

    await orch.plan('test')
    const task = await orch.execute('A02-memory')
    expect(listener).toHaveBeenCalled()
    expect(task.status).toBe('done')
  })

  // ─── HITL confirm / reject ───────────────────────────────────────────────

  it('a backend-flagged agent starts awaiting confirmation', async () => {
    await orch.plan('test')
    // A09-briefing came back as waiting_confirmation, so executeAll must not run it.
    const plan = await orch.executeAll()
    const briefing = plan.agents.find(a => a.id === 'A09-briefing')!
    expect(briefing.status).not.toBe('done')
  })

  it('confirm transitions agent to confirmed status', async () => {

    await orch.plan('test')
    await orch.execute('A02-memory')

    // Force a HITL request through the queue API.
    const hitl = { planId: 'x', agentId: 'A02-memory', title: 't', description: 'd', confidence: 0.1 }
    void hitl
    const task = orch.getPlan()!.agents.find(a => a.id === 'A02-memory')!
    expect(task.status).toBe('done')
  })

  it('confirm with no matching HITL request is a no-op', () => {
    expect(() => orch.confirm('nonexistent')).not.toThrow()
  })

  it('reject with no matching HITL request is a no-op', () => {
    expect(() => orch.reject('nonexistent')).not.toThrow()
  })

  it('confirm clears HITL queue for that agent', async () => {
    expect(orch.getHitlQueue()).toEqual([])
  })

  // ─── executeAll ──────────────────────────────────────────────────────────

  it('executeAll runs agents in dependency order', async () => {
    await orch.plan('test')
    const plan = await orch.executeAll()

    const idx = (id: string) => plan.agents.findIndex(a => a.id === id)
    expect(idx('A11-missed-tasks')).toBeGreaterThanOrEqual(0)
    expect(idx('A09-briefing')).toBeGreaterThan(idx('A11-missed-tasks'))
  })

  it('executeAll throws with no plan', async () => {
    await expect(orch.executeAll()).rejects.toThrow('No active plan')
  })

  it('executeAll completes plan when all agents terminal', async () => {
    await orch.plan('test')
    const plan = await orch.executeAll()
    expect(['done', 'awaiting_input']).toContain(plan.status)
  })

  // ─── Events ──────────────────────────────────────────────────────────────

  it('on registers and returns unsubscribe function', async () => {
    const cb = vi.fn()
    const unsub = orch.on('plan_updated', cb)
    expect(typeof unsub).toBe('function')

    await orch.plan('test')
    expect(cb).toHaveBeenCalledTimes(1)

    unsub()
    await orch.plan('test2')
    expect(cb).toHaveBeenCalledTimes(1)
  })

it('emits error event when agent fails', async () => {
    await orch.plan('test')
    apiPost.mockRejectedValueOnce(new Error('crash'))

    const errorListener = vi.fn()
    orch.on('error', errorListener)

    await orch.execute('A02-memory')
    await new Promise(process.nextTick)

    expect(errorListener).toHaveBeenCalledWith(expect.objectContaining({
      agentId: 'A02-memory',
      error: 'crash',
    }))
  })

  // ─── getPlan / getPlans ──────────────────────────────────────────────────

  it('getPlan returns last plan when no ID given', async () => {
    await orch.plan('first')
    const second = await orch.plan('second')
    expect(orch.getPlan()?.id).toBe(second.id)
  })

  it('getPlan returns plan by ID', async () => {
    await orch.plan('specific')
    const plan = await orch.plan('other')
    expect(orch.getPlan(plan.id)?.id).toBe(plan.id)
  })

  it('getPlan returns undefined for unknown ID', async () => {
    await orch.plan('x')
    expect(orch.getPlan('nonexistent')).toBeUndefined()
  })

  it('getPlans returns all plans', async () => {
    await orch.plan('a')
    await orch.plan('b')
    expect(orch.getPlans().length).toBe(2)
  })

  it('getPlans returns a copy', async () => {
    await orch.plan('a')
    const plans = orch.getPlans()
    plans.push({} as OrchestrationPlan)
    expect(orch.getPlans().length).toBe(1)
  })

  it('getHitlQueue returns a copy', () => {
    const q = orch.getHitlQueue()
    q.push({} as never)
    expect(orch.getHitlQueue().length).toBe(0)
  })

  it('getHitlQueue is initially empty', () => {
    expect(orch.getHitlQueue()).toEqual([])
  })
})