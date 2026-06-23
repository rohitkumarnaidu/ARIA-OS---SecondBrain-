'use client'

import { useEffect, useState } from 'react'
import { BarChart3, FileText } from 'lucide-react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/Card'

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

export default function TokenUsagePage() {
  const [data, setData] = useState<TokenUsageSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<TokenUsageSummary>('/api/v1/monitoring/token-usage/summary')
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-8 text-text-secondary">Loading...</div>

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <BarChart3 size={22} className="text-accent-primary" />
        <h1 className="text-2xl font-semibold text-text-primary">Token Usage & AI Monitoring</h1>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="text-xs text-text-secondary uppercase tracking-wider">Total Tokens</p>
          <p className="text-2xl font-bold text-text-primary mt-1">{(data?.total_tokens ?? 0).toLocaleString()}</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-text-secondary uppercase tracking-wider">API Calls</p>
          <p className="text-2xl font-bold text-text-primary mt-1">{data?.total_calls ?? 0}</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-text-secondary uppercase tracking-wider">Avg Response</p>
          <p className="text-2xl font-bold text-text-primary mt-1">{data?.avg_duration_ms ?? 0}ms</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-text-secondary uppercase tracking-wider">Est. Cost</p>
          <p className="text-2xl font-bold text-accent-neon mt-1">${data?.estimated_cost_usd?.toFixed(4) ?? '0.000'}</p>
        </Card>
      </div>
      <Card className="p-5">
        <h2 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
          <FileText size={14} /> Response Time Percentiles
        </h2>
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'P50', value: data?.p50_ms },
            { label: 'P95', value: data?.p95_ms },
            { label: 'P99', value: data?.p99_ms },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <p className="text-xs text-text-secondary">{label}</p>
              <p className="text-lg font-semibold text-text-primary">{value ?? 0}ms</p>
            </div>
          ))}
        </div>
      </Card>
      {data?.by_agent && Object.keys(data.by_agent).length > 0 && (
        <Card className="p-5">
          <h2 className="text-sm font-semibold text-text-primary mb-3">By Agent</h2>
          {Object.entries(data.by_agent).map(([agent, tokens]) => (
            <div key={agent} className="flex items-center justify-between py-1.5 border-b border-border-default last:border-0">
              <span className="text-sm text-text-primary">{agent}</span>
              <span className="text-sm text-text-secondary font-mono">{tokens.toLocaleString()} tokens</span>
            </div>
          ))}
        </Card>
      )}
    </div>
  )
}
