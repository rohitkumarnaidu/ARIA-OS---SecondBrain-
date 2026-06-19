'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Database, RefreshCw, Download, Trash2, Search, BookOpen, Clock, User, TrendingUp, Lightbulb, MessageSquare, Code, Target, Zap, ChevronDown, ChevronUp } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { cn } from '@/components/ui/utils'
import { useMemoryStore } from '@/lib/stores'

type MemoryCategory = 'all' | 'preferences' | 'patterns' | 'facts'
type Confidence = 'high' | 'medium' | 'low'

interface MemoryItem {
  id: string
  category: Exclude<MemoryCategory, 'all'>
  content: string
  fullContent: string
  confidence: Confidence
  createdAt: string
  sourceIcon: string
  sourceContext: string
}

const CATEGORY_TABS: { key: MemoryCategory; label: string; icon: typeof Brain }[] = [
  { key: 'all', label: 'All', icon: Database },
  { key: 'preferences', label: 'Preferences', icon: User },
  { key: 'patterns', label: 'Patterns', icon: TrendingUp },
  { key: 'facts', label: 'Facts', icon: BookOpen },
]

const CONFIDENCE_CONFIG: Record<Confidence, { label: string; variant: 'default' | 'success' | 'warning' | 'error' | 'info' | 'outline' }> = {
  high: { label: 'High', variant: 'success' },
  medium: { label: 'Medium', variant: 'warning' },
  low: { label: 'Low', variant: 'outline' },
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
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [allowLearning, setAllowLearning] = useState(true)
  const [showClearConfirm, setShowClearConfirm] = useState(false)
  const { items: storeItems, loading, error, fetch, remove } = useMemoryStore()

  const memories = storeItems.map((m: any) => ({
      id: m.id,
      category: m.type === 'preference' || m.type === 'pattern' || m.type === 'fact' ? m.type : 'patterns',
      content: typeof m.value === 'string' ? m.value : m.key,
      fullContent: `${m.key}: ${JSON.stringify(m.value)}`,
      confidence: m.importance === 'high' || m.importance === 'critical' ? 'high' as const : m.importance === 'medium' ? 'medium' as const : 'low' as const,
      createdAt: m.created_at,
      sourceIcon: 'brain',
      sourceContext: `Importance: ${m.importance}`,
    }))

  useEffect(() => { setMounted(true); fetch() }, [fetch])

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
    const blob = new Blob([JSON.stringify(memories, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'aria-memories.json'
    a.click()
    URL.revokeObjectURL(url)
  }, [memories])

  const filteredMemories = useMemo(() => {
    let result = memories
    if (activeTab !== 'all') {
      result = result.filter((m) => m.category === activeTab)
    }
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase()
      result = result.filter(
        (m) =>
          m.content.toLowerCase().includes(q) ||
          m.fullContent.toLowerCase().includes(q) ||
          m.category.toLowerCase().includes(q)
      )
    }
    return result
  }, [memories, activeTab, searchQuery])

  const stats = useMemo(() => ({
    total: memories.length,
    preferences: memories.filter((m) => m.category === 'preferences').length,
    patterns: memories.filter((m) => m.category === 'patterns').length,
    facts: memories.filter((m) => m.category === 'facts').length,
    lastUpdated: memories.length > 0
      ? getRelativeDate([...memories].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())[0].createdAt)
      : 'Never',
  }), [memories])

  const statCards = useMemo(() => [
    { label: 'Total Memories', value: stats.total, icon: Database, color: 'var(--accent-primary)' },
    { label: 'Preferences', value: stats.preferences, icon: User, color: 'var(--accent-secondary)' },
    { label: 'Patterns', value: stats.patterns, icon: TrendingUp, color: 'var(--accent-warning)' },
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
                placeholder="Search memories..."
                className="w-full h-10 pl-10 pr-4 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                aria-label="Search memories"
              />
            </div>

            <div className="flex gap-1 overflow-x-auto pb-1" role="tablist" aria-label="Memory categories">
              {CATEGORY_TABS.map((tab) => {
                const Icon = tab.icon
                const isActive = activeTab === tab.key
                const count = tab.key === 'all'
                  ? memories.length
                  : memories.filter((m) => m.category === tab.key).length
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
                    ? 'Try a different search term'
                    : `Continue using ARIA to build your profile — ${activeTab} will appear here as they're detected`
                }
              />
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <AnimatePresence mode="popLayout">
                {filteredMemories.map((memory, index) => {
                  const isExpanded = expandedIds.has(memory.id)
                  const Icon = SOURCE_ICONS[memory.sourceIcon] || Brain

                  return (
                    <motion.div
                      key={memory.id}
                      layout
                      initial={{ opacity: 0, scale: 0.97 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.97 }}
                      transition={{ delay: index * 0.03, type: 'spring', stiffness: 250, damping: 25 }}
                    >
                      <Card
                        variant="interactive"
                        onClick={() => toggleExpand(memory.id)}
                        className="h-full"
                      >
                        <CardContent>
                          <div className="flex items-start gap-3 mb-2">
                            <Badge
                              variant={
                                memory.category === 'preferences'
                                  ? 'default'
                                  : memory.category === 'patterns'
                                    ? 'info'
                                    : 'success'
                              }
                              className="shrink-0"
                            >
                              {memory.category}
                            </Badge>
                            <Badge variant={CONFIDENCE_CONFIG[memory.confidence].variant}>
                              {CONFIDENCE_CONFIG[memory.confidence].label}
                            </Badge>
                            <span className="text-xs text-[var(--text-tertiary)] ml-auto shrink-0">
                              {getRelativeDate(memory.createdAt)}
                            </span>
                          </div>

                          <p className={cn(
                            'text-sm text-[var(--text-primary)] leading-relaxed',
                            !isExpanded && 'line-clamp-2'
                          )}>
                            {isExpanded ? memory.fullContent : memory.content}
                          </p>

                          {isExpanded && (
                            <motion.div
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                              className="mt-3 pt-3 border-t border-[var(--border)]"
                            >
                              <div className="flex items-center gap-2 text-xs text-[var(--text-tertiary)]">
                                <Icon size={12} />
                                <span>{memory.sourceContext}</span>
                              </div>
                            </motion.div>
                          )}

                          <div className="flex items-center justify-end mt-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                toggleExpand(memory.id)
                              }}
                              className="flex items-center gap-1 text-xs text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] rounded"
                              aria-label={isExpanded ? 'Collapse memory' : 'Expand memory'}
                            >
                              {isExpanded ? (
                                <>
                                  Show less <ChevronUp size={12} />
                                </>
                              ) : (
                                <>
                                  Show more <ChevronDown size={12} />
                                </>
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
                  disabled={memories.length === 0}
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
                  disabled={memories.length === 0}
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
