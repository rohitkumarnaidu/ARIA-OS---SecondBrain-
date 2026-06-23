'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Database, RefreshCw, Download, Trash2, Search, BookOpen, Clock, User, TrendingUp, Lightbulb, MessageSquare, Code, Target, Zap, ChevronDown, ChevronUp, Plus, Pencil } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { cn } from '@/components/ui/utils'
import { useMemoryStore } from '@/lib/stores'
import { MemoryEditModal } from '@/components/memory/MemoryEditModal'
import type { Memory, MemoryUpdate } from '@/lib/types'

type MemoryCategory = 'all' | 'preference' | 'pattern' | 'fact' | 'context' | 'learning'
type MemoryImportance = 'all' | 'low' | 'medium' | 'high' | 'critical'

const CATEGORY_TABS: { key: MemoryCategory; label: string; icon: typeof Brain }[] = [
  { key: 'all', label: 'All', icon: Database },
  { key: 'preference', label: 'Preferences', icon: User },
  { key: 'pattern', label: 'Patterns', icon: TrendingUp },
  { key: 'fact', label: 'Facts', icon: BookOpen },
  { key: 'context', label: 'Context', icon: Brain },
  { key: 'learning', label: 'Learning', icon: Lightbulb },
]

const IMPORTANCE_CONFIG: Record<string, { label: string; variant: 'default' | 'success' | 'warning' | 'error' | 'info' | 'outline'; color: string }> = {
  critical: { label: 'Critical', variant: 'error', color: 'var(--accent-danger)' },
  high: { label: 'High', variant: 'warning', color: 'var(--accent-warning)' },
  medium: { label: 'Medium', variant: 'info', color: 'var(--accent-primary)' },
  low: { label: 'Low', variant: 'outline', color: 'var(--text-tertiary)' },
}

const SOURCE_ICONS: Record<string, typeof Brain> = {
  brain: Brain,
  message: MessageSquare,
  code: Code,
  target: Target,
  zap: Zap,
  trending: TrendingUp,
  user: User,
  clock: Clock,
}

function getRelativeDate(dateStr: string): string {
  const now = Date.now()
  const date = new Date(dateStr).getTime()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  return `${Math.floor(diffDays / 30)} months ago`
}

function formatValue(val: unknown): string {
  if (typeof val === 'string') return val
  if (val === null || val === undefined) return ''
  try { return JSON.stringify(val) } catch { return String(val) }
}

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.06 },
  },
}

const statVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 },
}

export default function MemoryPage(): JSX.Element {
  const [mounted, setMounted] = useState(false)
  const [activeTab, setActiveTab] = useState<MemoryCategory>('all')
  const [importanceFilter, setImportanceFilter] = useState<MemoryImportance>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [allowLearning, setAllowLearning] = useState(true)
  const [showClearConfirm, setShowClearConfirm] = useState(false)
  const [editTarget, setEditTarget] = useState<Memory | null>(null)
  const [editOpen, setEditOpen] = useState(false)
  const [showMemoryGraph, setShowMemoryGraph] = useState(false)
  const { items: storeItems, loading, error, fetch, remove, update } = useMemoryStore()

  useEffect(() => { setMounted(true); fetch() }, [fetch])

  const handleEdit = useCallback((m: Memory) => {
    setEditTarget(m)
    setEditOpen(true)
  }, [])

  const handleSaveEdit = useCallback(async (id: string, data: MemoryUpdate) => {
    await update(id, data)
  }, [update])

  const handleDeleteEdit = useCallback(async (id: string) => {
    await remove(id)
  }, [remove])

  const toggleExpand = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  const handleClearMemories = useCallback(async () => {
    try {
      for (const m of storeItems) await remove(m.id)
    } catch { /* ignore */ }
    setShowClearConfirm(false)
  }, [storeItems, remove])

  const handleExportMemories = useCallback(() => {
    const blob = new Blob([JSON.stringify(storeItems, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'aria-memories.json'
    a.click()
    URL.revokeObjectURL(url)
  }, [storeItems])

  const filteredMemories = useMemo(() => {
    let result = storeItems
    if (activeTab !== 'all') {
      result = result.filter((m) => m.type === activeTab)
    }
    if (importanceFilter !== 'all') {
      result = result.filter((m) => m.importance === importanceFilter)
    }
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase()
      result = result.filter(
        (m) =>
          m.key.toLowerCase().includes(q) ||
          formatValue(m.value).toLowerCase().includes(q) ||
          m.type.toLowerCase().includes(q) ||
          (m.tags ?? []).some(t => t.toLowerCase().includes(q))
      )
    }
    return result
  }, [storeItems, activeTab, importanceFilter, searchQuery])

  const stats = useMemo(() => ({
    total: storeItems.length,
    critical: storeItems.filter((m) => m.importance === 'critical').length,
    high: storeItems.filter((m) => m.importance === 'high').length,
    medium: storeItems.filter((m) => m.importance === 'medium').length,
    low: storeItems.filter((m) => m.importance === 'low').length,
    grouped: storeItems.reduce((acc, m) => {
      acc[m.type] = (acc[m.type] || 0) + 1
      return acc
    }, {} as Record<string, number>),
    lastUpdated: storeItems.length > 0
      ? getRelativeDate([...storeItems].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0].created_at)
      : 'Never',
  }), [storeItems])

  const statCards = useMemo(() => [
    { label: 'Total Memories', value: stats.total, icon: Database, color: 'var(--accent-primary)' },
    { label: 'High/Critical', value: stats.high + stats.critical, icon: Brain, color: 'var(--accent-warning)' },
    { label: 'Types', value: Object.keys(stats.grouped).length, icon: BookOpen, color: 'var(--accent-secondary)' },
    { label: 'Last Updated', value: stats.lastUpdated, icon: Clock, color: 'var(--accent-info)' },
  ], [stats])

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (loading) {
    return (
      <div className="space-y-6 pb-8">
        <Skeleton variant="text" className="h-8 w-56" />
        <Skeleton variant="text" className="h-4 w-72" />
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="card" className="h-24" />
          ))}
        </div>
        <Skeleton variant="card" className="h-10 w-96" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="card" className="h-28" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6 pb-8"
    >
      <PageHeader
        title="AI Memory Explorer"
        description="Everything ARIA has learned about you — preferences, patterns, and facts"
      />

      <motion.div variants={statVariants} className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.label}>
              <CardContent>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-[var(--text-tertiary)] font-medium uppercase tracking-wider">
                    {stat.label}
                  </span>
                  <Icon size={18} style={{ color: stat.color }} className="opacity-60" />
                </div>
                <div className="text-2xl font-display font-bold text-[var(--text-primary)]">
                  {stat.value}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </motion.div>

      <motion.div variants={statVariants}>
        <Card>
          <CardContent className="space-y-4">
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search memories by key, value, type, or tags..."
                className="w-full h-10 pl-10 pr-4 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                aria-label="Search memories"
              />
            </div>

            <div className="flex flex-wrap gap-2 items-center">
              <div className="flex gap-1 overflow-x-auto pb-1" role="tablist" aria-label="Memory categories">
                {CATEGORY_TABS.map((tab) => {
                  const Icon = tab.icon
                  const isActive = activeTab === tab.key
                  const count = tab.key === 'all'
                    ? storeItems.length
                    : storeItems.filter((m) => m.type === tab.key).length
                  return (
                    <button
                      key={tab.key}
                      role="tab"
                      aria-selected={isActive}
                      aria-controls={`panel-${tab.key}`}
                      onClick={() => setActiveTab(tab.key)}
                      className={cn(
                        'flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-all whitespace-nowrap shrink-0',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] focus-visible:ring-offset-1',
                        isActive
                          ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--accent-primary)]/20'
                          : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--background-elevated)] border border-transparent'
                      )}
                    >
                      <Icon size={14} />
                      {tab.label}
                      <span className="text-[10px] opacity-60">({count})</span>
                    </button>
                  )
                })}
              </div>

              <div className="flex items-center gap-1 ml-auto" role="group" aria-label="Importance filter">
                {(['all', 'critical', 'high', 'medium', 'low'] as const).map((level) => {
                  const isActive = importanceFilter === level
                  return (
                    <button
                      key={level}
                      onClick={() => setImportanceFilter(level)}
                      className={cn(
                        'px-2.5 py-1.5 rounded-lg text-[10px] font-medium transition-all',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]',
                        isActive
                          ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--accent-primary)]/20'
                          : 'text-[var(--text-tertiary)] hover:text-[var(--text-primary)] border border-transparent'
                      )}
                    >
                      {level === 'all' ? 'All' : IMPORTANCE_CONFIG[level].label}
                    </button>
                  )
                })}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={statVariants}>
        <div
          role="tabpanel"
          id={`panel-${activeTab}`}
          aria-labelledby={activeTab}
        >
          {filteredMemories.length === 0 ? (
            <Card className="py-12">
              <EmptyState
                icon={<Brain size={48} />}
                title={
                  searchQuery
                    ? `No memories match "${searchQuery}"`
                    : `No ${activeTab === 'all' ? '' : activeTab} learned yet`
                }
                description={
                  searchQuery
                    ? 'Try a different search term or clear the importance filter'
                    : `Continue using ARIA to build your profile — ${activeTab} will appear here as they're detected`
                }
              />
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <AnimatePresence mode="popLayout">
                {filteredMemories.map((memory, index) => {
                  const isExpanded = expandedIds.has(memory.id)
                  const impConf = IMPORTANCE_CONFIG[memory.importance] ?? IMPORTANCE_CONFIG.medium
                  const tags = memory.tags ?? []

                  return (
                    <motion.div
                      key={memory.id}
                      layout
                      initial={{ opacity: 0, scale: 0.97 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.97 }}
                      transition={{ delay: index * 0.03, type: 'spring', stiffness: 250, damping: 25 }}
                    >
                      <Card className="h-full group relative">
                        <CardContent>
                          <div className="flex items-start gap-2 mb-2">
                            <Badge variant={memory.type === 'preference' ? 'default' : memory.type === 'pattern' ? 'info' : memory.type === 'fact' ? 'success' : memory.type === 'context' ? 'warning' : 'outline'} className="shrink-0">
                              {memory.type}
                            </Badge>
                            <Badge variant={impConf.variant}>
                              {impConf.label}
                            </Badge>
                            {tags.slice(0, 3).map(tag => (
                              <Badge key={tag} variant="outline" className="text-[10px]">
                                {tag}
                              </Badge>
                            ))}
                            <span className="text-xs text-[var(--text-tertiary)] ml-auto shrink-0">
                              {getRelativeDate(memory.created_at)}
                            </span>
                          </div>

                          <div className="flex items-start gap-2">
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-medium text-[var(--text-secondary)] mb-0.5 font-mono">
                                {memory.key}
                              </p>
                              <p className={cn(
                                'text-sm text-[var(--text-primary)] leading-relaxed',
                                !isExpanded && 'line-clamp-2'
                              )}>
                                {formatValue(memory.value)}
                              </p>
                            </div>
                          </div>

                          {isExpanded && (
                            <motion.div
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                              className="mt-3 pt-3 border-t border-[var(--border)] space-y-2"
                            >
                              <div className="text-xs text-[var(--text-tertiary)] font-mono">
                                ID: {memory.id}
                              </div>
                              {memory.expires_at && (
                                <div className="text-xs text-[var(--accent-warning)]">
                                  Expires: {new Date(memory.expires_at).toLocaleDateString()}
                                </div>
                              )}
                            </motion.div>
                          )}

                          <div className="flex items-center justify-end gap-1 mt-2">
                            <button
                              onClick={(e) => { e.stopPropagation(); handleEdit(memory) }}
                              className="p-1.5 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] hover:bg-[var(--background-elevated)] transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100"
                              aria-label="Edit memory"
                            >
                              <Pencil size={12} />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                toggleExpand(memory.id)
                              }}
                              className="flex items-center gap-1 text-xs text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] rounded"
                              aria-label={isExpanded ? 'Collapse memory' : 'Expand memory'}
                            >
                              {isExpanded ? (
                                <>Show less <ChevronUp size={12} /></>
                              ) : (
                                <>Show more <ChevronDown size={12} /></>
                              )}
                            </button>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>
          )}
        </div>
      </motion.div>

      <motion.div variants={statVariants}>
        <Card>
          <CardHeader>
            <CardTitle>
              <div className="flex items-center gap-2">
                <Database size={16} className="text-[var(--accent-primary)]" />
                <span>Memory Controls</span>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <button
                  role="switch"
                  aria-checked={allowLearning}
                  aria-label="Toggle AI learning from chat"
                  onClick={() => setAllowLearning((prev) => !prev)}
                  className={cn(
                    'relative w-10 h-6 rounded-full transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] focus-visible:ring-offset-1',
                    allowLearning ? 'bg-[var(--accent-primary)]' : 'bg-[var(--background-elevated)]'
                  )}
                >
                  <span
                    className={cn(
                      'block w-4 h-4 rounded-full bg-white shadow-sm transition-transform duration-200',
                      allowLearning ? 'translate-x-5' : 'translate-x-1'
                    )}
                  />
                </button>
                <div>
                  <div className="text-sm font-medium text-[var(--text-primary)]">
                    Allow AI to learn from chat
                  </div>
                  <div className="text-xs text-[var(--text-tertiary)]">
                    {allowLearning ? 'ARIA is actively building your profile' : 'Learning is paused'}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleExportMemories}
                  disabled={storeItems.length === 0}
                  aria-label="Export memories as JSON"
                >
                  <Download size={14} />
                  Export
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fetch()}
                  aria-label="Refresh memories"
                >
                  <RefreshCw size={14} />
                  Refresh
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-[var(--accent-error)] hover:bg-[var(--accent-error)]/10"
                  onClick={() => setShowClearConfirm(true)}
                  disabled={storeItems.length === 0}
                  aria-label="Clear all memories"
                >
                  <Trash2 size={14} />
                  Clear All
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <MemoryEditModal
        memory={editTarget}
        open={editOpen}
        onClose={() => { setEditOpen(false); setEditTarget(null) }}
        onSave={handleSaveEdit}
        onDelete={handleDeleteEdit}
      />

      <AnimatePresence>
        {showClearConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-[var(--z-modal)] p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="clear-memories-title"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="bg-[var(--background-card)] border border-[var(--border)] rounded-2xl p-6 w-full max-w-sm"
            >
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-[var(--accent-error)]/10 flex items-center justify-center mx-auto mb-4">
                  <Trash2 size={24} className="text-[var(--accent-error)]" />
                </div>
                <h2 id="clear-memories-title" className="text-lg font-display font-semibold text-[var(--text-primary)] mb-2">
                  Clear All Memories?
                </h2>
                <p className="text-sm text-[var(--text-secondary)] mb-6">
                  This action cannot be undone. ARIA will lose everything it has learned about you and will start fresh.
                </p>
                <div className="flex gap-3">
                  <Button variant="outline" onClick={() => setShowClearConfirm(false)} className="flex-1">
                    Cancel
                  </Button>
                  <Button variant="destructive" onClick={handleClearMemories} className="flex-1">
                    <Trash2 size={14} />
                    Clear Everything
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
