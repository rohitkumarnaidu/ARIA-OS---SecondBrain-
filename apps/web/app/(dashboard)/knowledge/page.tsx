'use client'

import { useState, useMemo, useCallback, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, List, Map, FileText, Link, Lightbulb, AlertTriangle } from 'lucide-react'
import { useKnowledgeStore } from '@/lib/stores'
import { KnowledgeGraph, NodeDetail, KnowledgeSearch } from '@/components/knowledge'
import { PageHeader } from '@/components/ui/PageHeader'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { Button } from '@/components/ui/Button'
import { cn } from '@/components/ui/utils'
import type { GraphEdge } from '@/components/knowledge'
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

function LoadingSkeleton(): JSX.Element {
  return (
    <div className="space-y-6 pb-8" role="status" aria-label="Loading knowledge vault">
      <Skeleton variant="text" className="h-8 w-64" />
      <Skeleton variant="text" className="h-4 w-96" />
      <div className="flex gap-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} variant="text" className="h-8 w-24" />
        ))}
      </div>
      <Skeleton variant="card" className="h-10 w-full max-w-xl" />
      <Skeleton variant="chart" className="h-[500px] w-full" />
    </div>
  )
}

export default function KnowledgePage(): JSX.Element {
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

  const filteredEdges = useMemo<GraphEdge[]>(() => {
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

  const clearFilters = useCallback(() => {
    setSearchQuery('')
    setSearchFilters({ types: [], tags: [] })
  }, [])

  const hasActiveFilters =
    searchQuery.trim().length > 0 || searchFilters.types.length > 0 || searchFilters.tags.length > 0

  if (loading && nodes.length === 0) return <LoadingSkeleton />

  if (error && nodes.length === 0) {
    return (
      <div className="space-y-6 pb-8">
        <PageHeader
          title="Knowledge Vault"
          description="Explore your knowledge graph — notes, resources, and ideas connected by context."
        />
        <ErrorState
          status={500}
          title="Couldn't load your knowledge vault"
          description={error}
          onRetry={() => { void fetchKnowledge() }}
        />
      </div>
    )
  }

  // Partial: the graph resolved but nothing is linked. Say so instead of
  // showing a bare canvas that reads as a broken render.
  const hasNoConnections = nodes.length > 0 && edges.length === 0 && !error
  const showNoResults = nodes.length > 0 && filteredNodes.length === 0

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

      {error && (
        <motion.div
          variants={sectionVariants}
          role="alert"
          className="flex items-center justify-between gap-3 rounded-lg border border-accent-error/30 bg-accent-error/10 px-4 py-3"
        >
          <span className="text-sm text-text-primary">{error}</span>
          <Button variant="outline" size="sm" onClick={() => { void fetchKnowledge() }}>
            Retry
          </Button>
        </motion.div>
      )}

      <motion.div variants={sectionVariants} className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-1 p-1 rounded-lg bg-background-card border border-border" role="group" aria-label="View mode">
          {VIEW_OPTIONS.map(({ value, label, icon: Icon }) => (
            <button
              key={value}
              type="button"
              onClick={() => handleViewMode(value)}
              aria-pressed={viewMode === value}
              className={cn(
                'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all font-body',
                viewMode === value
                  ? 'bg-accent-primary/20 text-accent-primary shadow-sm'
                  : 'text-text-secondary hover:text-text-primary hover:bg-background-elevated',
              )}
            >
              <Icon size={16} aria-hidden="true" />
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

      {nodes.length === 0 ? (
        <motion.div variants={sectionVariants}>
          <div className="rounded-xl border border-border bg-background-card">
            <EmptyState
              icon={<BarChart3 size={40} aria-hidden="true" />}
              title="Your knowledge vault is empty"
              description="Add notes, resources and ideas and ARIA will connect them into a graph you can explore."
            />
          </div>
        </motion.div>
      ) : (
        <>
          {hasNoConnections && !showNoResults && (
            <motion.p
              variants={sectionVariants}
              className="flex items-center gap-2 rounded-lg border border-border bg-background-card px-4 py-3 text-sm text-text-secondary"
            >
              <AlertTriangle size={16} className="shrink-0 text-accent-warning" aria-hidden="true" />
              Your items loaded, but none of them are connected yet — the graph view will stay empty until links exist.
            </motion.p>
          )}

          <motion.div
            variants={sectionVariants}
            className="relative"
            style={{ height: 'calc(100vh - 340px)', minHeight: '500px' }}
          >
            {showNoResults ? (
              <div className="h-full rounded-xl border border-border bg-background-card">
                <EmptyState
                  icon={<List size={40} aria-hidden="true" />}
                  title="No results"
                  description={`Nothing in your vault matches "${searchQuery.trim()}".`}
                  action={hasActiveFilters ? { label: 'Clear search and filters', onClick: clearFilters } : undefined}
                />
              </div>
            ) : viewMode === 'graph' ? (
              <KnowledgeGraph
                nodes={filteredNodes}
                edges={filteredEdges}
                onNodeClick={handleNodeClick}
                searchQuery={searchQuery}
              />
            ) : viewMode === 'list' ? (
              <div className="h-full rounded-xl border border-border bg-background-card overflow-y-auto">
                <div className="divide-y divide-border">
                  {filteredNodes.map(node => {
                    const TypeIcon = typeIcon[node.type] || FileText
                    const badgeVariant = typeBadgeVariant[node.type] || 'info'
                    return (
                      <button
                        key={node.id}
                        onClick={() => handleNodeClick(node.id)}
                        className="w-full flex items-start gap-3 px-5 py-4 text-left hover:bg-glass-light transition-colors"
                      >
                        <div className="flex items-center justify-center w-8 h-8 rounded-lg shrink-0 mt-0.5 bg-glass-light">
                          <TypeIcon size={14} className="text-accent-secondary" aria-hidden="true" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-text-primary">{node.title}</p>
                          <p className="text-xs text-text-secondary mt-0.5 line-clamp-2">{node.description}</p>
                          <div className="flex items-center gap-2 mt-2 flex-wrap">
                            <Badge variant={badgeVariant} className="text-[10px] px-1.5 py-0.5">{node.type}</Badge>
                            {node.tags?.slice(0, 3).map(tag => (
                              <span
                                key={tag}
                                className="text-[10px] font-mono text-text-tertiary px-1.5 py-0.5 rounded bg-background-elevated"
                              >
                                #{tag}
                              </span>
                            ))}
                            {node.tags && node.tags.length > 3 && (
                              <span className="text-[10px] text-text-tertiary">+{node.tags.length - 3}</span>
                            )}
                          </div>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full rounded-xl border border-border bg-background-card">
                <div className="text-center space-y-3">
                  <Map size={32} className="mx-auto text-text-tertiary" aria-hidden="true" />
                  <div className="text-text-tertiary text-lg font-display">Map View</div>
                  <p className="text-sm text-text-tertiary font-body max-w-[280px]">
                    Map view coming soon — spatial exploration of your knowledge graph.
                  </p>
                </div>
              </div>
            )}
          </motion.div>
        </>
      )}

      <NodeDetail
        node={selectedNode}
        edges={filteredEdges}
        nodes={filteredNodes}
        onClose={() => setSelectedNodeId(null)}
        onNodeClick={handleNodeClick}
      />
    </motion.div>
  )
}
