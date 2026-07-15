'use client'

import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'

const filterTabs = [
  { label: 'All Courses', value: 'all' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Not Started', value: 'not_started' },
  { label: 'Completed', value: 'completed' },
] as const

interface CourseFiltersProps {
  activeFilter: string
  onFilterChange: (filter: string) => void
  counts?: Record<string, number>
}

export function CourseFilters({ activeFilter, onFilterChange, counts }: CourseFiltersProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.2 }}
      className="flex gap-2 overflow-x-auto no-scrollbar pb-2"
      role="tablist"
      aria-label="Course filters"
    >
      {filterTabs.map((tab) => {
        const count = counts?.[tab.value]
        return (
          <button
            key={tab.value}
            role="tab"
            aria-selected={activeFilter === tab.value}
            onClick={() => onFilterChange(tab.value)}
            className={cn(
              'relative px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all duration-200',
              activeFilter === tab.value
                ? 'bg-accent-primary text-white shadow-glow-sm'
                : 'bg-background-elevated text-text-secondary hover:text-text-primary border border-border hover:border-border-light',
            )}
          >
            {tab.label}
            {count !== undefined && (
              <span
                className={cn(
                  'ml-2 px-1.5 py-0.5 rounded text-xs',
                  activeFilter === tab.value ? 'bg-white/20' : 'bg-background-card',
                )}
              >
                {count}
              </span>
            )}
          </button>
        )
      })}
    </motion.div>
  )
}
