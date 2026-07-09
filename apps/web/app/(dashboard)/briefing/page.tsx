'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { format } from 'date-fns'
import {
  Sun, Moon, RefreshCw, Target, Clock,
  Bell, ArrowRight,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { PageHeader } from '@/components/ui/PageHeader'
import { cn } from '@/components/ui/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import { useBriefingStore } from '@/lib/stores'
import { EmptyState } from '@/components/ui/EmptyState'

const containerVariants = {
  initial: {},
  animate: { transition: { staggerChildren: 0.1 } },
}

const cardVariants = {
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
}

function ScheduleTimeline({ blocks }: { blocks: { time: string; title: string; description: string }[] }): JSX.Element {
  return (
    <div className="relative">
      {blocks.map((block, i) => {
        const isLast = i === blocks.length - 1
        return (
          <div key={i} className="relative flex gap-4 pb-6 last:pb-0">
            <div className="flex flex-col items-center">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 z-10 bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]">
                <Clock size={16} aria-hidden="true" />
              </div>
              {!isLast && <div className="w-px flex-1 bg-[var(--border)] mt-1" aria-hidden="true" />}
            </div>
            <div className="flex-1 pb-2">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-xs text-[var(--accent-primary)] font-mono tabular-nums font-medium">{block.time}</span>
              </div>
              <h5 className="text-sm font-medium text-[var(--text-primary)] font-body">{block.title}</h5>
              <p className="text-xs text-[var(--text-secondary)] font-body mt-0.5 leading-relaxed">{block.description}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function StatCard({ stat, index }: { stat: { label: string; value: string | number; icon: typeof Target }; index: number }): JSX.Element {
  const Icon = stat.icon
  const iconColors: Record<string, string> = {
    [Target.name]: 'text-[var(--accent-error)]',
    [Clock.name]: 'text-[var(--accent-info)]',
    [Bell.name]: 'text-[var(--accent-warning)]',
  }
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.3 + index * 0.08 }}
      className="flex items-center gap-3 p-4 rounded-xl bg-[var(--surface-secondary)] border border-[var(--border)]"
    >
      <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center bg-[var(--surface-tertiary)]', iconColors[Icon.name] ?? 'text-[var(--text-secondary)]')}>
        <Icon size={18} aria-hidden="true" />
      </div>
      <div>
        <span className="text-xl font-bold font-display tabular-nums text-[var(--text-primary)]">{stat.value}</span>
        <p className="text-xs text-[var(--text-tertiary)] font-body">{stat.label}</p>
      </div>
    </motion.div>
  )
}

function BriefingSkeleton(): JSX.Element {
  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader title="Daily Briefing" description="Your AI-curated morning briefing" />
      <div className="space-y-4">
        <Skeleton variant="card" className="h-[140px] opacity-40" />
        <Skeleton variant="card" className="h-[180px] opacity-40" />
        <Skeleton variant="card" className="h-[280px] opacity-40" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} variant="card" className="h-[80px] opacity-40" />)}
        </div>
      </div>
    </div>
  )
}

export default function BriefingPage(): JSX.Element {
  const [regenerateKey, setRegenerateKey] = useState(0)
  const [mounted, setMounted] = useState(false)
  const { today, loading, getToday } = useBriefingStore()

  useEffect(() => {
    setMounted(true)
    getToday()
  }, [getToday])

  useEffect(() => {
    if (regenerateKey > 0) getToday()
  }, [regenerateKey, getToday])

  const greeting = useMemo(() => {
    const hour = new Date().getHours()
    if (hour < 12) return { text: 'Good morning.', icon: Sun }
    if (hour < 17) return { text: 'Good afternoon.', icon: Sun }
    return { text: 'Good evening.', icon: Moon }
  }, [])

  const todayFormatted = useMemo(() => format(new Date(), 'EEEE, MMMM d, yyyy'), [])

  const handleRegenerate = useCallback(() => {
    setRegenerateKey(prev => prev + 1)
  }, [])

  if (!mounted) return <div className="min-h-screen" />

  const GreetingIcon = greeting.icon

  return (
    <motion.div variants={containerVariants} initial="initial" animate="animate" className="flex flex-col gap-6 p-6 pb-8">
      <motion.div variants={cardVariants}>
        <PageHeader
          title="Daily Briefing"
          description="Your AI-curated morning briefing"
          actions={
            <Button variant="ghost" size="sm" onClick={handleRegenerate} aria-label="Regenerate briefing" className="focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]">
              <RefreshCw size={14} />
              Regenerate
            </Button>
          }
        />
      </motion.div>

      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div key="skeleton" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
            <Skeleton variant="card" className="h-[140px] opacity-40" />
            <Skeleton variant="card" className="h-[180px] opacity-40" />
            <Skeleton variant="card" className="h-[280px] opacity-40" />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} variant="card" className="h-[80px] opacity-40" />)}
            </div>
          </motion.div>
        ) : today ? (
          <motion.div key={regenerateKey} variants={containerVariants} initial="initial" animate="animate" className="space-y-6">
            <motion.div variants={cardVariants}>
              <Card className="relative overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl from-[var(--accent-primary)]/5 to-transparent rounded-bl-full pointer-events-none" aria-hidden="true" />
                <CardContent className="pt-5">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[var(--accent-primary)]/20 to-[var(--accent-secondary)]/20 flex items-center justify-center shrink-0 border border-[var(--border)]">
                      <GreetingIcon size={28} className="text-[var(--accent-primary)]" aria-hidden="true" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h2 className="text-lg font-display font-semibold text-[var(--text-primary)]">{greeting.text}</h2>
                      <p className="text-sm text-[var(--text-tertiary)] font-body mt-0.5">{todayFormatted}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-sm text-[var(--text-secondary)] font-body leading-relaxed">{today.ai_insight || today.summary}</p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {today.top_priority && (
              <motion.div variants={cardVariants}>
                <div className="rounded-xl bg-gradient-to-r from-[var(--accent-success)]/10 to-transparent border border-[var(--accent-success)]/20 p-5 relative overflow-hidden">
                  <div className="absolute left-0 top-0 bottom-0 w-[3px] bg-gradient-to-b from-[var(--accent-success)] to-[var(--accent-secondary)]" aria-hidden="true" />
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <Target size={16} className="text-[var(--accent-success)]" aria-hidden="true" />
                        <span className="text-xs font-semibold uppercase tracking-wider text-[var(--accent-success)] font-body">Today's Priority</span>
                      </div>
                      <h2 className="text-base font-semibold text-[var(--text-primary)] font-display mb-1">{today.top_priority}</h2>
                    </div>
                    <Button variant="primary" size="sm" className="shrink-0 mt-1" aria-label={`Start working on ${today.top_priority}`}>
                      Start Now
                      <ArrowRight size={14} />
                    </Button>
                  </div>
                </div>
              </motion.div>
            )}

            <motion.div variants={cardVariants}>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <StatCard stat={{ label: 'Tasks Due Today', value: today.tasks_count, icon: Target }} index={0} />
                <StatCard stat={{ label: 'Habits Streak', value: today.habits_streak, icon: Bell }} index={1} />
                {today.sleep_score != null && (
                  <StatCard stat={{ label: 'Sleep Score', value: `${today.sleep_score}/10`, icon: Clock }} index={2} />
                )}
                {today.top_priority && (
                  <StatCard stat={{ label: 'Priority Set', value: 1, icon: Target }} index={3} />
                )}
              </div>
            </motion.div>
          </motion.div>
        ) : (
          <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <Card>
              <CardContent>
                <EmptyState
                  title="No Briefing Yet"
                  description="Your daily briefing hasn't been generated yet. It will appear here once ready."
                  action={{ label: 'Generate Briefing', onClick: handleRegenerate }}
                />
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
