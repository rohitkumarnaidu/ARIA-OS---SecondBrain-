'use client'

import { memo,  forwardRef, useState, useRef, useEffect, useCallback  } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from './utils'

interface PopoverProps {
  trigger: React.ReactNode
  children: React.ReactNode
  open?: boolean
  onOpenChange?: (open: boolean) => void
  align?: 'start' | 'center' | 'end'
  side?: 'top' | 'bottom' | 'left' | 'right'
  className?: string
}

const Popover = memo(forwardRef<HTMLDivElement, PopoverProps>(
  ({ trigger, children, open: controlledOpen, onOpenChange, align = 'center', side = 'bottom', className }, ref) => {
    const [internalOpen, setInternalOpen] = useState(false)
    const isOpen = controlledOpen ?? internalOpen
    const setOpen = onOpenChange ?? setInternalOpen
    const triggerRef = useRef<HTMLDivElement>(null)
    const contentRef = useRef<HTMLDivElement>(null)

    const handleClickOutside = useCallback((e: MouseEvent) => {
      if (
        contentRef.current &&
        !contentRef.current.contains(e.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(e.target as Node)
      ) {
        setOpen(false)
      }
    }, [setOpen])

    useEffect(() => {
      if (isOpen) {
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
      }
    }, [isOpen, handleClickOutside])

    const sideStyles: Record<string, React.CSSProperties> = {
      top: { bottom: 'calc(100% + 8px)', left: align === 'center' ? '50%' : align === 'end' ? 'auto' : '0', right: align === 'end' ? '0' : 'auto', transform: align === 'center' ? 'translateX(-50%)' : 'none' },
      bottom: { top: 'calc(100% + 8px)', left: align === 'center' ? '50%' : align === 'end' ? 'auto' : '0', right: align === 'end' ? '0' : 'auto', transform: align === 'center' ? 'translateX(-50%)' : 'none' },
      left: { right: 'calc(100% + 8px)', top: align === 'center' ? '50%' : align === 'end' ? 'auto' : '0', bottom: align === 'end' ? '0' : 'auto', transform: align === 'center' ? 'translateY(-50%)' : 'none' },
      right: { left: 'calc(100% + 8px)', top: align === 'center' ? '50%' : align === 'end' ? 'auto' : '0', bottom: align === 'end' ? '0' : 'auto', transform: align === 'center' ? 'translateY(-50%)' : 'none' },
    }

    const arrowStyles: Record<string, React.CSSProperties> = {
      top: { bottom: '-4px', left: '50%', transform: 'translateX(-50%) rotate(45deg)' },
      bottom: { top: '-4px', left: '50%', transform: 'translateX(-50%) rotate(45deg)' },
      left: { right: '-4px', top: '50%', transform: 'translateY(-50%) rotate(45deg)' },
      right: { left: '-4px', top: '50%', transform: 'translateY(-50%) rotate(45deg)' },
    }

    return (
      <div className="relative inline-flex" ref={ref}>
        <div
          ref={triggerRef}
          onClick={() => setOpen(!isOpen)}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setOpen(!isOpen) } }}
          role="button"
          tabIndex={0}
          aria-haspopup="true"
          aria-expanded={isOpen}
        >
          {trigger}
        </div>
        <AnimatePresence>
          {isOpen && (
            <motion.div
              ref={contentRef}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              className={cn(
                'absolute z-popover rounded-xl p-4 min-w-[180px]',
                'bg-background-card border border-border',
                'shadow-[var(--shadow-elevation-3)]',
                className,
              )}
              style={{ ...sideStyles[side], transformOrigin: side === 'bottom' ? 'top center' : 'bottom center' }}
              role="menu"
            >
              <div
                className="absolute w-3 h-3"
                style={{
                  ...arrowStyles[side],
                  background: 'var(--glass-light)',
                  borderLeft: '1px solid var(--border)',
                  borderTop: '1px solid var(--border)',
                }}
                aria-hidden="true"
              />
              {children}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  },
)
)
Popover.displayName = 'Popover'

export { Popover }
export type { PopoverProps }
