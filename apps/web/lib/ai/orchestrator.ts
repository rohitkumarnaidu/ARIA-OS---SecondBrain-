import { api } from '@/lib/api'

export interface AgentTask {
  id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'done' | 'failed'
  result?: string
  error?: string
}

export interface OrchestrationPlan {
  id: string
  query: string
  agents: AgentTask[]
  status: 'planning' | 'running' | 'done' | 'failed'
  summary?: string
}

type AgentDef = {
  id: string
  name: string
  description: string
  endpoint: string
}

const AGENTS: AgentDef[] = [
  { id: 'planner', name: 'Planner', description: 'Break down complex tasks', endpoint: '/api/v1/automation/plan' },
  { id: 'memory', name: 'Memory', description: 'Recall past context and preferences', endpoint: '/api/v1/memory/search' },
  { id: 'learning', name: 'Learning', description: 'Detect patterns and insights', endpoint: '/api/v1/analytics/patterns' },
  { id: 'opportunity', name: 'Opportunity Radar', description: 'Match opportunities to profile', endpoint: '/api/v1/opportunities/match' },
]

export class Orchestrator {
  private currentPlan: OrchestrationPlan | null = null

  async plan(query: string): Promise<OrchestrationPlan> {
    const plan: OrchestrationPlan = {
      id: crypto.randomUUID(),
      query,
      agents: AGENTS.map(a => ({
        id: a.id,
        name: a.name,
        description: a.description,
        status: 'pending' as const,
      })),
      status: 'planning',
    }

    this.currentPlan = plan
    return plan
  }

  async execute(agentId: string): Promise<AgentTask> {
    const plan = this.currentPlan
    if (!plan) throw new Error('No active plan')

    const task = plan.agents.find(a => a.id === agentId)
    if (!task) throw new Error(`Agent ${agentId} not found in plan`)

    const agent = AGENTS.find(a => a.id === agentId)
    if (!agent) throw new Error(`Agent ${agentId} not registered`)

    task.status = 'running'
    this.notify()

    try {
      const res = await api.post<{ result: string }>(agent.endpoint, {
        query: plan.query,
        context: { plan_id: plan.id },
      })
      task.status = 'done'
      task.result = res.result
    } catch (err) {
      task.status = 'failed'
      task.error = err instanceof Error ? err.message : 'Agent execution failed'
    }

    this.notify()
    return task
  }

  async executeAll(): Promise<OrchestrationPlan> {
    const plan = this.currentPlan
    if (!plan) throw new Error('No active plan')

    plan.status = 'running'
    await Promise.all(plan.agents.map(a => this.execute(a.id)))

    const done = plan.agents.filter(a => a.status === 'done').length
    const failed = plan.agents.filter(a => a.status === 'failed').length
    plan.status = failed > 0 && done === 0 ? 'failed' : 'done'
    plan.summary = `${done} agent${done !== 1 ? 's' : ''} completed, ${failed} failed`

    this.notify()
    return plan
  }

  getPlan(): OrchestrationPlan | null {
    return this.currentPlan
  }

  private listeners: Set<() => void> = new Set()

  subscribe(cb: () => void): () => void {
    this.listeners.add(cb)
    return () => this.listeners.delete(cb)
  }

  private notify(): void {
    this.listeners.forEach(cb => cb())
  }
}

export const orchestrator = new Orchestrator()
