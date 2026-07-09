'use client'

import { useState, useEffect, useCallback } from 'react'
import { useAutomationStore } from '@/lib/stores'
import type { LucideIcon } from 'lucide-react'
import {
  Zap, Target, Clock, Moon, Bell, Play, RefreshCw,
  ChevronDown, ChevronUp, Settings, Timer,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { PageHeader } from '@/components/ui/PageHeader'
import { cn } from '@/components/ui/utils'
import type { Automation, AutomationId, RunStatus } from '@/types/automation'
import { createLogger } from '@/lib/utils/logger'

const iconMap: Record<string, LucideIcon> = { Zap, Target, Clock, Moon, Bell }

const automationColors: Record<AutomationId, { head: string; tail: string; bg: string; border: string }> = {
  briefing:      { head: 'bg-accent-primary/20', tail: 'from-accent-primary/25 to-transparent', bg: 'bg-accent-primary/12', border: 'border-accent-primary/30' },
  radar:         { head: 'bg-accent-secondary/20', tail: 'from-accent-secondary/25 to-transparent', bg: 'bg-accent-secondary/12', border: 'border-accent-secondary/30' },
  weekly:        { head: 'bg-accent-warning/20', tail: 'from-accent-warning/25 to-transparent', bg: 'bg-accent-warning/12', border: 'border-accent-warning/30' },
  sleep_analysis:{ head: 'bg-accent-info/20', tail: 'from-accent-info/25 to-transparent', bg: 'bg-accent-info/12', border: 'border-accent-info/30' },
  sleep_bedtime: { head: 'bg-accent-error/20', tail: 'from-accent-error/25 to-transparent', bg: 'bg-accent-error/12', border: 'border-accent-error/30' },
  nudges:        { head: 'bg-[var(--accent-primary)]/[0.08]', tail: 'from-[var(--accent-info)]/20 to-transparent', bg: 'bg-[var(--accent-success)]/12', border: 'border-[var(--accent-success)]/30' },
}

const automationAccentVar: Record<AutomationId, string> = {
  briefing:      'var(--accent-primary)',
  radar:         'var(--accent-secondary)',
  weekly:        'var(--accent-warning)',
  sleep_analysis:'var(--accent-info)',
  sleep_bedtime: 'var(--accent-error)',
  nudges:        'var(--accent-success)',
}

function getRelativeTime(iso: string): string {
  const now = Date.now()
  const diff = now - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  const hours = Math.floor(mins / 60)
  const days = Math.floor(hours / 24)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days === 1) return 'Yesterday'
  if (days < 7) return new Date(iso).toLocaleDateString('en-US', { weekday: 'short' })
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function getStatusDotColor(status: RunStatus): string {
  switch (status) {
    case 'success': return 'bg-accent-success'
    case 'error':   return 'bg-accent-error'
    case 'running': return 'bg-accent-warning'
    default:        return 'bg-text-tertiary'
  }
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
}

type RunAction =
  | { type: 'idle' }
  | { type: 'running' }

// ─── Sub-components ──────────────────────────────────────────────────────

function TimelineView({
  automations,
  disabled,
}: {
  automations: Automation[]
  disabled: boolean
}): JSX.Element {
  const [now, setNow] = useState(new Date())

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 30000)
    return () => clearInterval(id)
  }, [])

  const hours = Array.from({ length: 24 }, (_, i) => i)
  const currentPos = ((now.getHours() * 60 + now.getMinutes()) / (24 * 60)) * 100

  const scheduled = automations.filter((a) => a.scheduleHour >= 0 && a.enabled)
  const onDemand = automations.filter((a) => a.scheduleHour < 0 && a.enabled)

  if (disabled) {
    return (
      <Card className="space-y-4">
        <div className="flex items-center gap-2 text-text-secondary">
          <Clock size={18} aria-hidden="true" />
          <h3 className="font-semibold text-text-primary">Schedule Timeline</h3>
        </div>
        <div className="flex items-center justify-center h-32 rounded-xl border border-dashed border-border">
          <p className="text-sm text-text-tertiary">All automations are disabled — enable one above to see it on the timeline</p>
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <div className="flex items-center gap-2 mb-5">
        <Timer size={18} className="text-text-secondary" aria-hidden="true" />
        <h3 className="font-semibold text-text-primary">Schedule Timeline</h3>
        <span className="ml-auto text-xs text-text-tertiary tabular-nums">
          {now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>

      <div className="relative overflow-x-auto pb-2" role="region" aria-label="24-hour automation schedule timeline">
        <div className="relative h-44 min-w-[600px]">
          {/* Hour grid lines */}
          <div className="absolute inset-0 flex">
            {hours.map((h) => (
              <div key={h} className="flex-1 border-l border-border/40 first:border-l-0 relative">
                <span className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[10px] text-text-tertiary tabular-nums">
                  {h.toString().padStart(2, '0')}
                </span>
              </div>
            ))}
          </div>

          {/* Automation blocks */}
          <div className="absolute inset-0 top-0 bottom-6">
            {scheduled.map((a) => {
              const left = ((a.scheduleHour + 1) / 24) * 100
              const color = automationAccentVar[a.id] || 'var(--accent-primary)'
              const Icon = iconMap[a.icon] || Zap
              return (
                <motion.div
                  key={a.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ scale: 1.03, zIndex: 10 }}
                  style={{
                    left: `${left}%`,
                    backgroundColor: `color-mix(in srgb, ${color} 22%, transparent)`,
                    borderColor: `color-mix(in srgb, ${color} 50%, transparent)`,
                  }}
                  className="absolute top-2 -translate-x-1/2 h-9 rounded-full border px-2.5 flex items-center gap-1.5 cursor-default select-none shadow-sm"
                  title={`${a.name} — ${a.schedule}`}
                  role="listitem"
                  aria-label={`${a.name} scheduled at ${a.schedule}`}
                >
                  <Icon size={13} style={{ color }} aria-hidden="true" />
                  <span className="text-[11px] font-medium text-text-primary truncate max-w-[80px] leading-none">
                    {a.name}
                  </span>
                </motion.div>
              )
            })}
          </div>

          {/* Current time indicator */}
          <motion.div
            aria-hidden="true"
            className="absolute top-0 bottom-6 w-px bg-accent-secondary/80 shadow-neon-sm"
            style={{ left: `${currentPos}%`, translateX: '-50%' }}
          >
            <motion.div
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              className="absolute -top-0.5 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-accent-secondary"
            />
          </motion.div>
        </div>
      </div>

      {/* On-demand items */}
      {onDemand.length > 0 && (
        <div className="mt-6 pt-4 border-t border-border">
          <p className="text-xs text-text-tertiary mb-2 font-medium uppercase tracking-wider">On-demand</p>
          <div className="flex flex-wrap gap-2">
            {onDemand.map((a) => {
              const color = automationAccentVar[a.id] || 'var(--accent-primary)'
              const Icon = iconMap[a.icon] || Zap
              return (
                <div
                  key={a.id}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border"
                  style={{
                    backgroundColor: `color-mix(in srgb, ${color} 16%, transparent)`,
                    borderColor: `color-mix(in srgb, ${color} 35%, transparent)`,
                    color,
                  }}
                  role="listitem"
                  aria-label={`${a.name} — on-demand`}
                >
                  <Icon size={12} aria-hidden="true" />
                  {a.name}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </Card>
  )
}

function AutomationCard({
  automation,
  action,
  onRun,
  onToggle,
}: {
  automation: Automation
  action: RunAction
  onRun: () => void
  onToggle: () => void
}): JSX.Element {
  const [expanded, setExpanded] = useState(false)
  const Icon = iconMap[automation.icon] || Zap
  const colors = automationColors[automation.id] || automationColors.briefing
  const colorVar = automationAccentVar[automation.id] || 'var(--accent-primary)'

  return (
    <motion.div
      layout
      className={cn(
        'rounded-xl backdrop-blur-[20px] border p-4 transition-all duration-300',
        'bg-[var(--background-card)]',
        colors.border,
      )}
    >
      {/* Header */}
      <div className="flex items-start gap-3 mb-3">
        <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center shrink-0', colors.head)}>
          <Icon size={20} style={{ color: colorVar }} aria-hidden="true" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-text-primary truncate">{automation.name}</h3>
          <p className="text-xs text-text-tertiary mt-0.5">{automation.description}</p>
        </div>
      </div>

      {/* Schedule */}
      <div className="flex items-center gap-1.5 mb-3">
        <Clock size={13} className="text-text-tertiary shrink-0" aria-hidden="true" />
        <span className="text-xs text-text-secondary">{automation.schedule}</span>
      </div>

      {/* Last-run status */}
      <div className="flex items-center gap-2 mb-3">
        {automation.lastRun ? (
          <>
            <span className={cn('w-2 h-2 rounded-full shrink-0', getStatusDotColor(automation.lastRun.status))} aria-hidden="true" />
            <span className="text-xs text-text-secondary">
              {automation.lastRun.status === 'success' ? 'Success' : 'Error'}
              {' · '}{formatDuration(automation.lastRun.duration)}
            </span>
            <span className="text-xs text-text-tertiary ml-auto">{getRelativeTime(automation.lastRun.timestamp)}</span>
          </>
        ) : (
          <span className="text-xs text-text-tertiary italic">Never run</span>
        )}
      </div>

      {/* Actions row */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {/* Run Now button */}
          <AnimatePresence mode="wait">
            {action.type === 'idle' && (
              <motion.div
                key="idle"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Button
                  variant="primary"
                  size="sm"
                  icon={<Play size={14} />}
                  onClick={onRun}
                  disabled={!automation.enabled}
                  aria-label={`Run ${automation.name}`}
                >
                  Run Now
                </Button>
              </motion.div>
            )}

            {action.type === 'running' && (
              <motion.div
                key="running"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Button
                  variant="outline"
                  size="sm"
                  loading
                  disabled
                  aria-label="Automation is running"
                >
                  Running...
                </Button>
              </motion.div>
            )}

          </AnimatePresence>
        </div>

        {/* Toggle */}
        <button
          onClick={onToggle}
          role="switch"
          aria-checked={automation.enabled}
          aria-label={`${automation.enabled ? 'Disable' : 'Enable'} ${automation.name}`}
          className={cn(
            'relative w-10 h-5 rounded-full transition-colors duration-200 shrink-0',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background-card',
            automation.enabled ? 'bg-accent-primary' : 'bg-border',
          )}
        >
          <motion.span
            animate={{ x: automation.enabled ? 20 : 2 }}
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            className="absolute top-[2.5px] w-4 h-4 bg-white rounded-full shadow-sm"
            aria-hidden="true"
          />
        </button>
      </div>

      {/* Expandable result panel */}
      {automation.lastRun && (
        <div className="mt-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-text-tertiary hover:text-text-secondary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary rounded"
            aria-expanded={expanded}
            aria-label={`Toggle last run details for ${automation.name}`}
          >
            {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            Last run details
          </button>
          <AnimatePresence>
            {expanded && (
              <motion.pre
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="mt-2 p-3 rounded-lg bg-background-elevated text-[11px] text-text-secondary overflow-x-auto font-mono leading-relaxed"
              >
{JSON.stringify(automation.lastRun, null, 2)}
              </motion.pre>
            )}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  )
}

// ─── Main page ────────────────────────────────────────────────────────────

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}

export default function AutomationPage(): JSX.Element {
  const { automations, loading, error, running, fetch, trigger, toggle } = useAutomationStore()
  const logger = createLogger('AutomationPage')
  const [mounted, setMounted] = useState(false)

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    logger.info('Fetching automations')
    fetch().catch((err: unknown) => {
      logger.error('Failed to fetch automations', { error: err instanceof Error ? err.message : String(err) })
    })
  }, [fetch])

  const getAction = useCallback(
    (id: AutomationId): RunAction => {
      if (running === id) return { type: 'running' }
      return { type: 'idle' }
    },
    [running],
  )

  const handleTrigger = useCallback((id: AutomationId) => {
    logger.info('Triggering automation', { id })
    trigger(id)
  }, [trigger])

  const handleToggle = useCallback((id: AutomationId) => {
    const enabled = automations.find(a => a.id === id)?.enabled
    logger.info('Toggling automation', { id, enabled: !enabled })
    toggle(id)
  }, [toggle, automations])

  const data = automations
  const allDisabled = data.every((a) => !a.enabled)
  const hasAny = data.length > 0

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" role="status" aria-label="Loading">
        <motion.div
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="w-12 h-12 rounded-full border-4 border-accent-primary border-t-transparent"
        />
        <span className="sr-only">Loading automation center…</span>
      </div>
    )
  }

  if (!hasAny) {
    return (
      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-6">
        <PageHeader title="Automation Center" description="Manage your AI agent schedule" />
        <motion.div variants={itemVariants}>
          <Card className="flex flex-col items-center justify-center py-16 gap-4 text-center">
            <Zap size={40} className="text-text-tertiary" aria-hidden="true" />
            <div>
              <h2 className="text-lg font-semibold text-text-primary">No automations configured</h2>
              <p className="text-sm text-text-tertiary mt-1">Get started by enabling your first automation</p>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    )
  }

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-6">
      {error && (
        <motion.div variants={itemVariants}>
          <div className="bg-accent-danger/10 border border-accent-danger/30 text-text-primary px-4 py-3 rounded-lg">
            {error}
          </div>
        </motion.div>
      )}

      {/* Page header */}
      <motion.div variants={itemVariants}>
        <PageHeader title="Automation Center" description="Manage your AI agent schedule" />
      </motion.div>

      {/* Section 1: Schedule Visualization */}
      <motion.div variants={itemVariants}>
        <TimelineView automations={data} disabled={allDisabled} />
      </motion.div>

      {/* Section 2: Automation Grid */}
      <motion.div variants={itemVariants}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <AnimatePresence mode="popLayout">
            {data.map((a) => (
              <motion.div
                key={a.id}
                layout
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.96 }}
              >
                <AutomationCard
                  automation={a}
                  action={getAction(a.id)}
                  onRun={() => handleTrigger(a.id)}
                  onToggle={() => handleToggle(a.id)}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Section 3: Automation Settings */}
      <motion.div variants={itemVariants}>
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <Settings size={18} className="text-text-secondary" aria-hidden="true" />
            <h3 className="font-semibold text-text-primary">Automation Settings</h3>
          </div>
          <div className="space-y-1">
            {data.map((a, idx) => {
              const Icon = iconMap[a.icon] || Zap
              const colorVar = automationAccentVar[a.id] || 'var(--accent-primary)'
              return (
                <motion.div
                  key={a.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-background-elevated/50 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                      style={{ backgroundColor: `color-mix(in srgb, ${colorVar} 15%, transparent)` }}
                    >
                      <Icon size={15} style={{ color: colorVar }} aria-hidden="true" />
                    </div>
                    <div className="min-w-0">
                      <span className="text-sm font-medium text-text-primary">{a.name}</span>
                      <p className="text-[11px] text-text-tertiary truncate">{a.schedule}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span
                      className={cn(
                        'w-1.5 h-1.5 rounded-full',
                        a.enabled ? 'bg-accent-success' : 'bg-text-tertiary',
                      )}
                      aria-hidden="true"
                    />
                    <button
                      onClick={() => handleToggle(a.id)}
                      role="switch"
                      aria-checked={a.enabled}
                      aria-label={`${a.enabled ? 'Disable' : 'Enable'} ${a.name} in settings`}
                      className={cn(
                        'relative w-10 h-5 rounded-full transition-colors duration-200',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background-card',
                        a.enabled ? 'bg-accent-primary' : 'bg-border',
                      )}
                    >
                      <motion.span
                        animate={{ x: a.enabled ? 20 : 2 }}
                        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                        className="absolute top-[2.5px] w-4 h-4 bg-white rounded-full shadow-sm"
                        aria-hidden="true"
                      />
                    </button>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}
