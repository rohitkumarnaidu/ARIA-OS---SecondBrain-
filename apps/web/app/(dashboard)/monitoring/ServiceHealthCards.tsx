'use client'

import { memo } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/components/ui/utils'

interface ServiceHealth {
  status: 'ok' | 'degraded' | 'unavailable' | 'not_configured'
  uptime: number
  last_checked: string
  latency_ms: number
}

interface ServiceHealthCardsProps {
  services: Record<string, ServiceHealth>
  loading?: boolean
}

const SERVICE_LABELS: Record<string, string> = {
  api: 'API Server',
  supabase: 'Database (Supabase)',
  ai: 'AI (Ollama/Claude)',
  scheduler: 'Scheduler',
}

const STATUS_CONFIG = {
  ok: { badge: 'success' as const, label: 'UP', border: 'border-l-accent-success' },
  degraded: { badge: 'warning' as const, label: 'DEGRADED', border: 'border-l-accent-warning' },
  unavailable: { badge: 'error' as const, label: 'DOWN', border: 'border-l-accent-error' },
  not_configured: { badge: 'outline' as const, label: 'N/A', border: 'border-l-border-default' },
}

function formatLastChecked(iso: string): string {
  try {
    const diff = Date.now() - new Date(iso).getTime()
    const secs = Math.floor(diff / 1000)
    if (secs < 60) return `${secs}s ago`
    const mins = Math.floor(secs / 60)
    if (mins < 60) return `${mins}m ago`
    return `${Math.floor(mins / 60)}h ago`
  } catch {
    return 'unknown'
  }
}

const HealthCard = memo(function HealthCard({
  name,
  health,
  index,
}: {
  name: string
  health: ServiceHealth
  index: number
}) {
  const cfg = STATUS_CONFIG[health.status] || STATUS_CONFIG.unavailable

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 + index * 0.06 }}
    >
      <Card
        className={cn(
          'border-l-4 transition-all duration-300',
          cfg.border,
          'hover:shadow-glow-sm',
        )}
      >
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-text-primary">{SERVICE_LABELS[name] || name}</span>
          <Badge variant={cfg.badge}>{cfg.label}</Badge>
        </div>
        <div className="grid grid-cols-3 gap-3 text-xs">
          <div>
            <p className="text-text-tertiary uppercase tracking-wider mb-0.5">Uptime</p>
            <p className="text-text-primary font-mono font-medium">{health.uptime}%</p>
          </div>
          <div>
            <p className="text-text-tertiary uppercase tracking-wider mb-0.5">Latency</p>
            <p className="text-text-primary font-mono font-medium">
              {health.latency_ms > 0 ? `${health.latency_ms}ms` : '-'}
            </p>
          </div>
          <div>
            <p className="text-text-tertiary uppercase tracking-wider mb-0.5">Checked</p>
            <p className="text-text-primary font-mono font-medium">{formatLastChecked(health.last_checked)}</p>
          </div>
        </div>
      </Card>
    </motion.div>
  )
})

export function ServiceHealthCards({ services, loading }: ServiceHealthCardsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="p-4 border-l-4 border-l-border-default">
            <Skeleton variant="text" className="w-28 h-4 mb-3" />
            <div className="grid grid-cols-3 gap-3">
              <Skeleton variant="text" className="h-8" />
              <Skeleton variant="text" className="h-8" />
              <Skeleton variant="text" className="h-8" />
            </div>
          </Card>
        ))}
      </div>
    )
  }

  const entries = Object.entries(services)
  if (entries.length === 0) {
    return (
      <Card className="p-6 text-center">
        <p className="text-text-secondary text-sm">Service health data unavailable.</p>
      </Card>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {entries.map(([name, health], i) => (
        <HealthCard key={name} name={name} health={health} index={i} />
      ))}
    </div>
  )
}
