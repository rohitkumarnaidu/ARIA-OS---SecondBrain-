'use client'

import { useState, useMemo } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { FileText, Sparkles, Filter } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import type { DeepAnalysisReport } from '@/types/analytics'

interface DeepAnalysisListProps {
  reports: DeepAnalysisReport[]
}

const typeConfig = {
  weekly: { label: 'Weekly', className: 'badge-primary' },
  monthly: { label: 'Monthly', className: 'badge-warning' },
  insight: { label: 'Insight', className: 'badge-info' },
} as const

export function DeepAnalysisList({ reports }: DeepAnalysisListProps) {
  const [filter, setFilter] = useState<string>('all')

  const types = useMemo(() => {
    const set = new Set(reports.map((r) => r.type))
    return ['all', ...Array.from(set)]
  }, [reports])

  const filtered = useMemo(
    () => (filter === 'all' ? reports : reports.filter((r) => r.type === filter)),
    [reports, filter],
  )

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-accent-warning/10 flex items-center justify-center">
            <FileText size={20} className="text-accent-warning" />
          </div>
          <div>
            <h2 className="text-lg font-display font-semibold text-text-primary">Deep Analysis</h2>
            <p className="text-xs text-text-tertiary">AI-generated reports</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Filter size={14} className="text-text-tertiary" />
          {types.map((t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={cn(
                'px-2.5 py-1 text-[10px] font-medium rounded-lg transition-all duration-200',
                filter === t
                  ? 'bg-accent-primary/15 text-accent-primary'
                  : 'text-text-tertiary hover:text-text-secondary hover:bg-background-elevated',
              )}
            >
              {t === 'all' ? 'All' : typeConfig[t as keyof typeof typeConfig]?.label ?? t}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2 max-h-[320px] overflow-y-auto pr-1 -mr-1 no-scrollbar">
        <AnimatePresence mode="popLayout">
          {filtered.map((report, i) => {
            const config = typeConfig[report.type]
            return (
              <motion.div
                key={report.id}
                layout
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ delay: i * 0.04 }}
                className={cn(
                  'p-3 rounded-xl border border-border/50 transition-all duration-200',
                  'hover:border-border hover:bg-background-elevated/30 cursor-pointer group',
                )}
              >
                <div className="flex items-start justify-between gap-3 mb-1.5">
                  <div className="flex items-center gap-2 min-w-0">
                    {report.type === 'insight' && (
                      <Sparkles size={14} className="text-accent-warning shrink-0" />
                    )}
                    <h3 className="text-sm font-medium text-text-primary truncate">
                      {report.title}
                    </h3>
                  </div>
                  <span className={cn('badge shrink-0', config.className)}>
                    {config.label}
                  </span>
                </div>
                <p className="text-xs text-text-tertiary line-clamp-2 leading-relaxed mb-2">
                  {report.summary}
                </p>
                <time
                  dateTime={report.createdAt}
                  className="text-[10px] text-text-disabled"
                >
                  {formatDistanceToNow(new Date(report.createdAt), { addSuffix: true })}
                </time>
              </motion.div>
            )
          })}
        </AnimatePresence>
        {filtered.length === 0 && (
          <p className="text-center text-sm text-text-tertiary py-8">No reports found</p>
        )}
      </div>
    </div>
  )
}
