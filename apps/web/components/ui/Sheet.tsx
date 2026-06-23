'use client'

import { memo,  forwardRef, useEffect, useRef, useCallback  } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { cn } from './utils'

interface SheetProps {
  open: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  width?: 'sm' | 'md' | 'lg'
  className?: string
}

const widthClasses: Record<string, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
}

const Sheet = memo(forwardRef<HTMLDivElement, SheetProps>(
  ({ open, onClose, title, children, width = 'md', className }, ref) => {
    const contentRef = useRef<HTMLDivElement>(null)
    const previousFocusRef = useRef<HTMLElement | null>(null)

    useEffect(() => {
      if (open) {
        previousFocusRef.current = document.activeElement as HTMLElement
        setTimeout(() => contentRef.current?.focus(), 50)
      } else {
        previousFocusRef.current?.focus()
      }
    }, [open])

    useEffect(() => {
      if (!open) return
      const handleKey = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onClose()
      }
      document.addEventListener('keydown', handleKey)
      document.body.style.overflow = 'hidden'
      return () => {
        document.removeEventListener('keydown', handleKey)
        document.body.style.overflow = ''
      }
    }, [open, onClose])

    return (
      <AnimatePresence>
        {open && (
          <div className="fixed inset-0 z-modal" ref={ref}>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-0"
              style={{ background: 'rgba(10,11,15,0.6)', backdropFilter: 'blur(4px)' }}
              onClick={onClose}
              aria-hidden="true"
            />
            <motion.div
              ref={contentRef}
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 35 }}
              className={cn(
                'absolute right-0 top-0 bottom-0 w-full flex flex-col',
                'bg-background-card border-l border-border',
                'shadow-[var(--shadow-elevation-4)]',
                widthClasses[width],
              )}
              role="dialog"
              aria-modal="true"
              aria-label={title || 'Sheet panel'}
              tabIndex={-1}
              style={{ maxWidth: width === 'lg' ? '480px' : width === 'md' ? '384px' : '320px' }}
            >
              {title && (
                <div
                  className="flex items-center justify-between px-6 py-4 shrink-0"
                  style={{ borderBottom: '1px solid var(--border)' }}
                >
                  <h2
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
                    aria-label="Close sheet"
                    type="button"
                  >
                    <X size={18} />
                  </button>
                </div>
              )}
              <div className="flex-1 overflow-y-auto p-6" style={{ color: 'var(--text-primary)' }}>
                {children}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    )
  },
)
)
Sheet.displayName = 'Sheet'

export { Sheet }
export type { SheetProps }
