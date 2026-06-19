'use client'

import { Search, X, ToggleLeft, ToggleRight } from 'lucide-react'
import { motion } from 'framer-motion'

interface ResourceFiltersProps {
  tags: string[]
  selectedTags: string[]
  onTagsChange: (tags: string[]) => void
  selectedType: string
  onTypeChange: (type: string) => void
  searchQuery: string
  onSearchChange: (q: string) => void
  tagMode: 'or' | 'and'
  onTagModeChange: (mode: 'or' | 'and') => void
}

const resourceTypes = ['all', 'resource', 'note', 'link', 'bookmark']

export function ResourceFilters({
  tags,
  selectedTags,
  onTagsChange,
  selectedType,
  onTypeChange,
  searchQuery,
  onSearchChange,
  tagMode,
  onTagModeChange,
}: ResourceFiltersProps) {
  const toggleTag = (tag: string) => {
    if (selectedTags.includes(tag)) {
      onTagsChange(selectedTags.filter((t) => t !== tag))
    } else {
      onTagsChange([...selectedTags, tag])
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search resources..."
            className="w-full h-10 pl-9 pr-8 rounded-lg bg-background-input border border-border text-text-primary text-sm placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-primary transition-colors"
              aria-label="Clear search"
            >
              <X size={14} />
            </button>
          )}
        </div>

        <div className="flex items-center gap-1 bg-background-elevated rounded-lg p-1 border border-border">
          {resourceTypes.map((type) => (
            <button
              key={type}
              onClick={() => onTypeChange(type)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium capitalize transition-all ${
                selectedType === type
                  ? 'bg-accent-primary/20 text-accent-primary shadow-glow-sm'
                  : 'text-text-tertiary hover:text-text-primary'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {tags.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">Tags</span>
            <button
              onClick={() => onTagModeChange(tagMode === 'or' ? 'and' : 'or')}
              className="flex items-center gap-1 text-[10px] text-text-tertiary hover:text-text-primary transition-colors"
              aria-label={`Toggle tag filter mode, currently ${tagMode.toUpperCase()}`}
            >
              {tagMode === 'or' ? <ToggleRight size={14} /> : <ToggleLeft size={14} />}
              <span className="uppercase tracking-wider">{tagMode}</span>
            </button>
            {selectedTags.length > 0 && (
              <button
                onClick={() => onTagsChange([])}
                className="text-[10px] text-accent-error hover:underline ml-auto"
              >
                Clear all
              </button>
            )}
          </div>
          <motion.div layout className="flex flex-wrap gap-1.5">
            {tags.map((tag) => {
              const selected = selectedTags.includes(tag)
              return (
                <motion.button
                  key={tag}
                  layout
                  onClick={() => toggleTag(tag)}
                  className={`text-xs px-2.5 py-1 rounded-full border transition-all ${
                    selected
                      ? 'bg-accent-primary/20 text-accent-primary border-accent-primary/30 shadow-glow-sm'
                      : 'bg-transparent text-text-tertiary border-border hover:border-border-light hover:text-text-secondary'
                  }`}
                >
                  {tag}
                </motion.button>
              )
            })}
          </motion.div>
        </div>
      )}
    </div>
  )
}
