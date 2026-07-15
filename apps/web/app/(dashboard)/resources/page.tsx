'use client'

import { useEffect, useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useResourceStore } from '@/lib/stores'
import { Button } from '@/components/ui/Button'
import { Plus } from 'lucide-react'
import { motion } from 'framer-motion'
import { ResourceGrid, ResourceFilters, CollectionGroup } from '@/components/resources'
import { DailyNudge, TrendingTopics, ActiveCollections } from '@/components/knowledge'
import type { Resource, Collection } from '@/types/resource'
import { createLogger } from '@/lib/utils/logger'

const resourceTypes = ['article', 'book', 'github', 'tool', 'paper', 'thread', 'other']

const coverColors = [
  'rgba(99, 102, 241, 0.08)',
  'rgba(0, 255, 163, 0.08)',
  'rgba(244, 63, 94, 0.08)',
  'rgba(59, 130, 246, 0.08)',
  'rgba(245, 158, 11, 0.08)',
]

export default function ResourcesPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const { items: storeItems, fetch: storeFetch, create: storeCreate, update: storeUpdate, remove: storeRemove, loading: storeLoading, error: storeError } = useResourceStore()
  const logger = createLogger('ResourcesPage')
  const resources = useMemo(() =>
    storeItems.map(r => ({
      id: r.id,
      title: r.title,
      type: r.resource_type,
      tags: r.tags || [],
      url: r.url || undefined,
      createdAt: r.created_at,
      description: r.notes || undefined,
    })),
  [storeItems])
  const [showAddModal, setShowAddModal] = useState(false)
  const [mounted, setMounted] = useState(false)

  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [tagMode, setTagMode] = useState<'or' | 'and'>('or')

  const [newResource, setNewResource] = useState({ title: '', url: '', resource_type: 'article', tags: '', notes: '' })

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (user) storeFetch()
  }, [user, storeFetch])

  const handleAddResource = async () => {
    if (!newResource.title.trim() || !newResource.url.trim()) return
    logger.info('Adding resource', { title: newResource.title, type: newResource.resource_type })
    try {
      await storeCreate({
        title: newResource.title,
        url: newResource.url,
        resource_type: newResource.resource_type,
        tags: newResource.tags.split(',').map(t => t.trim()).filter(Boolean),
        notes: newResource.notes || undefined,
      })
      logger.info('Resource created successfully', { title: newResource.title })
      setNewResource({ title: '', url: '', resource_type: 'article', tags: '', notes: '' })
      setShowAddModal(false)
    } catch (err) {
      logger.error('Failed to create resource', { error: err instanceof Error ? err.message : String(err) })
    }
  }

  const handleDelete = async (id: string) => {
    logger.info('Deleting resource', { id })
    try {
      await storeRemove(id)
      logger.info('Resource deleted successfully', { id })
    } catch (err) {
      logger.error('Failed to delete resource', { error: err instanceof Error ? err.message : String(err) })
    }
  }

  const tagCounts = useMemo(() => {
    const counts = new Map<string, number>()
    resources.forEach((r) => r.tags.forEach((t) => counts.set(t, (counts.get(t) || 0) + 1)))
    return counts
  }, [resources])

  const derivedCollections = useMemo<Collection[]>(() => {
    const tagEntries = Array.from(tagCounts.entries()).sort((a, b) => b[1] - a[1])
    return tagEntries.slice(0, 10).map(([name, count], i) => ({
      id: `tag-${name}`,
      name: name.charAt(0).toUpperCase() + name.slice(1).replace(/-/g, ' '),
      itemCount: count,
      coverColor: coverColors[i % coverColors.length],
      lastEdited: new Date().toISOString().split('T')[0],
    }))
  }, [tagCounts])

  const derivedTopics = useMemo(() => {
    const entries = Array.from(tagCounts.entries()).sort((a, b) => b[1] - a[1])
    return entries.slice(0, 8).map(([tag, count]) => ({
      tag,
      count,
      growth: Math.floor(Math.random() * 50) - 10,
    }))
  }, [tagCounts])

  const activeCollections = useMemo(() => {
    return resources.slice(0, 5).map((r, i) => ({
      id: r.id,
      name: r.title.length > 30 ? r.title.slice(0, 30) + '...' : r.title,
      itemCount: r.tags.length,
      lastEdited: r.createdAt || new Date().toISOString(),
    }))
  }, [resources])

  const allTags = useMemo(() => {
    const tagSet = new Set<string>()
    resources.forEach((r) => r.tags.forEach((t) => tagSet.add(t)))
    return Array.from(tagSet).sort()
  }, [resources])

  const filteredResources = useMemo(() => {
    return resources.filter((r) => {
      if (selectedType !== 'all' && r.type !== selectedType) return false
      if (searchQuery) {
        const q = searchQuery.toLowerCase()
        if (!r.title.toLowerCase().includes(q) && !r.tags.some((t) => t.toLowerCase().includes(q))) return false
      }
      if (selectedTags.length > 0) {
        if (tagMode === 'or') {
          if (!selectedTags.some((t) => r.tags.includes(t))) return false
        } else {
          if (!selectedTags.every((t) => r.tags.includes(t))) return false
        }
      }
      return true
    })
  }, [resources, selectedType, searchQuery, selectedTags, tagMode])

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (authLoading || (storeLoading && resources.length === 0)) return (
    <div className="flex items-center justify-center h-64" role="status" aria-label="Loading">
      <div className="relative">
        <div className="w-12 h-12 border-2 border-accent-primary/30 rounded-full" />
        <div className="absolute inset-0 w-12 h-12 border-2 border-transparent border-t-accent-primary rounded-full animate-spin" />
        <div className="absolute inset-1 w-10 h-10 border border-accent-info/50 rounded-full animate-pulse-glow" />
      </div>
      <span className="sr-only">Loading...</span>
    </div>
  )

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-text-primary text-gradient bg-gradient-to-r from-accent-primary via-accent-info to-accent-success">
            Resource Library
          </h1>
          <p className="text-text-secondary">Save articles, books, tools, and more</p>
        </div>
        <Button variant="primary" icon={<Plus size={20} />} onClick={() => setShowAddModal(true)}>
          Add Resource
        </Button>
      </motion.div>

      {storeError && (
        <div className="bg-accent-danger/10 border border-accent-danger/30 text-text-primary px-4 py-3 rounded-lg mb-6">
          {storeError}
        </div>
      )}

      <DailyNudge />

      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Total', value: resources.length },
          { label: 'Active', value: resources.filter(r => !('is_archived' in r)).length },
          { label: 'Tags', value: allTags.length },
          { label: 'Collections', value: derivedCollections.length },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="card"
          >
            <div className="text-2xl font-bold text-text-primary">{stat.value}</div>
            <div className="text-text-secondary text-sm">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      <ResourceFilters
        tags={allTags}
        selectedTags={selectedTags}
        onTagsChange={setSelectedTags}
        selectedType={selectedType}
        onTypeChange={setSelectedType}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        tagMode={tagMode}
        onTagModeChange={setTagMode}
      />

      {derivedCollections.length > 0 && (
        <CollectionGroup
          collections={derivedCollections}
          onCollectionClick={(id) => console.log('Collection clicked:', id)}
        />
      )}

      <ResourceGrid
        resources={filteredResources}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />

      {derivedTopics.length > 0 && <TrendingTopics topics={derivedTopics} />}
      {activeCollections.length > 0 && <ActiveCollections collections={activeCollections} />}

      {/* Add Resource Modal */}
      {showAddModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50"
          onClick={() => setShowAddModal(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Add Resource</h2>
              <Button variant="ghost" size="icon" onClick={() => setShowAddModal(false)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-text-tertiary">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </Button>
            </div>
            <div className="space-y-4">
              <div>
                <label htmlFor="resource-title" className="block text-text-secondary text-sm mb-1">Title *</label>
                <input
                  id="resource-title"
                  type="text"
                  value={newResource.title}
                  onChange={e => setNewResource({ ...newResource, title: e.target.value })}
                  className="w-full bg-background-input border border-border rounded-lg px-4 py-2 text-text-primary"
                />
              </div>
              <div>
                <label htmlFor="resource-url" className="block text-text-secondary text-sm mb-1">URL *</label>
                <input
                  id="resource-url"
                  type="url"
                  value={newResource.url}
                  onChange={e => setNewResource({ ...newResource, url: e.target.value })}
                  className="w-full bg-background-input border border-border rounded-lg px-4 py-2 text-text-primary"
                />
              </div>
              <div>
                <label htmlFor="resource-type" className="block text-text-secondary text-sm mb-1">Type</label>
                <select
                  id="resource-type"
                  value={newResource.resource_type}
                  onChange={e => setNewResource({ ...newResource, resource_type: e.target.value })}
                  className="w-full bg-background-input border border-border rounded-lg px-4 py-2 text-text-primary capitalize"
                >
                  {resourceTypes.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="resource-tags" className="block text-text-secondary text-sm mb-1">Tags (comma separated)</label>
                <input
                  id="resource-tags"
                  type="text"
                  value={newResource.tags}
                  onChange={e => setNewResource({ ...newResource, tags: e.target.value })}
                  className="w-full bg-background-input border border-border rounded-lg px-4 py-2 text-text-primary"
                  placeholder="react, python, ai"
                />
              </div>
              <div>
                <label htmlFor="resource-notes" className="block text-text-secondary text-sm mb-1">Notes</label>
                <textarea
                  id="resource-notes"
                  value={newResource.notes}
                  onChange={e => setNewResource({ ...newResource, notes: e.target.value })}
                  className="w-full bg-background-input border border-border rounded-lg px-4 py-2 text-text-primary"
                  rows={2}
                />
              </div>
              <Button variant="primary" onClick={handleAddResource} className="w-full">
                Save Resource
              </Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}
