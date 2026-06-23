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
  createdAt: number
  updatedAt: number
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

type AgentDef = {
  id: string
  name: string
  description: string
  endpoint: string
  dependsOn: string[]
  confirmationThreshold: number
}

const AGENTS: AgentDef[] = [
  { id: 'planner', name: 'Planner', description: 'Break down complex tasks', endpoint: '/api/v1/automation/plan', dependsOn: [], confirmationThreshold: 0.3 },
  { id: 'memory', name: 'Memory', description: 'Recall past context and preferences', endpoint: '/api/v1/memory/search', dependsOn: ['planner'], confirmationThreshold: 0.2 },
  { id: 'learning', name: 'Learning', description: 'Detect patterns and insights', endpoint: '/api/v1/analytics/patterns', dependsOn: ['memory'], confirmationThreshold: 0.2 },
  { id: 'opportunity', name: 'Opportunity Radar', description: 'Match opportunities to profile', endpoint: '/api/v1/opportunities/match', dependsOn: ['memory'], confirmationThreshold: 0.4 },
  { id: 'executor', name: 'Executor', description: 'Create tasks, update records', endpoint: '/api/v1/automation/execute', dependsOn: ['planner', 'memory'], confirmationThreshold: 0.6 },
]

interface OrchestratorState {
  plans: OrchestrationPlan[]
  hitlQueue: HitlRequest[]
}

function createId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID()
  return `plan_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}

export class Orchestrator {
  private state: OrchestratorState = { plans: [], hitlQueue: [] }
  private listeners: Map<string, Set<(data: unknown) => void>> = new Map()

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
      agents: AGENTS.map((a) => ({
        id: a.id,
        name: a.name,
        description: a.description,
        status: 'pending' as AgentStatus,
        dependsOn: a.dependsOn,
        confirmationRequired: false,
      })),
      status: 'planning',
      createdAt: Date.now(),
      updatedAt: Date.now(),
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

    const agentDef = AGENTS.find((a) => a.id === agentId)
    if (!agentDef) throw new Error(`Agent ${agentId} not registered`)

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
      const res = await api.post<{ result: string; preview?: string; confidence?: number }>(agentDef.endpoint, {
        query: plan.query,
        context: { plan_id: plan.id },
      })

      task.confidence = res.confidence ?? 0.9
      task.preview = res.preview
      task.confirmationRequired = (task.confidence ?? 1) < agentDef.confirmationThreshold

      if (task.confirmationRequired) {
        task.status = 'waiting_confirmation'
        const hitl: HitlRequest = {
          planId: plan.id,
          agentId: task.id,
          title: `Confirm: ${task.name}`,
          description: res.preview || res.result || task.description,
          confidence: task.confidence ?? 0,
          onConfirm: async () => {
            task.status = 'confirmed'
            task.result = res.result
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
        task.result = res.result
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
      ['done', 'failed', 'skipped'].includes(a.status)
    )
    if (!allTerminal) return

    const done = plan.agents.filter((a) => a.status === 'done').length
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

export const orchestrator = new Orchestrator()
