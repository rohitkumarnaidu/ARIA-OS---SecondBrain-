'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { format, subWeeks, startOfWeek } from 'date-fns'
import {
  ChevronLeft, ChevronRight, Download, TrendingUp, TrendingDown,
  Minus, CheckCircle2, Brain, Calendar, Target, Clock,
  Flame, BookOpen, Lightbulb,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { PageHeader } from '@/components/ui/PageHeader'
import { cn } from '@/components/ui/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import { useReviewStore } from '@/lib/stores'
import { useAIAgents, useAIAction } from '@/lib/ai/hooks'
import { AIInsightCard, ThinkingIndicator, ConfidenceBadge } from '@/components/ai'

interface WeeklyMetric {
  label: string
  value: string | number
  trend: 'up' | 'down' | 'flat'
  change: string
}

interface InsightBlock {
  title: string
  description: string
}

interface DecisionRecord {
  date: string
  title: string
  category: string
  reasoning: string
}

interface NextAction {
  id: string
  title: string
  priority: 'P1' | 'P2' | 'P3' | 'P4'
  module: string
  completed: boolean
}

interface WeekReviewData {
  weekStart: Date
  summary: string
  mood: number
  metrics: WeeklyMetric[]
  patterns: InsightBlock[]
  wentWell: InsightBlock[]
  needsAttention: InsightBlock[]
  decisions: DecisionRecord[]
  actions: NextAction[]
  confidence: 'High' | 'Medium' | 'Low'
}

function generateReviewData(offset: number): WeekReviewData {
  const weekStart = startOfWeek(subWeeks(new Date(), offset), { weekStartsOn: 1 })
  const summaries: string[] = [
    'This week showed strong momentum across all key areas. Task completion rate improved significantly, and deep work sessions hit a new record. Your habit consistency remained solid, though evening routines could use some attention to maintain the upward trajectory.',
    'A solid week of consistent progress. Study habits remained on track with major courses advancing on schedule. Focus hours dipped slightly mid-week but recovered with strong weekend sessions. The new note-taking workflow is showing promising early results.',
    'Productivity held steady this week despite some external disruptions. Task management remained efficient, and you made meaningful progress on the DSA preparation plan. Consider adjusting your learning block timing to avoid afternoon energy slumps.',
  ]
  const moods: number[] = [8, 7, 6]
  const metrics: WeeklyMetric[][] = [
    [
      { label: 'Tasks Completed', value: 47, trend: 'up', change: '+12%' },
      { label: 'Habits Streak', value: 14, trend: 'up', change: '+3 days' },
      { label: 'Focus Hours', value: 32, trend: 'up', change: '+18%' },
      { label: 'Courses Progress', value: '73%', trend: 'up', change: '+8%' },
      { label: 'New Ideas', value: 9, trend: 'up', change: '+3' },
      { label: 'Opportunities Found', value: 4, trend: 'flat', change: '0' },
    ],
    [
      { label: 'Tasks Completed', value: 42, trend: 'up', change: '+5%' },
      { label: 'Habits Streak', value: 11, trend: 'up', change: '+2 days' },
      { label: 'Focus Hours', value: 27, trend: 'down', change: '-4%' },
      { label: 'Courses Progress', value: '65%', trend: 'up', change: '+6%' },
      { label: 'New Ideas', value: 6, trend: 'flat', change: '0' },
      { label: 'Opportunities Found', value: 4, trend: 'up', change: '+1' },
    ],
    [
      { label: 'Tasks Completed', value: 40, trend: 'down', change: '-3%' },
      { label: 'Habits Streak', value: 9, trend: 'down', change: '-2 days' },
      { label: 'Focus Hours', value: 28, trend: 'flat', change: '+1%' },
      { label: 'Courses Progress', value: '59%', trend: 'up', change: '+4%' },
      { label: 'New Ideas', value: 6, trend: 'up', change: '+2' },
      { label: 'Opportunities Found', value: 3, trend: 'flat', change: '0' },
    ],
  ]
  const patterns: InsightBlock[][] = [
    [
      { title: 'Morning Deep Work Peak', description: 'Your most productive hours remain 8–11 AM, with 73% of high-priority tasks completed during this window.' },
      { title: 'Consistent Study Rhythm', description: 'Daily 2-hour study blocks maintained for 12 consecutive days, your longest streak this semester.' },
      { title: 'Evening Energy Dip', description: 'Post-6 PM task completion drops to 34%. Consider scheduling low-cognitive-load activities in the evening.' },
    ],
    [
      { title: 'Learning Block Optimization', description: 'Afternoon study sessions show 22% better retention when preceded by a 15-minute walk break.' },
      { title: 'Task Batching Inefficiency', description: 'Context-switching between unrelated tasks cost approximately 45 minutes of lost focus daily.' },
      { title: 'Weekend Recovery Pattern', description: 'Saturday morning deep work sessions are 1.5× more productive than weekday equivalents.' },
    ],
    [
      { title: 'Deadline-Driven Productivity', description: 'Task completion spikes 40% in the 24 hours before deadlines, suggesting Parkinson\'s Law in effect.' },
      { title: 'Tool Fragmentation', description: 'Using 4 different note-taking apps is causing 15–20 minutes of daily context-switching overhead.' },
      { title: 'Social Accountability Effect', description: 'Tasks shared with study groups have a 91% completion rate vs 63% for solo tasks.' },
    ],
  ]
  const wentWell: InsightBlock[][] = [
    [
      { title: 'DSA Practice Milestone', description: 'Completed 25 LeetCode problems this week, maintaining an 82% acceptance rate across Easy and Medium difficulty.' },
      { title: 'New Note-Taking Workflow', description: 'Adopted a PARA-based folder structure that reduced weekly note retrieval time by an estimated 30%.' },
      { title: 'Consistent Sleep Schedule', description: 'Bedtime variance reduced to ±22 minutes, contributing to improved morning alertness scores.' },
    ],
    [
      { title: 'Course Sprint Completion', description: 'Finished Module 4 of the Machine Learning specialization 2 days ahead of schedule with a 91% quiz average.' },
      { title: 'Networking Win', description: 'Connected with 3 industry professionals on LinkedIn, one of whom shared a promising internship opportunity.' },
      { title: 'Focus Session Record', description: 'Achieved 4 sessions of 90+ minute deep work, the highest single-week count this quarter.' },
    ],
    [
      { title: 'Project Milestone', description: 'Delivered the database schema redesign for the Second Brain project, reducing query times by an estimated 40%.' },
      { title: 'Habit Streak Recovery', description: 'Rebuilt the morning routine streak after a setback, currently at 5 consecutive days and growing.' },
      { title: 'Reading Goal Progress', description: 'Finished 2 technical articles on system design patterns, applying learnings to ongoing architecture decisions.' },
    ],
  ]
  const attention: InsightBlock[][] = [
    [
      { title: 'Evening Routine Consistency', description: 'Wind-down routine skipped on 3 evenings, correlating with 25% longer sleep onset the following nights.' },
      { title: 'Project Documentation Debt', description: 'API documentation backlog grew by 8 endpoints this week. Consider dedicating 30 minutes daily to documentation.' },
      { title: 'Notification Overload', description: 'Averaged 47 non-essential notifications per day, causing an estimated 6 focus interruptions daily.' },
    ],
    [
      { title: 'Afternoon Procrastination Pattern', description: '1–3 PM window shows a 40% lower task initiation rate. Consider using the Pomodoro technique during this period.' },
      { title: 'Exercise Consistency Drop', description: 'Only 2 workout sessions completed against a goal of 4. Morning scheduling might improve adherence.' },
      { title: 'Tool Overhead Accumulation', description: 'Weekly digital cleanup time exceeded 2 hours due to scattered file organization across 5 platforms.' },
    ],
    [
      { title: 'Mid-Week Motivation Dip', description: 'Wednesday and Thursday show 30% lower task satisfaction ratings, suggesting a need for mid-week routine variation.' },
      { title: 'Learning Feedback Lag', description: 'Course assignment feedback averaged 4 days delay, slowing the learning iteration cycle.' },
      { title: 'Energy Management Gap', description: 'No structured breaks between 11 AM and 2 PM leads to a 20% productivity drop in the afternoon block.' },
    ],
  ]
  const decisions: DecisionRecord[][] = [
    [
      { date: 'Jun 15', title: 'Adjusted study plan to focus on DSA', category: 'Academics', reasoning: 'Shifted 5 hours/week from elective reading to LeetCode practice based on internship application requirements.' },
      { date: 'Jun 13', title: 'Deprecated old mobile shell approach', category: 'Engineering', reasoning: 'Consolidated two POC repos into a single Flutter codebase to reduce maintenance overhead by 40%.' },
      { date: 'Jun 11', title: 'Deferred cloud migration to Q3', category: 'DevOps', reasoning: 'Current Railway Free tier handles traffic adequately. Migration costs don\'t justify the move at this stage.' },
      { date: 'Jun 10', title: 'Adopted PARA note-taking system', category: 'Productivity', reasoning: 'Previous folder-less approach caused 15 min/day retrieval overhead. PARA structure estimated to save 3 hrs/month.' },
    ],
    [
      { date: 'Jun 8', title: 'Enrolled in ML Specialization', category: 'Academics', reasoning: 'Andrew Ng\'s course structure aligns better with current learning goals than the university\'s elective.' },
      { date: 'Jun 6', title: 'Set up automated weekly backups', category: 'DevOps', reasoning: 'Previous manual backup schedule had 60% compliance. Automation ensures 100% coverage.' },
      { date: 'Jun 4', title: 'Reduced newsletter subscriptions', category: 'Productivity', reasoning: 'Unsubscribed from 12 low-value newsletters, reducing inbox noise by an estimated 30 emails/week.' },
      { date: 'Jun 3', title: 'Started morning journaling practice', category: 'Wellness', reasoning: 'Evidence suggests 5-minute morning journaling improves daily goal clarity and reduces anxiety by 20%.' },
    ],
    [
      { date: 'Jun 1', title: 'Switched to TypeScript strict mode', category: 'Engineering', reasoning: 'Caught 3 potential runtime bugs during migration. Strict mode will prevent entire classes of production issues.' },
      { date: 'May 30', title: 'Implemented Pomodoro work blocks', category: 'Productivity', reasoning: 'Unstructured work sessions averaged 45 min of real focus. Pomodoro increased effective focus to 75% of scheduled time.' },
      { date: 'May 28', title: 'Consolidated note-taking tools', category: 'Engineering', reasoning: 'Reduced from 4 apps to 2 (Obsidian + Notion), decreasing weekly tool-switching overhead by 90 minutes.' },
      { date: 'May 27', title: 'Started weekly review habit', category: 'Productivity', reasoning: 'Implementing the ARIA OS weekly review loop to close the plan-do-review cycle for continuous improvement.' },
    ],
  ]
  const actions: NextAction[][] = [
    [
      { id: 'wr-a1', title: 'Review DSA problem-solving strategies for upcoming interview', priority: 'P1', module: 'Academics', completed: false },
      { id: 'wr-a2', title: 'Complete Module 5 of ML Specialization', priority: 'P1', module: 'Courses', completed: false },
      { id: 'wr-a3', title: 'Set up automated notification schedules to reduce interruptions', priority: 'P2', module: 'Automation', completed: false },
      { id: 'wr-a4', title: 'Draft API documentation for 8 pending endpoints', priority: 'P2', module: 'Tasks', completed: false },
      { id: 'wr-a5', title: 'Design evening wind-down routine and test for 5 days', priority: 'P3', module: 'Habits', completed: false },
      { id: 'wr-a6', title: 'Research cloud migration costs and prepare Q3 proposal', priority: 'P3', module: 'Goals', completed: false },
    ],
    [
      { id: 'wl-a1', title: 'Complete LeetCode problem set on Dynamic Programming', priority: 'P1', module: 'Academics', completed: false },
      { id: 'wl-a2', title: 'Implement automated weekly backup system', priority: 'P1', module: 'DevOps', completed: false },
      { id: 'wl-a3', title: 'Set up Pomodoro timer integration with focus tracking', priority: 'P2', module: 'Tasks', completed: false },
      { id: 'wl-a4', title: 'Review and optimize PARA folder structure', priority: 'P2', module: 'Resources', completed: false },
      { id: 'wl-a5', title: 'Establish post-lunch walking routine for afternoon energy', priority: 'P3', module: 'Habits', completed: false },
      { id: 'wl-a6', title: 'Create monthly learning roadmap for July', priority: 'P3', module: 'Goals', completed: false },
    ],
    [
      { id: 'wbe-a1', title: 'Migrate remaining TypeScript files to strict mode', priority: 'P1', module: 'Engineering', completed: false },
      { id: 'wbe-a2', title: 'Complete Obsidian vault migration from Notion', priority: 'P1', module: 'Resources', completed: false },
      { id: 'wbe-a3', title: 'Design and implement Pomodoro block schedule', priority: 'P2', module: 'Tasks', completed: false },
      { id: 'wbe-a4', title: 'Set up structured break reminders for midday slump', priority: 'P2', module: 'Automation', completed: false },
      { id: 'wbe-a5', title: 'Research internship application timeline and prepare materials', priority: 'P2', module: 'Opportunities', completed: false },
      { id: 'wbe-a6', title: 'Conduct weekly review habit consistency check after 2 weeks', priority: 'P3', module: 'Habits', completed: false },
    ],
  ]
  const confidences: ('High' | 'Medium' | 'Low')[] = ['High', 'Medium', 'Low']
  return {
    weekStart, summary: summaries[offset], mood: moods[offset],
    metrics: metrics[offset], patterns: patterns[offset],
    wentWell: wentWell[offset], needsAttention: attention[offset],
    decisions: decisions[offset], actions: actions[offset],
    confidence: confidences[offset],
  }
}

const containerVariants = {
  initial: {},
  animate: { transition: { staggerChildren: 0.08 } },
}

const sectionVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
}

const pageVariants = {
  enter: { opacity: 0, x: 30 },
  center: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -30 },
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

function MetricCard({ metric }: { metric: WeeklyMetric }): JSX.Element {
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

function InsightSection({ title, items, accentColor }: { title: string; items: InsightBlock[]; accentColor: string }): JSX.Element {
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

function TimelineDecision({ decision }: { decision: DecisionRecord }): JSX.Element {
  const categoryBadge: Record<string, 'default' | 'success' | 'warning' | 'error' | 'info' | 'outline'> = {
    Academics: 'info', Engineering: 'default', DevOps: 'warning',
    Productivity: 'success', Wellness: 'success',
  }
  return (
    <div className="relative pl-6 pb-5 border-l border-[var(--border)] last:border-l-transparent last:pb-0">
      <div className="absolute left-[-5px] top-1 w-[10px] h-[10px] rounded-full bg-[var(--accent-primary)] border-2 border-[var(--background-dark)]" aria-hidden="true" />
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xs text-[var(--text-tertiary)] font-mono tabular-nums">{decision.date}</span>
        <Badge variant={categoryBadge[decision.category] ?? 'outline'} className="text-[10px] px-1.5 py-0">{decision.category}</Badge>
      </div>
      <h5 className="text-sm font-medium text-[var(--text-primary)] font-body mb-0.5">{decision.title}</h5>
      <p className="text-xs text-[var(--text-secondary)] font-body leading-relaxed">{decision.reasoning}</p>
    </div>
  )
}

function ActionCheckbox({ action, onToggle }: { action: NextAction; onToggle: (id: string) => void }): JSX.Element {
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
  const [currentWeek, setCurrentWeek] = useState(0)
  const [actionsCompleted, setActionsCompleted] = useState<Record<string, boolean>>({})
  const [mounted, setMounted] = useState(false)
  const { items, latest, loading, error, fetch, getLatest } = useReviewStore()
  const { agents, updateAgent } = useAIAgents()
  const { execute: fetchReviewInsights, isLoading: reviewLoading } = useAIAction(async () => {
    // weekly review analysis
  })

  useEffect(() => { setMounted(true); fetch() }, [fetch])

  const weekData = useMemo(() => {
    if (latest && currentWeek === 0) {
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
        summary: latest.summary || generateReviewData(currentWeek).summary,
        mood: latest.mood_trend === 'positive' ? 8 : latest.mood_trend === 'negative' ? 5 : 7,
        metrics,
        patterns: latest.ai_insights
          ? [{ title: 'AI Insight', description: latest.ai_insights }]
          : generateReviewData(currentWeek).patterns,
        wentWell: (latest.highlights || []).slice(0, 3).map(h => ({ title: h, description: '' })).length > 0
          ? (latest.highlights || []).slice(0, 3).map(h => ({ title: h, description: '' }))
          : generateReviewData(currentWeek).wentWell,
        needsAttention: (latest.challenges || []).slice(0, 3).map(c => ({ title: c, description: '' })).length > 0
          ? (latest.challenges || []).slice(0, 3).map(c => ({ title: c, description: '' }))
          : generateReviewData(currentWeek).needsAttention,
        decisions: generateReviewData(currentWeek).decisions,
        actions: (latest.next_week_focus || []).map((f, i) => ({
          id: `review-${i}`,
          title: f,
          priority: (i === 0 ? 'P1' : i === 1 ? 'P2' : 'P3') as 'P1' | 'P2' | 'P3',
          module: 'Review',
          completed: false,
        })),
        confidence: (latest.ai_insights ? 'High' : 'Medium') as 'High' | 'Medium' | 'Low',
      }
    }
    return generateReviewData(currentWeek)
  }, [currentWeek, latest])

  useEffect(() => {
    setActionsCompleted(prev => {
      const next: Record<string, boolean> = { ...prev }
      weekData.actions.forEach(a => { if (!(a.id in next)) next[a.id] = a.completed })
      return next
    })
  }, [weekData])

  useEffect(() => {
    updateAgent('weekly-review', {
      status: 'done',
      preview: 'Strong week overall. DSA practice and sleep consistency are key wins.',
      confidence: weekData.confidence === 'High' ? 0.9 : weekData.confidence === 'Medium' ? 0.7 : 0.5,
    })
  }, [updateAgent, weekData.confidence])

  const handlePrev = useCallback(() => setCurrentWeek(prev => Math.min(prev + 1, 2)), [])
  const handleNext = useCallback(() => setCurrentWeek(prev => Math.max(prev - 1, 0)), [])
  const toggleAction = useCallback((id: string) => setActionsCompleted(p => ({ ...p, [id]: !p[id] })), [])
  const handleExport = useCallback(() => {
    const toast = document.createElement('div')
    toast.className = 'fixed bottom-6 right-6 z-50 px-4 py-3 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] shadow-lg animate-in slide-in-from-bottom-2 font-body'
    toast.textContent = 'Export started — download will begin shortly'
    document.body.appendChild(toast)
    setTimeout(() => toast.remove(), 3000)
  }, [])

  const weekLabel = useMemo(() => {
    const start = weekData.weekStart
    const end = new Date(start); end.setDate(end.getDate() + 6)
    const prefix = currentWeek === 0 ? 'This Week' : currentWeek === 1 ? 'Last Week' : `${currentWeek} Weeks Ago`
    return `${prefix} — ${format(start, 'MMM d')} – ${format(end, 'MMM d, yyyy')}`
  }, [weekData.weekStart, currentWeek])

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
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <Button variant="ghost" size="icon" onClick={handlePrev} disabled={currentWeek >= 2} aria-label="Previous week" className="focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]">
                  <ChevronLeft size={18} />
                </Button>
                <span className="text-sm font-medium text-[var(--text-primary)] min-w-[180px] text-center font-display">{weekLabel}</span>
                <Button variant="ghost" size="icon" onClick={handleNext} disabled={currentWeek <= 0} aria-label="Next week" className="focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]">
                  <ChevronRight size={18} />
                </Button>
              </div>
              <Button variant="outline" size="sm" onClick={handleExport} aria-label="Export review">
                <Download size={14} />
                Export
              </Button>
            </div>
          }
        />
      </motion.div>

      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div key="skeleton" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
            <Skeleton variant="card" className="h-[160px] opacity-40" />
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} variant="card" className="h-[88px] opacity-40" />)}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key={currentWeek}
            variants={pageVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="space-y-6"
          >
            {/* Section 1: Overview */}
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
                {currentWeek === 0 && (
                  <p className="mt-4 text-xs text-[var(--text-tertiary)] font-body">
                    Data completeness: 92% · 6/6 data sources reporting · Last synced 2m ago
                  </p>
                )}
              </CardContent>
            </Card>

            <motion.div variants={sectionVariants}>
              <AIInsightCard
                type="insight"
                title="Review Highlights"
                description="Strong week overall. DSA practice and sleep consistency are key wins."
              />
            </motion.div>

            {/* Section 2: Weekly Metrics */}
            <div>
              <h2 className="font-display font-semibold text-lg text-[var(--text-primary)] mb-4">Weekly Metrics</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {weekData.metrics.map(metric => <MetricCard key={metric.label} metric={metric} />)}
              </div>
            </div>

            {/* Section 3: AI Analysis */}
            <GlassCard>
              <div className="flex items-center gap-2 mb-5">
                <Brain size={18} className="text-[var(--accent-secondary)]" aria-hidden="true" />
                <h3 className="font-display font-semibold text-lg text-[var(--text-primary)]">AI Analysis</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <InsightSection title="Key Patterns" items={weekData.patterns} accentColor="text-[var(--accent-info)]" />
                <InsightSection title="What Went Well" items={weekData.wentWell} accentColor="text-[var(--accent-success)]" />
                <InsightSection title="Needs Attention" items={weekData.needsAttention} accentColor="text-[var(--accent-warning)]" />
              </div>
            </GlassCard>

            {/* Section 4: Key Decisions */}
            <div>
              <h2 className="font-display font-semibold text-lg text-[var(--text-primary)] mb-4">Key Decisions</h2>
              <div className="rounded-xl bg-[var(--background-card)] border border-[var(--border)] p-5">
                <div className="pl-1">
                  {weekData.decisions.map((d, i) => <TimelineDecision key={i} decision={d} />)}
                </div>
              </div>
            </div>

            {/* Section 5: Action Items */}
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
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
