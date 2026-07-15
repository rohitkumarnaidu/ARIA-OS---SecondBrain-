'use client'

import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, AlertOctagon, X } from 'lucide-react'
import { cn } from '@/components/ui/utils'

interface DeadlineInfo {
  id: string
  title: string
  hoursLeft: number
  severity: 'critical' | 'warning'
}

interface DeadlineAlertBannerProps {
  deadlines: DeadlineInfo[]
}

export function DeadlineAlertBanner({ deadlines }: DeadlineAlertBannerProps) {
  const [dismissed, setDismissed] = useState(false)

  const critical = useMemo(() => deadlines.filter((d) => d.severity === 'critical'), [deadlines])
  const warning = useMemo(() => deadlines.filter((d) => d.severity === 'warning'), [deadlines])

  if (dismissed || deadlines.length === 0) return null

  const isCritical = critical.length > 0
  const count = deadlines.length
  const label = isCritical ? 'critical' : 'upcoming'

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={cn(
          'flex items-center gap-3 px-4 py-3 rounded-xl border transition-all',
          isCritical
            ? 'bg-accent-danger/10 border-accent-danger/30'
            : 'bg-accent-warning/10 border-accent-warning/30'
        )}
      >
        {isCritical ? (
          <AlertOctagon size={20} className="text-accent-danger shrink-0" />
        ) : (
          <AlertTriangle size={20} className="text-accent-warning shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <p className={cn(
            'text-sm font-medium',
            isCritical ? 'text-accent-danger' : 'text-accent-warning'
          )}>
            {count} {label} deadline{count > 1 ? 's' : ''} closing soon
          </p>
          <p className="text-xs text-text-secondary mt-0.5">
            {critical.length > 0 && `${critical.length} critical`}
            {critical.length > 0 && warning.length > 0 && ' · '}
            {warning.length > 0 && `${warning.length} within 48h`}
          </p>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="shrink-0 w-7 h-7 rounded-lg flex items-center justify-center hover:bg-background-card-hover transition-colors"
          aria-label="Dismiss"
        >
          <X size={14} className="text-text-secondary" />
        </button>
      </motion.div>
    </AnimatePresence>
  )
}
