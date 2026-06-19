'use client'

import { forwardRef, useState, useRef, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Check, ChevronsUpDown } from 'lucide-react'
import { cn } from './utils'

interface MultiSelectItem {
  value: string
  label: string
}

interface MultiSelectProps {
  items: MultiSelectItem[]
  values: string[]
  onChange: (values: string[]) => void
  placeholder?: string
  maxItems?: number
  className?: string
}

const MultiSelect = forwardRef<HTMLDivElement, MultiSelectProps>(
  ({ items, values, onChange, placeholder = 'Select...', maxItems, className }, ref) => {
    const [open, setOpen] = useState(false)
    const [search, setSearch] = useState('')
    const [activeIndex, setActiveIndex] = useState(-1)
    const containerRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null)
    const listRef = useRef<HTMLDivElement>(null)

    const filtered = useMemo(
      () =>
        search
          ? items.filter((i) => i.label.toLowerCase().includes(search.toLowerCase()))
          : items,
      [items, search],
    )

    const handleOutsideClick = useCallback((e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
        setSearch('')
      }
    }, [])

    useEffect(() => {
      if (open) document.addEventListener('mousedown', handleOutsideClick)
      else document.removeEventListener('mousedown', handleOutsideClick)
      return () => document.removeEventListener('mousedown', handleOutsideClick)
    }, [open, handleOutsideClick])

    useEffect(() => {
      if (open) setTimeout(() => inputRef.current?.focus(), 50)
      else { setSearch(''); setActiveIndex(-1) }
    }, [open])

    useEffect(() => {
      if (open && filtered.length > 0 && activeIndex >= 0) {
        const el = listRef.current?.querySelector(`[data-index="${activeIndex}"]`)
        if (el) (el as HTMLElement).scrollIntoView({ block: 'nearest' })
      }
    }, [activeIndex, open, filtered.length])

    const toggle = useCallback(
      (value: string) => {
        if (maxItems && values.length >= maxItems && !values.includes(value)) return
        onChange(
          values.includes(value)
            ? values.filter((v) => v !== value)
            : [...values, value],
        )
      },
      [values, onChange, maxItems],
    )

    const removeValue = useCallback(
      (value: string, e: React.MouseEvent) => {
        e.stopPropagation()
        onChange(values.filter((v) => v !== value))
      },
      [values, onChange],
    )

    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (!open && (e.key === 'Enter' || e.key === 'ArrowDown')) {
        e.preventDefault(); setOpen(true); return
      }
      if (!open) return
      switch (e.key) {
        case 'ArrowDown': e.preventDefault(); setActiveIndex((p) => Math.min(p + 1, filtered.length - 1)); break
        case 'ArrowUp': e.preventDefault(); setActiveIndex((p) => Math.max(p - 1, 0)); break
        case 'Enter':
          e.preventDefault()
          if (activeIndex >= 0 && filtered[activeIndex]) {
            toggle(filtered[activeIndex].value)
          }
          break
        case 'Escape': e.preventDefault(); setOpen(false); break
      }
    }

    return (
      <div ref={ref} className={cn('relative', className)}>
        <div ref={containerRef}>
          <div
            role="combobox"
            aria-expanded={open}
            aria-haspopup="listbox"
            aria-controls="multiselect-list"
            tabIndex={0}
            onKeyDown={handleKeyDown}
            onClick={() => setOpen(!open)}
            className={cn(
              'flex items-center flex-wrap gap-1 w-full rounded-lg px-3 py-1.5 text-sm cursor-pointer transition-colors min-h-[44px]',
              'bg-background-input border',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
              open ? 'border-accent-primary' : 'border-border hover:border-border-light',
            )}
          >
            {values.length > 0 ? (
              values.map((v) => {
                const label = items.find((i) => i.value === v)?.label || v
                return (
                  <span
                    key={v}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium"
                    style={{ background: 'var(--accent-primary)/15', color: 'var(--accent-primary)', border: '1px solid color-mix(in oklab, var(--accent-primary) 30%, transparent)' }}
                  >
                    {label}
                    <button
                      onClick={(e) => removeValue(v, e)}
                      className="flex items-center justify-center rounded-sm hover:bg-black/20"
                      aria-label={`Remove ${label}`}
                    >
                      <X size={12} />
                    </button>
                  </span>
                )
              })
            ) : (
              <span style={{ color: 'var(--text-tertiary)' }}>{placeholder}</span>
            )}
            <div className="flex-1 min-w-[60px]" />
            <ChevronsUpDown size={16} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
          </div>

          {open && (
            <div className="absolute left-0 right-0 mt-1 z-popover rounded-xl overflow-hidden" style={{ background: 'var(--background-card)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-elevation-3)' }}>
              <div className="flex items-center gap-2 px-3 py-2" style={{ borderBottom: '1px solid var(--border)' }}>
                <input
                  ref={inputRef}
                  type="text"
                  value={search}
                  onChange={(e) => { setSearch(e.target.value); setActiveIndex(0) }}
                  placeholder="Search..."
                  className="flex-1 bg-transparent border-none outline-none text-sm"
                  style={{ color: 'var(--text-primary)' }}
                  onClick={(e) => e.stopPropagation()}
                  aria-label="Search options"
                />
              </div>
              <div
                ref={listRef}
                id="multiselect-list"
                role="listbox"
                aria-multiselectable="true"
                className="overflow-y-auto"
                style={{ maxHeight: '240px' }}
              >
                {filtered.length === 0 && (
                  <div className="px-3 py-4 text-sm text-center" style={{ color: 'var(--text-tertiary)' }}>No results found.</div>
                )}
                {filtered.map((item, index) => {
                  const isSelected = values.includes(item.value)
                  const isActive = activeIndex === index
                  const atLimit = maxItems ? values.length >= maxItems && !isSelected : false
                  return (
                    <div
                      key={item.value}
                      role="option"
                      aria-selected={isSelected}
                      data-index={index}
                      onClick={() => { if (!atLimit) toggle(item.value) }}
                      onMouseEnter={() => setActiveIndex(index)}
                      className={cn(
                        'flex items-center gap-2 px-3 py-2.5 text-sm cursor-pointer transition-colors',
                        atLimit && 'opacity-40 pointer-events-none',
                      )}
                      style={{
                        background: isActive ? 'var(--glass-heavy)' : 'transparent',
                        color: 'var(--text-primary)',
                      }}
                    >
                      <span
                        className={cn(
                          'flex items-center justify-center w-4 h-4 rounded border transition-colors',
                          isSelected ? 'bg-[var(--accent-primary)] border-[var(--accent-primary)]' : 'border-border',
                        )}
                      >
                        {isSelected && <Check size={12} color="#fff" />}
                      </span>
                      <span className="flex-1">{item.label}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.12 }}
            />
          )}
        </AnimatePresence>
      </div>
    )
  },
)

MultiSelect.displayName = 'MultiSelect'

export { MultiSelect }
export type { MultiSelectProps, MultiSelectItem }
