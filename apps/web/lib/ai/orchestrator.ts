import { api } from '@/lib/api'

export type AgentStatus = 'pending' | 'running' | 'waiting_confirmation' | 'confirmed' | 'done' | 'failed' | 'skipped'

export interface AgentTask {
  id: string
  name: string
  description: string
  status: AgentStatus
  dependsOn: string[]
  confirmationRequired: boolean
  confidence?: number
  preview?: string
  result?: string
  error?: string
}

export interface OrchestrationPlan {
  id: string
  query: string
  agents: AgentTask[]
  status: 'planning' | 'running' | 'awaiting_input' | 'done' | 'failed'
  summary?: string
  intent?: string
  createdAt: number
  updatedAt: number
}

/** Agents with no mutation still get a threshold, so HITL stays reachable. */
const CONFIRMATION_THRESHOLD_BY_MUTATION: Record<string, number> = {
  mutating: 0.9,
  readOnly: 0,
}

export interface HitlRequest {
  planId: string
  agentId: string
  title: string
  description: string
  confidence: number
  onConfirm: () => Promise<void>
  onReject: () => void
}

export type OrchestratorEvent = 'plan_updated' | 'agent_status' | 'hitl_request' | 'error'

/**
 * Envelope every mutating endpoint in this API returns.
 *
 * The previous version of this file typed responses as `{ result, preview?,
 * confidence? }` and read `res.result` directly. No endpoint ever returned that:
 * `/automation/plan`, `/memory/search`, `/analytics/patterns`,
 * `/opportunities/match` and `/automation/execute` all return `{status, data}`.
 * Every agent task therefore completed with `result === undefined` and rendered
 * an empty card, and the confidence check that drives HITL never fired because
 * `res.confidence` was always undefined and defaulted to 0.9.
 *
 * The backend contract was not changed, because it is the convention across all
 * 31 routers and ~80 endpoints; changing it here would have meant changing every
 * route and every one of their tests. The mismatch was on this side.
 */
interface ApiEnvelope<T> {
  status?: string
  data?: T
}

/** The per-endpoint payloads, normalised to what the UI needs. */
interface RawPlanPayload {
  plan_id?: string
  intent?: string
  confidence?: number
  summary?: string
  agents?: Array<{
    id: string
    name: string
    description?: string
    status?: AgentStatus
    dependsOn?: string[]
    confirmationRequired?: boolean
    confidence?: number
    mutates?: boolean
  }>
  steps?: Array<{ action?: string; target?: string; reasoning?: string; confidence?: number }>
}

interface RawExecutePayload {
  action?: string
  summary?: string
  result?: {
    plan_id?: string
    intent?: string
    confidence?: number
    response?: string
    steps?: Array<{ agent_id?: string; status?: AgentStatus; error?: string | null }>
  }
}

interface RawMemoryPayload {
  summary?: string
  memories?: Array<{ key?: string; value?: unknown }>
}

interface RawPatternPayload {
  summary?: string
  patterns?: Array<{ type?: string; description?: string; confidence?: number }>
  insights?: Array<{ type?: string; description?: string }>
}

interface RawMatchPayload {
  summary?: string
  matches?: Array<{ id?: string; title?: string; score?: number; reasoning?: string }>
}

/** Turn any agent payload into the `{result, preview, confidence}` the UI renders. */
function normalise(payload: unknown, confidence?: number): { result: string; preview?: string; confidence?: number } {
  if (payload == null) return { result: '', confidence }

  if (typeof payload === 'string') return { result: payload, confidence }

  if (Array.isArray(payload)) {
    const lines = payload
      .map(item => (typeof item === 'string' ? item : JSON.stringify(item)))
      .filter(Boolean)
    return { result: lines.join('\n'), confidence }
  }

  if (typeof payload !== 'object') return { result: String(payload), confidence }
  const p = payload as Record<string, unknown>

  // /automation/execute: the synthesized reply, or the action summary.
  const exec = p.result as RawExecutePayload['result'] | undefined
  if (exec && typeof exec === 'object' && typeof exec.response === 'string') {
    return { result: exec.response, preview: exec.intent, confidence: exec.confidence ?? confidence }
  }

  const summary = typeof p.summary === 'string' ? p.summary : undefined

  if (Array.isArray(p.memories)) {
    const mem = p as unknown as RawMemoryPayload
    const lines = (mem.memories ?? []).map(m => `${m.key ?? 'memory'}: ${JSON.stringify(m.value ?? '')}`)
    return { result: [summary, ...lines].filter(Boolean).join('\n'), preview: summary, confidence }
  }

  if (Array.isArray(p.patterns)) {
    const pat = p as unknown as RawPatternPayload
    const lines = (pat.patterns ?? []).map(x => `${x.type ?? 'pattern'}: ${x.description ?? ''}`)
    return { result: [summary, ...lines].filter(Boolean).join('\n'), preview: summary, confidence }
  }

  if (Array.isArray(p.matches)) {
    const mat = p as unknown as RawMatchPayload
    const lines = (mat.matches ?? []).map(m => `${m.title ?? m.id ?? 'match'} (score ${m.score ?? 'n/a'})`)
    return { result: [summary, ...lines].filter(Boolean).join('\n'), preview: summary, confidence }
  }

  if (typeof p.result === 'string') {
    return { result: p.result, preview: summary, confidence }
  }

  return { result: summary ?? JSON.stringify(payload), preview: summary, confidence }
}

interface OrchestratorState {
  plans: OrchestrationPlan[]
  hitlQueue: HitlRequest[]
}

function createId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID()
  return `plan_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}

/**
 * Fallback used only when the registry endpoint is unreachable.
 *
 * The plan comes from the backend's real agent registry at
 * `POST /api/v1/automation/plan`, which classifies the query and returns the
 * agents that will actually run. This list exists so the page stays usable when
 * that call fails; it is not the source of truth, and it is intentionally one
 * read-only agent rather than the old five-agent fiction.
 */
const FALLBACK_AGENTS = [
  { id: 'A02-memory', name: 'Memory', description: 'Recall stored preferences and prior context' },
]

export class Orchestrator {
  private state: OrchestratorState = { plans: [], hitlQueue: [] }
  private listeners: Map<string, Set<(data: unknown) => void>> = new Map()
  /** confirmationThreshold per agent, learned from the backend plan. */
  private thresholds: Map<string, number> = new Map()

  on(event: OrchestratorEvent, cb: (data: unknown) => void): () => void {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set())
    this.listeners.get(event)!.add(cb)
    return () => this.listeners.get(event)?.delete(cb)
  }

  private emit(event: OrchestratorEvent, data: unknown): void {
    this.listeners.get(event)?.forEach((cb) => cb(data))
  }

  private getTopologicalOrder(agents: AgentTask[]): AgentTask[] {
    const visited = new Set<string>()
    const order: AgentTask[] = []
    const visit = (id: string) => {
      if (visited.has(id)) return
      visited.add(id)
      const agent = agents.find((a) => a.id === id)
      if (agent) {
        for (const dep of agent.dependsOn) visit(dep)
        order.push(agent)
      }
    }
    for (const agent of agents) visit(agent.id)
    return order
  }

  async plan(query: string): Promise<OrchestrationPlan> {
    const plan: OrchestrationPlan = {
      id: createId(),
      query,
      agents: [],
      status: 'planning',
      createdAt: Date.now(),
      updatedAt: Date.now(),
    }

    try {
      const res = await api.post<ApiEnvelope<RawPlanPayload>>('/api/v1/automation/plan', {
        query,
        context: {},
      })
      const data = res?.data
      const remoteAgents = data?.agents ?? []

      if (remoteAgents.length > 0 && data) {
        plan.id = data.plan_id ?? plan.id
        plan.intent = data.intent
        plan.summary = data.summary
        plan.agents = remoteAgents.map(a => ({
          id: a.id,
          name: a.name,
          description: a.description ?? '',
          status: a.status ?? 'pending',
          dependsOn: a.dependsOn ?? [],
          confirmationRequired: a.confirmationRequired ?? false,
          confidence: a.confidence,
        }))
        // A mutating agent needs human sign-off unless it is very confident;
        // a read-only one is never gated.
        for (const a of remoteAgents) {
          this.thresholds.set(
            a.id,
            a.mutates ? CONFIRMATION_THRESHOLD_BY_MUTATION.mutating : CONFIRMATION_THRESHOLD_BY_MUTATION.readOnly,
          )
        }
      } else {
        plan.agents = FALLBACK_AGENTS.map(a => ({
          id: a.id,
          name: a.name,
          description: a.description,
          status: 'pending' as AgentStatus,
          dependsOn: [],
          confirmationRequired: false,
        }))
      }
    } catch {
      // Registry unreachable. The page still renders and can still execute.
      plan.agents = FALLBACK_AGENTS.map(a => ({
        id: a.id,
        name: a.name,
        description: a.description,
        status: 'pending' as AgentStatus,
        dependsOn: [],
        confirmationRequired: false,
      }))
      plan.summary = 'Agent registry unavailable; running the minimal fallback set.'
    }

    this.state.plans.push(plan)
    this.emit('plan_updated', plan)
    return plan
  }

  async execute(agentId: string, planId?: string): Promise<AgentTask> {
    const plan = this.state.plans.find((p) => p.id === (planId || this.state.plans[this.state.plans.length - 1]?.id))
    if (!plan) throw new Error('No active plan')

    const task = plan.agents.find((a) => a.id === agentId)
    if (!task) throw new Error(`Agent ${agentId} not found in plan`)

    const depsUnmet = task.dependsOn.some((depId) => {
      const dep = plan.agents.find((a) => a.id === depId)
      return !dep || dep.status !== 'done'
    })
    if (depsUnmet) {
      task.status = 'skipped'
      task.error = 'Dependencies not met'
      this.emit('agent_status', task)
      return task
    }

    task.status = 'running'
    plan.updatedAt = Date.now()
    plan.status = 'running'
    this.emit('agent_status', task)
    this.emit('plan_updated', plan)

    try {
      const { endpoint, body } = endpointFor(agentId)
      const res = await api.post<ApiEnvelope<unknown>>(endpoint, body(plan))

      const { result, preview, confidence } = normalise(res?.data, task.confidence)

      task.confidence = confidence ?? 0.9
      task.preview = preview
      task.result = result

      // HITL only for agents the backend flagged as needing it, or whose
      // reported confidence sits below their threshold.
      const threshold = this.thresholds.get(agentId) ?? 0.0
      task.confirmationRequired = task.confirmationRequired || (task.confidence ?? 1) < threshold

      if (task.confirmationRequired) {
        task.status = 'waiting_confirmation'
        const hitl: HitlRequest = {
          planId: plan.id,
          agentId: task.id,
          title: `Confirm: ${task.name}`,
          description: task.preview || task.result || task.description,
          confidence: task.confidence ?? 0,
          onConfirm: async () => {
            task.status = 'confirmed'
            this.emit('agent_status', task)
            this.state.hitlQueue = this.state.hitlQueue.filter((h) => h.agentId !== task.id)
            await this.tryComplete(plan)
          },
          onReject: () => {
            task.status = 'skipped'
            task.error = 'Rejected by user'
            this.emit('agent_status', task)
            this.state.hitlQueue = this.state.hitlQueue.filter((h) => h.agentId !== task.id)
            this.tryComplete(plan)
          },
        }
        this.state.hitlQueue.push(hitl)
        plan.status = 'awaiting_input'
        this.emit('hitl_request', hitl)
      } else {
        task.status = 'done'
        this.emit('agent_status', task)
      }
    } catch (err) {
      task.status = 'failed'
      task.error = err instanceof Error ? err.message : 'Agent execution failed'
      this.emit('agent_status', task)
      this.emit('error', { agentId: task.id, error: task.error })
    }

    plan.updatedAt = Date.now()
    this.emit('plan_updated', plan)
    await this.tryComplete(plan)
    return task
  }

  async executeAll(planId?: string): Promise<OrchestrationPlan> {
    const plan = this.state.plans.find((p) => p.id === (planId || this.state.plans[this.state.plans.length - 1]?.id))
    if (!plan) throw new Error('No active plan')

    plan.status = 'running'
    const ordered = this.getTopologicalOrder(plan.agents)

    for (const agent of ordered) {
      if (agent.status === 'waiting_confirmation') continue
      if (agent.status === 'pending' || agent.status === 'failed') {
        await this.execute(agent.id, plan.id)
      }
    }

    await this.tryComplete(plan)
    return plan
  }

  private async tryComplete(plan: OrchestrationPlan): Promise<void> {
    if (this.state.hitlQueue.some((h) => h.planId === plan.id)) return

    const allTerminal = plan.agents.every((a) =>
      ['done', 'failed', 'skipped', 'confirmed'].includes(a.status)
    )
    if (!allTerminal) {
      // An agent the backend already flagged needs a human before anything else
      // can be called complete. Without this the plan sits in 'running' forever.
      if (plan.agents.some((a) => a.status === 'waiting_confirmation')) {
        plan.status = 'awaiting_input'
        plan.updatedAt = Date.now()
        this.emit('plan_updated', plan)
      }
      return
    }

    const done = plan.agents.filter((a) => a.status === 'done' || a.status === 'confirmed').length
    const failed = plan.agents.filter((a) => a.status === 'failed').length
    const skipped = plan.agents.filter((a) => a.status === 'skipped').length

    plan.status = failed > 0 && done === 0 ? 'failed' : 'done'
    plan.summary = `${done} completed, ${failed} failed, ${skipped} skipped`
    plan.updatedAt = Date.now()
    this.emit('plan_updated', plan)
  }

  confirm(agentId: string, planId?: string): void {
    const req = this.state.hitlQueue.find(
      (h) => h.agentId === agentId && (planId ? h.planId === planId : true)
    )
    req?.onConfirm()
  }

  reject(agentId: string, planId?: string): void {
    const req = this.state.hitlQueue.find(
      (h) => h.agentId === agentId && (planId ? h.planId === planId : true)
    )
    req?.onReject()
  }

  getPlan(planId?: string): OrchestrationPlan | undefined {
    if (planId) return this.state.plans.find((p) => p.id === planId)
    return this.state.plans[this.state.plans.length - 1]
  }

  getPlans(): OrchestrationPlan[] {
    return [...this.state.plans]
  }

  getHitlQueue(): HitlRequest[] {
    return [...this.state.hitlQueue]
  }
}

/**
 * Which endpoint serves which registry agent.
 *
 * `/automation/execute` is the orchestrator: it classifies, plans and executes
 * the agent set, and returns the synthesized reply. It replaced the four
 * per-agent endpoints the previous hardcoded list named, three of which
 * (`/memory/search`, `/analytics/patterns`, `/opportunities/match`) exist but
 * only served one agent each while the UI presented them as a collaborating
 * pipeline.
 */
function endpointFor(agentId: string): {
  endpoint: string
  body: (plan: OrchestrationPlan) => Record<string, unknown>
} {
  return {
    endpoint: '/api/v1/automation/execute',
    body: (plan: OrchestrationPlan) => ({
      query: plan.query,
      context: { plan_id: plan.id, agent_id: agentId },
    }),
  }
}

export const orchestrator = new Orchestrator()