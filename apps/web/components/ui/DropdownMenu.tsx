'use client'

import { forwardRef, useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronRight } from 'lucide-react'
import { cn } from './utils'

interface DropdownItem {
  label: string
  icon?: React.ElementType
  onClick?: () => void
  disabled?: boolean
  divider?: boolean
  subItems?: DropdownItem[]
}

interface DropdownMenuProps {
  trigger: React.ReactNode
  items: DropdownItem[]
  align?: 'start' | 'end'
  className?: string
}

const DropdownMenu = forwardRef<HTMLDivElement, DropdownMenuProps>(
  ({ trigger, items, align = 'start', className }, ref) => {
    const [open, setOpen] = useState(false)
    const [activeSubmenu, setActiveSubmenu] = useState<string | null>(null)
    const containerRef = useRef<HTMLDivElement>(null)
    const subTimer = useRef<ReturnType<typeof setTimeout>>()

    const handleClickOutside = useCallback((e: globalThis.MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
        setActiveSubmenu(null)
      }
    }, [])

    useEffect(() => {
      if (open) {
        document.addEventListener('mousedown', handleClickOutside)
      } else {
        document.removeEventListener('mousedown', handleClickOutside)
      }
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [open, handleClickOutside])

    useEffect(() => {
      return () => { if (subTimer.current) clearTimeout(subTimer.current) }
    }, [])

    const handleItemClick = (item: DropdownItem) => {
      if (item.disabled) return
      if (item.subItems) return
      item.onClick?.()
      setOpen(false)
    }

    const handleSubEnter = (label: string) => {
      if (subTimer.current) clearTimeout(subTimer.current)
      subTimer.current = setTimeout(() => setActiveSubmenu(label), 200)
    }

    const handleSubLeave = () => {
      if (subTimer.current) clearTimeout(subTimer.current)
      subTimer.current = setTimeout(() => setActiveSubmenu(null), 300)
    }

    return (
      <div ref={ref} className="relative inline-flex">
        <div
          ref={containerRef}
          onClick={() => setOpen(!open)}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setOpen(!open) } }}
          role="button"
          tabIndex={0}
          aria-haspopup="true"
          aria-expanded={open}
        >
          {trigger}
        </div>
        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -4 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -4 }}
              transition={{ duration: 0.12 }}
              className={cn(
                'absolute top-full mt-1 z-popover min-w-[200px] rounded-xl overflow-hidden',
                'bg-background-card border border-border',
                'shadow-[var(--shadow-elevation-3)]',
                align === 'end' ? 'right-0' : 'left-0',
                className,
              )}
              role="menu"
            >
              {items.map((item, i) => (
                <div key={item.label + i}>
                  {item.divider && (
                    <div className="mx-2" style={{ borderBottom: '1px solid var(--border)', height: '1px' }} />
                  )}
                  <div
                    role="menuitem"
                    aria-disabled={item.disabled || undefined}
                    tabIndex={item.disabled ? -1 : 0}
                    onClick={() => handleItemClick(item)}
                    onMouseEnter={() => {
                      handleSubEnter(item.label)
                      if (!item.disabled) {
                        (document.activeElement as HTMLElement)?.blur()
                      }
                    }}
                    onMouseLeave={handleSubLeave}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault()
                        handleItemClick(item)
                      }
                    }}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2.5 text-sm cursor-pointer transition-colors relative',
                      item.disabled && 'opacity-40 cursor-not-allowed',
                    )}
                    style={{
                      color: 'var(--text-primary)',
                      background: 'transparent',
                    }}
                  >
                    {item.icon && (
                      <item.icon size={16} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
                    )}
                    <span className="flex-1">{item.label}</span>
                    {item.subItems && (
                      <ChevronRight size={14} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
                    )}
                    {item.subItems && activeSubmenu === item.label && (
                      <motion.div
                        initial={{ opacity: 0, x: -4 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -4 }}
                        className="absolute left-full top-0 ml-1 min-w-[180px] rounded-xl overflow-hidden"
                        style={{
                          background: 'var(--background-card)',
                          border: '1px solid var(--border)',
                          boxShadow: 'var(--shadow-elevation-3)',
                        }}
                        onMouseEnter={() => handleSubEnter(item.label)}
                        onMouseLeave={handleSubLeave}
                      >
                        {item.subItems.map((sub, j) => (
                          <div
                            key={sub.label + j}
                            role="menuitem"
                            aria-disabled={sub.disabled || undefined}
                            tabIndex={sub.disabled ? -1 : 0}
                            onClick={() => { if (!sub.disabled) { sub.onClick?.(); setOpen(false) } }}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault()
                                if (!sub.disabled) { sub.onClick?.(); setOpen(false) }
                              }
                            }}
                            className={cn(
                              'flex items-center gap-3 px-3 py-2.5 text-sm cursor-pointer transition-colors',
                              sub.disabled && 'opacity-40 cursor-not-allowed',
                            )}
                            style={{ color: 'var(--text-primary)', background: 'transparent' }}
                          >
                            {sub.icon && (
                              <sub.icon size={16} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
                            )}
                            <span className="flex-1">{sub.label}</span>
                          </div>
                        ))}
                      </motion.div>
                    )}
                  </div>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  },
)

DropdownMenu.displayName = 'DropdownMenu'

export { DropdownMenu }
export type { DropdownMenuProps, DropdownItem }
