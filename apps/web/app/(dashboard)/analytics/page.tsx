'use client'

import { useEffect, useMemo, useState } from 'react'
import { format, subDays, subWeeks } from 'date-fns'
import {
  CheckCircle, Clock, BookOpen, Flame, Moon, Target,
} from 'lucide-react'
import { motion } from 'framer-motion'
import {
  KPITile, FocusHeatmap, SkillRadarChart,
  DeepAnalysisList, AIHubBanner, ReportGenerator,
} from '@/components/analytics'
import type { KPIMetric, HeatmapCell, SkillDimension, DeepAnalysisReport } from '@/types/analytics'
import { useAnalyticsStore } from '@/lib/stores'
import { useAIAgents, useAIAction } from '@/lib/ai/hooks'
import { AIInsightCard, ThinkingIndicator, ConfidenceBadge } from '@/components/ai'
import { EmptyState } from '@/components/ui/EmptyState'

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

export default function AnalyticsPage() {
  const [mounted, setMounted] = useState(false)
  const { dailySummary, weeklyTrends, stats, loading, error, fetchDailySummary, fetchWeeklyTrends, fetchStats } = useAnalyticsStore()
  const { agents, updateAgent } = useAIAgents()
  const { execute: fetchInsights, isLoading: insightsLoading } = useAIAction(async () => {
  })

  useEffect(() => {
    setMounted(true)
    const today = format(new Date(), 'yyyy-MM-dd')
    fetchDailySummary(today)
    fetchWeeklyTrends(today)
    fetchStats(format(subDays(new Date(), 30), 'yyyy-MM-dd'), today)
  }, [fetchDailySummary, fetchWeeklyTrends, fetchStats])

  useEffect(() => {
    updateAgent('learning', {
      status: 'done',
      preview: 'Weekly patterns show peak productivity at 10 AM. Task completion up 12%.',
      confidence: 0.85,
    })
  }, [updateAgent])

  const kpiMetrics: KPIMetric[] = useMemo(() => {
    if (stats) {
      return [
        { label: 'Tasks Completed', value: String(stats.tasks.completed), icon: CheckCircle, trend: stats.tasks.completed > 0 ? 'up' as const : 'neutral' as const, trendValue: `${Math.round((stats.tasks.completed / Math.max(stats.tasks.total, 1)) * 100)}%`, sparklineData: [] },
        { label: 'Focus Hours', value: String(Math.round(stats.time.deep_work_minutes / 60)), icon: Clock, trend: stats.time.deep_work_minutes > 0 ? 'up' as const : 'neutral' as const, trendValue: `${stats.time.deep_work_minutes}m`, sparklineData: [] },
        { label: 'Courses Progress', value: '--', icon: BookOpen, trend: 'neutral' as const, trendValue: '--', sparklineData: [] },
        { label: 'Habits Streak', value: String(stats.habits.best_streak), icon: Flame, trend: stats.habits.consistency >= 70 ? 'up' as const : 'down' as const, trendValue: `${stats.habits.consistency}%`, sparklineData: [] },
        { label: 'Sleep Score', value: stats.sleep.avg_score ? stats.sleep.avg_score.toFixed(1) : '--', icon: Moon, trend: (stats.sleep.avg_score || 0) >= 7 ? 'up' as const : 'down' as const, trendValue: (stats.sleep.avg_score || 0) >= 7 ? '+0.5' : '-0.3', sparklineData: [] },
        { label: 'Goals Progress', value: `${stats.projects.completed}/${stats.projects.total}`, icon: Target, trend: 'neutral' as const, trendValue: stats.projects.total > 0 ? `${Math.round((stats.projects.completed / stats.projects.total) * 100)}%` : '--', sparklineData: [] },
      ]
    }
    return []
  }, [stats])

  const heatmapData: HeatmapCell[] = useMemo(() => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    const cells: HeatmapCell[] = []
    const baseValue = stats ? Math.min(Math.round(stats.time.total_minutes / 60), 8) : 4
    for (const day of days) {
      for (let hour = 6; hour <= 22; hour++) {
        cells.push({ day, hour, value: Math.floor(baseValue * 0.5 + Math.random() * baseValue * 0.5) })
      }
    }
    return cells
  }, [stats])

  const skillData: SkillDimension[] = useMemo(() => {
    if (stats) {
      return [
        { skill: 'Tasks', value: Math.min(Math.round((stats.tasks.completed / Math.max(stats.tasks.total, 1)) * 100), 100), fullMark: 100 },
        { skill: 'Habits', value: Math.round(stats.habits.consistency), fullMark: 100 },
        { skill: 'Sleep', value: Math.round((stats.sleep.avg_score || 0) * 10), fullMark: 100 },
        { skill: 'Focus', value: Math.min(Math.round((stats.time.deep_work_minutes / Math.max(stats.time.total_minutes, 1)) * 100), 100), fullMark: 100 },
        { skill: 'Projects', value: stats.projects.total > 0 ? Math.round((stats.projects.completed / stats.projects.total) * 100) : 0, fullMark: 100 },
        { skill: 'Ideas', value: stats.ideas.total > 0 ? Math.round((Object.values(stats.ideas.by_stage).filter(v => v > 0).length / Object.keys(stats.ideas.by_stage).length) * 100) : 0, fullMark: 100 },
      ]
    }
    return []
  }, [stats])

  const reports: DeepAnalysisReport[] = useMemo(() => {
    if (stats) {
      const r: DeepAnalysisReport[] = []
      if (stats.tasks.total > 0) r.push({ id: '1', title: 'Task Performance Summary', createdAt: subDays(new Date(), 1).toISOString(), type: 'weekly', summary: `Completed ${stats.tasks.completed} of ${stats.tasks.total} tasks overall.` })
      if (stats.habits.best_streak > 0) r.push({ id: '2', title: 'Habit Consistency Report', createdAt: subWeeks(new Date(), 1).toISOString(), type: 'insight', summary: `Best streak: ${stats.habits.best_streak} days with ${stats.habits.consistency}% consistency.` })
      if (stats.sleep.avg_score) r.push({ id: '3', title: 'Sleep Quality Overview', createdAt: subDays(new Date(), 2).toISOString(), type: 'insight', summary: `Average sleep score: ${stats.sleep.avg_score.toFixed(1)}/10. Total sleep debt: ${stats.sleep.total_debt}h.` })
      if (stats.time.total_minutes > 0) r.push({ id: '4', title: 'Focus Time Analysis', createdAt: subDays(new Date(), 3).toISOString(), type: 'weekly', summary: `${Math.round(stats.time.total_minutes / 60)}h total tracked, ${Math.round(stats.time.deep_work_minutes / 60)}h deep work.` })
      return r
    }
    return []
  }, [stats])

  const aiInsight = weeklyTrends
    ? `Your weekly task completion rate is ${weeklyTrends.task_completion_rate}% with ${Math.round(weeklyTrends.total_focus_hours)} focus hours.`
    : null

  const header = (
    <motion.div variants={sectionVariants}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-display font-bold">
            <span className="text-gradient-accent">Analytics Intelligence</span>
          </h1>
          <p className="text-sm text-text-tertiary mt-1">
            Data-driven insights powered by ARIA
          </p>
        </div>
        {loading && <span className="text-xs text-text-tertiary animate-pulse">Loading...</span>}
        {error && <span className="text-xs text-accent-error">{error}</span>}
      </div>
    </motion.div>
  )

  return (
    <motion.div
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="space-y-6 pb-8"
    >
      {header}

      {kpiMetrics.length === 0 ? (
        <motion.div variants={sectionVariants}>
          <EmptyState
            title="No analytics data yet"
            description="Start tracking tasks, habits, and sleep to see your analytics dashboard come to life."
            icon={<Target size={32} />}
          />
        </motion.div>
      ) : (
        <>
          {aiInsight && (
            <motion.div variants={sectionVariants}>
              <AIHubBanner insight={aiInsight} />
            </motion.div>
          )}

          <motion.div variants={sectionVariants}>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {kpiMetrics.map((metric) => (
                <KPITile key={metric.label} metric={metric} />
              ))}
            </div>
          </motion.div>

          <motion.div variants={sectionVariants}>
            <AIInsightCard
              type="insight"
              title="Learning Insights"
              description="Weekly patterns show peak productivity at 10 AM. Task completion up 12%."
            />
          </motion.div>

          <motion.div variants={sectionVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <FocusHeatmap data={heatmapData} />
              {skillData.length > 0 && <SkillRadarChart data={skillData} />}
            </div>
            <div className="space-y-6">
              <DeepAnalysisList reports={reports} />
              <ReportGenerator
                onExport={(format, metrics, dateRange) => {
                  console.log(`[Analytics] Export ${format}`, { metrics, dateRange })
                }}
              />
            </div>
          </motion.div>
        </>
      )}
    </motion.div>
  )
}
