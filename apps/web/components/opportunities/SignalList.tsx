'use client'

import { useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Target, TrendingUp, Briefcase, HelpingHand, ExternalLink } from 'lucide-react'
import { cn } from '@/components/ui/utils'
import type { Opportunity, OpportunityType } from '@/types/opportunity'

interface SignalListProps {
  signals: Opportunity[]
  activeCategory: string
  onCategoryChange: (cat: string) => void
  onViewDetail: (id: string) => void
}

const categories = [
  { key: 'all', label: 'All', icon: undefined },
  { key: 'strategic', label: 'Strategic', icon: Target },
  { key: 'financial', label: 'Financial', icon: TrendingUp },
  { key: 'partnership', label: 'Partnership', icon: HelpingHand },
  { key: 'career', label: 'Career', icon: Briefcase },
] as const

const typeIconMap: Record<OpportunityType, typeof Target> = {
  strategic: Target,
  financial: TrendingUp,
  partnership: HelpingHand,
  career: Briefcase,
}

const scoreBadgeColor = (score: number) => {
  if (score >= 90) return { bg: 'rgba(0, 255, 163, 0.15)', text: 'var(--accent-neon)' }
  if (score >= 70) return { bg: 'rgba(99, 102, 241, 0.15)', text: 'var(--accent-primary)' }
  return { bg: 'rgba(245, 158, 11, 0.15)', text: 'var(--accent-warning)' }
}

function deadlineBadge(deadline?: string) {
  if (!deadline) return null
  const now = Date.now()
  const deadlineMs = new Date(deadline).getTime()
  const hoursLeft = (deadlineMs - now) / 3600000
  if (hoursLeft <= 0 || hoursLeft > 48) return null

  const urgent = hoursLeft < 24
  return (
    <span
      className="text-[10px] px-1.5 py-0.5 rounded font-medium"
      style={{
        backgroundColor: urgent ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
        color: urgent ? '#EF4444' : '#F59E0B',
      }}
    >
      {Math.round(hoursLeft)}h
    </span>
  )
}

function SignalItem({
  signal,
  onViewDetail,
}: {
  signal: Opportunity
  onViewDetail: (id: string) => void
}) {
  const Icon = typeIconMap[signal.type]
  const colors = scoreBadgeColor(signal.score)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="flex items-center gap-3 p-3 rounded-xl bg-[var(--background-card)] border border-[var(--border)] hover:border-[var(--border-light)] transition-all cursor-pointer group"
      onClick={() => onViewDetail(signal.id)}
    >
      <div className="w-9 h-9 rounded-lg bg-[var(--background-elevated)] flex items-center justify-center flex-shrink-0">
        <Icon size={16} className="text-[var(--text-secondary)]" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h4 className="text-sm font-medium text-[var(--text-primary)] truncate">{signal.title}</h4>
          <span
            className="flex-shrink-0 text-[10px] font-bold px-1.5 py-0.5 rounded"
            style={{ backgroundColor: colors.bg, color: colors.text }}
          >
            {signal.score}%
          </span>
          {deadlineBadge(signal.deadline)}
        </div>
        <p className="text-xs text-[var(--text-tertiary)] truncate mt-0.5">{signal.organization}</p>
      </div>
      <button
        onClick={(e) => { e.stopPropagation(); onViewDetail(signal.id) }}
        className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-[var(--background-elevated)]"
      >
        <ExternalLink size={14} className="text-[var(--text-secondary)]" />
      </button>
    </motion.div>
  )
}

export function SignalList({
  signals,
  activeCategory,
  onCategoryChange,
  onViewDetail,
}: SignalListProps) {
  const filtered = useMemo(
    () => activeCategory === 'all' ? signals : signals.filter((s) => s.type === activeCategory),
    [signals, activeCategory]
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-1">
        {categories.map((cat) => {
          const Icon = cat.icon
          return (
            <button
              key={cat.key}
              onClick={() => onCategoryChange(cat.key)}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 whitespace-nowrap',
                activeCategory === cat.key
                  ? 'bg-[var(--accent-primary)] text-white shadow-[0_0_12px_var(--accent-primary)]'
                  : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:bg-[var(--background-elevated)]'
              )}
            >
              {Icon && <Icon size={14} />}
              {cat.label}
            </button>
          )
        })}
      </div>

      <div className="space-y-2">
        <AnimatePresence mode="popLayout">
          {filtered.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-8"
            >
              <Target size={32} className="text-[var(--text-tertiary)] mx-auto mb-2" />
              <p className="text-sm text-[var(--text-tertiary)]">No signals in this category</p>
            </motion.div>
          ) : (
            filtered.map((signal) => (
              <SignalItem key={signal.id} signal={signal} onViewDetail={onViewDetail} />
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
