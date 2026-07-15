'use client'

import { useEffect, useState, useCallback } from 'react'
import {
  Brain, TrendingUp, Clock, BookOpen, BarChart3,
  RefreshCw, Sparkles, Target, Zap, Activity,
} from 'lucide-react'
import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { AIInsightCard } from '@/components/ai/AIInsightCard'
import { learningService } from '@/lib/services/learning'
import { showSuccess, showError } from '@/lib/toast'
import type { LearningInsightsResponse } from '@/lib/services/learning'

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

export default function LearningPage() {
  const [data, setData] = useState<LearningInsightsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const fetchData = useCallback(async (refresh = false) => {
    if (refresh) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }
    setError(null)
    try {
      const result = await learningService.getInsights(refresh)
      setData(result)
      if (refresh) {
        showSuccess('Learning analysis refreshed')
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load learning insights'
      setError(msg)
      if (refresh) {
        showError('Failed to refresh analysis')
      }
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    if (mounted) {
      fetchData()
    }
  }, [mounted, fetchData])

  if (!mounted) {
    return <div className="min-h-screen bg-background-page" />
  }

  const isEmpty = data && (
    data.progress?.tasks_created === 0 &&
    data.progress?.courses_enrolled === 0 &&
    data.progress?.active_habits === 0
  )

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton variant="text" className="h-8 w-64" />
            <Skeleton variant="text" className="h-4 w-48 mt-2" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="card" />
          ))}
        </div>
        <Skeleton variant="chart" />
        <Skeleton variant="card" />
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="space-y-6 pb-8"
    >
      <motion.div variants={sectionVariants}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl md:text-3xl font-display font-bold">
              <span className="text-gradient">Learning Insights</span>
            </h1>
            <p className="text-sm text-text-secondary mt-1">
              Pattern detection powered by ARIA Learning Agent
            </p>
          </div>
          <Button
            variant="primary"
            onClick={() => fetchData(true)}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
            {refreshing ? 'Analyzing...' : 'Refresh Analysis'}
          </Button>
        </div>
      </motion.div>

      {error && (
        <motion.div variants={sectionVariants}>
          <div className="bg-accent-danger/10 border border-accent-danger/30 text-text-primary px-4 py-3 rounded-lg">
            {error}
          </div>
        </motion.div>
      )}

      {!data || isEmpty ? (
        <motion.div variants={sectionVariants}>
          <EmptyState
            title="Not enough data yet"
            description="Continue using the system and check back after 2 weeks for personalized learning insights."
            icon={<Brain size={32} />}
          />
        </motion.div>
      ) : (
        <>
          <motion.div variants={sectionVariants}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Tasks Created (7d)', value: data.progress?.tasks_created ?? 0, icon: Target },
                { label: 'Completion Rate', value: `${data.productivity_patterns?.recent_completion_rate ?? 0}%`, icon: TrendingUp },
                { label: 'Courses Enrolled', value: data.progress?.courses_enrolled ?? 0, icon: BookOpen },
                { label: 'Active Habits', value: data.progress?.active_habits ?? 0, icon: Activity },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="card"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <stat.icon size={16} className="text-accent-primary" />
                    <span className="text-xs text-text-secondary">{stat.label}</span>
                  </div>
                  <div className="text-2xl font-bold text-text-primary font-display">{stat.value}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <motion.div variants={sectionVariants}>
              <Card>
                <CardHeader>
                  <CardTitle>
                    <span className="flex items-center gap-2">
                      <TrendingUp size={18} className="text-accent-primary" />
                      Productivity Patterns
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center py-2 border-b border-border">
                      <span className="text-sm text-text-secondary">Total Tasks</span>
                      <Badge>{data.productivity_patterns?.total_tasks ?? 0}</Badge>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-border">
                      <span className="text-sm text-text-secondary">Completed</span>
                      <Badge variant="success">{data.productivity_patterns?.completed_tasks ?? 0}</Badge>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-border">
                      <span className="text-sm text-text-secondary">Pending</span>
                      <Badge variant="warning">{data.productivity_patterns?.pending_tasks ?? 0}</Badge>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-border">
                      <span className="text-sm text-text-secondary">Recent Completion Rate</span>
                      <Badge variant={data.productivity_patterns?.recent_completion_rate >= 70 ? 'success' : 'warning'}>
                        {data.productivity_patterns?.recent_completion_rate ?? 0}%
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-sm text-text-secondary">Overall Completion Rate</span>
                      <Badge variant={data.productivity_patterns?.overall_completion_rate >= 70 ? 'success' : 'warning'}>
                        {data.productivity_patterns?.overall_completion_rate ?? 0}%
                      </Badge>
                    </div>
                  </div>
                  {data.productivity_patterns?.tasks_by_priority && (
                    <div className="mt-4 pt-3 border-t border-border">
                      <span className="text-xs text-text-tertiary">By Priority</span>
                      <div className="flex gap-2 mt-2">
                        {Object.entries(data.productivity_patterns.tasks_by_priority).map(([p, c]) => (
                          <Badge key={p} variant={p === 'high' ? 'error' : p === 'medium' ? 'warning' : 'info'}>
                            {p}: {c}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={sectionVariants}>
              <Card>
                <CardHeader>
                  <CardTitle>
                    <span className="flex items-center gap-2">
                      <BookOpen size={18} className="text-accent-secondary" />
                      Study Habits
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center py-2 border-b border-border">
                      <span className="text-sm text-text-secondary">Total Courses</span>
                      <Badge>{data.study_habits?.total_courses ?? 0}</Badge>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-border">
                      <span className="text-sm text-text-secondary">Active Habits</span>
                      <Badge variant="success">{data.study_habits?.active_habits ?? 0}</Badge>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-border">
                      <span className="text-sm text-text-secondary">Habit Consistency</span>
                      <Badge variant={data.study_habits?.habit_consistency >= 70 ? 'success' : 'warning'}>
                        {data.study_habits?.habit_consistency ?? 0}%
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-sm text-text-secondary">Best Streak</span>
                      <Badge variant="info">{data.study_habits?.best_streak ?? 0} days</Badge>
                    </div>
                  </div>
                  {data.study_habits?.courses_by_status && (
                    <div className="mt-4 pt-3 border-t border-border">
                      <span className="text-xs text-text-tertiary">Courses by Status</span>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {Object.entries(data.study_habits.courses_by_status).map(([s, c]) => (
                          <Badge key={s} variant={
                            s === 'completed' ? 'success' :
                            s === 'in_progress' ? 'info' :
                            s === 'not_started' ? 'warning' : 'default'
                          }>
                            {s.replace('_', ' ')}: {c}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </div>

          <motion.div variants={sectionVariants}>
            <Card>
              <CardHeader>
                <CardTitle>
                  <span className="flex items-center gap-2">
                    <Clock size={18} className="text-accent-neon" />
                    Peak Performance Times
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-background-elevated rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Zap size={14} className="text-accent-warning" />
                      <span className="text-xs text-text-secondary">Best Hours</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {data.peak_times?.peak_hours?.length > 0 ? (
                        data.peak_times.peak_hours.map((h) => (
                          <Badge key={h} variant="success">{h}</Badge>
                        ))
                      ) : (
                        <span className="text-sm text-text-tertiary">No data yet</span>
                      )}
                    </div>
                  </div>
                  <div className="bg-background-elevated rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <BarChart3 size={14} className="text-accent-primary" />
                      <span className="text-xs text-text-secondary">Deep Work (7d)</span>
                    </div>
                    <div className="text-xl font-bold text-text-primary font-display">
                      {data.peak_times?.deep_work_minutes_7d ?? 0}m
                    </div>
                  </div>
                  <div className="bg-background-elevated rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Activity size={14} className="text-accent-secondary" />
                      <span className="text-xs text-text-secondary">Deep Work Ratio</span>
                    </div>
                    <div className="text-xl font-bold text-text-primary font-display">
                      {data.peak_times?.deep_work_ratio ?? 0}%
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {data.insights && data.insights.length > 0 && (
            <motion.div variants={sectionVariants}>
              <Card>
                <CardHeader>
                  <CardTitle>
                    <span className="flex items-center gap-2">
                      <Sparkles size={18} className="text-accent-neon" />
                      AI-Generated Insights
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {data.insights.map((insight, i) => (
                      <AIInsightCard
                        key={i}
                        type={i === 0 ? 'insight' : i === 1 ? 'recommendation' : 'alert'}
                        title={`Insight ${i + 1}`}
                        description={insight}
                      />
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </>
      )}
    </motion.div>
  )
}
