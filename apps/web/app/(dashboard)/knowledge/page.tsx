'use client'

import { useState, useMemo, useCallback, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, List, Map, FileText, Link, Lightbulb } from 'lucide-react'
import { useKnowledgeStore } from '@/lib/stores'
import { KnowledgeGraph, NodeDetail, KnowledgeSearch } from '@/components/knowledge'
import { PageHeader } from '@/components/ui/PageHeader'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/components/ui/utils'
import type { GraphNode, GraphEdge } from '@/components/knowledge'
import type { SearchFilters } from '@/components/knowledge'

type ViewMode = 'graph' | 'list' | 'map'

const VIEW_OPTIONS: { value: ViewMode; label: string; icon: typeof BarChart3 }[] = [
  { value: 'graph', label: 'Graph', icon: BarChart3 },
  { value: 'list', label: 'List', icon: List },
  { value: 'map', label: 'Map', icon: Map },
]

const typeBadgeVariant: Record<string, 'success' | 'info' | 'warning'> = {
  note: 'success',
  resource: 'info',
  idea: 'warning',
}

const typeIcon: Record<string, React.ElementType> = {
  note: FileText,
  resource: Link,
  idea: Lightbulb,
}



const containerVariants = {
  initial: {},
  animate: { transition: { staggerChildren: 0.08 } },
}

const sectionVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
}

export default function KnowledgePage() {
  const [viewMode, setViewMode] = useState<ViewMode>('graph')
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({ types: [], tags: [] })

  const { nodes, edges, loading, error, fetch: fetchKnowledge } = useKnowledgeStore()

  useEffect(() => {
    fetchKnowledge()
    try {
      const saved = localStorage.getItem('knowledge-view')
      if (saved === 'graph' || saved === 'list' || saved === 'map') setViewMode(saved)
    } catch { /* ignore */ }
  }, [fetchKnowledge])

  const handleViewMode = useCallback((mode: ViewMode) => {
    setViewMode(mode)
    try { localStorage.setItem('knowledge-view', mode) } catch { /* ignore */ }
  }, [])

  const allTags = useMemo(() => {
    const set = new Set<string>()
    for (const n of nodes) { n.tags?.forEach(t => set.add(t)) }
    return Array.from(set).sort()
  }, [nodes])

  const filteredNodes = useMemo(() => {
    return nodes.filter(n => {
      if (searchQuery) {
        const q = searchQuery.toLowerCase()
        const match = n.title.toLowerCase().includes(q) || n.tags?.some(t => t.includes(q))
        if (!match) return false
      }
      if (searchFilters.types.length > 0 && !searchFilters.types.includes(n.type)) return false
      if (searchFilters.tags.length > 0 && !n.tags?.some(t => searchFilters.tags.includes(t))) return false
      return true
    })
  }, [searchQuery, searchFilters, nodes])

  const filteredEdges = useMemo(() => {
    const ids = new Set(filteredNodes.map(n => n.id))
    return edges.filter(e => ids.has(e.source) && ids.has(e.target))
  }, [filteredNodes, edges])

  const selectedNode = useMemo(() => {
    if (!selectedNodeId) return null
    return nodes.find(n => n.id === selectedNodeId) ?? null
  }, [selectedNodeId, nodes])

  const handleSearch = useCallback((query: string, filters: SearchFilters) => {
    setSearchQuery(query)
    setSearchFilters(filters)
  }, [])

  const handleNodeClick = useCallback((id: string) => {
    setSelectedNodeId(id)
  }, [])

  return (
    <motion.div
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="space-y-6 pb-8 h-full"
    >
      <motion.div variants={sectionVariants}>
        <PageHeader
          title="Knowledge Vault"
          description="Explore your knowledge graph — notes, resources, and ideas connected by context."
        />
      </motion.div>

      <motion.div variants={sectionVariants} className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-1 p-1 rounded-lg bg-[var(--background-card)] border border-[var(--border)]">
          {VIEW_OPTIONS.map(({ value, label, icon: Icon }) => (
            <button
              key={value}
              onClick={() => handleViewMode(value)}
              className={cn(
                'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all font-body',
                viewMode === value
                  ? 'bg-[var(--accent-primary)]/20 text-[var(--accent-primary)] shadow-sm'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--background-elevated)]',
              )}
            >
              <Icon size={16} />
              {label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="success" className="text-xs">Notes</Badge>
          <Badge variant="info" className="text-xs">Resources</Badge>
          <Badge variant="warning" className="text-xs">Ideas</Badge>
        </div>
      </motion.div>

      <motion.div variants={sectionVariants}>
        <KnowledgeSearch onSearch={handleSearch} tags={allTags} />
      </motion.div>

      <motion.div
        variants={sectionVariants}
        className="relative"
        style={{ height: 'calc(100vh - 340px)', minHeight: '500px' }}
      >
        {viewMode === 'graph' ? (
          <KnowledgeGraph
            nodes={filteredNodes}
            edges={filteredEdges}
            onNodeClick={handleNodeClick}
            searchQuery={searchQuery}
          />
        ) : viewMode === 'list' ? (
          <div className="h-full rounded-xl border border-[var(--border)] bg-[var(--background-card)] overflow-y-auto">
            {filteredNodes.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-2">
                  <div className="text-[var(--text-tertiary)] text-lg font-display">No results</div>
                  <p className="text-sm text-[var(--text-tertiary)] font-body">Try adjusting your search or filters.</p>
                </div>
              </div>
            ) : (
              <div className="divide-y divide-[var(--border)]">
                {filteredNodes.map(node => {
                  const TypeIcon = typeIcon[node.type] || FileText
                  const badgeVariant = typeBadgeVariant[node.type] || 'info'
                  return (
                    <button
                      key={node.id}
                      onClick={() => handleNodeClick(node.id)}
                      className="w-full flex items-start gap-3 px-5 py-4 text-left hover:bg-[var(--glass-light)] transition-colors"
                    >
                      <div className="flex items-center justify-center w-8 h-8 rounded-lg shrink-0 mt-0.5 bg-[var(--glass-light)]">
                        <TypeIcon size={14} className="text-[var(--accent-secondary)]" aria-hidden="true" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-[var(--text-primary)]">{node.title}</p>
                        <p className="text-xs text-[var(--text-secondary)] mt-0.5 line-clamp-2">{node.description}</p>
                        <div className="flex items-center gap-2 mt-2 flex-wrap">
                          <Badge variant={badgeVariant} className="text-[10px] px-1.5 py-0.5">{node.type}</Badge>
                          {node.tags?.slice(0, 3).map(tag => (
                            <span
                              key={tag}
                              className="text-[10px] font-mono text-[var(--text-tertiary)] px-1.5 py-0.5 rounded bg-[var(--background-elevated)]"
                            >
                              #{tag}
                            </span>
                          ))}
                          {node.tags && node.tags.length > 3 && (
                            <span className="text-[10px] text-[var(--text-tertiary)]">+{node.tags.length - 3}</span>
                          )}
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full rounded-xl border border-[var(--border)] bg-[var(--background-card)]">
            <div className="text-center space-y-3">
              <Map size={32} className="mx-auto text-[var(--text-tertiary)]" aria-hidden="true" />
              <div className="text-[var(--text-tertiary)] text-lg font-display">Map View</div>
              <p className="text-sm text-[var(--text-tertiary)] font-body max-w-[280px]">
                Map view coming soon — spatial exploration of your knowledge graph.
              </p>
            </div>
          </div>
        )}
      </motion.div>

      <NodeDetail
        node={selectedNode}
        onClose={() => setSelectedNodeId(null)}
        onNodeClick={handleNodeClick}
      />
    </motion.div>
  )
}
