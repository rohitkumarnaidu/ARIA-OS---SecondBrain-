'use client'

import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Grid3x3, List, Search, X, Plus, ChevronLeft, ChevronRight,
  Eye, EyeOff, CheckCircle2, Clock, ExternalLink,
  FolderPlus, Edit2, Check, Youtube, Tag, Play,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { EmptyState } from '@/components/ui/EmptyState'
import { cn } from '@/components/ui/utils'
import type { YouTubeVideo, VideoCollection, VideoStatus, ViewMode } from '@/types/youtube'

const MOCK_COLLECTIONS: VideoCollection[] = [
  { id: 'col-cs', name: 'CS Courses', videoIds: ['v1', 'v2', 'v3', 'v4'] },
  { id: 'col-ai', name: 'AI/ML', videoIds: ['v5', 'v6', 'v7', 'v8'] },
  { id: 'col-proj', name: 'Project Ideas', videoIds: ['v9', 'v10', 'v11', 'v12'] },
]

const MOCK_VIDEOS: YouTubeVideo[] = [
  {
    id: 'v1', title: 'MIT 6.006 Introduction to Algorithms', url: 'https://youtube.com/watch?v=example1',
    thumbnail: 'https://picsum.photos/seed/v1/320/180', channel: 'MIT OpenCourseWare', duration: '45:22',
    tags: ['algorithms', 'python', 'data-structures'], status: 'watched',
    statusChangedAt: '2026-06-14T08:00:00Z', collectionId: 'col-cs', notes: 'Great course on algorithmic thinking',
    created_at: '2026-06-01T10:00:00Z',
  },
  {
    id: 'v2', title: 'Computer Architecture — Coursera', url: 'https://youtube.com/watch?v=example2',
    thumbnail: 'https://picsum.photos/seed/v2/320/180', channel: 'Princeton University', duration: '1:12:08',
    tags: ['architecture', 'computer-science', 'hardware'], status: 'watching',
    statusChangedAt: '2026-06-15T14:30:00Z', collectionId: 'col-cs', notes: '',
    created_at: '2026-06-02T10:00:00Z',
  },
  {
    id: 'v3', title: 'Operating Systems: Three Easy Pieces', url: 'https://youtube.com/watch?v=example3',
    thumbnail: 'https://picsum.photos/seed/v3/320/180', channel: 'CS Education', duration: '38:15',
    tags: ['os', 'concurrency', 'c'], status: 'to_watch',
    statusChangedAt: '2026-06-10T09:00:00Z', collectionId: 'col-cs', notes: '',
    created_at: '2026-06-03T10:00:00Z',
  },
  {
    id: 'v4', title: 'Discrete Mathematics Full Course', url: 'https://youtube.com/watch?v=example4',
    thumbnail: 'https://picsum.photos/seed/v4/320/180', channel: 'freeCodeCamp', duration: '8:45:30',
    tags: ['mathematics', 'logic', 'combinatorics'], status: 'to_watch',
    statusChangedAt: '2026-06-12T11:00:00Z', collectionId: 'col-cs', notes: '',
    created_at: '2026-06-04T10:00:00Z',
  },
  {
    id: 'v5', title: 'Attention Is All You Need Explained', url: 'https://youtube.com/watch?v=example5',
    thumbnail: 'https://picsum.photos/seed/v5/320/180', channel: 'Yannic Kilcher', duration: '22:14',
    tags: ['transformers', 'nlp', 'deep-learning'], status: 'watched',
    statusChangedAt: '2026-06-13T18:00:00Z', collectionId: 'col-ai', notes: 'Core transformer architecture paper walkthrough',
    created_at: '2026-06-05T10:00:00Z',
  },
  {
    id: 'v6', title: 'Building LLMs from Scratch', url: 'https://youtube.com/watch?v=example6',
    thumbnail: 'https://picsum.photos/seed/v6/320/180', channel: 'Andrej Karpathy', duration: '2:05:33',
    tags: ['llm', 'pytorch', 'nlp'], status: 'watching',
    statusChangedAt: '2026-06-15T20:00:00Z', collectionId: 'col-ai', notes: 'Halfway through',
    created_at: '2026-06-06T10:00:00Z',
  },
  {
    id: 'v7', title: 'Reinforcement Learning — Full Course', url: 'https://youtube.com/watch?v=example7',
    thumbnail: 'https://picsum.photos/seed/v7/320/180', channel: 'David Silver', duration: '10:12:00',
    tags: ['rl', 'machine-learning', 'algorithms'], status: 'to_watch',
    statusChangedAt: '2026-06-11T07:00:00Z', collectionId: 'col-ai', notes: '',
    created_at: '2026-06-07T10:00:00Z',
  },
  {
    id: 'v8', title: 'Stable Diffusion From the Ground Up', url: 'https://youtube.com/watch?v=example8',
    thumbnail: 'https://picsum.photos/seed/v8/320/180', channel: 'AI Coffee Break', duration: '35:40',
    tags: ['diffusion', 'generative-ai', 'computer-vision'], status: 'to_watch',
    statusChangedAt: '2026-06-09T16:00:00Z', collectionId: 'col-ai', notes: '',
    created_at: '2026-06-08T10:00:00Z',
  },
  {
    id: 'v9', title: 'Build a SaaS Product in 30 Days', url: 'https://youtube.com/watch?v=example9',
    thumbnail: 'https://picsum.photos/seed/v9/320/180', channel: 'IndieHacker TV', duration: '1:30:22',
    tags: ['startup', 'saas', 'product'], status: 'watched',
    statusChangedAt: '2026-06-12T12:00:00Z', collectionId: 'col-proj', notes: 'Actionable roadmap for MVP',
    created_at: '2026-06-09T10:00:00Z',
  },
  {
    id: 'v10', title: 'Full Stack Next.js 14 E-Commerce', url: 'https://youtube.com/watch?v=example10',
    thumbnail: 'https://picsum.photos/seed/v10/320/180', channel: 'Coding With Josh', duration: '4:15:00',
    tags: ['nextjs', 'react', 'typescript', 'fullstack'], status: 'watching',
    statusChangedAt: '2026-06-16T09:00:00Z', collectionId: 'col-proj', notes: 'Good patterns for auth and payments',
    created_at: '2026-06-10T10:00:00Z',
  },
  {
    id: 'v11', title: 'Designing Data-Intensive Applications', url: 'https://youtube.com/watch?v=example11',
    thumbnail: 'https://picsum.photos/seed/v11/320/180', channel: 'Martin Kleppmann', duration: '48:09',
    tags: ['system-design', 'databases', 'distributed-systems'], status: 'to_watch',
    statusChangedAt: '2026-06-08T14:00:00Z', collectionId: 'col-proj', notes: '',
    created_at: '2026-06-11T10:00:00Z',
  },
  {
    id: 'v12', title: 'CI/CD Pipeline with GitHub Actions', url: 'https://youtube.com/watch?v=example12',
    thumbnail: 'https://picsum.photos/seed/v12/320/180', channel: 'DevOps Toolkit', duration: '26:50',
    tags: ['devops', 'ci-cd', 'github-actions'], status: 'to_watch',
    statusChangedAt: '2026-06-07T10:00:00Z', collectionId: 'col-proj', notes: '',
    created_at: '2026-06-12T10:00:00Z',
  },
]

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
    })
  } catch {
    return ''
  }
}

function statusLabel(status: VideoStatus): string {
  switch (status) {
    case 'to_watch': return 'To Watch'
    case 'watching': return 'Watching'
    case 'watched': return 'Watched'
  }
}

function allExistingTags(videos: YouTubeVideo[]): string[] {
  const set = new Set<string>()
  for (const v of videos) {
    for (const t of v.tags) set.add(t)
  }
  return Array.from(set).sort()
}

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
}

const cardVariants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 200, damping: 20 } },
}

const listVariants = {
  hidden: { opacity: 0, x: -8 },
  show: { opacity: 1, x: 0, transition: { type: 'spring', stiffness: 250, damping: 22 } },
}

export function YouTubeVault(): JSX.Element {
  const [videos, setVideos] = useState<YouTubeVideo[]>(MOCK_VIDEOS)
  const [collections, setCollections] = useState<VideoCollection[]>(MOCK_COLLECTIONS)
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')
  const [tagSuggestions, setTagSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [activeCollection, setActiveCollection] = useState<string | null>(null)
  const [editingCollectionId, setEditingCollectionId] = useState<string | null>(null)
  const [editingName, setEditingName] = useState('')
  const [dragOverCollection, setDragOverCollection] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

  const searchRef = useRef<HTMLInputElement>(null)
  const tagInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    setMounted(true)
    try {
      const stored = localStorage.getItem('youtube-view-mode')
      if (stored === 'grid' || stored === 'list') setViewMode(stored)
    } catch { /* localStorage unavailable */ }
  }, [])

  useEffect(() => {
    if (mounted) {
      try { localStorage.setItem('youtube-view-mode', viewMode) } catch { /* noop */ }
    }
  }, [viewMode, mounted])

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchQuery), 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  const allTags = useMemo(() => allExistingTags(videos), [videos])

  useEffect(() => {
    if (tagInput.trim()) {
      const lower = tagInput.toLowerCase()
      const matches = allTags.filter((t) => t.toLowerCase().includes(lower) && !selectedTags.includes(t))
      setTagSuggestions(matches)
      setShowSuggestions(matches.length > 0)
    } else {
      setTagSuggestions([])
      setShowSuggestions(false)
    }
  }, [tagInput, allTags, selectedTags])

  const addTag = useCallback((tag: string) => {
    const trimmed = tag.trim().toLowerCase()
    if (trimmed && !selectedTags.includes(trimmed)) {
      setSelectedTags((prev) => [...prev, trimmed])
    }
    setTagInput('')
    setShowSuggestions(false)
    tagInputRef.current?.focus()
  }, [selectedTags])

  const removeTag = useCallback((tag: string) => {
    setSelectedTags((prev) => prev.filter((t) => t !== tag))
  }, [])

  const filteredVideos = useMemo(() => {
    return videos.filter((v) => {
      if (debouncedSearch) {
        const q = debouncedSearch.toLowerCase()
        if (!v.title.toLowerCase().includes(q) &&
            !v.channel.toLowerCase().includes(q) &&
            !v.tags.some((t) => t.toLowerCase().includes(q))) return false
      }
      if (selectedTags.length > 0) {
        if (!selectedTags.some((t) => v.tags.includes(t))) return false
      }
      if (activeCollection) {
        const col = collections.find((c) => c.id === activeCollection)
        if (col) return col.videoIds.includes(v.id)
      }
      return true
    })
  }, [videos, debouncedSearch, selectedTags, activeCollection, collections])

  const getVideosForCollection = useCallback((collectionId: string): YouTubeVideo[] => {
    const col = collections.find((c) => c.id === collectionId)
    if (!col) return []
    return col.videoIds.map((vid) => videos.find((v) => v.id === vid)).filter(Boolean) as YouTubeVideo[]
  }, [collections, videos])

  const uncategorizedVideos = useMemo(() => {
    const inCollections = new Set(collections.flatMap((c) => c.videoIds))
    return videos.filter((v) => !inCollections.has(v.id))
  }, [videos, collections])

  const handleStatusChange = useCallback((videoId: string, newStatus: VideoStatus) => {
    setVideos((prev) =>
      prev.map((v) =>
        v.id === videoId
          ? { ...v, status: newStatus, statusChangedAt: new Date().toISOString() }
          : v
      )
    )
  }, [])

  const handleAddCollection = useCallback(() => {
    const id = `col-${Date.now()}`
    const newCol: VideoCollection = { id, name: 'New Collection', videoIds: [] }
    setCollections((prev) => [...prev, newCol])
    setEditingCollectionId(id)
    setEditingName('New Collection')
    setActiveCollection(id)
  }, [])

  const handleRenameCollection = useCallback((collectionId: string) => {
    if (editingName.trim()) {
      setCollections((prev) =>
        prev.map((c) => (c.id === collectionId ? { ...c, name: editingName.trim() } : c))
      )
    }
    setEditingCollectionId(null)
    setEditingName('')
  }, [editingName])

  const handleDragStart = useCallback((e: React.DragEvent, videoId: string, sourceCollectionId?: string) => {
    e.dataTransfer.setData('text/plain', videoId)
    e.dataTransfer.setData('sourceCollection', sourceCollectionId || '')
    e.dataTransfer.effectAllowed = 'move'
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent, collectionId: string) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    setDragOverCollection(collectionId)
  }, [])

  const handleDragLeave = useCallback(() => {
    setDragOverCollection(null)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent, targetCollectionId: string) => {
    e.preventDefault()
    setDragOverCollection(null)
    const videoId = e.dataTransfer.getData('text/plain')
    const sourceCollectionId = e.dataTransfer.getData('sourceCollection')

    if (!videoId) return

    setCollections((prev) => {
      const next = prev.map((c) => ({
        ...c,
        videoIds: c.id === sourceCollectionId
          ? c.videoIds.filter((id) => id !== videoId)
          : c.id === targetCollectionId
            ? c.videoIds.includes(videoId)
              ? c.videoIds
              : [...c.videoIds, videoId]
            : c.videoIds,
      }))
      return next
    })

    setVideos((prev) =>
      prev.map((v) =>
        v.id === videoId ? { ...v, collectionId: targetCollectionId } : v
      )
    )
  }, [])

  const handleDropUncategorized = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOverCollection(null)
    const videoId = e.dataTransfer.getData('text/plain')
    const sourceCollectionId = e.dataTransfer.getData('sourceCollection')
    if (!videoId) return

    setCollections((prev) =>
      prev.map((c) =>
        c.id === sourceCollectionId
          ? { ...c, videoIds: c.videoIds.filter((id) => id !== videoId) }
          : c
      )
    )
    setVideos((prev) =>
      prev.map((v) =>
        v.id === videoId ? { ...v, collectionId: undefined } : v
      )
    )
  }, [])

  const statusIcon = (status: VideoStatus) => {
    switch (status) {
      case 'to_watch': return <Clock size={12} aria-hidden="true" />
      case 'watching': return <Eye size={12} aria-hidden="true" />
      case 'watched': return <CheckCircle2 size={12} aria-hidden="true" />
    }
  }

  const statusVariant = (status: VideoStatus): 'default' | 'warning' | 'success' => {
    switch (status) {
      case 'to_watch': return 'default'
      case 'watching': return 'warning'
      case 'watched': return 'success'
    }
  }

  const allCollections = useMemo(() => {
    return collections.map((c) => ({
      ...c,
      videos: getVideosForCollection(c.id),
    }))
  }, [collections, getVideosForCollection])

  const hasUncategorized = uncategorizedVideos.length > 0

  if (!mounted) {
    return (
      <div className="flex items-center justify-center h-64" role="status" aria-label="Loading">
        <div className="w-10 h-10 border-2 border-[var(--accent-primary)] border-t-transparent rounded-full animate-spin" />
        <span className="sr-only">Loading vault</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Search + View Toggle Bar */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] pointer-events-none"
            aria-hidden="true"
          />
          <input
            ref={searchRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search videos, channels, tags..."
            aria-label="Search videos"
            className={cn(
              'w-full h-10 pl-9 pr-8 rounded-lg text-sm',
              'bg-[var(--surface-primary)] border border-[var(--border)]',
              'text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]',
              'transition-all duration-200',
              'focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/40 focus:border-[var(--accent-primary)]',
            )}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)] transition-colors"
              aria-label="Clear search"
            >
              <X size={14} />
            </button>
          )}
        </div>

        <div className="flex items-center gap-1 p-1 rounded-lg bg-[var(--surface-primary)] border border-[var(--border)]" role="radiogroup" aria-label="View mode">
          <button
            onClick={() => setViewMode('grid')}
            className={cn(
              'p-2 rounded-md transition-all duration-200',
              viewMode === 'grid'
                ? 'bg-[var(--accent-primary)] text-white shadow-[var(--shadow-glow-sm)]'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)]',
            )}
            aria-label="Grid view"
            role="radio"
            aria-checked={viewMode === 'grid'}
          >
            <Grid3x3 size={16} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={cn(
              'p-2 rounded-md transition-all duration-200',
              viewMode === 'list'
                ? 'bg-[var(--accent-primary)] text-white shadow-[var(--shadow-glow-sm)]'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)]',
            )}
            aria-label="List view"
            role="radio"
            aria-checked={viewMode === 'list'}
          >
            <List size={16} />
          </button>
        </div>

        <button
          onClick={() => setSidebarOpen((prev) => !prev)}
          className={cn(
            'p-2 rounded-lg border transition-all duration-200 lg:hidden',
            sidebarOpen
              ? 'bg-[var(--accent-primary)]/10 border-[var(--accent-primary)]/30 text-[var(--accent-primary)]'
              : 'bg-[var(--surface-primary)] border-[var(--border)] text-[var(--text-secondary)]',
          )}
          aria-label={sidebarOpen ? 'Hide collections' : 'Show collections'}
          aria-expanded={sidebarOpen}
        >
          <FolderPlus size={16} />
        </button>
      </div>

      {/* Tag Filter Area */}
      <div className="flex flex-wrap items-center gap-2">
        {selectedTags.map((tag) => (
          <span key={tag} className="inline-flex items-center gap-1">
            <Badge variant="info" className="pr-1 gap-1">
              <Tag size={10} aria-hidden="true" />
              {tag}
              <button
                onClick={() => removeTag(tag)}
                className="ml-0.5 p-0.5 rounded hover:bg-[var(--accent-error)]/20 hover:text-[var(--accent-error)] transition-colors"
                aria-label={`Remove tag ${tag}`}
              >
                <X size={10} />
              </button>
            </Badge>
          </span>
        ))}
        <div className="relative">
          <input
            ref={tagInputRef}
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault()
                addTag(tagInput)
              }
              if (e.key === 'Backspace' && !tagInput && selectedTags.length > 0) {
                removeTag(selectedTags[selectedTags.length - 1])
              }
            }}
            onFocus={() => {
              if (tagSuggestions.length > 0) setShowSuggestions(true)
            }}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
            placeholder={selectedTags.length === 0 ? 'Filter by tag...' : 'Add another tag...'}
            aria-label="Add tag filter"
            className={cn(
              'h-7 px-2 rounded text-xs w-[130px]',
              'bg-[var(--surface-primary)] border border-[var(--border)]',
              'text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]',
              'focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]/40',
            )}
          />
          {showSuggestions && (
            <div
              className="absolute top-full left-0 mt-1 w-48 max-h-40 overflow-y-auto rounded-lg bg-[var(--surface-primary)] border border-[var(--border)] shadow-lg z-[var(--z-dropdown)]"
              role="listbox"
              aria-label="Tag suggestions"
            >
              {tagSuggestions.map((tag) => (
                <button
                  key={tag}
                  onMouseDown={(e) => {
                    e.preventDefault()
                    addTag(tag)
                  }}
                  className="w-full text-left px-3 py-1.5 text-xs text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)] transition-colors"
                  role="option"
                  aria-selected={false}
                >
                  {tag}
                </button>
              ))}
            </div>
          )}
        </div>
        {(selectedTags.length > 0 || searchQuery) && (
          <button
            onClick={() => {
              setSelectedTags([])
              setSearchQuery('')
              setDebouncedSearch('')
            }}
            className="text-xs text-[var(--text-tertiary)] hover:text-[var(--accent-error)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] rounded px-1"
            aria-label="Clear all filters"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Collection Indicator */}
      {activeCollection && (
        <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
          <span>Collection:</span>
          <Badge variant="outline" className="gap-1">
            {collections.find((c) => c.id === activeCollection)?.name || 'Unknown'}
          </Badge>
          <button
            onClick={() => setActiveCollection(null)}
            className="text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
            aria-label="Clear collection filter"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Main Layout */}
      <div className="flex gap-4">
        {/* Collections Sidebar */}
        <AnimatePresence mode="wait">
          {sidebarOpen && (
            <motion.aside
              initial={{ opacity: 0, x: -20, width: 0 }}
              animate={{ opacity: 1, x: 0, width: 'auto' }}
              exit={{ opacity: 0, x: -20, width: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 28 }}
              className={cn(
                'shrink-0 flex flex-col gap-1',
                'w-full lg:w-64',
                'lg:relative lg:block',
                'fixed inset-0 z-30 lg:z-auto',
                'bg-[var(--background)]/95 backdrop-blur-xl lg:bg-transparent lg:backdrop-blur-none',
                'p-4 lg:p-0',
              )}
              role="navigation"
              aria-label="Video collections"
            >
              {/* Mobile close */}
              <div className="flex items-center justify-between mb-3 lg:hidden">
                <span className="text-sm font-medium text-[var(--text-primary)]">Collections</span>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
                  aria-label="Close collections"
                >
                  <X size={18} />
                </button>
              </div>

              <div className="space-y-0.5">
                {/* All Videos */}
                <button
                  onClick={() => setActiveCollection(null)}
                  className={cn(
                    'w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-200',
                    !activeCollection
                      ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--accent-primary)]/20'
                      : 'text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)] border border-transparent',
                  )}
                  aria-current={!activeCollection ? 'page' : undefined}
                >
                  <div className="flex items-center justify-between">
                    <span>All Videos</span>
                    <span className="text-xs text-[var(--text-tertiary)]">{videos.length}</span>
                  </div>
                </button>

                {/* Uncategorized */}
                <div
                  onDragOver={(e) => { e.preventDefault(); setDragOverCollection('__uncategorized') }}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDropUncategorized}
                  className={cn(
                    'rounded-lg transition-all duration-200',
                    dragOverCollection === '__uncategorized' && 'ring-2 ring-[var(--accent-primary)]/40 bg-[var(--accent-primary)]/5',
                  )}
                >
                  <button
                    onClick={() => setActiveCollection('__uncategorized')}
                    className={cn(
                      'w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-200',
                      activeCollection === '__uncategorized'
                        ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--accent-primary)]/20'
                        : 'text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)] border border-transparent',
                    )}
                    aria-current={activeCollection === '__uncategorized' ? 'page' : undefined}
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <Tag size={12} aria-hidden="true" />
                        Uncategorized
                      </span>
                      <span className="text-xs text-[var(--text-tertiary)]">{uncategorizedVideos.length}</span>
                    </div>
                  </button>
                </div>

                {/* Collection divider */}
                <div className="h-px bg-[var(--border)] my-2" role="separator" />

                {/* Collections */}
                {allCollections.map((col) => (
                  <div
                    key={col.id}
                    onDragOver={(e) => handleDragOver(e, col.id)}
                    onDragLeave={handleDragLeave}
                    onDrop={(e) => handleDrop(e, col.id)}
                    className={cn(
                      'rounded-lg transition-all duration-200',
                      dragOverCollection === col.id && 'ring-2 ring-[var(--accent-primary)]/40 bg-[var(--accent-primary)]/5',
                    )}
                  >
                    {editingCollectionId === col.id ? (
                      <div className="flex items-center gap-1 px-2 py-1">
                        <input
                          type="text"
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleRenameCollection(col.id)
                            if (e.key === 'Escape') {
                              setEditingCollectionId(null)
                              setEditingName('')
                            }
                          }}
                          className={cn(
                            'flex-1 h-8 px-2 rounded text-sm',
                            'bg-[var(--surface-primary)] border border-[var(--accent-primary)]/40',
                            'text-[var(--text-primary)]',
                            'focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]',
                          )}
                          autoFocus
                          aria-label="Collection name"
                        />
                        <button
                          onClick={() => handleRenameCollection(col.id)}
                          className="p-1 rounded text-[var(--accent-secondary)] hover:bg-[var(--accent-secondary)]/10"
                          aria-label="Save collection name"
                        >
                          <Check size={14} />
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setActiveCollection(col.id)}
                        className={cn(
                          'w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-200 group',
                          activeCollection === col.id
                            ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--accent-primary)]/20'
                            : 'text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)] border border-transparent',
                        )}
                        aria-current={activeCollection === col.id ? 'page' : undefined}
                        draggable
                      >
                        <div className="flex items-center justify-between">
                          <span className="truncate">{col.name}</span>
                          <div className="flex items-center gap-1 shrink-0">
                            <span className="text-xs text-[var(--text-tertiary)]">{col.videos.length}</span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                setEditingCollectionId(col.id)
                                setEditingName(col.name)
                              }}
                              className="p-0.5 rounded opacity-0 group-hover:opacity-100 text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-all"
                              aria-label={`Rename ${col.name}`}
                            >
                              <Edit2 size={10} />
                            </button>
                          </div>
                        </div>
                      </button>
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={handleAddCollection}
                className={cn(
                  'mt-2 flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all duration-200',
                  'text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] hover:bg-[var(--accent-primary)]/5',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]',
                )}
                aria-label="Add new collection"
              >
                <Plus size={14} />
                <span>New Collection</span>
              </button>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Content Area */}
        <div className="flex-1 min-w-0">
          {filteredVideos.length === 0 ? (
            <EmptyState
              title="No videos yet"
              description="Paste a YouTube URL to add your first video"
              icon={<Youtube size={40} aria-hidden="true" />}
            />
          ) : viewMode === 'grid' ? (
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="show"
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3"
            >
              <AnimatePresence mode="popLayout">
                {filteredVideos.map((video) => (
                  <motion.div
                    key={video.id}
                    layout
                    variants={cardVariants}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] rounded-xl"
                  >
                    <div
                      draggable
                      onDragStart={(e: React.DragEvent<HTMLDivElement>) =>
                        handleDragStart(e, video.id, video.collectionId)
                      }
                      className={cn(
                        'group relative rounded-xl overflow-hidden cursor-grab active:cursor-grabbing',
                        'bg-[var(--surface-primary)] border border-[var(--border)]',
                        'hover:border-[var(--accent-primary)]/30 hover:shadow-[var(--shadow-glow-sm)]',
                        'transition-all duration-300',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]',
                      )}
                      tabIndex={0}
                      role="article"
                      aria-label={`${video.title} by ${video.channel}`}
                    >
                    {/* Thumbnail */}
                    <div className="relative aspect-video bg-[var(--surface-secondary)] overflow-hidden">
                      {video.thumbnail ? (
                        <img
                          src={video.thumbnail}
                          alt=""
                          loading="lazy"
                          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                      ) : (
                        <div className="flex items-center justify-center h-full text-[var(--text-tertiary)]">
                          <Youtube size={32} />
                        </div>
                      )}
                      {video.duration && (
                        <span className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded text-[10px] font-mono bg-black/70 text-white/90">
                          {video.duration}
                        </span>
                      )}
                      {/* Status overlay top-right */}
                      <div className="absolute top-2 right-2" title={`${statusLabel(video.status)} on ${formatDate(video.statusChangedAt)}`}>
                        <Badge variant={statusVariant(video.status)} className="gap-1 text-[10px] px-1.5 py-0.5">
                          {statusIcon(video.status)}
                          {statusLabel(video.status)}
                        </Badge>
                      </div>
                    </div>

                    {/* Info */}
                    <div className="p-3 space-y-1.5">
                      <h3 className="text-sm font-medium text-[var(--text-primary)] line-clamp-2 leading-tight">
                        {video.title}
                      </h3>
                      <p className="text-xs text-[var(--text-tertiary)] truncate">{video.channel}</p>

                      {/* Tags */}
                      {video.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          {video.tags.slice(0, 3).map((tag) => (
                            <span
                              key={tag}
                              className="text-[10px] px-1.5 py-0.5 rounded-full bg-[var(--surface-secondary)] text-[var(--text-tertiary)] border border-[var(--border)]"
                            >
                              {tag}
                            </span>
                          ))}
                          {video.tags.length > 3 && (
                            <span className="text-[10px] text-[var(--text-tertiary)]">+{video.tags.length - 3}</span>
                          )}
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center justify-between pt-1.5">
                        <div className="flex items-center gap-1">
                          {video.status !== 'to_watch' && (
                            <button
                              onClick={() => handleStatusChange(video.id, 'to_watch')}
                              className={cn(
                                'p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)]',
                                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]',
                                'transition-colors',
                              )}
                              aria-label="Mark as to watch"
                            >
                              <Clock size={12} />
                            </button>
                          )}
                          {video.status !== 'watching' && (
                            <button
                              onClick={() => handleStatusChange(video.id, 'watching')}
                              className={cn(
                                'p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--accent-warning)] hover:bg-[var(--accent-warning)]/10',
                                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]',
                                'transition-colors',
                              )}
                              aria-label="Mark as watching"
                            >
                              <Eye size={12} />
                            </button>
                          )}
                          {video.status !== 'watched' && (
                            <button
                              onClick={() => handleStatusChange(video.id, 'watched')}
                              className={cn(
                                'p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--accent-secondary)] hover:bg-[var(--accent-secondary)]/10',
                                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]',
                                'transition-colors',
                              )}
                              aria-label="Mark as watched"
                            >
                              <CheckCircle2 size={12} />
                            </button>
                          )}
                        </div>
                        <a
                          href={video.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={cn(
                            'p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] hover:bg-[var(--accent-primary)]/10',
                            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]',
                            'transition-colors',
                          )}
                          aria-label={`Open ${video.title} on YouTube`}
                        >
                          <ExternalLink size={12} />
                        </a>
                      </div>
                    </div>
                      </div>
                    </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>
          ) : (
            /* List View */
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="show"
              className="flex flex-col gap-1"
              role="list"
              aria-label="Video list"
            >
              <AnimatePresence mode="popLayout">
                {filteredVideos.map((video, idx) => (
                  <motion.div
                    key={video.id}
                    layout
                    variants={listVariants}
                    exit={{ opacity: 0, x: -16 }}
                    className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] rounded-lg"
                  >
                    <div
                      draggable
                      onDragStart={(e: React.DragEvent<HTMLDivElement>) =>
                        handleDragStart(e, video.id, video.collectionId)
                      }
                      className={cn(
                        'flex items-center gap-3 p-2 rounded-lg cursor-grab active:cursor-grabbing',
                        'bg-[var(--surface-primary)] border border-[var(--border)]',
                        'hover:border-[var(--accent-primary)]/20 hover:bg-[var(--surface-secondary)]',
                        'transition-all duration-200',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]',
                      )}
                      tabIndex={0}
                      role="listitem"
                      aria-label={`${video.title} by ${video.channel}`}
                    >
                      {/* Small thumbnail */}
                      <div className="relative w-24 h-14 shrink-0 rounded-md overflow-hidden bg-[var(--surface-secondary)]">
                        {video.thumbnail ? (
                          <img src={video.thumbnail} alt="" loading="lazy" className="w-full h-full object-cover" />
                        ) : (
                          <div className="flex items-center justify-center h-full text-[var(--text-tertiary)]">
                            <Youtube size={16} />
                          </div>
                        )}
                        {video.duration && (
                          <span className="absolute bottom-1 right-1 px-1 rounded text-[9px] font-mono bg-black/70 text-white/80">
                            {video.duration}
                          </span>
                        )}
                      </div>

                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-[var(--text-primary)] truncate">{video.title}</h3>
                        <p className="text-xs text-[var(--text-tertiary)]">{video.channel}</p>
                      </div>

                      {/* Tags */}
                      {video.tags.length > 0 && (
                        <div className="hidden md:flex items-center gap-1 max-w-[180px] flex-wrap">
                          {video.tags.slice(0, 2).map((tag) => (
                            <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded-full bg-[var(--surface-secondary)] text-[var(--text-tertiary)] border border-[var(--border)] whitespace-nowrap">
                              {tag}
                            </span>
                          ))}
                          {video.tags.length > 2 && (
                            <span className="text-[10px] text-[var(--text-tertiary)]">+{video.tags.length - 2}</span>
                          )}
                        </div>
                      )}

                      {/* Status badge */}
                      <div title={`${statusLabel(video.status)} on ${formatDate(video.statusChangedAt)}`}>
                        <Badge variant={statusVariant(video.status)} className="gap-1 text-[10px] px-1.5 py-0.5 whitespace-nowrap">
                          {statusIcon(video.status)}
                          {statusLabel(video.status)}
                        </Badge>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-0.5 shrink-0">
                        {video.status !== 'to_watch' && (
                          <button
                            onClick={() => handleStatusChange(video.id, 'to_watch')}
                            className="p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)] transition-colors"
                            aria-label="Mark as to watch"
                          >
                            <Clock size={12} />
                          </button>
                        )}
                        {video.status !== 'watching' && (
                          <button
                            onClick={() => handleStatusChange(video.id, 'watching')}
                            className="p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--accent-warning)] hover:bg-[var(--accent-warning)]/10 transition-colors"
                            aria-label="Mark as watching"
                          >
                            <Eye size={12} />
                          </button>
                        )}
                        {video.status !== 'watched' && (
                          <button
                            onClick={() => handleStatusChange(video.id, 'watched')}
                            className="p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--accent-secondary)] hover:bg-[var(--accent-secondary)]/10 transition-colors"
                            aria-label="Mark as watched"
                          >
                            <CheckCircle2 size={12} />
                          </button>
                        )}
                        <a
                          href={video.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] hover:bg-[var(--accent-primary)]/10 transition-colors"
                          aria-label={`Open ${video.title} on YouTube`}
                        >
                          <ExternalLink size={12} />
                        </a>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
