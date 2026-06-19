'use client'

import { forwardRef, useState, useRef, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, ChevronsUpDown, X } from 'lucide-react'
import { cn } from './utils'

interface ComboboxItem {
  value: string
  label: string
}

interface ComboboxProps {
  items: ComboboxItem[]
  value?: string
  onChange?: (value: string) => void
  placeholder?: string
  searchPlaceholder?: string
  emptyText?: string
  disabled?: boolean
  className?: string
}

const Combobox = forwardRef<HTMLDivElement, ComboboxProps>(
  ({ items, value, onChange, placeholder = 'Select...', searchPlaceholder = 'Search...', emptyText = 'No results found.', disabled = false, className }, ref) => {
    const [open, setOpen] = useState(false)
    const [search, setSearch] = useState('')
    const [activeIndex, setActiveIndex] = useState(-1)
    const containerRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null)
    const listRef = useRef<HTMLDivElement>(null)

    const selectedLabel = useMemo(
      () => items.find((i) => i.value === value)?.label ?? '',
      [items, value],
    )

    const filtered = useMemo(
      () =>
        search ? items.filter((i) => i.label.toLowerCase().includes(search.toLowerCase())) : items,
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
            onChange?.(filtered[activeIndex].value)
            setOpen(false)
          }
          break
        case 'Escape': e.preventDefault(); setOpen(false); break
      }
    }

    return (
      <div ref={ref} className={cn('relative', className)}>
        <div ref={containerRef} className="relative">
          <div
            role="combobox"
            aria-expanded={open}
            aria-haspopup="listbox"
            aria-controls="combobox-list"
            tabIndex={disabled ? -1 : 0}
            onKeyDown={handleKeyDown}
            onClick={() => { if (!disabled) setOpen(!open) }}
            className={cn(
              'flex items-center w-full rounded-lg px-3 py-2 text-sm cursor-pointer transition-colors',
              'bg-background-input border',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
              disabled && 'opacity-50 cursor-not-allowed',
              open ? 'border-accent-primary' : 'border-border hover:border-border-light',
            )}
            style={{ minHeight: '44px' }}
          >
            {open ? (
              <input
                ref={inputRef}
                type="text"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setActiveIndex(0) }}
                placeholder={searchPlaceholder}
                className="flex-1 bg-transparent border-none outline-none text-sm"
                style={{ color: 'var(--text-primary)' }}
                onClick={(e) => e.stopPropagation()}
                aria-label="Search"
              />
            ) : (
              <span className="flex-1 truncate" style={{ color: value ? 'var(--text-primary)' : 'var(--text-tertiary)' }}>
                {value ? selectedLabel : placeholder}
              </span>
            )}
            {value && !open && (
              <button
                onClick={(e) => { e.stopPropagation(); onChange?.('') }}
                className="flex items-center justify-center mr-1 rounded hover:bg-[var(--glass-heavy)]"
                style={{ width: '20px', height: '20px', color: 'var(--text-tertiary)' }}
                aria-label="Clear selection"
              >
                <X size={14} />
              </button>
            )}
            <ChevronsUpDown size={16} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
          </div>
        </div>

        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.12 }}
              className="absolute left-0 right-0 mt-1 z-popover rounded-xl overflow-hidden"
              style={{ background: 'var(--background-card)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-elevation-3)' }}
            >
              <div
                ref={listRef}
                id="combobox-list"
                role="listbox"
                className="overflow-y-auto"
                style={{ maxHeight: '240px' }}
              >
                {filtered.length === 0 && (
                  <div className="px-3 py-4 text-sm text-center" style={{ color: 'var(--text-tertiary)' }}>{emptyText}</div>
                )}
                {filtered.map((item, index) => {
                  const isSelected = item.value === value
                  const isActive = activeIndex === index
                  return (
                    <div
                      key={item.value}
                      role="option"
                      aria-selected={isSelected}
                      data-index={index}
                      onClick={() => { onChange?.(item.value); setOpen(false) }}
                      onMouseEnter={() => setActiveIndex(index)}
                      className="flex items-center gap-2 px-3 py-2.5 text-sm cursor-pointer transition-colors"
                      style={{
                        background: isActive ? 'var(--glass-heavy)' : 'transparent',
                        color: 'var(--text-primary)',
                      }}
                    >
                      <span className="flex-1">{item.label}</span>
                      {isSelected && <Check size={14} style={{ color: 'var(--accent-primary)', flexShrink: 0 }} />}
                    </div>
                  )
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  },
)

Combobox.displayName = 'Combobox'

export { Combobox }
export type { ComboboxProps, ComboboxItem }
