'use client'

import { useEffect, useCallback, useMemo, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Calendar, Tag, Link2 } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/components/ui/utils'
import type { GraphNode, GraphEdge } from './KnowledgeGraph'

interface NodeDetailProps {
  node: GraphNode | null
  edges: GraphEdge[]
  nodes: GraphNode[]
  onClose: () => void
  onNodeClick: (id: string) => void
}

const PANEL_TITLE_ID = 'node-detail-title'

const typeConfig: Record<string, { label: string; variant: 'success' | 'info' | 'warning' }> = {
  note: { label: 'Note', variant: 'success' },
  resource: { label: 'Resource', variant: 'info' },
  idea: { label: 'Idea', variant: 'warning' },
}

export function NodeDetail({ node, edges, nodes, onClose, onNodeClick }: NodeDetailProps): JSX.Element {
  const closeRef = useRef<HTMLButtonElement>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    },
    [onClose],
  )

  useEffect(() => {
    if (!node) return
    previousFocusRef.current = document.activeElement as HTMLElement
    document.addEventListener('keydown', handleKeyDown)
    closeRef.current?.focus()
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      previousFocusRef.current?.focus()
    }
  }, [node, handleKeyDown])

  // Real neighbours only — derived from the edges the store actually returned.
  const connections = useMemo(() => {
    if (!node) return []
    const ids = new Set<string>()
    for (const e of edges) {
      if (e.source === node.id) ids.add(e.target)
      else if (e.target === node.id) ids.add(e.source)
    }
    return nodes.filter(n => ids.has(n.id))
  }, [node, edges, nodes])

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
            aria-hidden="true"
          />
          <motion.aside
            role="dialog"
            aria-modal="true"
            aria-labelledby={PANEL_TITLE_ID}
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className={cn(
              'fixed right-0 top-0 h-full w-full max-w-[400px] z-modal',
              'backdrop-blur-[12px] bg-background-card/95',
              'border-l border-border shadow-2xl',
              'flex flex-col',
            )}
          >
            <div className="flex items-center justify-between p-6 border-b border-border">
              <div className="flex items-center gap-3 min-w-0">
                <Badge
                  variant={typeConfig[node.type]?.variant ?? 'default'}
                  className="shrink-0"
                >
                  {typeConfig[node.type]?.label ?? node.type}
                </Badge>
              </div>
              <button
                ref={closeRef}
                type="button"
                onClick={onClose}
                className={cn(
                  'p-2 rounded-lg transition-colors',
                  'text-text-secondary hover:text-text-primary',
                  'hover:bg-accent-primary/10',
                )}
                aria-label="Close panel"
              >
                <X size={18} aria-hidden="true" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              <div>
                <h2 id={PANEL_TITLE_ID} className="text-xl font-display font-semibold text-text-primary">
                  {node.title}
                </h2>
              </div>

              <div className="flex items-center gap-2 text-sm text-text-secondary">
                <Calendar size={14} aria-hidden="true" />
                <time dateTime={node.createdAt} className="font-body">
                  {new Date(node.createdAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </time>
              </div>

              {node.description && (
                <div>
                  <p className="text-sm text-text-secondary font-body leading-relaxed">
                    {node.description}
                  </p>
                </div>
              )}

              {node.tags && node.tags.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-text-secondary">
                    <Tag size={14} aria-hidden="true" />
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
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <Link2 size={14} aria-hidden="true" />
                  <span className="font-medium">Connections</span>
                </div>
                {connections.length === 0 ? (
                  <p className="text-xs text-text-muted font-body">
                    Nothing is linked to this item yet.
                  </p>
                ) : (
                  <ul className="space-y-1">
                    {connections.map((c) => (
                      <li key={c.id}>
                        <button
                          type="button"
                          onClick={() => onNodeClick(c.id)}
                          className="w-full truncate rounded-lg border border-border px-3 py-2 text-left text-xs text-text-secondary transition-colors hover:border-accent-primary/30 hover:text-text-primary hover:bg-accent-primary/10"
                        >
                          {c.title}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="p-4 border-t border-border">
              <button
                type="button"
                onClick={onClose}
                className={cn(
                  'w-full py-2.5 px-4 rounded-lg text-sm font-medium transition-all',
                  'border border-border text-text-secondary',
                  'hover:bg-accent-primary/10 hover:text-text-primary',
                  'hover:border-accent-primary/30',
                )}
              >
                Close
              </button>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}

export type { NodeDetailProps }
