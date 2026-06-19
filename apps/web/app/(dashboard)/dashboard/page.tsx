'use client'

import { useEffect, useMemo, useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useTaskStore } from '@/lib/stores/taskStore'
import { useCourseStore } from '@/lib/stores/courseStore'
import { useGoalStore } from '@/lib/stores/goalStore'
import {
  StatsGrid, TaskPreviewList,
  QuickActions, ActivityMatrix, AriasPick,
  MorningBriefing, KPIStrip, WidgetToggle, useWidgetVisibility,
  SmartScheduleCard,
} from '@/components/dashboard'
import { ProgressRing } from '@/components/ui/ProgressRing'
import { Timeline } from '@/components/ui/Timeline'
import type { TimelineItem } from '@/components/ui/Timeline'
import { motion } from 'framer-motion'
import { CheckCircle, Target, BookOpen, Zap, Radar, Calendar, Brain, AlertTriangle, Moon, Flame, Heart } from 'lucide-react'
import { usePredictions } from '@/hooks'
import { computeSentiment } from '@/lib/ai'
import type { KPIItem } from '@/components/dashboard/KPIStrip'

const sectionVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
}

const containerVariants = {
  initial: {},
  animate: {
    transition: { staggerChildren: 0.08 },
  },
}

function generateSparklineData(value: number, count = 7): { value: number }[] {
  const base = value / count
  return Array.from({ length: count }, (_, i) => ({
    value: Math.max(0, Math.round(base + (Math.random() - 0.5) * base)),
  }))
}

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth()
  const { tasks, fetchTasks, error: taskError } = useTaskStore()
  const { items: courses, fetch: fetchCourses, error: courseError } = useCourseStore()
  const { items: goals, fetch: fetchGoals, error: goalError } = useGoalStore()
  const { visibility, isVisible, toggle: toggleWidget } = useWidgetVisibility()
  const { tasks: predTasks, habits: predHabits, sleep: predSleep, slots: predSlots, loading: predLoading } = usePredictions()
  const sentiment = useMemo(() => {
    if (!predTasks || !predHabits || !predSleep) return null
    return computeSentiment({
      taskAtRisk: predTasks.at_risk_count,
      habitAtRisk: predHabits.at_risk_count,
      sleepTrend: predSleep.trend,
      avgSleepScore: predSleep.average_score,
    })
  }, [predTasks, predHabits, predSleep])
  const [mounted, setMounted] = useState(false)

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (!authLoading && user) {
      fetchTasks()
      fetchCourses()
      fetchGoals()
    }
  }, [authLoading, user, fetchTasks, fetchCourses, fetchGoals])

  const activeCourses = courses.filter(c => c.status === 'in_progress').length
  const activeGoals = goals.filter(g => g.status === 'active').length

  const stats = useMemo(() => {
    const pending = tasks.filter(t => t.status === 'pending')
    const inProgress = tasks.filter(t => t.status === 'in_progress')
    const completed = tasks.filter(t => t.status === 'completed')
    const total = tasks.length
    const productivity = total > 0 ? Math.round((completed.length / total) * 100) : 0
    const today = new Date().toISOString().split('T')[0]
    const todayTasks = tasks.filter(t => t.due_date?.startsWith(today))
    return [
      { label: 'Productivity', value: `${productivity}%`, icon: Zap, trend: productivity >= 50 ? 'up' as const : 'down' as const },
      { label: 'Tasks Today', value: todayTasks.length || '0', icon: CheckCircle, trend: todayTasks.length > 0 ? 'up' as const : undefined },
      { label: 'Active Courses', value: String(activeCourses), icon: BookOpen },
      { label: 'Active Goals', value: String(activeGoals), icon: Target },
    ]
  }, [tasks, activeCourses, activeGoals])

  const kpiItems = useMemo((): KPIItem[] => [
    { label: 'Productivity', value: String(stats[0].value), trend: stats[0].trend === 'up' ? 'up' : 'down', data: generateSparklineData(parseInt(String(stats[0].value)) || 0), color: '#6366F1' },
    { label: 'Tasks Done', value: String(tasks.filter(t => t.status === 'completed').length), trend: 'up', data: generateSparklineData(tasks.filter(t => t.status === 'completed').length), color: '#00FFA3' },
    { label: 'Streak', value: '--', trend: 'neutral', data: generateSparklineData(0), color: '#F59E0B' },
    { label: 'Focus Hours', value: '--', trend: 'neutral', data: generateSparklineData(0), color: '#818CF8' },
  ], [stats, tasks])

  const completedToday = useMemo(() => {
    const today = new Date().toISOString().split('T')[0]
    return tasks.filter(t => t.completed_at?.startsWith(today)).length
  }, [tasks])

  const todayTotal = useMemo(() => {
    const today = new Date().toISOString().split('T')[0]
    return tasks.filter(t => t.due_date?.startsWith(today)).length
  }, [tasks])

  const previewTasks = useMemo(() => {
    return tasks
      .filter(t => t.status === 'pending' || t.status === 'in_progress')
      .slice(0, 5)
  }, [tasks])

  const activityData = useMemo(() => {
    const dateMap = new Map<string, number>()
    for (const task of tasks) {
      const date = task.created_at?.split('T')[0]
      if (date) dateMap.set(date, (dateMap.get(date) || 0) + 1)
    }
    return Array.from(dateMap.entries()).map(([date, count]) => ({ date, count }))
  }, [tasks])

  const ariaInsight = useMemo(() => {
    const pending = tasks.filter(t => t.status === 'pending')
    const inProgress = tasks.filter(t => t.status === 'in_progress')
    const completed = tasks.filter(t => t.status === 'completed')

    if (tasks.length === 0) {
      return "Welcome to ARIA OS! Add your first task to unlock personalized productivity insights."
    }
    if (pending.length === 0 && inProgress.length === 0) {
      const rate = Math.round((completed.length / tasks.length) * 100)
      return `All done at ${rate}% completion — you're on fire! Time to plan your next big goal.`
    }
    const top = pending[0] || inProgress[0]
    if (top) {
      return `Start with "${top.title}" — it's your top priority and will set a productive tone for the day.`
    }
    return `You've completed ${completed.length} of ${tasks.length} tasks. Keep the momentum going!`
  }, [tasks])

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="relative">
          <div className="w-12 h-12 rounded-xl border-2 border-accent-primary/30 animate-pulse-glow" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      </div>
    )
  }

  const userName = user?.email?.split('@')[0] || 'there'
  const storeError = taskError || courseError || goalError

  return (
    <motion.div
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="space-y-6 pb-8"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-text-primary">Dashboard</h1>
          <p className="text-sm text-text-tertiary">Your command center at a glance</p>
        </div>
        <WidgetToggle visibility={visibility} onToggle={toggleWidget} />
      </div>

      {storeError && (
        <div className="bg-accent-danger/10 border border-accent-danger/30 text-text-primary px-4 py-3 rounded-lg mb-6">
          {storeError}
        </div>
      )}

      {isVisible('morning-briefing') && (
        <motion.div variants={sectionVariants} key="morning-briefing">
          <MorningBriefing
            completedToday={completedToday}
            totalToday={todayTotal}
            userName={userName}
          />
        </motion.div>
      )}

      {isVisible('stats-grid') && (
        <motion.div variants={sectionVariants} key="stats-grid">
          <StatsGrid stats={stats} />
        </motion.div>
      )}

      {isVisible('kpi-strip') && (
        <motion.div variants={sectionVariants} key="kpi-strip">
          <KPIStrip items={kpiItems} />
        </motion.div>
      )}

      {isVisible('arias-pick') && (
        <motion.div variants={sectionVariants} key="arias-pick">
          <AriasPick insight={ariaInsight} />
        </motion.div>
      )}

      {isVisible('predictions') && !predLoading && (predTasks || predHabits || predSleep) && (
        <motion.div variants={sectionVariants} key="predictions">
          <div className="rounded-xl border border-[var(--border)] bg-[var(--background-card)] p-5">
            <div className="flex items-center gap-2 mb-4">
              <Brain size={16} className="text-[var(--accent-neon)]" aria-hidden="true" />
              <h3 className="text-sm font-display font-semibold text-[var(--text-primary)]">AI Predictions</h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {predTasks && (
                <div className="flex items-start gap-3 p-3 rounded-lg bg-[var(--background-elevated)]">
                  <AlertTriangle size={18} className="text-[var(--accent-warning)] shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-xs text-[var(--text-secondary)]">Task Completion</p>
                    <p className="text-sm font-medium text-[var(--text-primary)] mt-0.5">
                      {predTasks.at_risk_count} of {predTasks.total_pending} tasks at risk
                    </p>
                    <p className="text-xs text-[var(--text-tertiary)] mt-0.5">
                      {predTasks.high_completion} likely to complete
                    </p>
                  </div>
                </div>
              )}
              {predHabits && (
                <div className="flex items-start gap-3 p-3 rounded-lg bg-[var(--background-elevated)]">
                  <Flame size={18} className="text-[var(--accent-warning)] shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-xs text-[var(--text-secondary)]">Habit Risk</p>
                    <p className="text-sm font-medium text-[var(--text-primary)] mt-0.5">
                      {predHabits.at_risk_count} of {predHabits.total_active} habits at risk
                    </p>
                    <p className="text-xs text-[var(--text-tertiary)] mt-0.5">
                      {predHabits.predictions.filter(p => p.risk_level === 'Low').length} habits on track
                    </p>
                  </div>
                </div>
              )}
              {predSleep && predSleep.average_score > 0 && (
                <div className="flex items-start gap-3 p-3 rounded-lg bg-[var(--background-elevated)]">
                  <Moon size={18} className="text-accent-primary shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-xs text-[var(--text-secondary)]">Sleep Trend</p>
                    <p className="text-sm font-medium text-[var(--text-primary)] mt-0.5">
                      {predSleep.trend === 'improving' ? 'Improving' : predSleep.trend === 'declining' ? 'Declining' : 'Stable'} &middot; {predSleep.average_score}/100
                    </p>
                    <p className="text-xs text-[var(--text-tertiary)] mt-0.5">
                      {predSleep.recommendation}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {sentiment && sentiment.level !== 'low' && (
        <motion.div variants={sectionVariants} key="sentiment">
          <div className="rounded-xl border border-accent-warning/20 bg-accent-warning/5 p-4">
            <div className="flex items-start gap-3">
              <Heart size={18} className="text-[var(--accent-warning)] shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-[var(--text-primary)]">Check-in</p>
                <p className="text-xs text-[var(--text-secondary)] mt-1">{sentiment.message}</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {isVisible('task-preview') && (
        <motion.div variants={sectionVariants} key="task-preview" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <TaskPreviewList tasks={previewTasks} />
          </div>
          <div className="lg:col-span-1">
            <QuickActions />
          </div>
        </motion.div>
      )}

      {isVisible('activity-matrix') && (
        <motion.div variants={sectionVariants} key="activity-matrix">
          <ActivityMatrix data={activityData} />
        </motion.div>
      )}

      {/* Course Progress */}
      <motion.div variants={sectionVariants} key="course-progress">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--background-card)] p-5">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen size={16} className="text-[var(--accent-primary)]" aria-hidden="true" />
            <h3 className="text-sm font-display font-semibold text-[var(--text-primary)]">Course Progress</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { name: 'Machine Learning Fundamentals', progress: 65, status: 'On Track', color: 'var(--accent-success)' },
              { name: 'System Design & Architecture', progress: 30, status: 'Needs Attention', color: 'var(--priority-urgent)' },
              { name: 'Advanced TypeScript Patterns', progress: 88, status: 'Almost Done', color: 'var(--accent-primary)' },
            ].map(course => (
              <div key={course.name} className="flex flex-col items-center gap-3 p-4 rounded-lg bg-[var(--background-elevated)]">
                <ProgressRing progress={course.progress} size={80} strokeWidth={6} color={course.color}>
                  <span className="text-sm font-bold font-mono" style={{ color: course.color }}>{course.progress}%</span>
                </ProgressRing>
                <div className="text-center min-w-0">
                  <p className="text-xs font-medium text-[var(--text-primary)] truncate w-full">{course.name}</p>
                  <span
                    className="inline-block mt-1 text-[10px] font-mono font-medium px-1.5 py-0.5 rounded"
                    style={{
                      background: `color-mix(in oklab, ${course.color} 20%, transparent)`,
                      color: course.color,
                    }}
                  >
                    {course.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Opportunity Feed + Smart Schedule row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={sectionVariants} key="opportunity-feed">
          <div className="rounded-xl border border-[var(--border)] bg-[var(--background-card)] p-5 h-full">
            <div className="flex items-center gap-2 mb-4">
              <Radar size={16} className="text-[var(--accent-warning)]" aria-hidden="true" />
              <h3 className="text-sm font-display font-semibold text-[var(--text-primary)]">Opportunity Feed</h3>
            </div>
            <div className="space-y-3">
              {[
                { title: 'Google Summer of Code 2026', score: 92, desc: 'Your profile matches 3 projects in ML and distributed systems.' },
                { title: 'AI Research Intern — DeepMind', score: 78, desc: 'Strong match based on your research papers and coursework.' },
              ].map(opp => (
                <div key={opp.title} className="flex items-start gap-3 p-3 rounded-lg bg-[var(--background-elevated)]">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-[var(--text-primary)]">{opp.title}</p>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5 line-clamp-2">{opp.desc}</p>
                  </div>
                  <span
                    className="shrink-0 flex items-center justify-center min-w-[40px] h-6 rounded-full text-[11px] font-mono font-bold"
                    style={{
                      background: `color-mix(in oklab, ${opp.score >= 90 ? 'var(--accent-success)' : opp.score >= 70 ? 'var(--accent-warning)' : 'var(--priority-urgent)'} 20%, transparent)`,
                      color: opp.score >= 90 ? 'var(--accent-success)' : opp.score >= 70 ? 'var(--accent-warning)' : 'var(--priority-urgent)',
                    }}
                  >
                    {opp.score}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        <motion.div variants={sectionVariants} key="smart-schedule">
          <SmartScheduleCard
            slots={predSlots?.slots || []}
            bestHour={predSlots?.best_hour || 9}
            bestDay={predSlots?.best_day || 0}
            loading={predLoading}
          />
        </motion.div>
      </div>

      {/* Milestone Timeline */}
      <motion.div variants={sectionVariants} key="milestone-timeline">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--background-card)] p-5">
          <div className="flex items-center gap-2 mb-4">
            <Calendar size={16} className="text-[var(--accent-secondary)]" aria-hidden="true" />
            <h3 className="text-sm font-display font-semibold text-[var(--text-primary)]">Milestone Timeline</h3>
          </div>
          <Timeline
            items={[
              { id: 'm1', title: 'Project Proposal', date: 'Jun 10', status: 'completed' as const },
              { id: 'm2', title: 'Core Architecture', date: 'Jun 15', status: 'current' as const },
              { id: 'm3', title: 'MVP Development', date: 'Jun 30', status: 'upcoming' as const },
              { id: 'm4', title: 'Testing & QA', date: 'Jul 10', status: 'upcoming' as const },
              { id: 'm5', title: 'Production Launch', date: 'Jul 25', status: 'upcoming' as const },
            ]}
          />
        </div>
      </motion.div>
    </motion.div>
  )
}
