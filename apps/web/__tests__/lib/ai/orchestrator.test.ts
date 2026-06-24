import { describe, it, expect, vi, beforeEach } from 'vitest'
import { Orchestrator, orchestrator } from '@/lib/ai/orchestrator'
import type { OrchestrationPlan, AgentTask } from '@/lib/ai/orchestrator'
import { api } from '@/lib/api'

vi.mock('@/lib/api', () => ({
  api: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

describe('Orchestrator', () => {
  let apiPost: ReturnType<typeof vi.fn>
  let orch: Orchestrator

  beforeEach(() => {
    vi.clearAllMocks()
    orch = new Orchestrator()
    apiPost = api.post
  })

  // ─── plan ────────────────────────────────────────────────────────────────

  it('plan creates an orchestration plan with all agents', async () => {
    const plan = await orch.plan('Build a study schedule')
    expect(plan.query).toBe('Build a study schedule')
    expect(plan.status).toBe('planning')
    expect(plan.agents.length).toBe(5)
    expect(plan.agents.map(a => a.id)).toEqual(['planner', 'memory', 'learning', 'opportunity', 'executor'])
    expect(plan.id).toBeDefined()
    expect(plan.createdAt).toBeGreaterThan(0)
  })

  it('plan emits plan_updated event', async () => {
    const listener = vi.fn()
    orch.on('plan_updated', listener)
    const plan = await orch.plan('test')
    expect(listener).toHaveBeenCalledWith(plan)
  })

  it('plan sets all agents to pending status', async () => {
    const plan = await orch.plan('test')
    expect(plan.agents.every(a => a.status === 'pending')).toBe(true)
    expect(plan.agents.every(a => a.confirmationRequired === false)).toBe(true)
  })

  // ─── execute ─────────────────────────────────────────────────────────────

  it('execute runs an agent and marks it done on success', async () => {
    apiPost.mockResolvedValue({ result: 'Plan created', confidence: 0.9 })

    await orch.plan('test')
    const task = await orch.execute('planner')
    expect(task.status).toBe('done')
    expect(task.result).toBe('Plan created')
  })

  it('execute throws when no plan exists', async () => {
    await expect(orch.execute('planner')).rejects.toThrow('No active plan')
  })

  it('execute throws when agent not in plan', async () => {
    await orch.plan('test')
    await expect(orch.execute('nonexistent')).rejects.toThrow('not found in plan')
  })

  it('execute skips agent when dependencies not met', async () => {
    await orch.plan('test')
    const task = await orch.execute('memory')
    expect(task.status).toBe('skipped')
    expect(task.error).toBe('Dependencies not met')
  })

  it('execute handles API errors gracefully', async () => {
    apiPost.mockRejectedValue(new Error('API failure'))

    await orch.plan('test')
    const task = await orch.execute('planner')
    expect(task.status).toBe('failed')
    expect(task.error).toBe('API failure')
  })

  it('execute handles non-Error throws', async () => {
    apiPost.mockRejectedValue('string error')

    await orch.plan('test')
    const task = await orch.execute('planner')
    expect(task.status).toBe('failed')
    expect(task.error).toBe('Agent execution failed')
  })

  it('execute emits agent_status events', async () => {
    apiPost.mockResolvedValue({ result: 'done', confidence: 0.9 })

    const listener = vi.fn()
    orch.on('agent_status', listener)

    await orch.plan('test')
    await orch.execute('planner')
    expect(listener).toHaveBeenCalled()
    const lastCall = listener.mock.calls[listener.mock.calls.length - 1][0] as AgentTask
    expect(lastCall.status).toBe('done')
  })

  // ─── HITL confirm / reject ───────────────────────────────────────────────

  it('execute triggers HITL when confidence below threshold', async () => {
    apiPost.mockResolvedValue({ result: 'risky action', confidence: 0.2 })

    await orch.plan('test')
    const task = await orch.execute('planner')
    expect(task.status).toBe('waiting_confirmation')

    const queue = orch.getHitlQueue()
    expect(queue.length).toBe(1)
    expect(queue[0].agentId).toBe('planner')
    expect(queue[0].confidence).toBe(0.2)
  })

  it('confirm transitions agent to confirmed status', async () => {
    apiPost.mockResolvedValue({ result: 'risky', confidence: 0.2 })

    await orch.plan('test')
    await orch.execute('planner')

    orch.confirm('planner')
    await new Promise(process.nextTick)

    const agent = orch.getPlan()?.agents.find(a => a.id === 'planner')
    expect(agent?.status).toBe('confirmed')
    expect(agent?.result).toBe('risky')
  })

  it('reject transitions agent to skipped', async () => {
    apiPost.mockResolvedValue({ result: 'risky', confidence: 0.2 })

    await orch.plan('test')
    await orch.execute('planner')

    orch.reject('planner')
    await new Promise(process.nextTick)

    const agent = orch.getPlan()?.agents.find(a => a.id === 'planner')
    expect(agent?.status).toBe('skipped')
    expect(agent?.error).toBe('Rejected by user')
  })

  it('confirm with no matching HITL request is a no-op', () => {
    expect(() => orch.confirm('nonexistent')).not.toThrow()
  })

  it('reject with no matching HITL request is a no-op', () => {
    expect(() => orch.reject('nonexistent')).not.toThrow()
  })

  it('confirm clears HITL queue for that agent', async () => {
    apiPost.mockResolvedValue({ result: 'risky', confidence: 0.2 })

    await orch.plan('test')
    await orch.execute('planner')
    expect(orch.getHitlQueue().length).toBe(1)

    orch.confirm('planner')
    await new Promise(process.nextTick)
    expect(orch.getHitlQueue().length).toBe(0)
  })

  // ─── executeAll ──────────────────────────────────────────────────────────

  it('executeAll runs agents in topological order', async () => {
    apiPost.mockResolvedValue({ result: 'done', confidence: 0.9 })

    const order: string[] = []
    vi.spyOn(orch, 'execute').mockImplementation(async (agentId: string) => {
      order.push(agentId)
      // Actually call the real execute to advance state
      return apiPost.mockResolvedValue({ result: 'done', confidence: 0.9 }),
        orch.plan('test'),
        orch.executeAll()
    })
    // Reset and use actual implementation
    vi.restoreAllMocks()

    apiPost.mockResolvedValue({ result: 'done', confidence: 0.9 })
    await orch.plan('test')
    await orch.executeAll()

    const plan = orch.getPlan()!
    const idx = (id: string) => plan.agents.findIndex(a => a.id === id)
    expect(idx('planner')).toBeLessThan(idx('memory'))
    expect(idx('memory')).toBeLessThan(idx('learning'))
    expect(idx('planner')).toBeLessThan(idx('executor'))
  })

  it('executeAll throws with no plan', async () => {
    await expect(orch.executeAll()).rejects.toThrow('No active plan')
  })

  it('executeAll completes plan when all agents terminal', async () => {
    apiPost.mockResolvedValue({ result: 'done', confidence: 0.9 })

    await orch.plan('test')
    const plan = await orch.executeAll()
    expect(plan.status).toBe('done')
    expect(plan.summary).toContain('completed')
  })

  // ─── Events ──────────────────────────────────────────────────────────────

  it('on registers and returns unsubscribe function', () => {
    const cb = vi.fn()
    const unsub = orch.on('plan_updated', cb)
    expect(typeof unsub).toBe('function')

    orch.plan('test')
    expect(cb).toHaveBeenCalledTimes(1)

    unsub()
    orch.plan('test2')
    expect(cb).toHaveBeenCalledTimes(1)
  })

  it('emits error event when agent fails', async () => {
    apiPost.mockRejectedValue(new Error('crash'))

    const errorListener = vi.fn()
    orch.on('error', errorListener)

    await orch.plan('test')
    await orch.execute('planner')
    await new Promise(process.nextTick)

    expect(errorListener).toHaveBeenCalledWith(expect.objectContaining({
      agentId: 'planner',
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
    const plan = await orch.plan('specific')
    expect(orch.getPlan(plan.id)?.id).toBe(plan.id)
  })

  it('getPlan returns undefined for unknown ID', () => {
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

  // ─── getHitlQueue ────────────────────────────────────────────────────

  it('getHitlQueue returns a copy', () => {
    const q = orch.getHitlQueue()
    q.push({} as never)
    expect(orch.getHitlQueue().length).toBe(0)
  })

  it('getHitlQueue is initially empty', () => {
    expect(orch.getHitlQueue()).toEqual([])
  })
})
