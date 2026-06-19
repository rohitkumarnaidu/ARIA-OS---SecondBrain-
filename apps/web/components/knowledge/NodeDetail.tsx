'use client'

import { useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Calendar, Tag, Link2 } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/components/ui/utils'
import type { GraphNode } from './KnowledgeGraph'

interface NodeDetailProps {
  node: GraphNode | null
  onClose: () => void
  onNodeClick: (id: string) => void
}

const typeConfig: Record<string, { label: string; variant: 'success' | 'info' | 'warning' }> = {
  note: { label: 'Note', variant: 'success' },
  resource: { label: 'Resource', variant: 'info' },
  idea: { label: 'Idea', variant: 'warning' },
}

export function NodeDetail({ node, onClose, onNodeClick }: NodeDetailProps) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    },
    [onClose],
  )

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  return (
    <AnimatePresence>
      {node && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 z-30"
            onClick={onClose}
          />
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className={cn(
              'fixed right-0 top-0 h-full w-full max-w-[400px] z-40',
              'backdrop-blur-[12px] bg-[var(--background-card)]/95',
              'border-l border-[var(--border)] shadow-2xl',
              'flex flex-col',
            )}
          >
            <div className="flex items-center justify-between p-6 border-b border-[var(--border)]">
              <div className="flex items-center gap-3 min-w-0">
                <Badge
                  variant={typeConfig[node.type]?.variant ?? 'default'}
                  className="shrink-0"
                >
                  {typeConfig[node.type]?.label ?? node.type}
                </Badge>
              </div>
              <button
                onClick={onClose}
                className={cn(
                  'p-2 rounded-lg transition-colors',
                  'text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
                  'hover:bg-[var(--accent-primary)]/10',
                )}
                aria-label="Close panel"
              >
                <X size={18} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              <div>
                <h2 className="text-xl font-display font-semibold text-[var(--text-primary)]">
                  {node.title}
                </h2>
              </div>

              <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                <Calendar size={14} />
                <span className="font-body">
                  {new Date(node.createdAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </span>
              </div>

              {node.description && (
                <div>
                  <p className="text-sm text-[var(--text-secondary)] font-body leading-relaxed">
                    {node.description}
                  </p>
                </div>
              )}

              {node.tags && node.tags.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                    <Tag size={14} />
                    <span className="font-medium">Tags</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {node.tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                  <Link2 size={14} />
                  <span className="font-medium">Connections</span>
                </div>
                <p className="text-xs text-[var(--text-muted)] font-body">
                  Interact with the graph to explore connected entities.
                </p>
              </div>
            </div>

            <div className="p-4 border-t border-[var(--border)]">
              <button
                onClick={onClose}
                className={cn(
                  'w-full py-2.5 px-4 rounded-lg text-sm font-medium transition-all',
                  'border border-[var(--border)] text-[var(--text-secondary)]',
                  'hover:bg-[var(--accent-primary)]/10 hover:text-[var(--text-primary)]',
                  'hover:border-[var(--accent-primary)]/30',
                )}
              >
                Close
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
