'use client'

import { memo } from 'react'
import { motion } from 'framer-motion'
import { Wallet, TrendingUp, Clock, Trash2 } from 'lucide-react'
import { cn } from '@/components/ui/utils'
import { Button } from '@/components/ui/Button'
import type { IncomeEntry } from '@/lib/types'

interface IncomeCardProps {
  entry: IncomeEntry
  onEdit?: (entry: IncomeEntry) => void
  onDelete?: (id: string) => void
}

export const IncomeCard = memo(function IncomeCard({ entry, onEdit, onDelete }: IncomeCardProps) {
  const formattedAmount = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(entry.amount)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="card card-interactive group"
      role="article"
      aria-label={`Income entry: ${formattedAmount} from ${entry.source_type}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0 flex-1">
          <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-accent-success/10 flex items-center justify-center">
            <Wallet size={20} className="text-accent-success" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h3
                className="font-medium text-text-primary truncate group-hover:text-accent-primary transition-colors cursor-pointer"
                onClick={() => onEdit?.(entry)}
                onKeyDown={(e) => { if (e.key === 'Enter') onEdit?.(entry) }}
                tabIndex={0}
                role="button"
                aria-label={`Edit income entry from ${entry.source_type}`}
              >
                {entry.source_type}
              </h3>
              {entry.effective_hourly_rate && (
                <span className="flex items-center gap-1 text-xs text-accent-success">
                  <TrendingUp size={12} aria-hidden="true" />
                  ${entry.effective_hourly_rate}/hr
                </span>
              )}
            </div>
            {entry.description && (
              <p className="text-sm text-text-tertiary mt-0.5 line-clamp-1">{entry.description}</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="text-lg font-display font-bold text-accent-success">
            {formattedAmount}
          </span>
          {onDelete && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(entry.id)}
              aria-label={`Delete income entry from ${entry.source_type}`}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <Trash2 size={16} className="text-accent-error" />
            </Button>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3 mt-3 flex-wrap text-xs text-text-tertiary">
        {entry.platform && (
          <span className="px-2 py-0.5 rounded bg-background-elevated text-text-secondary border border-border">
            {entry.platform}
          </span>
        )}
        <span className="flex items-center gap-1">
          {new Date(entry.date).toLocaleDateString()}
        </span>
        {entry.hours_spent && (
          <span className="flex items-center gap-1">
            <Clock size={12} aria-hidden="true" />
            {entry.hours_spent}h spent
          </span>
        )}
      </div>
    </motion.div>
  )
})
