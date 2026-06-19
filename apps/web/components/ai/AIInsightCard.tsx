'use client'

import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import { Lightbulb, Sparkles, AlertTriangle, ChevronRight } from 'lucide-react'

interface AIInsightCardProps {
  type: 'recommendation' | 'insight' | 'alert'
  icon?: React.ReactNode
  title: string
  description: string
  action?: { label: string; onClick: () => void }
  className?: string
}

const gradientMap = {
  recommendation: {
    bg: 'from-accent-primary/10 via-accent-primary/5 to-transparent',
    border: 'border-accent-primary/20 hover:border-accent-primary/40',
    overlay: 'bg-gradient-to-br from-accent-primary/8 to-transparent',
    glow: 'rgba(99,102,241,0.15)',
    defaultIcon: <Lightbulb size={16} className="text-accent-primary" aria-hidden="true" />,
  },
  insight: {
    bg: 'from-accent-neon/10 via-accent-neon/5 to-transparent',
    border: 'border-accent-neon/20 hover:border-accent-neon/40',
    overlay: 'bg-gradient-to-br from-accent-neon/[0.08] to-transparent',
    glow: 'rgba(0,255,163,0.15)',
    defaultIcon: <Sparkles size={16} className="text-accent-neon" aria-hidden="true" />,
  },
  alert: {
    bg: 'from-accent-warning/10 via-accent-warning/5 to-transparent',
    border: 'border-accent-warning/20 hover:border-accent-warning/40',
    overlay: 'bg-gradient-to-br from-accent-warning/8 to-transparent',
    glow: 'rgba(245,158,11,0.15)',
    defaultIcon: <AlertTriangle size={16} className="text-accent-warning" aria-hidden="true" />,
  },
}

const cardVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: 'easeOut' },
  },
}

export function AIInsightCard({ type, icon, title, description, action, className }: AIInsightCardProps) {
  const style = gradientMap[type]

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover={{ y: -1 }}
      className={clsx(
        'group relative overflow-hidden rounded-xl p-4',
        'bg-background-card border border-border',
        'transition-all duration-300',
        style.border,
        className,
      )}
      style={{ boxShadow: `0 1px 8px ${style.glow}` }}
    >
      <div className={clsx('absolute inset-0 opacity-40 group-hover:opacity-60 transition-opacity duration-500', style.overlay)} />

      <div className="relative flex items-start gap-3">
        <span className="shrink-0 flex items-center justify-center w-8 h-8 rounded-lg bg-background-elevated border border-border/60">
          {icon ?? style.defaultIcon}
        </span>

        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-text-primary font-display truncate">{title}</h4>
          <p className="mt-1 text-xs text-text-secondary leading-relaxed line-clamp-2">{description}</p>

          {action && (
            <motion.button
              initial={{ opacity: 0, y: 4 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              onClick={action.onClick}
              className={clsx(
                'mt-2 inline-flex items-center gap-1 text-xs font-medium',
                'transition-all duration-200',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background-dark',
                'min-h-[36px] px-2 -ml-2 rounded-md',
                type === 'recommendation' && 'text-accent-primary hover:text-accent-primaryHover hover:bg-accent-primary/10',
                type === 'insight' && 'text-accent-neon hover:text-accent-neon/80 hover:bg-accent-neon/10',
                type === 'alert' && 'text-accent-warning hover:text-accent-warning/80 hover:bg-accent-warning/10',
              )}
              aria-label={action.label}
            >
              {action.label}
              <ChevronRight size={12} aria-hidden="true" className="transition-transform group-hover:translate-x-0.5" />
            </motion.button>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export type { AIInsightCardProps }
