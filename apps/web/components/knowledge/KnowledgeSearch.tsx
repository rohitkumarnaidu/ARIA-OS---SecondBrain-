'use client'

import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Filter, X } from 'lucide-react'
import { cn } from '@/components/ui/utils'

export interface SearchFilters {
  types: string[]
  tags: string[]
}

interface KnowledgeSearchProps {
  onSearch: (query: string, filters: SearchFilters) => void
  tags: string[]
}

type NodeType = 'note' | 'resource' | 'idea'

const NODE_TYPES: { value: NodeType; label: string }[] = [
  { value: 'note', label: 'Note' },
  { value: 'resource', label: 'Resource' },
  { value: 'idea', label: 'Idea' },
]

export function KnowledgeSearch({ onSearch, tags }: KnowledgeSearchProps) {
  const [query, setQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [selectedTags, setSelectedTags] = useState<string[]>([])

  const emitSearch = useCallback(
    (q: string, types: string[], tgs: string[]) => {
      onSearch(q, { types, tags: tgs })
    },
    [onSearch],
  )

  const handleQueryChange = (val: string) => {
    setQuery(val)
    emitSearch(val, selectedTypes, selectedTags)
  }

  const toggleType = (type: string) => {
    const next = selectedTypes.includes(type)
      ? selectedTypes.filter(t => t !== type)
      : [...selectedTypes, type]
    setSelectedTypes(next)
    emitSearch(query, next, selectedTags)
  }

  const toggleTag = (tag: string) => {
    const next = selectedTags.includes(tag)
      ? selectedTags.filter(t => t !== tag)
      : [...selectedTags, tag]
    setSelectedTags(next)
    emitSearch(query, selectedTypes, next)
  }

  const clearFilters = () => {
    setQuery('')
    setSelectedTypes([])
    setSelectedTags([])
    emitSearch('', [], [])
  }

  const hasActiveFilters = selectedTypes.length > 0 || selectedTags.length > 0 || query.length > 0

  return (
    <div className="space-y-3">
      <div
        className={cn(
          'relative flex items-center gap-2',
          'rounded-xl backdrop-blur-[12px]',
          'bg-[var(--background-card)]/80 border border-[var(--border)]',
          'focus-within:border-[var(--accent-primary)]/50 focus-within:shadow-[0_0_20px_var(--accent-primary)]/10',
          'transition-all duration-300',
        )}
      >
        <div className="pl-4 text-[var(--text-muted)]">
          <Search size={18} />
        </div>
        <input
          type="text"
          value={query}
          onChange={e => handleQueryChange(e.target.value)}
          placeholder="Search knowledge vault..."
          className={cn(
            'flex-1 bg-transparent py-3 pr-3 text-sm text-[var(--text-primary)]',
            'placeholder:text-[var(--text-muted)]',
            'focus:outline-none',
            'font-body',
          )}
        />
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={cn(
            'p-2 mr-1 rounded-lg transition-colors',
            showFilters || hasActiveFilters
              ? 'text-[var(--accent-primary)] bg-[var(--accent-primary)]/10'
              : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]',
          )}
          aria-label="Toggle filters"
        >
          <Filter size={18} />
        </button>
      </div>

      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div
              className={cn(
                'p-4 rounded-xl space-y-4',
                'bg-[var(--background-card)]/80 border border-[var(--border)]',
                'backdrop-blur-[8px]',
              )}
            >
              <div className="space-y-2">
                <p className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider font-body">
                  Type
                </p>
                <div className="flex flex-wrap gap-2">
                  {NODE_TYPES.map(({ value, label }) => (
                    <button
                      key={value}
                      onClick={() => toggleType(value)}
                      className={cn(
                        'px-3 py-1.5 rounded-lg text-xs font-medium transition-all font-body',
                        selectedTypes.includes(value)
                          ? 'bg-[var(--accent-primary)]/20 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30'
                          : 'bg-[var(--background-dark)] text-[var(--text-secondary)] border border-[var(--border)] hover:border-[var(--border-light)]',
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {tags.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider font-body">
                    Tags
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {tags.map((tag) => (
                      <button
                        key={tag}
                        onClick={() => toggleTag(tag)}
                        className={cn(
                          'px-3 py-1.5 rounded-lg text-xs font-medium transition-all font-body',
                          selectedTags.includes(tag)
                            ? 'bg-[var(--accent-warning)]/20 text-[var(--accent-warning)] border border-[var(--accent-warning)]/30'
                            : 'bg-[var(--background-dark)] text-[var(--text-secondary)] border border-[var(--border)] hover:border-[var(--border-light)]',
                        )}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="flex items-center gap-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors font-body"
                >
                  <X size={12} />
                  Clear all filters
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
