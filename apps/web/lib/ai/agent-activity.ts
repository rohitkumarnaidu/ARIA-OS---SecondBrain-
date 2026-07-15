'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '@/hooks/useAuth'
import type { Activity } from '@/components/ai/AgentActivityFeed'

interface AgentActivityOptions {
  maxActivities?: number
  pollIntervalMs?: number
  enabled?: boolean
}

interface AgentActivityApiItem {
  id: string
  agent_name: string
  status: string
  started_at: string
  completed_at?: string | null
  duration_ms?: number | null
  error_message?: string | null
  input_summary?: string | null
  output_summary?: string | null
}

const AGENT_DISPLAY_NAMES: Record<string, string> = {
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

function formatAgentName(raw: string): string {
  return AGENT_DISPLAY_NAMES[raw] || raw.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function buildAction(item: AgentActivityApiItem): string {
  if (item.status === 'running') {
    return `${formatAgentName(item.agent_name)} in progress`
  }
  if (item.status === 'failed') {
    return item.error_message || `${formatAgentName(item.agent_name)} encountered an error`
  }
  return item.output_summary || `${formatAgentName(item.agent_name)} task completed`
}

function mapApiItem(item: AgentActivityApiItem): Activity {
  return {
    id: item.id,
    agentName: formatAgentName(item.agent_name),
    action: buildAction(item),
    timestamp: item.started_at,
    status: item.status as 'running' | 'completed' | 'failed',
  }
}

export function useAgentActivity({
  maxActivities = 20,
  pollIntervalMs = 30000,
  enabled = true,
}: AgentActivityOptions = {}) {
  const { user } = useAuth()
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const fetchActivities = useCallback(async () => {
    if (!user?.id) return
    setLoading(true)
    try {
      const res = await fetch(`/api/v1/monitoring/activity?limit=${maxActivities}&offset=0`, {
        headers: { 'Content-Type': 'application/json' },
      })
      if (!res.ok) {
        setActivities([])
        return
      }
      const json = await res.json()
      const items: AgentActivityApiItem[] = json?.data ?? []
      setActivities(items.map(mapApiItem))
    } catch {
      setActivities([])
    } finally {
      setLoading(false)
    }
  }, [user?.id, maxActivities])

  useEffect(() => {
    if (!enabled) return
    fetchActivities()
    intervalRef.current = setInterval(fetchActivities, pollIntervalMs)
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [enabled, fetchActivities, pollIntervalMs])

  const clearActivities = useCallback(() => {
    setActivities([])
  }, [])

  return {
    activities,
    loading,
    refresh: fetchActivities,
    clearActivities,
  }
}