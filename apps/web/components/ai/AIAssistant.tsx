'use client'

import { useCallback, type ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, X, GripHorizontal } from 'lucide-react'
import { cn } from '@/components/ui/utils'

interface AIAssistantProps {
  isOpen: boolean
  onClose: () => void
  suggestions?: string[]
  onSuggestionClick?: (suggestion: string) => void
  className?: string
  children?: ReactNode
}

export function AIAssistant({
  isOpen,
  onClose,
  suggestions = [],
  onSuggestionClick,
  className,
  children,
}: AIAssistantProps) {
  const handleSuggestionClick = useCallback(
    (s: string) => {
      onSuggestionClick?.(s)
    },
    [onSuggestionClick],
  )

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 24, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 24, scale: 0.95 }}
          transition={{ type: 'spring', stiffness: 350, damping: 28 }}
          className={cn(
            'fixed bottom-6 right-6 z-50',
            'w-[calc(100vw-32px)] sm:w-[360px]',
            'rounded-2xl overflow-hidden',
            'flex flex-col',
            className,
          )}
          style={{
            background: 'rgba(18, 18, 26, 0.96)',
            border: '1px solid rgba(70,70,79,0.25)',
            boxShadow: '0 0 40px rgba(99,102,241,0.25), 0 24px 48px rgba(0,0,0,0.5)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
          }}
          role="dialog"
          aria-label="AI Assistant"
        >
          <div
            className="flex items-center justify-center py-1 cursor-grab active:cursor-grabbing select-none"
            style={{ borderBottom: '1px solid rgba(70,70,79,0.15)' }}
          >
            <GripHorizontal size={14} className="text-text-tertiary" aria-hidden="true" />
          </div>

          <div className="flex items-center justify-between px-4 py-3 shrink-0">
            <div className="flex items-center gap-2">
              <div
                className="flex items-center justify-center w-8 h-8 rounded-lg"
                style={{
                  background: 'rgba(99,102,241,0.15)',
                  boxShadow: '0 0 12px rgba(99,102,241,0.2)',
                }}
              >
                <Sparkles size={16} style={{ color: 'var(--accent-primary)' }} aria-hidden="true" />
              </div>
              <div>
                <span className="text-sm font-semibold text-text-primary font-display">ARIA</span>
                <p className="text-[11px] text-text-tertiary font-body">AI Assistant</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="flex items-center justify-center w-7 h-7 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-elevated/80 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary"
              aria-label="Close AI Assistant"
            >
              <X size={14} aria-hidden="true" />
            </button>
          </div>

          <div className="flex-1 px-4 py-3 max-h-[360px] overflow-y-auto scroll-smooth">
            {children ? (
              children
            ) : (
              <div className="space-y-4">
                <p className="text-sm text-text-secondary font-body leading-relaxed">
                  Hello! I&apos;m ARIA, your AI assistant. How can I help you today?
                </p>

                {suggestions.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-text-tertiary font-body uppercase tracking-wider">
                      Suggestions
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {suggestions.map((suggestion) => (
                        <button
                          key={suggestion}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className={cn(
                            'text-xs font-medium px-3 py-1.5 rounded-lg',
                            'transition-all duration-200',
                            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary',
                          )}
                          style={{
                            background: 'rgba(99,102,241,0.1)',
                            border: '1px solid rgba(99,102,241,0.2)',
                            color: 'var(--accent-secondary)',
                          }}
                          aria-label={`Suggestion: ${suggestion}`}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <div
                  className="rounded-xl p-3"
                  style={{
                    background: 'rgba(0,255,163,0.04)',
                    border: '1px solid rgba(0,255,163,0.1)',
                  }}
                >
                  <p className="text-xs text-accent-neon/70 font-body">
                    I can help with tasks, goals, scheduling, and more. Just ask!
                  </p>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export type { AIAssistantProps }
