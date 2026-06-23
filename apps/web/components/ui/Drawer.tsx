'use client'

import { memo,  forwardRef, useEffect, useRef, useState, useCallback  } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { cn } from './utils'

interface DrawerProps {
  open: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  snapPoints?: number[]
  className?: string
}

const defaultSnapPoints = [25, 50, 75, 100]

const Drawer = memo(forwardRef<HTMLDivElement, DrawerProps>(
  ({ open, onClose, title, children, snapPoints = defaultSnapPoints, className }, ref) => {
    const [snapIndex, setSnapIndex] = useState(snapPoints.length - 1)
    const [dragY, setDragY] = useState(0)
    const [isDragging, setIsDragging] = useState(false)
    const drawerRef = useRef<HTMLDivElement>(null)
    const startY = useRef(0)
    const previousFocusRef = useRef<HTMLElement | null>(null)

    const sortedSnapPoints = [...snapPoints].sort((a, b) => a - b)
    const currentSnap = sortedSnapPoints[snapIndex]

    useEffect(() => {
      if (open) {
        previousFocusRef.current = document.activeElement as HTMLElement
        setSnapIndex(sortedSnapPoints.length - 1)
        setDragY(0)
        document.body.style.overflow = 'hidden'
      } else {
        previousFocusRef.current?.focus()
        document.body.style.overflow = ''
      }
      return () => { document.body.style.overflow = '' }
    }, [open, sortedSnapPoints.length])

    useEffect(() => {
      if (!open) return
      const handleKey = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onClose()
      }
      document.addEventListener('keydown', handleKey)
      return () => document.removeEventListener('keydown', handleKey)
    }, [open, onClose])

    const handleDragStart = useCallback((clientY: number) => {
      startY.current = clientY
      setIsDragging(true)
    }, [])

    const handleDragMove = useCallback((clientY: number) => {
      const delta = clientY - startY.current
      setDragY(Math.max(0, delta))
    }, [])

    const handleDragEnd = useCallback(() => {
      setIsDragging(false)
      const height = window.innerHeight
      const dragPercent = (dragY / height) * 100

      if (dragPercent > 20) {
        const currentSnapVal = sortedSnapPoints[snapIndex]
        let newIndex = snapIndex - 1
        if (newIndex < 0) {
          onClose()
          setDragY(0)
          return
        }
        setSnapIndex(newIndex)
      } else if (dragY > 40 && snapIndex === 0) {
        onClose()
      } else {
        const currentSnapVal = sortedSnapPoints[snapIndex]
        const midPoints = sortedSnapPoints.map((s) => s)
        let closest = snapIndex
        for (let i = 0; i < midPoints.length; i++) {
          if (Math.abs(midPoints[i] - (currentSnapVal - dragPercent)) < Math.abs(midPoints[closest] - (currentSnapVal - dragPercent))) {
            closest = i
          }
        }
        setSnapIndex(closest)
      }
      setDragY(0)
    }, [dragY, snapIndex, sortedSnapPoints, onClose])

    const translateY = isDragging ? dragY : 0

    return (
      <AnimatePresence>
        {open && (
          <div ref={ref} className="fixed inset-0 z-modal">
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
              ref={drawerRef}
              initial={{ y: '100%' }}
              animate={{
                y: 0,
                translateY: translateY,
              }}
              exit={{ y: '100%' }}
              transition={isDragging ? { type: 'tween', duration: 0 } : { type: 'spring', stiffness: 300, damping: 35 }}
              className={cn(
                'absolute bottom-0 left-0 right-0 flex flex-col rounded-t-2xl',
                'bg-background-card border border-border',
                'shadow-[var(--shadow-elevation-5)]',
                className,
              )}
              style={{ height: `${currentSnap}vh`, maxHeight: '100vh' }}
              role="dialog"
              aria-modal="true"
              aria-label={title || 'Drawer'}
            >
              {/* Drag handle */}
              <div
                className="flex justify-center pt-2 pb-1 shrink-0 cursor-grab active:cursor-grabbing"
                onMouseDown={(e) => handleDragStart(e.clientY)}
                onTouchStart={(e) => handleDragStart(e.touches[0].clientY)}
                onMouseMove={(e) => { if (isDragging) handleDragMove(e.clientY) }}
                onTouchMove={(e) => { if (isDragging) handleDragMove(e.touches[0].clientY) }}
                onMouseUp={handleDragEnd}
                onTouchEnd={handleDragEnd}
                onMouseLeave={handleDragEnd}
              >
                <div
                  className="w-10 h-1 rounded-full"
                  style={{ background: 'var(--text-tertiary)' }}
                  aria-hidden="true"
                />
              </div>

              {/* Header */}
              {title && (
                <div className="flex items-center justify-between px-5 py-3 shrink-0">
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
                    aria-label="Close drawer"
                    type="button"
                  >
                    <X size={18} />
                  </button>
                </div>
              )}

              {/* Content */}
              <div className="flex-1 overflow-y-auto px-5 pb-6" style={{ color: 'var(--text-primary)' }}>
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
Drawer.displayName = 'Drawer'

export { Drawer }
export type { DrawerProps }
