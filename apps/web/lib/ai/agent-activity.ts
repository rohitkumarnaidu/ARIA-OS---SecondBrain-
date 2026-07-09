'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import type { Activity } from '@/components/ai/AgentActivityFeed'

interface AgentActivityOptions {
  maxActivities?: number
}

const AGENT_ACTIONS: Record<string, string> = {
  planner: 'Planning your schedule',
  memory: 'Consolidating memories',
  learning: 'Detecting patterns',
  briefing: 'Generating morning briefing',
  opportunity: 'Scanning opportunities',
  sleep: 'Analyzing sleep patterns',
  weekly_review: 'Generating weekly review',
  nudge: 'Checking course progress',
  roadmap: 'Optimizing skill roadmap',
}

const agentNameMap: Record<string, string> = {
  planner: 'Planner',
  memory: 'Memory',
  learning: 'Learning',
  briefing: 'Daily Briefing',
  opportunity: 'Opportunity Radar',
  sleep: 'Sleep Coach',
  weekly_review: 'Weekly Review',
  nudge: 'Nudge Engine',
  roadmap: 'Roadmap Optimizer',
}

let activityCounter = 0

export function useAgentActivity({ maxActivities = 20 }: AgentActivityOptions = {}) {
  const [activities, setActivities] = useState<Activity[]>([])
  const pendingComplete = useRef<Map<string, NodeJS.Timeout>>(new Map())

  const addActivity = useCallback((agentId: string, action: string) => {
    activityCounter++
    const id = `act-${Date.now()}-${activityCounter}`
    const agentName = agentNameMap[agentId] || agentId

    const newActivity: Activity = {
      id,
      agentName,
      action,
      timestamp: new Date().toISOString(),
      status: 'running',
    }

    setActivities(prev => [newActivity, ...prev].slice(0, maxActivities))
    return id
  }, [maxActivities])

  const completeActivity = useCallback((activityId: string, status: 'completed' | 'failed' = 'completed') => {
    setActivities(prev =>
      prev.map(a => (a.id === activityId ? { ...a, status } : a))
    )
  }, [])

  const agentStarted = useCallback((agentId: string, customAction?: string) => {
    const action = customAction || AGENT_ACTIONS[agentId] || `${agentNameMap[agentId] || agentId} running`
    const id = addActivity(agentId, action)

    const timeout = setTimeout(() => {
      completeActivity(id, 'completed')
      pendingComplete.current.delete(id)
    }, 3000 + Math.random() * 4000)

    pendingComplete.current.set(id, timeout)
    return id
  }, [addActivity, completeActivity])

  const agentFailed = useCallback((agentId: string, error?: string) => {
    const action = error || AGENT_ACTIONS[agentId] || `${agentNameMap[agentId] || agentId} failed`
    const id = addActivity(agentId, action)
    completeActivity(id, 'failed')
    return id
  }, [addActivity, completeActivity])

  const agentCompleted = useCallback((agentId: string, result?: string) => {
    const action = result || AGENT_ACTIONS[agentId] || `${agentNameMap[agentId] || agentId} completed`
    const id = addActivity(agentId, action)
    completeActivity(id, 'completed')
    return id
  }, [addActivity, completeActivity])

  const clearActivities = useCallback(() => {
    pendingComplete.current.forEach(timeout => clearTimeout(timeout))
    pendingComplete.current.clear()
    setActivities([])
  }, [])

  useEffect(() => {
    const timeouts = pendingComplete.current
    return () => {
      timeouts.forEach(timeout => clearTimeout(timeout))
      timeouts.clear()
    }
  }, [])

  return {
    activities,
    agentStarted,
    agentFailed,
    agentCompleted,
    clearActivities,
  }
}
