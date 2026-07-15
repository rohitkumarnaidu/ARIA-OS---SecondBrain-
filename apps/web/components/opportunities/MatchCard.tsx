'use client'

import { motion } from 'framer-motion'
import { ExternalLink } from 'lucide-react'
import { cn } from '@/components/ui/utils'
import type { Opportunity } from '@/types/opportunity'

interface MatchCardProps {
  match: Opportunity
  onViewDetail: (id: string) => void
}

const scoreColor = (score: number) => {
  if (score >= 90) return { bg: 'rgba(0, 255, 163, 0.15)', text: 'var(--accent-neon)', glow: '0 0 20px rgba(0, 255, 163, 0.3)' }
  if (score >= 70) return { bg: 'rgba(99, 102, 241, 0.15)', text: 'var(--accent-primary)', glow: '0 0 20px rgba(99, 102, 241, 0.3)' }
  return { bg: 'rgba(245, 158, 11, 0.15)', text: 'var(--accent-warning)', glow: '0 0 20px rgba(245, 158, 11, 0.3)' }
}

const typeLabels: Record<string, string> = {
  strategic: 'Strategic',
  financial: 'Financial',
  partnership: 'Partnership',
  career: 'Career',
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
      className="text-[10px] px-2 py-0.5 rounded-full font-medium"
      style={{
        backgroundColor: urgent ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
        color: urgent ? '#EF4444' : '#F59E0B',
      }}
    >
      Closes in {Math.round(hoursLeft)}h
    </span>
  )
}

export function MatchCard({ match, onViewDetail }: MatchCardProps) {
  const colors = scoreColor(match.score)

  return (
    <motion.div
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="card card-interactive group cursor-pointer"
      onClick={() => onViewDetail(match.id)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-[var(--text-primary)] truncate">
            {match.title}
          </h3>
          <p className="text-xs text-[var(--text-tertiary)] mt-0.5">{match.organization}</p>
        </div>
        <div
          className="flex-shrink-0 ml-3 w-12 h-12 rounded-xl flex items-center justify-center text-sm font-bold"
          style={{
            backgroundColor: colors.bg,
            color: colors.text,
            boxShadow: colors.glow,
          }}
        >
          {match.score}%
        </div>
      </div>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-[var(--background-elevated)] text-[var(--text-tertiary)] uppercase tracking-wider">
          {typeLabels[match.type]}
        </span>
        <span className={cn(
          'text-[10px] px-2 py-0.5 rounded-full capitalize',
          match.status === 'new' && 'bg-[color-mix(in_oklab,var(--accent-neon)_15%,transparent)] text-[var(--accent-neon)]',
          match.status === 'viewed' && 'bg-[color-mix(in_oklab,var(--accent-primary)_15%,transparent)] text-[var(--accent-primary)]',
          match.status === 'saved' && 'bg-[color-mix(in_oklab,var(--accent-warning)_15%,transparent)] text-[var(--accent-warning)]',
          match.status === 'applied' && 'bg-[color-mix(in_oklab,var(--accent-primary)_15%,transparent)] text-[var(--accent-primary)]',
          match.status === 'interviewing' && 'bg-[color-mix(in_oklab,var(--accent-info)_15%,transparent)] text-[var(--accent-info)]',
          match.status === 'accepted' && 'bg-[color-mix(in_oklab,var(--accent-success)_15%,transparent)] text-[var(--accent-success)]',
          match.status === 'declined' && 'bg-[color-mix(in_oklab,var(--accent-error)_15%,transparent)] text-[var(--accent-error)]',
        )}>
          {match.status}
        </span>
        {deadlineBadge(match.deadline)}
      </div>
      <p className="text-xs text-[var(--text-tertiary)] line-clamp-2 mb-3">
        {match.description}
      </p>
      <button
        onClick={(e) => { e.stopPropagation(); onViewDetail(match.id) }}
        className="flex items-center gap-1 text-xs font-medium text-[var(--accent-primary)] hover:underline"
      >
        <ExternalLink size={12} />
        View Details
      </button>
    </motion.div>
  )
}
