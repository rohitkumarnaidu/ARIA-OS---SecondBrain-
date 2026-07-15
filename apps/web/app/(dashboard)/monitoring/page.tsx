'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { BarChart3, RefreshCw, Clock, Database } from 'lucide-react'
import { motion } from 'framer-motion'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { cn } from '@/components/ui/utils'
import { REDMetricsCard } from './REDMetricsCard'
import { AgentBreakdownTable } from './AgentBreakdownTable'
import { ServiceHealthCards } from './ServiceHealthCards'

interface SparklinePoint {
  timestamp: string
  value: number
}

interface MetricSeries {
  current: number
  sparkline: SparklinePoint[]
  trend: 'up' | 'down' | 'neutral'
  changePercent: number
}

interface AgentMetric {
  name: string
  calls: number
  tokens: number
  avg_duration_ms: number
  error_rate: number
  cost_usd: number
}

interface ServiceHealth {
  status: 'ok' | 'degraded' | 'unavailable' | 'not_configured'
  uptime: number
  last_checked: string
  latency_ms: number
}

interface MetricsResponse {
  rate: MetricSeries
  errors: MetricSeries
  duration: {
    p50: MetricSeries
    p95: MetricSeries
    p99: MetricSeries
  }
  agents: AgentMetric[]
  services: Record<string, ServiceHealth>
}

interface TokenUsageSummary {
  total_tokens: number
  total_calls: number
  by_agent: Record<string, number>
  avg_duration_ms: number
  p50_ms: number
  p95_ms: number
  p99_ms?: number
  estimated_cost_usd: number
}

interface AICacheStats {
  exact_entries: number
  semantic_entries: number
  hits: number
  misses: number
  hit_rate: number
  token_savings: number
  estimated_cost_saved: number
  max_size: number
  ttl_seconds: number
}

type Period = '1h' | '6h' | '24h' | '7d'

const PERIODS: { value: Period; label: string }[] = [
  { value: '1h', label: '1h' },
  { value: '6h', label: '6h' },
  { value: '24h', label: '24h' },
  { value: '7d', label: '7d' },
]

export default function MonitoringPage() {
  const [tokenData, setTokenData] = useState<TokenUsageSummary | null>(null)
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null)
  const [aiCache, setAiCache] = useState<AICacheStats | null>(null)
  const [tokenLoading, setTokenLoading] = useState(true)
  const [metricsLoading, setMetricsLoading] = useState(true)
  const [period, setPeriod] = useState<Period>('24h')
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [countdown, setCountdown] = useState(30)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const countdownRef = useRef<NodeJS.Timeout | null>(null)

  const fetchData = useCallback(async (currentPeriod: Period) => {
    setMetricsLoading(true)
    try {
      const [tokenRes, metricsRes, aiCacheRes] = await Promise.all([
        api.get<TokenUsageSummary>('/api/v1/monitoring/token-usage/summary'),
        api.get<MetricsResponse>('/api/v1/monitoring/metrics', { params: { period: currentPeriod } }),
        api.get<{ cache: AICacheStats }>('/api/v1/monitoring/ai-cache').catch(() => null),
      ])
      setTokenData(tokenRes)
      setMetrics(metricsRes)
      if (aiCacheRes) setAiCache(aiCacheRes.cache)
    } catch {
      // Partial data is fine — each sub-component handles its own empty state
    } finally {
      setTokenLoading(false)
      setMetricsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData(period)
  }, [period, fetchData])

  // Auto-refresh every 30s
  useEffect(() => {
    if (!autoRefresh) {
      if (intervalRef.current) clearInterval(intervalRef.current)
      if (countdownRef.current) clearInterval(countdownRef.current)
      setCountdown(30)
      return
    }

    intervalRef.current = setInterval(() => {
      fetchData(period)
      setCountdown(30)
    }, 30000)

    countdownRef.current = setInterval(() => {
      setCountdown((c) => Math.max(0, c - 1))
    }, 1000)

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
      if (countdownRef.current) clearInterval(countdownRef.current)
    }
  }, [autoRefresh, period, fetchData])

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div className="flex items-center gap-3">
          <BarChart3 size={22} className="text-accent-primary" />
          <h1 className="text-2xl font-semibold text-text-primary">Monitoring</h1>
        </div>
        <div className="flex items-center gap-3">
          {/* Period selector */}
          <div className="flex items-center gap-1 bg-background-elevated rounded-lg p-0.5">
            {PERIODS.map((p) => (
              <button
                key={p.value}
                onClick={() => setPeriod(p.value)}
                className={cn(
                  'px-3 py-1.5 text-xs font-medium rounded-md transition-all',
                  period === p.value
                    ? 'bg-accent-primary/15 text-accent-primary'
                    : 'text-text-tertiary hover:text-text-secondary',
                )}
              >
                {p.label}
              </button>
            ))}
          </div>
          {/* Auto-refresh toggle */}
          <button
            onClick={() => setAutoRefresh((r) => !r)}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all',
              autoRefresh
                ? 'bg-accent-primary/15 text-accent-primary'
                : 'bg-background-elevated text-text-tertiary hover:text-text-secondary',
            )}
          >
            <RefreshCw size={12} className={cn(autoRefresh && 'text-accent-primary')} />
            {autoRefresh ? `${countdown}s` : 'Auto'}
          </button>
        </div>
      </motion.div>

      {/* Token usage summary (existing) */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <p className="text-xs text-text-secondary uppercase tracking-wider">Total Tokens</p>
            <p className="text-2xl font-bold text-text-primary mt-1">
              {(tokenData?.total_tokens ?? 0).toLocaleString()}
            </p>
          </Card>
          <Card className="p-4">
            <p className="text-xs text-text-secondary uppercase tracking-wider">API Calls</p>
            <p className="text-2xl font-bold text-text-primary mt-1">{tokenData?.total_calls ?? 0}</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs text-text-secondary uppercase tracking-wider">Avg Response</p>
            <p className="text-2xl font-bold text-text-primary mt-1">{tokenData?.avg_duration_ms ?? 0}ms</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs text-text-secondary uppercase tracking-wider">Est. Cost</p>
            <p className="text-2xl font-bold text-accent-neon mt-1">
              ${tokenData?.estimated_cost_usd?.toFixed(4) ?? '0.000'}
            </p>
          </Card>
        </div>
      </motion.div>

      {/* Response time percentiles (existing) */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="p-5">
          <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
            <Clock size={14} /> Response Time Percentiles
          </h2>
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: 'P50', value: tokenData?.p50_ms },
              { label: 'P95', value: tokenData?.p95_ms },
              { label: 'P99', value: tokenData?.p99_ms },
            ].map(({ label, value }) => (
              <div key={label} className="text-center">
                <p className="text-xs text-text-secondary">{label}</p>
                <p className="text-lg font-semibold text-text-primary">{value ?? 0}ms</p>
              </div>
            ))}
          </div>
        </Card>
      </motion.div>

      {/* RED Metrics Dashboard */}
      {metrics && (
        <REDMetricsCard
          rate={metrics.rate}
          errors={metrics.errors}
          duration={metrics.duration}
          loading={metricsLoading}
        />
      )}

      {/* Agent breakdown table */}
      {metrics && (
        <AgentBreakdownTable agents={metrics.agents} loading={metricsLoading} />
      )}

      {/* Service health cards */}
      {metrics && (
        <section>
          <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
            <BarChart3 size={14} /> Service Health
          </h2>
          <ServiceHealthCards services={metrics.services} loading={metricsLoading} />
        </section>
      )}

      {/* AI Cache Stats */}
      {aiCache && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="p-5">
            <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
              <Database size={14} className="text-accent-neon" /> AI Response Cache
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div>
                <p className="text-xs text-text-secondary uppercase tracking-wider">Hit Rate</p>
                <p className="text-lg font-bold text-accent-neon mt-1">{aiCache.hit_rate}%</p>
              </div>
              <div>
                <p className="text-xs text-text-secondary uppercase tracking-wider">Token Savings</p>
                <p className="text-lg font-bold text-text-primary mt-1">
                  {aiCache.token_savings.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-xs text-text-secondary uppercase tracking-wider">Est. Cost Saved</p>
                <p className="text-lg font-bold text-text-primary mt-1">
                  ${aiCache.estimated_cost_saved.toFixed(4)}
                </p>
              </div>
              <div>
                <p className="text-xs text-text-secondary uppercase tracking-wider">Exact Entries</p>
                <p className="text-lg font-bold text-text-primary mt-1">{aiCache.exact_entries}</p>
              </div>
              <div>
                <p className="text-xs text-text-secondary uppercase tracking-wider">Semantic Entries</p>
                <p className="text-lg font-bold text-text-primary mt-1">{aiCache.semantic_entries}</p>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* By agent token breakdown (existing) */}
      {tokenData?.by_agent && Object.keys(tokenData.by_agent).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="p-5">
            <h2 className="text-sm font-semibold text-text-primary mb-3">Token Usage by Agent</h2>
            {Object.entries(tokenData.by_agent).map(([agent, tokens]) => (
              <div
                key={agent}
                className="flex items-center justify-between py-1.5 border-b border-border-default last:border-0"
              >
                <span className="text-sm text-text-primary">{agent}</span>
                <span className="text-sm text-text-secondary font-mono">{tokens.toLocaleString()} tokens</span>
              </div>
            ))}
          </Card>
        </motion.div>
      )}
    </div>
  )
}
