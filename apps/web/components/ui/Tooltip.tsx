'use client'

import { memo,  forwardRef, useState, useRef, useEffect  } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from './utils'

interface TooltipProps {
  children: React.ReactNode
  content: React.ReactNode
  side?: 'top' | 'bottom' | 'left' | 'right'
  className?: string
  delay?: number
  hideDelay?: number
}

const Tooltip = memo(forwardRef<HTMLDivElement, TooltipProps>(
  ({ children, content, side = 'top', className, delay = 300, hideDelay = 100 }, ref) => {
    const [visible, setVisible] = useState(false)
    const showTimer = useRef<ReturnType<typeof setTimeout>>()
    const hideTimer = useRef<ReturnType<typeof setTimeout>>()
    const triggerRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
      return () => {
        if (showTimer.current) clearTimeout(showTimer.current)
        if (hideTimer.current) clearTimeout(hideTimer.current)
      }
    }, [])

    const handleMouseEnter = () => {
      if (hideTimer.current) clearTimeout(hideTimer.current)
      showTimer.current = setTimeout(() => setVisible(true), delay)
    }

    const handleMouseLeave = () => {
      if (showTimer.current) clearTimeout(showTimer.current)
      hideTimer.current = setTimeout(() => setVisible(false), hideDelay)
    }

    const handleFocus = () => {
      if (hideTimer.current) clearTimeout(hideTimer.current)
      setVisible(true)
    }

    const handleBlur = () => {
      setVisible(false)
    }

    const sideStyles: Record<string, React.CSSProperties> = {
      top: { bottom: 'calc(100% + 6px)', left: '50%', transform: 'translateX(-50%)' },
      bottom: { top: 'calc(100% + 6px)', left: '50%', transform: 'translateX(-50%)' },
      left: { right: 'calc(100% + 6px)', top: '50%', transform: 'translateY(-50%)' },
      right: { left: 'calc(100% + 6px)', top: '50%', transform: 'translateY(-50%)' },
    }

    return (
      <div
        className="relative inline-flex"
        ref={ref}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onFocus={handleFocus}
        onBlur={handleBlur}
      >
        <div ref={triggerRef} tabIndex={0} role="button" aria-describedby={visible ? 'tooltip-content' : undefined}>
          {children}
        </div>
        <AnimatePresence>
          {visible && (
            <motion.div
              id="tooltip-content"
              role="tooltip"
              initial={{ opacity: 0, y: side === 'top' ? 4 : side === 'bottom' ? -4 : 0, x: side === 'left' ? 4 : side === 'right' ? -4 : 0 }}
              animate={{ opacity: 1, y: 0, x: 0 }}
              exit={{ opacity: 0, y: side === 'top' ? 4 : side === 'bottom' ? -4 : 0, x: side === 'left' ? 4 : side === 'right' ? -4 : 0 }}
              transition={{ duration: 0.12 }}
              className={cn(
                'absolute z-tooltip pointer-events-none rounded-lg px-2.5 py-1.5 text-xs leading-tight whitespace-nowrap',
                className,
              )}
              style={{
                ...sideStyles[side],
                background: 'rgba(19,19,23,0.95)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(70,70,79,0.3)',
                color: '#F1F5F9',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
              }}
            >
              {content}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  },
)
)
Tooltip.displayName = 'Tooltip'

export { Tooltip }
export type { TooltipProps }
