'use client'

import { useEffect, useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Moon, Clock, Sparkles, RefreshCw, Sun, ChevronRight } from 'lucide-react'
import { sleepService } from '@/lib/services'
import { Button } from '@/components/ui/Button'
import type { WindDownData } from '@/lib/types'

export function WindDownPanel() {
  const [data, setData] = useState<WindDownData | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const result = await sleepService.getWindDown()
      setData(result)
    } catch {
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const handleGenerate = async () => {
    setGenerating(true)
    await fetch()
    setGenerating(false)
  }

  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-lg bg-background-elevated" />
          <div className="h-5 w-48 rounded bg-background-elevated" />
        </div>
        <div className="space-y-2">
          <div className="h-4 w-full rounded bg-background-elevated" />
          <div className="h-4 w-3/4 rounded bg-background-elevated" />
          <div className="h-4 w-1/2 rounded bg-background-elevated" />
        </div>
      </div>
    )
  }

  if (!data || !data.available) {
    return (
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent-warning/10 border border-accent-warning/20 shrink-0">
            <Sun size={20} className="text-accent-warning" />
          </div>
          <div>
            <p className="text-sm text-text-primary font-medium">Good morning!</p>
            <p className="text-xs text-text-secondary">Check back tonight for your wind-down routine</p>
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      className="card relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-accent-neon/[0.04] to-transparent pointer-events-none" />

      <div className="relative">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent-neon/10 border border-accent-neon/20 shrink-0">
              <Moon size={20} className="text-accent-neon" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-text-primary flex items-center gap-1.5">
                <Sparkles size={14} className="text-accent-neon" />
                ARIA has a bedtime suggestion for you
              </h3>
              <p className="text-xs text-text-secondary mt-0.5">
                Wind-down routine for tonight
              </p>
            </div>
          </div>
          <Button variant="ghost" size="sm" loading={generating} onClick={handleGenerate}>
            <RefreshCw size={14} />
            Generate
          </Button>
        </div>

        <div className="flex flex-wrap gap-3 mb-4">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-background-elevated border border-border/50">
            <Moon size={14} className="text-accent-primary" />
            <div>
              <p className="text-[10px] text-text-tertiary uppercase tracking-wider">Bedtime</p>
              <p className="text-sm font-semibold text-text-primary">{data.suggested_bedtime}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-background-elevated border border-border/50">
            <Sun size={14} className="text-accent-warning" />
            <div>
              <p className="text-[10px] text-text-tertiary uppercase tracking-wider">Wake Up</p>
              <p className="text-sm font-semibold text-text-primary">{data.suggested_wake_time}</p>
            </div>
          </div>
        </div>

        {data.message && (
          <p className="text-sm text-text-secondary mb-3 leading-relaxed">{data.message}</p>
        )}

        {data.wind_down_routine && data.wind_down_routine.length > 0 && (
          <div className="mb-4">
            <h4 className="text-xs font-semibold text-text-primary uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Clock size={12} />
              Wind-Down Steps
            </h4>
            <div className="space-y-2">
              {data.wind_down_routine.map((step, i) => (
                <div key={i} className="flex items-start gap-2.5">
                  <div className="flex items-center justify-center w-6 h-6 rounded-full bg-accent-primary/10 border border-accent-primary/20 text-[10px] font-bold text-accent-primary shrink-0 mt-0.5">
                    {i + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      {step.time && (
                        <span className="text-[11px] font-mono text-accent-neon font-medium">{step.time}</span>
                      )}
                      <p className="text-sm text-text-primary">{step.action}</p>
                    </div>
                    {step.reason && (
                      <p className="text-xs text-text-tertiary mt-0.5">{step.reason}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.recommendations && data.recommendations.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-text-primary uppercase tracking-wider mb-2">Recommendations</h4>
            <div className="space-y-1.5">
              {data.recommendations.map((rec, i) => (
                <div key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                  <ChevronRight size={14} className="text-accent-primary shrink-0 mt-0.5" />
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
