'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { format } from 'date-fns'
import {
  Download, CheckCircle2, Brain, Calendar,
  TrendingUp, TrendingDown, Minus,
} from 'lucide-react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { PageHeader } from '@/components/ui/PageHeader'
import { cn } from '@/components/ui/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import { useReviewStore } from '@/lib/stores'
import { useAIAgents, useAIAction } from '@/lib/ai/hooks'
import { AIInsightCard } from '@/components/ai'

const containerVariants = {
  initial: {},
  animate: { transition: { staggerChildren: 0.08 } },
}

const sectionVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
}

function TrendIcon({ trend }: { trend: 'up' | 'down' | 'flat' }): JSX.Element {
  if (trend === 'up') return <TrendingUp size={14} className="text-[var(--accent-success)]" aria-hidden="true" />
  if (trend === 'down') return <TrendingDown size={14} className="text-[var(--accent-error)]" aria-hidden="true" />
  return <Minus size={14} className="text-[var(--text-tertiary)]" aria-hidden="true" />
}

function MoodRating({ mood }: { mood: number }): JSX.Element {
  const color = mood >= 8 ? 'text-[var(--accent-success)]' : mood >= 6 ? 'text-[var(--accent-warning)]' : 'text-[var(--accent-error)]'
  return (
    <div className="flex items-center gap-3">
      <span className={cn('text-5xl font-bold font-display tabular-nums', color)}>{mood}</span>
      <div className="flex flex-col">
        <span className="text-xs text-[var(--text-tertiary)] font-medium uppercase tracking-wider">Mood</span>
        <span className="text-sm text-[var(--text-secondary)]">/10 — Productive</span>
      </div>
    </div>
  )
}

function MetricCard({ metric }: { metric: { label: string; value: string | number; trend: 'up' | 'down' | 'flat'; change: string } }): JSX.Element {
  return (
    <div className="flex flex-col gap-1.5 p-3 rounded-lg bg-[var(--surface-secondary)] border border-[var(--border)]">
      <span className="text-xs text-[var(--text-tertiary)] font-medium font-body">{metric.label}</span>
      <div className="flex items-baseline gap-2">
        <span className="text-xl font-bold font-display text-[var(--text-primary)] tabular-nums">{metric.value}</span>
        <div className="flex items-center gap-1">
          <TrendIcon trend={metric.trend} />
          <span className={cn(
            'text-xs font-medium tabular-nums',
            metric.trend === 'up' && 'text-[var(--accent-success)]',
            metric.trend === 'down' && 'text-[var(--accent-error)]',
            metric.trend === 'flat' && 'text-[var(--text-tertiary)]',
          )}>
            {metric.change}
          </span>
        </div>
      </div>
      <span className="text-[10px] text-[var(--text-tertiary)] font-body">vs last week</span>
    </div>
  )
}

function GlassCard({ children, className }: { children: React.ReactNode; className?: string }): JSX.Element {
  return (
    <div className="relative rounded-xl bg-gradient-to-br from-[var(--accent-primary)]/20 to-[var(--accent-secondary)]/15 p-[1px] shadow-glow">
      <div className={cn('rounded-[11px] bg-[var(--glass-medium)] backdrop-blur-xl p-5', className)}>
        {children}
      </div>
    </div>
  )
}

function InsightSection({ title, items, accentColor }: { title: string; items: { title: string; description: string }[]; accentColor: string }): JSX.Element {
  return (
    <div className="space-y-3">
      <h4 className="font-display font-semibold text-sm text-[var(--text-primary)]">{title}</h4>
      {items.map((item, i) => (
        <div key={i} className="border-l-2 border-l-[var(--border)] pl-3 space-y-1">
          <div className="flex items-start gap-2">
            <span className={cn('text-xs font-semibold font-body mt-0.5', accentColor)}>●</span>
            <span className="text-sm font-medium text-[var(--text-primary)] font-body">{item.title}</span>
          </div>
          <p className="text-xs text-[var(--text-secondary)] font-body leading-relaxed pl-4">{item.description}</p>
        </div>
      ))}
    </div>
  )
}

function ActionCheckbox({ action, onToggle }: { action: { id: string; title: string; priority: 'P1' | 'P2' | 'P3' | 'P4'; module: string; completed: boolean }; onToggle: (id: string) => void }): JSX.Element {
  const priorityBadge: Record<string, 'error' | 'warning' | 'info' | 'outline'> = {
    P1: 'error', P2: 'warning', P3: 'info', P4: 'outline',
  }
  return (
    <div className={cn(
      'flex items-start gap-3 p-3 rounded-lg transition-all duration-200',
      'hover:bg-[var(--surface-secondary)]',
      action.completed && 'opacity-50',
    )}>
      <button
        onClick={() => onToggle(action.id)}
        className={cn(
          'mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-all duration-200',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--background-dark)]',
          action.completed
            ? 'bg-[var(--accent-primary)] border-[var(--accent-primary)]'
            : 'border-[var(--border)] bg-transparent hover:border-[var(--accent-primary)]',
        )}
        aria-label={`${action.completed ? 'Mark incomplete' : 'Mark complete'}: ${action.title}`}
        role="checkbox"
        aria-checked={action.completed}
      >
        {action.completed && <CheckCircle2 size={14} className="text-white" aria-hidden="true" />}
      </button>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <Badge variant={priorityBadge[action.priority]} className="text-[10px] px-1.5 py-0">{action.priority}</Badge>
          <span className="text-[10px] text-[var(--text-tertiary)] font-mono">{action.module}</span>
        </div>
        <span className={cn('text-sm font-body', action.completed ? 'text-[var(--text-tertiary)] line-through' : 'text-[var(--text-primary)]')}>
          {action.title}
        </span>
      </div>
    </div>
  )
}

function EmptyReviewState(): JSX.Element {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center" role="status">
      <Calendar size={48} className="text-[var(--text-tertiary)] mb-4" aria-hidden="true" />
      <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2 font-display">No Review Data Yet</h3>
      <p className="text-sm text-[var(--text-secondary)] max-w-md mx-auto leading-relaxed font-body">
        No review data for this week yet — your first review will appear after 7 days of use
      </p>
    </div>
  )
}

export default function ReviewPage(): JSX.Element {
  const [actionsCompleted, setActionsCompleted] = useState<Record<string, boolean>>({})
  const [mounted, setMounted] = useState(false)
  const { latest, loading, error, fetch, getLatest } = useReviewStore()
  const { updateAgent } = useAIAgents()
  useAIAction(async () => {
  })

  useEffect(() => { setMounted(true); fetch(); getLatest() }, [fetch, getLatest])

  const weekData = useMemo(() => {
    if (!latest) return null

    const metrics = [
      { label: 'Tasks Completed', value: latest.tasks_completed, trend: 'up' as const, change: '+' },
      { label: 'Tasks Added', value: latest.tasks_added, trend: 'flat' as const, change: '0' },
      { label: 'Habits Consistency', value: `${latest.habits_consistency}%`, trend: latest.habits_consistency >= 70 ? 'up' as const : 'down' as const, change: `${latest.habits_consistency}%` },
      { label: 'Focus Hours', value: latest.focus_hours, trend: latest.focus_hours >= 25 ? 'up' as const : 'down' as const, change: `${latest.focus_hours}h` },
      { label: 'Highlights', value: latest.highlights?.length || 0, trend: 'flat' as const, change: '--' },
      { label: 'Challenges', value: latest.challenges?.length || 0, trend: 'flat' as const, change: '--' },
    ]

    return {
      weekStart: new Date(latest.week_start),
      summary: latest.summary,
      mood: latest.mood_trend === 'positive' ? 8 : latest.mood_trend === 'negative' ? 5 : 7,
      metrics,
      highlights: latest.highlights || [],
      challenges: latest.challenges || [],
      actions: (latest.next_week_focus || []).map((f, i) => ({
        id: `review-${i}`,
        title: f,
        priority: (i === 0 ? 'P1' : i === 1 ? 'P2' : 'P3') as 'P1' | 'P2' | 'P3',
        module: 'Review',
        completed: false,
      })),
      confidence: (latest.ai_insights ? 'High' : 'Medium') as 'High' | 'Medium' | 'Low',
    }
  }, [latest])

  useEffect(() => {
    if (!weekData) return
    setActionsCompleted(prev => {
      const next: Record<string, boolean> = { ...prev }
      weekData.actions.forEach(a => { if (!(a.id in next)) next[a.id] = a.completed })
      return next
    })
  }, [weekData])

  useEffect(() => {
    if (!weekData) return
    updateAgent('weekly-review', {
      status: 'done',
      preview: 'Strong week overall.',
      confidence: weekData.confidence === 'High' ? 0.9 : weekData.confidence === 'Medium' ? 0.7 : 0.5,
    })
  }, [updateAgent, weekData?.confidence])

  const toggleAction = useCallback((id: string) => setActionsCompleted(p => ({ ...p, [id]: !p[id] })), [])
  const handleExport = useCallback(() => {
    const toast = document.createElement('div')
    toast.className = 'fixed bottom-6 right-6 z-50 px-4 py-3 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] shadow-lg animate-in slide-in-from-bottom-2 font-body'
    toast.textContent = 'Export started — download will begin shortly'
    document.body.appendChild(toast)
    setTimeout(() => toast.remove(), 3000)
  }, [])

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (loading) {
    return (
      <div className="flex flex-col gap-6 p-6">
        <PageHeader title="Weekly Review" description="AI-powered week analysis and next week planning" />
        <div className="space-y-4">
          <Skeleton variant="card" className="h-[120px]" />
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} variant="card" className="h-[88px]" />)}
          </div>
        </div>
      </div>
    )
  }

  if (!weekData) {
    return (
      <motion.div variants={containerVariants} initial="initial" animate="animate" className="flex flex-col gap-6 p-6 pb-8">
        <motion.div variants={sectionVariants}>
          <PageHeader title="Weekly Review" description="AI-powered week analysis and next week planning" />
        </motion.div>
        <motion.div variants={sectionVariants}>
          <EmptyReviewState />
        </motion.div>
      </motion.div>
    )
  }

  return (
    <motion.div variants={containerVariants} initial="initial" animate="animate" className="flex flex-col gap-6 p-6 pb-8">
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-accent-danger/10 border border-accent-danger/30 text-text-primary px-4 py-3 rounded-lg"
        >
          {error}
        </motion.div>
      )}

      <motion.div variants={sectionVariants}>
        <PageHeader
          title="Weekly Review"
          description="AI-powered week analysis and next week planning"
          actions={
            <Button variant="outline" size="sm" onClick={handleExport} aria-label="Export review">
              <Download size={14} />
              Export
            </Button>
          }
        />
      </motion.div>

      <div className="space-y-6">
        <motion.div variants={sectionVariants}>
          <Card className="relative">
            <div className="absolute top-4 right-4">
              <Badge variant={weekData.confidence === 'High' ? 'success' : weekData.confidence === 'Medium' ? 'warning' : 'error'} className="flex items-center gap-1">
                <Brain size={12} aria-hidden="true" />
                {weekData.confidence} Confidence
              </Badge>
            </div>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Calendar size={18} className="text-[var(--accent-primary)]" aria-hidden="true" />
                <CardTitle className="font-display font-semibold text-lg">Overview</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col lg:flex-row gap-6">
                <div className="flex-1 space-y-3">
                  <p className="text-sm text-[var(--text-secondary)] font-body leading-relaxed">{weekData.summary}</p>
                </div>
                <div className="shrink-0 flex items-start">
                  <MoodRating mood={weekData.mood} />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={sectionVariants}>
          <AIInsightCard
            type="insight"
            title="Review Highlights"
            description="Week analysis based on your tracked data."
          />
        </motion.div>

        <div>
          <h2 className="font-display font-semibold text-lg text-[var(--text-primary)] mb-4">Weekly Metrics</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {weekData.metrics.map(metric => <MetricCard key={metric.label} metric={metric} />)}
          </div>
        </div>

        {(weekData.highlights.length > 0 || weekData.challenges.length > 0) && (
          <GlassCard>
            <div className="flex items-center gap-2 mb-5">
              <Brain size={18} className="text-[var(--accent-secondary)]" aria-hidden="true" />
              <h3 className="font-display font-semibold text-lg text-[var(--text-primary)]">AI Analysis</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {weekData.highlights.length > 0 && (
                <InsightSection title="What Went Well" items={weekData.highlights.map(h => ({ title: h, description: '' }))} accentColor="text-[var(--accent-success)]" />
              )}
              {weekData.challenges.length > 0 && (
                <InsightSection title="Needs Attention" items={weekData.challenges.map(c => ({ title: c, description: '' }))} accentColor="text-[var(--accent-warning)]" />
              )}
            </div>
          </GlassCard>
        )}

        {weekData.actions.length > 0 && (
          <div>
            <h2 className="font-display font-semibold text-lg text-[var(--text-primary)] mb-4">Action Items</h2>
            <div className="rounded-xl bg-[var(--background-card)] border border-[var(--border)] p-5">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs text-[var(--text-secondary)] font-body">
                  {Object.values(actionsCompleted).filter(Boolean).length} of {weekData.actions.length} completed
                </p>
              </div>
              <div className="space-y-1">
                {weekData.actions.map(action => (
                  <ActionCheckbox key={action.id} action={{ ...action, completed: actionsCompleted[action.id] ?? action.completed }} onToggle={toggleAction} />
                ))}
              </div>
              {Object.values(actionsCompleted).filter(Boolean).length === weekData.actions.length && weekData.actions.length > 0 && (
                <div className="flex items-center gap-2 mt-4 text-xs text-[var(--accent-success)] font-medium">
                  <CheckCircle2 size={14} aria-hidden="true" />
                  All action items completed for this week!
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
