'use client'

import { forwardRef, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { cn } from './utils'

const FOCUSABLE_SELECTOR = 'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

interface DialogProps {
  open: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  className?: string
}

const sizeClasses: Record<string, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-full',
}

const Dialog = forwardRef<HTMLDivElement, DialogProps>(
  ({ open, onClose, title, children, size = 'md', className }, ref) => {
    const contentRef = useRef<HTMLDivElement>(null)
    const previousFocusRef = useRef<HTMLElement | null>(null)

    useEffect(() => {
      if (open) {
        previousFocusRef.current = document.activeElement as HTMLElement
        const timer = setTimeout(() => {
          const focusable = contentRef.current?.querySelectorAll(FOCUSABLE_SELECTOR)
          if (focusable?.length) (focusable[0] as HTMLElement).focus()
        }, 100)
        return () => clearTimeout(timer)
      } else {
        previousFocusRef.current?.focus()
      }
    }, [open])

    const trapFocus = useCallback((e: KeyboardEvent) => {
      if (!contentRef.current) return
      const focusable = contentRef.current.querySelectorAll(FOCUSABLE_SELECTOR)
      if (!focusable.length) return
      const first = focusable[0] as HTMLElement
      const last = focusable[focusable.length - 1] as HTMLElement
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus()
      }
    }, [])

    useEffect(() => {
      if (!open) return
      const handleKey = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onClose()
        if (e.key === 'Tab') trapFocus(e)
      }
      document.addEventListener('keydown', handleKey)
      document.body.style.overflow = 'hidden'
      return () => {
        document.removeEventListener('keydown', handleKey)
        document.body.style.overflow = ''
      }
    }, [open, onClose, trapFocus])

    return (
      <AnimatePresence>
        {open && (
          <div
            className="fixed inset-0 z-modal flex items-center justify-center p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="dialog-title"
            ref={ref}
          >
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="absolute inset-0"
              style={{ background: 'rgba(10,11,15,0.7)' }}
              onClick={onClose}
              aria-hidden="true"
            />
            <motion.div
              ref={contentRef}
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className={cn(
                'relative w-full overflow-y-auto rounded-2xl',
                'bg-background-card border border-border',
                'shadow-[var(--shadow-elevation-3)]',
                'max-h-[85vh]',
                sizeClasses[size],
                className,
              )}
            >
              <div
                className="flex items-center justify-between px-6 py-4"
                style={{ borderBottom: '1px solid var(--border)' }}
              >
                <h2
                  id="dialog-title"
                  className="text-lg font-display font-semibold"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {title}
                </h2>
                <button
                  onClick={onClose}
                  className="flex items-center justify-center rounded-lg transition-colors"
                  style={{
                    width: '36px',
                    height: '36px',
                    color: 'var(--text-secondary)',
                  }}
                  onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = 'var(--text-primary)' }}
                  onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = 'var(--text-secondary)' }}
                  aria-label="Close dialog"
                  type="button"
                >
                  <X size={18} />
                </button>
              </div>
              <div className="p-6" style={{ color: 'var(--text-primary)' }}>
                {children}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    )
  },
)

Dialog.displayName = 'Dialog'

export { Dialog }
export type { DialogProps }
