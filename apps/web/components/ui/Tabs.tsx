'use client'

import { forwardRef, useState, useRef, useCallback } from 'react'
import { motion } from 'framer-motion'
import { cn } from './utils'

interface Tab {
  value: string
  label: string
}

interface TabsProps {
  tabs: Tab[]
  value: string
  onChange: (value: string) => void
  className?: string
  tabClassName?: string
}

const Tabs = forwardRef<HTMLDivElement, TabsProps>(
  ({ tabs, value, onChange, className, tabClassName }, ref) => {
    const tabRefs = useRef<Map<string, HTMLButtonElement>>(new Map())

    const handleKeyDown = useCallback(
      (e: React.KeyboardEvent, currentIndex: number) => {
        let nextIndex: number | null = null
        if (e.key === 'ArrowRight') {
          nextIndex = (currentIndex + 1) % tabs.length
        } else if (e.key === 'ArrowLeft') {
          nextIndex = (currentIndex - 1 + tabs.length) % tabs.length
        }
        if (nextIndex !== null) {
          e.preventDefault()
          const nextTab = tabs[nextIndex]
          onChange(nextTab.value)
          tabRefs.current.get(nextTab.value)?.focus()
        }
      },
      [tabs, onChange],
    )

    return (
      <div
        ref={ref}
        role="tablist"
        aria-orientation="horizontal"
        className={cn(
          'inline-flex items-center gap-1 rounded-xl p-1',
          className,
        )}
        style={{
          background: 'var(--surface-secondary)',
          border: '1px solid var(--border)',
        }}
      >
        {tabs.map((tab, index) => {
          const isActive = tab.value === value
          return (
            <button
              key={tab.value}
              ref={(el) => { if (el) tabRefs.current.set(tab.value, el) }}
              role="tab"
              aria-selected={isActive}
              aria-controls={`tabpanel-${tab.value}`}
              id={`tab-${tab.value}`}
              tabIndex={isActive ? 0 : -1}
              onClick={() => onChange(tab.value)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              className={cn(
                'relative rounded-lg px-4 py-2 text-sm font-medium transition-colors',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]',
                tabClassName,
              )}
              style={{
                color: isActive ? 'var(--text-primary)' : 'var(--text-tertiary)',
              }}
            >
              {isActive && (
                <motion.div
                  layoutId="tab-underline"
                  className="absolute inset-0 rounded-lg"
                  style={{
                    background: 'var(--glass-heavy)',
                    border: '1px solid var(--border-light)',
                  }}
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              )}
              <span className="relative z-10">{tab.label}</span>
            </button>
          )
        })}
      </div>
    )
  },
)

Tabs.displayName = 'Tabs'

export { Tabs }
export type { TabsProps, Tab }
