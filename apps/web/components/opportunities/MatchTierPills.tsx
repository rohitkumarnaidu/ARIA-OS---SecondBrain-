'use client'

import { cn } from '@/components/ui/utils'

interface MatchTierPillsProps {
  activeTier: string | null
  onTierChange: (tier: string | null) => void
  counts: { exceptional: number; strong: number; moderate: number }
}

const tiers = [
  { key: 'exceptional', label: '≥90% Exceptional', color: 'var(--accent-neon)', glow: '0 0 12px var(--accent-neon)' },
  { key: 'strong', label: '70-89% Strong', color: 'var(--accent-primary)', glow: '0 0 12px var(--accent-primary)' },
  { key: 'moderate', label: '50-69% Moderate', color: 'var(--accent-warning)', glow: '0 0 12px var(--accent-warning)' },
] as const

export function MatchTierPills({ activeTier, onTierChange, counts }: MatchTierPillsProps) {
  const countMap: Record<string, number> = {
    exceptional: counts.exceptional,
    strong: counts.strong,
    moderate: counts.moderate,
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <button
        onClick={() => onTierChange(null)}
        className={cn(
          'px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200',
          'border border-[var(--border-subtle)]',
          activeTier === null
            ? 'bg-[var(--accent-primary)] text-white border-[var(--accent-primary)] shadow-[0_0_12px_var(--accent-primary)]'
            : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:border-[var(--border-light)]'
        )}
      >
        All
      </button>
      {tiers.map((tier) => (
        <button
          key={tier.key}
          onClick={() => onTierChange(activeTier === tier.key ? null : tier.key)}
          className={cn(
            'px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200',
            'border',
            activeTier === tier.key
              ? 'text-white'
              : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]'
          )}
          style={{
            backgroundColor: activeTier === tier.key ? tier.color : 'transparent',
            borderColor: activeTier === tier.key ? tier.color : 'var(--border-subtle)',
            boxShadow: activeTier === tier.key ? tier.glow : undefined,
          }}
        >
          {tier.label}
          <span className="ml-1.5 opacity-70">({countMap[tier.key]})</span>
        </button>
      ))}
    </div>
  )
}
