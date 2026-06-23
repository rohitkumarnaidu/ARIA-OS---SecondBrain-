'use client'

import { memo, useRef, useState } from 'react'
import { clsx } from 'clsx'
import { motion } from 'framer-motion'

interface SuggestionChip {
  id: string
  label: string
  icon?: React.ReactNode
}

interface SuggestionChipsProps {
  suggestions: SuggestionChip[]
  onSelect: (id: string) => void
  className?: string
}

const chipVariants = {
  hidden: { opacity: 0, y: 6 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.05, duration: 0.25, ease: 'easeOut' },
  }),
}

export const SuggestionChips = memo(function SuggestionChips({ suggestions, onSelect, className }: SuggestionChipsProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  if (!suggestions.length) return null

  return (
    <div
      ref={scrollRef}
      role="listbox"
      aria-label="Suggestions"
      className={clsx(
        'flex gap-2 overflow-x-auto scrollbar-none py-1 px-0.5',
        'snap-x snap-mandatory scroll-smooth',
        '[-ms-overflow-style:none] [scrollbar-width:none]',
        className,
      )}
      onMouseDown={() => setIsDragging(true)}
      onMouseUp={() => setIsDragging(false)}
      onMouseLeave={() => setIsDragging(false)}
    >
      {suggestions.map((chip, i) => (
        <motion.button
          key={chip.id}
          custom={i}
          variants={chipVariants}
          initial="hidden"
          animate="visible"
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          role="option"
          aria-label={chip.label}
          aria-selected={false}
          onClick={() => onSelect(chip.id)}
          className={clsx(
            'relative shrink-0 snap-start flex items-center gap-1.5',
            'h-9 px-3 rounded-lg text-xs font-medium',
            'border border-border/60',
            'bg-background-card/60',
            'text-text-secondary hover:text-text-primary',
            'transition-colors duration-200',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background-dark',
            'min-w-[44px] min-h-[44px]',
            isDragging ? 'cursor-grabbing' : 'cursor-pointer',
          )}
          style={{
            backgroundImage: `linear-gradient(var(--background-card), var(--background-card)), linear-gradient(135deg, var(--accent-primary), var(--accent-neon))`,
            backgroundOrigin: 'border-box',
            backgroundClip: 'padding-box, border-box',
            border: '1px solid transparent',
          }}
        >
          {chip.icon && <span className="shrink-0 text-accent-primary/70" aria-hidden="true">{chip.icon}</span>}
          <span className="truncate max-w-[160px]">{chip.label}</span>
        </motion.button>
      ))}
    </div>
  )
})

export type { SuggestionChip, SuggestionChipsProps }
