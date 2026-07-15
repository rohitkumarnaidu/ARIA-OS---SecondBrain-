'use client'

import { useState, useMemo, memo } from 'react'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/components/ui/utils'

interface AgentMetric {
  name: string
  calls: number
  tokens: number
  avg_duration_ms: number
  error_rate: number
  cost_usd: number
}

interface AgentBreakdownTableProps {
  agents: AgentMetric[]
  loading?: boolean
}

type SortKey = keyof AgentMetric
type SortDir = 'asc' | 'desc'

const PAGE_SIZE = 10

const AGENT_LABELS: Record<string, string> = {
  briefing: 'Daily Briefing',
  weekly_review: 'Weekly Review',
  opportunity: 'Opportunity Radar',
  opportunity_matching: 'Opportunity Matching',
  memory: 'Memory Agent',
  learning: 'Learning Agent',
  task: 'Task Agent',
  sleep: 'Sleep Agent',
  nudge: 'Nudge Agent',
  roadmap: 'Roadmap Agent',
}

function formatAgentName(raw: string): string {
  return AGENT_LABELS[raw] || raw.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function getDurationColor(ms: number): string {
  if (ms < 1000) return ''
  if (ms < 10000) return 'bg-accent-warning/10 text-accent-warning'
  return 'bg-accent-error/10 text-accent-error'
}

function getErrorRateColor(rate: number): string {
  if (rate === 0) return ''
  if (rate < 5) return 'bg-accent-warning/10 text-accent-warning'
  return 'bg-accent-error/10 text-accent-error'
}

const SortIcon = memo(function SortIcon({ sortKey, currentKey, direction }: { sortKey: SortKey; currentKey: SortKey; direction: SortDir }) {
  if (sortKey !== currentKey) return <ArrowUpDown size={12} className="opacity-40" />
  return direction === 'asc' ? <ArrowUp size={12} /> : <ArrowDown size={12} />
})

export function AgentBreakdownTable({ agents, loading }: AgentBreakdownTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>('calls')
  const [sortDir, setSortDir] = useState<SortDir>('desc')
  const [page, setPage] = useState(0)

  const sorted = useMemo(() => {
    const copy = [...agents]
    copy.sort((a, b) => {
      const aVal = a[sortKey]
      const bVal = b[sortKey]
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
      }
      return sortDir === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number)
    })
    return copy
  }, [agents, sortKey, sortDir])

  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE))
  const paged = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  const handleSort = (key: SortKey) => {
    if (key === sortKey) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  const columns: { key: SortKey; label: string }[] = [
    { key: 'name', label: 'Agent' },
    { key: 'calls', label: 'Calls' },
    { key: 'tokens', label: 'Tokens' },
    { key: 'avg_duration_ms', label: 'Avg Duration' },
    { key: 'error_rate', label: 'Error Rate' },
    { key: 'cost_usd', label: 'Cost' },
  ]

  if (loading) {
    return (
      <Card className="p-4">
        <Skeleton variant="text" className="w-40 h-5 mb-4" />
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} variant="table-row" className="mb-2" />
        ))}
      </Card>
    )
  }

  if (agents.length === 0) {
    return (
      <Card className="p-6 text-center">
        <p className="text-text-secondary text-sm">Not enough data yet. Continue using the system.</p>
      </Card>
    )
  }

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
      <Card className="p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border-default">
                {columns.map((col) => (
                  <th
                    key={col.key}
                    onClick={() => handleSort(col.key)}
                    className={cn(
                      'px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer select-none hover:text-text-primary transition-colors',
                      sortKey === col.key && 'text-accent-primary',
                    )}
                  >
                    <div className="flex items-center gap-1">
                      {col.label}
                      <SortIcon sortKey={col.key} currentKey={sortKey} direction={sortDir} />
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paged.map((agent, i) => (
                <motion.tr
                  key={agent.name}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="border-b border-border-default last:border-0 hover:bg-background-elevated/50 transition-colors"
                >
                  <td className="px-4 py-3 font-medium text-text-primary whitespace-nowrap">
                    {formatAgentName(agent.name)}
                  </td>
                  <td className="px-4 py-3 text-text-secondary font-mono">{agent.calls}</td>
                  <td className="px-4 py-3 text-text-secondary font-mono">{agent.tokens.toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <span className={cn('font-mono', getDurationColor(agent.avg_duration_ms) || 'text-text-secondary')}>
                      {agent.avg_duration_ms}ms
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Badge
                      variant={
                        agent.error_rate === 0 ? 'success' : agent.error_rate < 5 ? 'warning' : 'error'
                      }
                      className="font-mono"
                    >
                      {agent.error_rate}%
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-text-secondary font-mono">
                    ${agent.cost_usd.toFixed(4)}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-border-default">
            <span className="text-xs text-text-secondary">
              Page {page + 1} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="px-3 py-1 text-xs rounded-md bg-background-elevated text-text-secondary hover:text-text-primary disabled:opacity-40 transition-colors"
              >
                Prev
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="px-3 py-1 text-xs rounded-md bg-background-elevated text-text-secondary hover:text-text-primary disabled:opacity-40 transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </Card>
    </motion.div>
  )
}
