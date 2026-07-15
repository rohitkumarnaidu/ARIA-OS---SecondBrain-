'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ExternalLink, Heart, X, Target, TrendingUp, Briefcase, HelpingHand } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/components/ui/utils'
import { ScoreTooltip } from './ScoreTooltip'
import type { Opportunity, OpportunityStatus } from '@/types/opportunity'

interface OpportunityDetailProps {
  opportunity: Opportunity | null
  onClose: () => void
  onSave: (id: string) => void
  onStatusChange: (id: string, status: OpportunityStatus) => void
}

const typeIconMap = {
  strategic: Target,
  financial: TrendingUp,
  partnership: HelpingHand,
  career: Briefcase,
}

const typeLabels: Record<string, string> = {
  strategic: 'Strategic',
  financial: 'Financial',
  partnership: 'Partnership',
  career: 'Career',
}

const scoreColor = (score: number) => {
  if (score >= 90) return { bg: 'rgba(0, 255, 163, 0.15)', text: 'var(--accent-neon)', glow: '0 0 30px rgba(0, 255, 163, 0.4)' }
  if (score >= 70) return { bg: 'rgba(99, 102, 241, 0.15)', text: 'var(--accent-primary)', glow: '0 0 30px rgba(99, 102, 241, 0.4)' }
  return { bg: 'rgba(245, 158, 11, 0.15)', text: 'var(--accent-warning)', glow: '0 0 30px rgba(245, 158, 11, 0.4)' }
}

const barColor = (value: number) => {
  if (value >= 90) return 'var(--accent-neon)'
  if (value >= 70) return 'var(--accent-primary)'
  if (value >= 50) return 'var(--accent-warning)'
  return 'var(--accent-error)'
}

export function OpportunityDetail({
  opportunity,
  onClose,
  onSave,
  onStatusChange,
}: OpportunityDetailProps) {
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (opportunity) {
      setSaved(false)
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [opportunity])

  if (!opportunity) return null

  const colors = scoreColor(opportunity.score)
  const Icon = typeIconMap[opportunity.type]

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          className="absolute right-0 top-0 h-full w-full max-w-lg bg-[var(--background)] border-l border-[var(--border)] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="p-6 space-y-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div
                  className="w-16 h-16 rounded-2xl flex items-center justify-center text-xl font-bold"
                  style={{ backgroundColor: colors.bg, color: colors.text, boxShadow: colors.glow }}
                >
                  {opportunity.score}%
                </div>
                <div>
                  <h2 className="text-lg font-bold text-[var(--text-primary)]">{opportunity.title}</h2>
                  <p className="text-sm text-[var(--text-tertiary)]">{opportunity.organization}</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-[var(--background-elevated)] transition-colors"
              >
                <X size={18} className="text-[var(--text-secondary)]" />
              </button>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <span className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-[var(--background-elevated)] text-[var(--text-tertiary)]">
                <Icon size={12} />
                {typeLabels[opportunity.type]}
              </span>
              <span className={cn(
                'text-xs px-2.5 py-1 rounded-full capitalize',
                opportunity.status === 'new' && 'bg-[color-mix(in_oklab,var(--accent-neon)_15%,transparent)] text-[var(--accent-neon)]',
                opportunity.status === 'viewed' && 'bg-[color-mix(in_oklab,var(--accent-primary)_15%,transparent)] text-[var(--accent-primary)]',
                opportunity.status === 'saved' && 'bg-[color-mix(in_oklab,var(--accent-warning)_15%,transparent)] text-[var(--accent-warning)]',
                opportunity.status === 'applied' && 'bg-[color-mix(in_oklab,var(--accent-primary)_15%,transparent)] text-[var(--accent-primary)]',
                opportunity.status === 'interviewing' && 'bg-[color-mix(in_oklab,var(--accent-info)_15%,transparent)] text-[var(--accent-info)]',
                opportunity.status === 'accepted' && 'bg-[color-mix(in_oklab,var(--accent-success)_15%,transparent)] text-[var(--accent-success)]',
                opportunity.status === 'declined' && 'bg-[color-mix(in_oklab,var(--accent-error)_15%,transparent)] text-[var(--accent-error)]',
              )}>
                {opportunity.status}
              </span>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2">Description</h3>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                {opportunity.description}
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-[var(--text-primary)]">Match Breakdown</h3>
              </div>
              <div className="space-y-3">
                {opportunity.matchBreakdown.map((criterion) => (
                  <div key={criterion.label}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-[var(--text-secondary)]">{criterion.label}</span>
                      <span
                        className="text-xs font-semibold tabular-nums"
                        style={{ color: barColor(criterion.value) }}
                      >
                        {criterion.value}%
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-[var(--background-elevated)] overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{
                          width: `${criterion.value}%`,
                          backgroundColor: barColor(criterion.value),
                          boxShadow: `0 0 8px ${barColor(criterion.value)}`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2">
              {opportunity.url && (
                <Button asChild variant="primary" className="flex-1">
                  <a
                    href={opportunity.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <ExternalLink size={16} />
                    Apply
                  </a>
                </Button>
              )}
              <Button
                onClick={() => { setSaved(!saved); onSave(opportunity.id) }}
                variant="secondary"
                className={cn(
                  'w-11 h-11 p-0 flex items-center justify-center',
                  saved && 'text-[var(--accent-error)]'
                )}
              >
                <Heart size={18} fill={saved ? 'var(--accent-error)' : 'none'} />
              </Button>
              <Button onClick={onClose} variant="ghost" className="px-3">
                Dismiss
              </Button>
            </div>

            <div>
              <label htmlFor="opportunity-status" className="block text-xs font-medium text-[var(--text-tertiary)] mb-1.5">
                Status
              </label>
              <select
                id="opportunity-status"
                value={opportunity.status}
                onChange={(e) => onStatusChange(opportunity.id, e.target.value as OpportunityStatus)}
                className="w-full bg-[var(--background-elevated)] border border-[var(--border)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)]"
              >
                <option value="new">New</option>
                <option value="viewed">Viewed</option>
                <option value="saved">Saved</option>
                <option value="applied">Applied</option>
                <option value="interviewing">Interviewing</option>
                <option value="accepted">Accepted</option>
                <option value="declined">Declined</option>
              </select>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
