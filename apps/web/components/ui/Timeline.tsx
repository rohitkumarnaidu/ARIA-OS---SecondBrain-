'use client'

import { memo,  useId  } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { cn } from './utils'

interface TimelineItem {
  id: string
  title: string
  description?: string
  date?: string
  status?: 'completed' | 'current' | 'upcoming' | 'skipped'
  icon?: React.ReactNode
}

interface TimelineProps {
  items: TimelineItem[]
  orientation?: 'vertical' | 'horizontal'
  className?: string
}

const statusStyles = {
  completed: {
    node: 'bg-accent-success border-accent-success shadow-[0_0_8px_var(--accent-success)]',
    line: 'bg-gradient-to-b from-accent-success to-accent-success',
    label: 'text-accent-success',
  },
  current: {
    node: 'bg-accent-primary border-accent-primary shadow-[0_0_12px_var(--accent-primary)]',
    line: 'bg-gradient-to-b from-accent-primary to-surface-tertiary',
    label: 'text-accent-primary',
  },
  upcoming: {
    node: 'bg-transparent border-border-light',
    line: 'bg-surface-tertiary',
    label: 'text-text-tertiary',
  },
  skipped: {
    node: 'bg-transparent border-border border-dashed',
    line: 'bg-surface-tertiary bg-dashed',
    label: 'text-text-disabled',
  },
}

const TimelineNode = memo(function TimelineNode({ status = 'upcoming' }: { status?: TimelineItem['status'] }) {
  const style = statusStyles[status ?? 'upcoming']

  if (status === 'completed') {
    return (
      <div
        className={cn(
          'relative z-10 flex items-center justify-center w-5 h-5 rounded-full border-2',
          style.node,
        )}
        aria-hidden="true"
      >
        <motion.svg
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          width="10"
          height="10"
          viewBox="0 0 10 10"
          fill="none"
        >
          <motion.path
            d="M2 5L4 7L8 3"
            stroke="var(--background)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          />
        </motion.svg>
      </div>
    )
  }

  if (status === 'current') {
    return (
      <div className="relative z-10 flex items-center justify-center" aria-hidden="true">
        <motion.div
          className="w-5 h-5 rounded-full border-2"
          style={{ borderColor: 'var(--accent-primary)' }}
          animate={{ scale: [1, 1.15, 1] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute w-2.5 h-2.5 rounded-full"
          style={{ backgroundColor: 'var(--accent-primary)' }}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>
    )
  }

  if (status === 'skipped') {
    return (
      <div
        className={cn(
          'relative z-10 flex items-center justify-center w-5 h-5 rounded-full border-2',
          style.node,
        )}
        aria-hidden="true"
      >
        <div className="w-1.5 h-0.5 rounded-full bg-[var(--text-disabled)]" />
      </div>
    )
  }

  return (
    <div
      className={cn(
        'relative z-10 flex items-center justify-center w-5 h-5 rounded-full border-2',
        style.node,
      )}
      aria-hidden="true"
    />
  )
})

const Timeline = memo(function Timeline({ items, orientation = 'vertical', className }: TimelineProps) {
  const gradientId = useId()
  const reduced = useReducedMotion()

  if (items.length === 0) return null

  const isVertical = orientation === 'vertical'

  return (
    <div
      className={cn(
        isVertical ? 'flex flex-col' : 'flex flex-row overflow-x-auto pb-2 gap-0',
        className,
      )}
      role="list"
      aria-label="Timeline"
    >
      {items.map((item, index) => {
        const isLast = index === items.length - 1
        const style = statusStyles[item.status ?? 'upcoming']

        return (
          <div
            key={item.id}
            role="listitem"
            className={cn(
              'relative flex',
              isVertical ? 'flex-row pb-6 last:pb-0' : 'flex-col items-center shrink-0 min-w-[120px]',
            )}
          >
            {!isLast && (
              <div
                className={cn(
                  'absolute',
                  isVertical
                    ? 'left-[9px] top-5 w-[2px]'
                    : 'top-[9px] left-[50%] h-[2px]',
                  style.line,
                )}
                style={{
                  [isVertical ? 'height' : 'width']: reduced
                    ? '100%'
                    : undefined,
                }}
              >
                {!reduced && (
                  <motion.div
                    initial={{ [isVertical ? 'height' : 'width']: '0%' }}
                    whileInView={{ [isVertical ? 'height' : 'width']: '100%' }}
                    viewport={{ once: true, amount: 0.5 }}
                    transition={{ duration: 0.6, ease: 'easeOut' }}
                    className={cn(
                      isVertical ? 'w-full' : 'h-full',
                      'bg-gradient-to-b from-[var(--accent-primary)] to-[var(--accent-success)]',
                    )}
                  />
                )}
              </div>
            )}

            <div className={cn(isVertical ? 'flex-shrink-0 mr-3' : 'flex justify-center mb-2')}>
              <TimelineNode status={item.status} />
            </div>

            <motion.div
              initial={reduced ? undefined : { opacity: 0, y: isVertical ? 8 : 0, x: isVertical ? 0 : 8 }}
              whileInView={{ opacity: 1, y: 0, x: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.35, delay: index * 0.08, ease: 'easeOut' }}
              className={cn(
                'min-w-0',
                isVertical ? 'flex-1' : 'text-center px-2',
              )}
            >
              <div className="flex items-center gap-2 flex-wrap">
                <span className={cn('text-sm font-semibold text-[var(--text-primary)] font-display', item.status === 'skipped' && 'line-through opacity-50')}>
                  {item.title}
                </span>
                {item.icon && (
                  <span className="text-[var(--text-tertiary)] shrink-0" aria-hidden="true">
                    {item.icon}
                  </span>
                )}
              </div>
              {item.description && (
                <p className="text-xs text-[var(--text-secondary)] mt-0.5 line-clamp-2">
                  {item.description}
                </p>
              )}
              {item.date && (
                <p className={cn('text-[11px] mt-0.5 font-medium', style.label)}>
                  {item.date}
                </p>
              )}
            </motion.div>
          </div>
        )
      })}
    </div>
  )
})

export { Timeline }
export type { TimelineItem, TimelineProps }
