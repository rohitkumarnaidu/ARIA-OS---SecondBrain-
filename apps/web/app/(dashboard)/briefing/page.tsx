'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { format } from 'date-fns'
import {
  Sun, Moon, Cloud, RefreshCw, Target, Clock, BookOpen,
  Bell, Calendar, Brain, ArrowRight, Zap, Sparkles,
  ChevronRight,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { PageHeader } from '@/components/ui/PageHeader'
import { cn } from '@/components/ui/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import { useBriefingStore } from '@/lib/stores'

interface PriorityTask {
  title: string
  description: string
  estimatedTime: string
}

interface ScheduleBlock {
  time: string
  title: string
  description: string
  icon: typeof Clock
}

interface QuickStat {
  label: string
  value: string | number
  icon: typeof Target
}

interface BriefingData {
  opening: string
  priority: PriorityTask
  schedule: ScheduleBlock[]
  stats: QuickStat[]
}

const morningGreetings = [
  'Good morning, Developer. The day is yours to architect.',
  'Rise and shine. Another day, another breakthrough.',
  'Morning, Builder. Let\'s make today count.',
  'Good morning. Your systems are online and ready.',
] as const

const afternoonGreetings = [
  'Good afternoon. Halfway through — keep the momentum.',
  'Afternoon session. Time to crush the deep work.',
  'Good afternoon. The second half is where wins happen.',
] as const

const eveningGreetings = [
  'Good evening. Wind down and reflect on today\'s progress.',
  'Evening, Builder. Time to review and reset.',
  'Good evening. A few more focused minutes and you\'re done.',
] as const

const openingStatements = [
  'Today\'s landscape looks promising. Your task queue is lean, your focus blocks are optimally placed, and the priority for today aligns perfectly with your weekly goals. Let\'s dive in.',
  'A well-structured day ahead. I\'ve analyzed your energy patterns and scheduled your hardest cognitive work during your peak window. The rest of the day is designed for momentum.',
  'Today is set up for strong output. Your morning clarity window is clear, the learning block is aligned with your current sprint, and there are no scheduling conflicts to navigate.',
  'Great day to make progress. Your most important task is well-defined, the supporting work is minimal, and your energy curve supports deep focus before noon.',
] as const

const priorityTasks: PriorityTask[] = [
  { title: 'Complete DSA — Dynamic Programming Module', description: 'Finish the remaining 5 LeetCode problems on DP patterns. Focus on memoization vs tabulation trade-offs.', estimatedTime: '90 min' },
  { title: 'ML Specialization — Week 4 Assignment', description: 'Complete the neural network implementation assignment. Pay special attention to backpropagation vectorization.', estimatedTime: '120 min' },
  { title: 'Second Brain — API Documentation Sprint', description: 'Write OpenAPI specs for the 8 undocumented endpoints. Prioritize the chat and automation routers.', estimatedTime: '60 min' },
  { title: 'System Design — Database Schema Review', description: 'Review and optimize the current Supabase schema. Identify N+1 query patterns and add composite indexes.', estimatedTime: '75 min' },
  { title: 'Project — Architecture Decision Record', description: 'Draft ADR for migrating the notification system from polling to WebSocket-based push.', estimatedTime: '45 min' },
] as const

const scheduleTemplates: { blocks: Omit<ScheduleBlock, 'icon'>[]; label: string }[] = [
  {
    label: 'standard',
    blocks: [
      { time: '08:00 – 12:00', title: 'Morning Block', description: 'Deep focus on priority task. Pomodoro 25/5 with 15-min break at 10 AM.' },
      { time: '12:00 – 13:00', title: 'Midday Reset', description: 'Lunch, walk, and review morning progress. No screens.' },
      { time: '13:00 – 15:00', title: 'Learning Block', description: 'Course work, reading, or skill development. Active recall every 30 min.' },
      { time: '15:00 – 17:00', title: 'Deep Work', description: 'Second deep work window. Code, write, or architect.' },
      { time: '17:00 – 18:00', title: 'Review & Plan', description: 'Log progress, update tasks, prepare tomorrow\'s priority.' },
    ],
  },
  {
    label: 'intense',
    blocks: [
      { time: '07:30 – 11:00', title: 'Extended Deep Work', description: '3.5-hour focus block for complex problem-solving. No interruptions.' },
      { time: '11:00 – 12:00', title: 'Light Tasks', description: 'Emails, code reviews, and low-cognitive-overhead items.' },
      { time: '12:00 – 13:00', title: 'Break & Refuel', description: 'Proper lunch away from desk. 10-min mindfulness session.' },
      { time: '13:00 – 15:30', title: 'Project Sprint', description: 'Focused project work. Ship incremental progress.' },
      { time: '15:30 – 16:30', title: 'Learning & Growth', description: 'Course module or technical reading with active note-taking.' },
      { time: '16:30 – 17:30', title: 'Wrap & Review', description: 'Document wins, update logs, set tomorrow\'s intentions.' },
    ],
  },
  {
    label: 'light',
    blocks: [
      { time: '09:00 – 11:00', title: 'Priority Push', description: 'Single most important task first. Eliminate distractions.' },
      { time: '11:00 – 12:00', title: 'Catch-Up', description: 'Pending items, quick wins, and inbox zero.' },
      { time: '12:00 – 13:30', title: 'Extended Break', description: 'Leisurely lunch, walk, reading.' },
      { time: '13:30 – 15:00', title: 'Learning Session', description: 'Focused study or course work.' },
      { time: '15:00 – 16:00', title: 'Wind-Down Work', description: 'Documentation, organization, planning.' },
    ],
  },
] as const

const statTemplates: { blocks: Omit<QuickStat, 'icon'>[]; label: string }[] = [
  {
    label: 'default',
    blocks: [
      { label: 'Tasks Due Today', value: 4 },
      { label: 'Focus Sessions', value: 3 },
      { label: 'Habits Due', value: 6 },
      { label: 'New Since Yesterday', value: 2 },
    ],
  },
  {
    label: 'busy',
    blocks: [
      { label: 'Tasks Due Today', value: 7 },
      { label: 'Focus Sessions', value: 4 },
      { label: 'Habits Due', value: 5 },
      { label: 'New Since Yesterday', value: 3 },
    ],
  },
  {
    label: 'light',
    blocks: [
      { label: 'Tasks Due Today', value: 2 },
      { label: 'Focus Sessions', value: 2 },
      { label: 'Habits Due', value: 4 },
      { label: 'New Since Yesterday', value: 1 },
    ],
  },
] as const

function pickRandom<T>(arr: readonly T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

function getTimeGreeting(): { text: string; Icon: typeof Sun } {
  const hour = new Date().getHours()
  if (hour < 12) return { text: pickRandom(morningGreetings), Icon: Sun }
  if (hour < 17) return { text: pickRandom(afternoonGreetings), Icon: Cloud }
  return { text: pickRandom(eveningGreetings), Icon: Moon }
}

function generateBriefing(): BriefingData {
  const schedule = pickRandom(scheduleTemplates)
  const stats = pickRandom(statTemplates)
  return {
    opening: pickRandom(openingStatements),
    priority: pickRandom(priorityTasks as readonly PriorityTask[]),
    schedule: schedule.blocks.map(b => ({
      ...b,
      icon: b.title.includes('Learning') ? BookOpen : b.title.includes('Deep') || b.title.includes('Priority') || b.title.includes('Push') ? Zap : b.title.includes('Review') || b.title.includes('Wrap') ? Clock : b.title.includes('Break') || b.title.includes('Reset') ? Sun : Clock,
    })),
    stats: stats.blocks.map(b => ({
      ...b,
      icon: b.label.includes('Tasks') ? Target : b.label.includes('Focus') ? Clock : b.label.includes('Habits') ? Bell : Sparkles,
    })),
  }
}

const containerVariants = {
  initial: {},
  animate: { transition: { staggerChildren: 0.1 } },
}

const cardVariants = {
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
}

function FreshnessBadge({ generatedAt, now }: { generatedAt: Date; now: Date }): JSX.Element {
  const diffMs = now.getTime() - generatedAt.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const text = diffMin < 1 ? 'Generated just now' : `Generated ${diffMin}m ago`
  return (
    <span className="text-[11px] text-[var(--text-tertiary)] font-mono tabular-nums">{text}</span>
  )
}

function ScheduleTimeline({ blocks }: { blocks: ScheduleBlock[] }): JSX.Element {
  const iconBg: Record<string, string> = {
    [Zap.name]: 'bg-[var(--accent-warning)]/10 text-[var(--accent-warning)]',
    [BookOpen.name]: 'bg-[var(--accent-info)]/10 text-[var(--accent-info)]',
    [Clock.name]: 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]',
    [Sun.name]: 'bg-[var(--accent-success)]/10 text-[var(--accent-success)]',
  }

  return (
    <div className="relative">
      {blocks.map((block, i) => {
        const Icon = block.icon
        const isLast = i === blocks.length - 1
        return (
          <div key={i} className="relative flex gap-4 pb-6 last:pb-0">
            <div className="flex flex-col items-center">
              <div className={cn(
                'w-10 h-10 rounded-xl flex items-center justify-center shrink-0 z-10',
                iconBg[Icon.name] ?? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]',
              )}>
                <Icon size={16} aria-hidden="true" />
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

function StatCard({ stat, index }: { stat: QuickStat; index: number }): JSX.Element {
  const Icon = stat.icon
  const iconColors: Record<string, string> = {
    [Target.name]: 'text-[var(--accent-error)]',
    [Clock.name]: 'text-[var(--accent-info)]',
    [Bell.name]: 'text-[var(--accent-warning)]',
    [Sparkles.name]: 'text-[var(--accent-success)]',
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
  const [generatedAt, setGeneratedAt] = useState(new Date())
  const [now, setNow] = useState(new Date())
  const { today, loading, error, getToday } = useBriefingStore()

  useEffect(() => {
    setMounted(true)
    getToday()
    const interval = setInterval(() => setNow(new Date()), 60_000)
    return () => clearInterval(interval)
  }, [getToday])

  useEffect(() => {
    if (regenerateKey > 0) getToday()
  }, [regenerateKey, getToday])

  const greeting = useMemo(() => getTimeGreeting(), [])
  const todayFormatted = useMemo(() => format(new Date(), 'EEEE, MMMM d, yyyy'), [])

  const briefing = useMemo(() => {
    if (today) {
      return {
        opening: today.ai_insight || today.summary || generateBriefing().opening,
        priority: {
          title: today.top_priority || generateBriefing().priority.title,
          description: `Based on your ${today.tasks_count || 0} tasks today.`,
          estimatedTime: '60 min',
        },
        schedule: generateBriefing().schedule,
        stats: [
          { label: 'Tasks Due Today', value: today.tasks_count || 0, icon: Target },
          { label: 'Habits Streak', value: today.habits_streak || 0, icon: Bell },
          { label: 'Sleep Score', value: today.sleep_score ? `${today.sleep_score}/10` : '--', icon: Clock },
          { label: 'Priority Tasks', value: today.top_priority ? 1 : 0, icon: Sparkles },
        ],
      }
    }
    return generateBriefing()
  }, [regenerateKey, today]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleRegenerate = useCallback(() => {
    setRegenerateKey(prev => prev + 1)
    setGeneratedAt(new Date())
  }, [])

  if (!mounted) return <div className="min-h-screen" />

  const GreetingIcon = greeting.Icon

  return (
    <motion.div variants={containerVariants} initial="initial" animate="animate" className="flex flex-col gap-6 p-6 pb-8">
      <motion.div variants={cardVariants}>
        <PageHeader
          title="Daily Briefing"
          description="Your AI-curated morning briefing"
          actions={
            <div className="flex items-center gap-3">
              <FreshnessBadge generatedAt={generatedAt} now={now} />
              <Button variant="ghost" size="sm" onClick={handleRegenerate} aria-label="Regenerate briefing" className="focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]">
                <RefreshCw size={14} />
                Regenerate
              </Button>
            </div>
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
        ) : (
          <motion.div key={regenerateKey} variants={containerVariants} initial="initial" animate="animate" className="space-y-6">
            {/* Section 1: Morning Greeting */}
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
                    <p className="text-sm text-[var(--text-secondary)] font-body leading-relaxed">{briefing.opening}</p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Section 2: Today's Priority */}
            <motion.div variants={cardVariants}>
              <div className="rounded-xl bg-gradient-to-r from-[var(--accent-success)]/10 to-transparent border border-[var(--accent-success)]/20 p-5 relative overflow-hidden">
                <div className="absolute left-0 top-0 bottom-0 w-[3px] bg-gradient-to-b from-[var(--accent-success)] to-[var(--accent-secondary)]" aria-hidden="true" />
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <Target size={16} className="text-[var(--accent-success)]" aria-hidden="true" />
                      <span className="text-xs font-semibold uppercase tracking-wider text-[var(--accent-success)] font-body">Today's Priority</span>
                    </div>
                    <h3 className="text-base font-semibold text-[var(--text-primary)] font-display mb-1">{briefing.priority.title}</h3>
                    <p className="text-sm text-[var(--text-secondary)] font-body leading-relaxed mb-3">{briefing.priority.description}</p>
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className="text-[11px] flex items-center gap-1">
                        <Clock size={12} aria-hidden="true" />
                        {briefing.priority.estimatedTime}
                      </Badge>
                    </div>
                  </div>
                  <Button variant="primary" size="sm" className="shrink-0 mt-1" aria-label={`Start working on ${briefing.priority.title}`}>
                    Start Now
                    <ArrowRight size={14} />
                  </Button>
                </div>
              </div>
            </motion.div>

            {/* Section 3: Schedule Overview */}
            <motion.div variants={cardVariants}>
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <Calendar size={16} className="text-[var(--accent-primary)]" aria-hidden="true" />
                    <CardTitle className="font-display font-semibold text-lg">Today's Schedule</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <ScheduleTimeline blocks={briefing.schedule} />
                </CardContent>
              </Card>
            </motion.div>

            {/* Section 4: Quick Stats */}
            <motion.div variants={cardVariants}>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {briefing.stats.map((stat, i) => (
                  <StatCard key={stat.label} stat={stat} index={i} />
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
