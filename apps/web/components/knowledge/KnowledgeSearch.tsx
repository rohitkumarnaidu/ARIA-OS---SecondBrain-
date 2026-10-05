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

export function KnowledgeSearch({ onSearch, tags }: KnowledgeSearchProps): JSX.Element {
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
          'bg-background-card/80 border border-border',
          'focus-within:border-accent-primary/50 focus-within:shadow-glow-sm',
          'transition-all duration-300',
        )}
      >
        <div className="pl-4 text-text-muted">
          <Search size={18} aria-hidden="true" />
        </div>
        <input
          type="text"
          value={query}
          onChange={e => handleQueryChange(e.target.value)}
          placeholder="Search knowledge vault..."
          className={cn(
            'flex-1 bg-transparent py-3 pr-3 text-sm text-text-primary',
            'placeholder:text-text-muted',
            'focus:outline-none',
            'font-body',
          )}
        />
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className={cn(
            'p-2 mr-1 rounded-lg transition-colors',
            showFilters || hasActiveFilters
              ? 'text-accent-primary bg-accent-primary/10'
              : 'text-text-muted hover:text-text-secondary',
          )}
          aria-expanded={showFilters}
          aria-controls="knowledge-search-filters"
          aria-label="Toggle filters"
        >
          <Filter size={18} aria-hidden="true" />
        </button>
      </div>

      <AnimatePresence>
        {showFilters && (
          <motion.div
            id="knowledge-search-filters"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div
              className={cn(
                'p-4 rounded-xl space-y-4',
                'bg-background-card/80 border border-border',
                'backdrop-blur-[8px]',
              )}
            >
              <div className="space-y-2">
                <p className="text-xs font-medium text-text-secondary uppercase tracking-wider font-body">
                  Type
                </p>
                <div className="flex flex-wrap gap-2">
                  {NODE_TYPES.map(({ value, label }) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => toggleType(value)}
                      aria-pressed={selectedTypes.includes(value)}
                      className={cn(
                        'px-3 py-1.5 rounded-lg text-xs font-medium transition-all font-body',
                        selectedTypes.includes(value)
                          ? 'bg-accent-primary/20 text-accent-primary border border-accent-primary/30'
                          : 'bg-background-dark text-text-secondary border border-border hover:border-border-light',
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {tags.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-text-secondary uppercase tracking-wider font-body">
                    Tags
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {tags.map((tag) => (
                      <button
                        key={tag}
                        type="button"
                        onClick={() => toggleTag(tag)}
                        aria-pressed={selectedTags.includes(tag)}
                        className={cn(
                          'px-3 py-1.5 rounded-lg text-xs font-medium transition-all font-body',
                          selectedTags.includes(tag)
                            ? 'bg-accent-warning/20 text-accent-warning border border-accent-warning/30'
                            : 'bg-background-dark text-text-secondary border border-border hover:border-border-light',
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
                  type="button"
                  onClick={clearFilters}
                  className="flex items-center gap-1.5 text-xs text-text-muted hover:text-text-secondary transition-colors font-body"
                >
                  <X size={12} aria-hidden="true" />
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
