'use client'

import { memo,  useEffect, useRef, useCallback  } from 'react'
import { X } from 'lucide-react'
import { clsx } from 'clsx'
import { motion, AnimatePresence } from 'framer-motion'

const FOCUSABLE_SELECTOR = 'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  /** Unique id for the heading — required when more than one Modal can be mounted. */
  titleId?: string
  description?: string
}

export const Modal = memo(function Modal({ isOpen, onClose, title, children, size = 'md', titleId = 'modal-title', description }: ModalProps) {
  const contentRef = useRef<HTMLDivElement>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (!isOpen) return
    previousFocusRef.current = document.activeElement as HTMLElement
    const timer = setTimeout(() => {
      const focusable = contentRef.current?.querySelectorAll(FOCUSABLE_SELECTOR)
      if (focusable?.length) (focusable[0] as HTMLElement).focus()
      else contentRef.current?.focus()
    }, 100)
    return () => {
      clearTimeout(timer)
      previousFocusRef.current?.focus()
    }
  }, [isOpen])

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
    if (!isOpen) return
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
  }, [isOpen, onClose, trapFocus])

  const sizes = { sm: 'max-w-sm', md: 'max-w-md', lg: 'max-w-lg', xl: 'max-w-xl', full: 'max-w-[95vw] max-h-[95vh]' }

  const descriptionId = description ? `${titleId}-description` : undefined

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-modal flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby={titleId} aria-describedby={descriptionId}>
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} aria-hidden="true"
          />
          <motion.div
            ref={contentRef}
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            tabIndex={-1}
            className={clsx('relative w-full overflow-y-auto bg-background-card border border-border rounded-2xl shadow-2xl max-h-[85vh]', sizes[size])}
          >
            <div className="flex items-center justify-between p-6 border-b border-border sticky top-0 bg-background-card z-10">
              <h2 id={titleId} className="text-xl font-display font-semibold text-text-primary">{title}</h2>
              <button type="button" onClick={onClose} className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-elevated transition-colors" aria-label="Close dialog">
                <X size={20} aria-hidden="true" />
              </button>
            </div>
            <div className="p-6">
              {description && <p id={descriptionId} className="mb-4 text-sm text-text-secondary">{description}</p>}
              {children}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
})
