'use client'

import { memo,  useState, useCallback, type ReactNode  } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronRight } from 'lucide-react'
import { cn } from './utils'

interface TreeItem {
  id: string
  label: string
  icon?: ReactNode
  children?: TreeItem[]
  disabled?: boolean
}

interface TreeViewProps {
  items: TreeItem[]
  onSelect?: (item: TreeItem) => void
  defaultExpandedIds?: string[]
  className?: string
}

const TreeNode = memo(function TreeNode({
  item,
  depth,
  onSelect,
  expandedIds,
  toggleExpand,
  selectedId,
  setSelectedId,
}: {
  item: TreeItem
  depth: number
  onSelect?: (item: TreeItem) => void
  expandedIds: Set<string>
  toggleExpand: (id: string) => void
  selectedId: string | null
  setSelectedId: (id: string | null) => void
}) {
  const hasChildren = item.children && item.children.length > 0
  const isExpanded = expandedIds.has(item.id)
  const isSelected = selectedId === item.id

  const handleClick = () => {
    if (item.disabled) return
    setSelectedId(item.id)
    onSelect?.(item)
    if (hasChildren) toggleExpand(item.id)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
    if (e.key === 'ArrowRight' && hasChildren && !isExpanded) {
      e.preventDefault()
      toggleExpand(item.id)
    }
    if (e.key === 'ArrowLeft' && hasChildren && isExpanded) {
      e.preventDefault()
      toggleExpand(item.id)
    }
  }

  return (
    <div>
      <div
        role="treeitem"
        tabIndex={0}
        aria-expanded={hasChildren ? isExpanded : undefined}
				aria-selected={isSelected}
        aria-disabled={item.disabled || undefined}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        className={cn(
          'flex items-center gap-2 px-2 py-1.5 rounded-md text-sm cursor-pointer transition-all duration-150',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-1 focus-visible:ring-offset-[var(--background)]',
          item.disabled && 'opacity-40 cursor-not-allowed pointer-events-none',
          isSelected
            ? 'bg-[var(--accent-primary)]/15 text-[var(--accent-primary)]'
            : 'text-text-secondary hover:bg-[var(--glass-heavy)] hover:text-text-primary',
        )}
        style={{ paddingLeft: `${depth * 20 + 8}px` }}
      >
        {hasChildren && (
          <motion.span
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: 0.15 }}
            className="shrink-0 flex items-center"
          >
            <ChevronRight size={14} />
          </motion.span>
        )}
        {!hasChildren && <span className="w-[14px] shrink-0" />}
        {item.icon && <span className="shrink-0">{item.icon}</span>}
        <span className="truncate">{item.label}</span>
      </div>

      <AnimatePresence initial={false}>
        {hasChildren && isExpanded && (
          <motion.div
            key={`children-${item.id}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.15, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            {item.children!.map((child) => (
              <TreeNode
                key={child.id}
                item={child}
                depth={depth + 1}
                onSelect={onSelect}
                expandedIds={expandedIds}
                toggleExpand={toggleExpand}
                selectedId={selectedId}
                setSelectedId={setSelectedId}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
})

const TreeView = memo(function TreeView({ items, onSelect, defaultExpandedIds, className }: TreeViewProps) {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(
    () => new Set(defaultExpandedIds),
  )
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const toggleExpand = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  return (
    <div className={cn('flex flex-col gap-0.5', className)} role="tree">
      {items.map((item) => (
        <TreeNode
          key={item.id}
          item={item}
          depth={0}
          onSelect={onSelect}
          expandedIds={expandedIds}
          toggleExpand={toggleExpand}
          selectedId={selectedId}
          setSelectedId={setSelectedId}
        />
      ))}
    </div>
  )
})

TreeView.displayName = 'TreeView'

export { TreeView }
export type { TreeViewProps, TreeItem }
