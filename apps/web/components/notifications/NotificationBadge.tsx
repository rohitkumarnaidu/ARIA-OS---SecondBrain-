'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/components/ui/utils'

interface NotificationBadgeProps {
  count: number
  className?: string
}

export function NotificationBadge({ count, className }: NotificationBadgeProps): JSX.Element {
  return (
    <AnimatePresence mode="wait">
      {count > 0 && (
        <motion.span
          key={count}
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.5, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 500, damping: 25 }}
          className={cn(
            'absolute -top-0.5 -right-0.5 flex items-center justify-center',
            'w-[18px] h-[18px] rounded-full',
            'font-mono text-[10px] font-bold leading-none text-white',
            className,
          )}
          style={{ background: 'var(--priority-urgent)' }}
          role="status"
          aria-label={`${count} unread notifications`}
        >
          <motion.span
            key={`ping-${count}`}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 400, damping: 15 }}
          >
            {count > 99 ? '99+' : count}
          </motion.span>
        </motion.span>
      )}
    </AnimatePresence>
  )
}
