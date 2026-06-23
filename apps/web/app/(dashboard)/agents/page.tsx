'use client'

import { useState, useEffect, useCallback } from 'react'
import { orchestrator, type OrchestrationPlan } from '@/lib/ai/orchestrator'
import {
  Bot, Loader2, CheckCircle2, XCircle, Clock, Play, Cpu,
  HelpCircle, UserCheck, SkipForward,
} from 'lucide-react'
import { motion } from 'framer-motion'

const STATUS_CONFIG: Record<string, { icon: typeof Clock; color: string; bg: string }> = {
  pending: { icon: Clock, color: 'text-text-tertiary', bg: 'bg-background-elevated' },
  running: { icon: Loader2, color: 'text-accent-primary', bg: 'bg-accent-primary/5' },
  waiting_confirmation: { icon: HelpCircle, color: 'text-accent-warning', bg: 'bg-accent-warning/5' },
  confirmed: { icon: UserCheck, color: 'text-accent-primary', bg: 'bg-accent-primary/5' },
  done: { icon: CheckCircle2, color: 'text-accent-success', bg: 'bg-accent-success/5' },
  failed: { icon: XCircle, color: 'text-accent-error', bg: 'bg-accent-error/5' },
  skipped: { icon: SkipForward, color: 'text-text-tertiary', bg: 'bg-background-elevated' },
}

const EXAMPLE_QUERIES = [
  'What should I focus on today based on my habits and tasks?',
  'Find opportunities matching my ML coursework',
  'Analyze my productivity patterns this month',
]

const STATUS_LABELS: Record<string, string> = {
  planning: 'Planning',
  running: 'Running',
  awaiting_input: 'Awaiting Input',
  done: 'Completed',
  failed: 'Failed',
}

export default function AgentsPage() {
  const [plan, setPlan] = useState<OrchestrationPlan | null>(orchestrator.getPlan() ?? null)
  const [query, setQuery] = useState('')
  const [running, setRunning] = useState(false)

  useEffect(() => {
    const unsub = orchestrator.on('plan_updated', () => {
      setPlan(orchestrator.getPlan() ?? null)
    })
    return unsub
  }, [])

  const handleRun = useCallback(async () => {
    if (!query.trim() || running) return
    setRunning(true)
    try {
      const newPlan = await orchestrator.plan(query.trim())
      setPlan(newPlan)
      await orchestrator.executeAll()
    } catch {
      // handled by orchestrator
    } finally {
      setRunning(false)
    }
  }, [query, running])

  return (
    <div className="space-y-6 pb-8">
      <div>
        <h1 className="text-2xl font-display font-bold text-text-primary">Agent Collaboration</h1>
        <p className="text-sm text-text-tertiary">Multi-agent orchestration dashboard</p>
      </div>

      {/* Input */}
      <div className="rounded-xl border border-border-default bg-background-card p-5">
        <div className="flex items-center gap-3">
          <Bot size={20} className="text-accent-primary shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRun()}
            placeholder="Ask multiple agents to collaborate on a task..."
            disabled={running}
            className="flex-1 bg-transparent border-none outline-none text-sm text-text-primary placeholder:text-text-tertiary"
          />
          <button
            onClick={handleRun}
            disabled={!query.trim() || running}
            className="btn btn-primary btn-sm gap-1.5"
          >
            {running ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
            {running ? 'Running...' : 'Run'}
          </button>
        </div>
        <div className="flex gap-2 mt-3">
          {EXAMPLE_QUERIES.map(q => (
            <button
              key={q}
              onClick={() => setQuery(q)}
              className="text-[11px] text-text-tertiary hover:text-text-primary bg-background-elevated px-2 py-1 rounded-md transition-colors"
            >
              {q.length > 40 ? q.slice(0, 40) + '...' : q}
            </button>
          ))}
        </div>
      </div>

      {/* Plan Status */}
      {plan && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Summary */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <Cpu size={16} className="text-accent-primary" />
              Plan: <span className="text-text-primary font-medium">{plan.query.slice(0, 60)}</span>
            </div>
            <span className={`text-xs font-mono px-2 py-0.5 rounded-full ${
              plan.status === 'done' ? 'bg-accent-success/10 text-accent-success' :
              plan.status === 'failed' ? 'bg-accent-error/10 text-accent-error' :
              plan.status === 'running' ? 'bg-accent-primary/10 text-accent-primary' :
              'bg-background-elevated text-text-tertiary'
            }`}>
              {STATUS_LABELS[plan.status] || plan.status}
            </span>
          </div>

          {/* Agent Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {plan.agents.map((agent, i) => {
              const cfg = STATUS_CONFIG[agent.status]
              const Icon = cfg.icon
              return (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className={`rounded-xl border border-border-default p-4 ${cfg.bg} transition-colors`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Bot size={16} className={cfg.color} />
                      <span className="text-sm font-medium text-text-primary">{agent.name}</span>
                    </div>
                    <Icon size={14} className={`${cfg.color} ${agent.status === 'running' ? 'animate-spin' : ''}`} />
                  </div>
                  <p className="text-xs text-text-tertiary mb-2">{agent.description}</p>
                  {agent.result && (
                    <p className="text-xs text-text-secondary bg-background-card rounded p-2 mt-2 line-clamp-2">{agent.result}</p>
                  )}
                  {agent.error && (
                    <p className="text-xs text-accent-error bg-accent-error/5 rounded p-2 mt-2">{agent.error}</p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                      agent.status === 'done' ? 'bg-accent-success/10 text-accent-success' :
                      agent.status === 'failed' ? 'bg-accent-error/10 text-accent-error' :
                      agent.status === 'running' ? 'bg-accent-primary/10 text-accent-primary' :
                      'bg-background-elevated text-text-tertiary'
                    }`}>
                      {agent.status}
                    </span>
                  </div>
                </motion.div>
              )
            })}
          </div>

          {/* Summary */}
          {plan.summary && (
            <div className="rounded-xl border border-border-default bg-background-card p-4">
              <p className="text-sm text-text-primary">{plan.summary}</p>
            </div>
          )}
        </motion.div>
      )}

      {/* Empty state */}
      {!plan && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Bot size={40} className="text-text-tertiary mb-4" aria-hidden="true" />
          <p className="text-sm text-text-tertiary">Ask the agents to collaborate on a task</p>
          <p className="text-xs text-text-tertiary mt-1">Type a query above and press Run to start orchestration</p>
        </div>
      )}
    </div>
  )
}
