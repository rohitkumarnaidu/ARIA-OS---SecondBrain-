'use client'

import { useState, useEffect, useCallback } from 'react'
import { Brain, RefreshCw, Loader2, ChevronDown, ChevronRight } from 'lucide-react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/Card'

interface MemoryEntry {
  id: string
  content: string
  type: string
  confidence: number
  created_at: string
  metadata?: Record<string, any>
}

export function MemoryConsolidation() {
  const [entries, setEntries] = useState<MemoryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.get<MemoryEntry[]>('/api/v1/memory')
      setEntries(data ?? [])
    } catch {
      setError('Failed to load memory')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  return (
    <Card className="p-5 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain size={16} className="text-accent-primary" />
          <h3 className="text-sm font-semibold text-text-primary">Memory Consolidation</h3>
        </div>
        <button onClick={fetch} disabled={loading} className="p-1 rounded hover:bg-background-elevated text-text-tertiary hover:text-text-primary transition-colors">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {loading && !entries.length && (
        <div className="flex items-center justify-center py-6">
          <Loader2 size={18} className="animate-spin text-text-tertiary" />
        </div>
      )}

      {error && <p className="text-xs text-accent-error">{error}</p>}

      {!loading && !entries.length && !error && (
        <p className="text-xs text-text-tertiary">No memories yet. Chat with ARIA to build memory.</p>
      )}

      <div className="space-y-1 max-h-64 overflow-y-auto">
        {entries.map((entry) => (
          <div key={entry.id} className="group rounded-lg border border-border-default bg-background-page/50 p-2.5">
            <div className="flex items-start justify-between gap-2">
              <p className="text-xs text-text-primary leading-relaxed line-clamp-2">{entry.content}</p>
              <button
                onClick={() => {
                  const next = new Set(expanded)
                  next.has(entry.id) ? next.delete(entry.id) : next.add(entry.id)
                  setExpanded(next)
                }}
                className="shrink-0 p-0.5 rounded text-text-tertiary hover:text-text-primary"
              >
                {expanded.has(entry.id) ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
              </button>
            </div>
            <div className="flex items-center gap-2 mt-1.5">
              <span className="text-[10px] font-mono px-1 py-0.5 rounded bg-background-elevated text-text-tertiary">{entry.type}</span>
              <span className="text-[10px] text-text-tertiary">
                {Math.round(entry.confidence * 100)}%
              </span>
              <span className="text-[10px] text-text-tertiary ml-auto">
                {new Date(entry.created_at).toLocaleDateString()}
              </span>
            </div>
            {expanded.has(entry.id) && entry.metadata && (
              <pre className="mt-1.5 text-[10px] text-text-tertiary font-mono bg-background-elevated p-1.5 rounded overflow-x-auto">
                {JSON.stringify(entry.metadata, null, 1)}
              </pre>
            )}
          </div>
        ))}
      </div>
    </Card>
  )
}
