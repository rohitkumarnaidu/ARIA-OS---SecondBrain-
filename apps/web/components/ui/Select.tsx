'use client'

import { memo,  forwardRef, useState, useRef, useEffect, useCallback, useMemo  } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Search, Check } from 'lucide-react'
import { cn } from './utils'

interface SelectOption {
  value: string
  label: string
}

interface SelectProps {
  options: SelectOption[]
  value?: string
  onChange: (value: string) => void
  placeholder?: string
  searchable?: boolean
  disabled?: boolean
  className?: string
  id?: string
}

const Select = memo(forwardRef<HTMLDivElement, SelectProps>(
  ({ options, value, onChange, placeholder = 'Select...', searchable = true, disabled = false, className, id }, ref) => {
    const [open, setOpen] = useState(false)
    const [search, setSearch] = useState('')
    const [activeIndex, setActiveIndex] = useState(-1)
    const containerRef = useRef<HTMLDivElement>(null)
    const searchInputRef = useRef<HTMLInputElement>(null)
    const listRef = useRef<HTMLDivElement>(null)

    const filteredOptions = useMemo(
      () =>
        searchable && search
          ? options.filter((o) => o.label.toLowerCase().includes(search.toLowerCase()))
          : options,
      [options, search, searchable],
    )

    const selectedLabel = useMemo(
      () => options.find((o) => o.value === value)?.label || placeholder,
      [options, value, placeholder],
    )

    const handleClickOutside = useCallback((e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
        setSearch('')
        setActiveIndex(-1)
      }
    }, [])

    useEffect(() => {
      if (open) {
        document.addEventListener('mousedown', handleClickOutside)
        if (searchable) setTimeout(() => searchInputRef.current?.focus(), 50)
      } else {
        document.removeEventListener('mousedown', handleClickOutside)
      }
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [open, handleClickOutside, searchable])

    useEffect(() => {
      if (!open) {
        setSearch('')
        setActiveIndex(-1)
      }
    }, [open])

    useEffect(() => {
      if (open && filteredOptions.length > 0 && activeIndex >= 0) {
        const el = listRef.current?.querySelector(`[data-index="${activeIndex}"]`)
        if (el) (el as HTMLElement).scrollIntoView({ block: 'nearest' })
      }
    }, [activeIndex, open, filteredOptions.length])

    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (!open) {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
          e.preventDefault()
          setOpen(true)
        }
        return
      }
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setActiveIndex((prev) => (prev + 1) % Math.max(filteredOptions.length, 1))
          break
        case 'ArrowUp':
          e.preventDefault()
          setActiveIndex((prev) => (prev - 1 + Math.max(filteredOptions.length, 1)) % Math.max(filteredOptions.length, 1))
          break
        case 'Enter':
          e.preventDefault()
          if (activeIndex >= 0 && filteredOptions[activeIndex]) {
            onChange(filteredOptions[activeIndex].value)
            setOpen(false)
          }
          break
        case 'Escape':
          e.preventDefault()
          setOpen(false)
          break
      }
    }

    return (
      <div ref={ref} className={cn('relative', className)}>
        <div
          ref={containerRef}
          id={id}
          role="combobox"
          aria-expanded={open}
          aria-controls="select-list"
          aria-activedescendant={activeIndex >= 0 ? `select-option-${activeIndex}` : undefined}
          aria-haspopup="listbox"
          tabIndex={disabled ? -1 : 0}
          onKeyDown={handleKeyDown}
          onClick={() => { if (!disabled) setOpen(!open) }}
          className={cn(
            'flex items-center justify-between w-full rounded-lg px-3 py-2 text-sm cursor-pointer transition-colors',
            'bg-background-input border border-border',
            'hover:border-border-light',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
            disabled && 'opacity-50 cursor-not-allowed',
          )}
          style={{ minHeight: '44px' }}
        >
          <span style={{ color: value ? 'var(--text-primary)' : 'var(--text-tertiary)' }}>
            {selectedLabel}
          </span>
          <ChevronDown
            size={16}
            className={cn('transition-transform', open && 'rotate-180')}
            style={{ color: 'var(--text-tertiary)', flexShrink: 0 }}
          />
        </div>
        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.12 }}
              className="absolute left-0 right-0 mt-1 z-popover rounded-xl overflow-hidden"
              style={{
                background: 'var(--background-card)',
                border: '1px solid var(--border)',
                boxShadow: 'var(--shadow-elevation-3)',
              }}
            >
              {searchable && (
                <div className="flex items-center gap-2 px-3 py-2" style={{ borderBottom: '1px solid var(--border)' }}>
                  <Search size={14} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
                  <input
                    ref={searchInputRef}
                    type="text"
                    value={search}
                    onChange={(e) => { setSearch(e.target.value); setActiveIndex(0) }}
                    placeholder="Search..."
                    className="flex-1 bg-transparent border-none outline-none text-sm"
                    style={{ color: 'var(--text-primary)' }}
                    aria-label="Search options"
                  />
                </div>
              )}
              <div
                ref={listRef}
                id="select-list"
                role="listbox"
                className="overflow-y-auto"
                style={{ maxHeight: '240px' }}
              >
                {filteredOptions.length === 0 && (
                  <div
                    className="px-3 py-4 text-sm text-center"
                    style={{ color: 'var(--text-tertiary)' }}
                  >
                    No options found
                  </div>
                )}
                {filteredOptions.map((option, index) => {
                  const isSelected = option.value === value
                  const isActive = activeIndex === index
                  return (
                    <div
                      key={option.value}
                      id={`select-option-${index}`}
                      role="option"
                      tabIndex={-1}
                      aria-selected={isSelected}
                      data-index={index}
                      onClick={() => { onChange(option.value); setOpen(false) }}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onChange(option.value); setOpen(false) } }}
                      onMouseEnter={() => setActiveIndex(index)}
                      className="flex items-center gap-2 px-3 py-2.5 text-sm cursor-pointer transition-colors"
                      style={{
                        background: isActive ? 'var(--glass-heavy)' : 'transparent',
                        color: 'var(--text-primary)',
                      }}
                    >
                      <span className="flex-1">{option.label}</span>
                      {isSelected && (
                        <Check size={14} style={{ color: 'var(--accent-primary)', flexShrink: 0 }} />
                      )}
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
)
Select.displayName = 'Select'

export { Select }
export type { SelectProps, SelectOption }
