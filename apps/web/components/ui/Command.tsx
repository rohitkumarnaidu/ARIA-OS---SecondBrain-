'use client'

import { memo, 
  forwardRef,
  useState,
  useCallback,
  useRef,
  useEffect,
  type HTMLAttributes,
  type KeyboardEvent,
  type ElementType,
 } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search } from 'lucide-react'
import { cn } from './utils'

interface CommandItem {
  id: string
  label: string
  description?: string
  icon?: ElementType
  shortcut?: string[]
  disabled?: boolean
}

interface CommandGroup {
  heading: string
  items: CommandItem[]
}

interface CommandProps extends Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'onSelect'> {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  groups: CommandGroup[]
  placeholder?: string
  onSelect?: (item: CommandItem) => void
}

const Command = memo(forwardRef<HTMLDivElement, CommandProps>(
  (
    {
      open = true,
      onOpenChange,
      groups,
      placeholder = 'Search or type a command...',
      onSelect,
      className,
      ...props
    },
    ref,
  ) => {
    const [query, setQuery] = useState('')
    const [activeIndex, setActiveIndex] = useState(-1)
    const inputRef = useRef<HTMLInputElement>(null)
    const listRef = useRef<HTMLDivElement>(null)

    const filteredGroups = groups
      .map((g) => ({
        ...g,
        items: g.items.filter(
          (item) =>
            item.label.toLowerCase().includes(query.toLowerCase()) ||
            (item.description && item.description.toLowerCase().includes(query.toLowerCase())),
        ),
      }))
      .filter((g) => g.items.length > 0)

    const flatItems = filteredGroups.flatMap((g) => g.items)

    useEffect(() => {
      if (open) {
        setQuery('')
        setActiveIndex(-1)
        setTimeout(() => inputRef.current?.focus(), 0)
      }
    }, [open])

    useEffect(() => {
      setActiveIndex(-1)
    }, [query])

    const handleKeyDown = useCallback(
      (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          e.preventDefault()
          onOpenChange?.(false)
          return
        }

        if (e.key === 'ArrowDown') {
          e.preventDefault()
          setActiveIndex((prev) => (prev < flatItems.length - 1 ? prev + 1 : 0))
          return
        }

        if (e.key === 'ArrowUp') {
          e.preventDefault()
          setActiveIndex((prev) => (prev > 0 ? prev - 1 : flatItems.length - 1))
          return
        }

        if (e.key === 'Enter' && activeIndex >= 0 && activeIndex < flatItems.length) {
          e.preventDefault()
          const item = flatItems[activeIndex]
          if (!item.disabled) {
            onSelect?.(item)
          }
        }
      },
      [flatItems, activeIndex, onSelect, onOpenChange],
    )

    useEffect(() => {
      if (activeIndex < 0 || !listRef.current) return
      const items = listRef.current.querySelectorAll<HTMLElement>('[data-command-item]')
      items[activeIndex]?.scrollIntoView({ block: 'nearest' })
    }, [activeIndex])

    if (!open) return null

    return (
      <div
        className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
        data-slot="command-backdrop"
      >
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm"
          onClick={() => onOpenChange?.(false)}
          aria-hidden="true"
        />
        <div
          ref={ref}
          role="dialog"
          aria-modal="true"
          aria-label="Command palette"
          className={cn(
            'relative z-10 w-full max-w-lg rounded-xl border border-border bg-background-card shadow-2xl',
            'focus-visible:outline-none',
            className,
          )}
          onKeyDown={handleKeyDown}
          data-slot="command"
          {...props}
        >
          <div className="flex items-center gap-2 border-b border-border px-4">
            <Search className="size-4 shrink-0 text-text-secondary" aria-hidden="true" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={placeholder}
              className={cn(
                'h-12 w-full bg-transparent text-sm text-text-primary outline-none',
                'placeholder:text-text-tertiary',
              )}
              aria-autocomplete="list"
              aria-controls="command-list"
              autoComplete="off"
              spellCheck={false}
            />
          </div>

          <div
            ref={listRef}
            id="command-list"
            role="listbox"
            className="max-h-72 overflow-y-auto p-2"
          >
            <AnimatePresence mode="wait">
              {filteredGroups.length === 0 ? (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  transition={{ duration: 0.15 }}
                  className="flex flex-col items-center gap-1 py-8 text-center"
                >
                  <span className="text-sm text-text-secondary">No results found</span>
                  <span className="text-xs text-text-tertiary">
                    Try a different search term
                  </span>
                </motion.div>
              ) : (
                <motion.div
                  key={query || 'results'}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.1 }}
                >
                  {filteredGroups.map((group, gi) => {
                    let globalOffset = 0
                    for (let i = 0; i < gi; i++) {
                      globalOffset += filteredGroups[i].items.length
                    }

                    return (
                      <div key={group.heading} role="group" aria-label={group.heading}>
                        <div className="px-2 py-1.5 text-xs font-medium text-text-tertiary">
                          {group.heading}
                        </div>
                        {group.items.map((item, ii) => {
                          const globalIdx = globalOffset + ii
                          const isActive = globalIdx === activeIndex
                          const Icon = item.icon

                          return (
                            <div
                              key={item.id}
                              role="option"
                              aria-selected={isActive}
                              data-command-item
                              data-disabled={item.disabled || undefined}
                              className={cn(
                                'flex cursor-pointer items-center gap-2 rounded-lg px-2 py-2 text-sm transition-colors',
                                isActive && 'bg-accent-primary/10 text-accent-primary',
                                !isActive && 'text-text-primary hover:bg-background-elevated',
                                item.disabled && 'pointer-events-none opacity-40',
                              )}
                              onClick={() => {
                                if (!item.disabled) onSelect?.(item)
                              }}
                              onMouseEnter={() => setActiveIndex(globalIdx)}
                            >
                              {Icon && <Icon className="size-4 shrink-0 text-text-secondary" aria-hidden="true" />}
                              <div className="flex-1 truncate">
                                <div className="truncate">{item.label}</div>
                                {item.description && (
                                  <div className="truncate text-xs text-text-tertiary">
                                    {item.description}
                                  </div>
                                )}
                              </div>
                              {item.shortcut && (
                                <div className="flex shrink-0 items-center gap-0.5">
                                  {item.shortcut.map((key, ki) => (
                                    <kbd
                                      key={ki}
                                      className={cn(
                                        'inline-flex size-5 items-center justify-center rounded bg-background-elevated text-[10px] font-medium text-text-tertiary',
                                        'ring-1 ring-border',
                                      )}
                                    >
                                      {key}
                                    </kbd>
                                  ))}
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    )
                  })}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    )
  },
)
)
Command.displayName = 'Command'

export { Command }
export type { CommandProps, CommandItem, CommandGroup }
