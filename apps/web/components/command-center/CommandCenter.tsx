'use client'

import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import Fuse from 'fuse.js'
import {
  LayoutDashboard,
  CheckSquare,
  BookOpen,
  Target,
  MessageCircle,
  Moon,
  FolderKanban,
  Radar,
  FileText,
  Sparkles,
  X,
  Clock,
  Search,
  Bot,
  Command,
  Navigation,
  Plus,
  HelpCircle,
  CheckCircle2,
  BellOff,
} from 'lucide-react'
import { showSuccess, showError } from '@/lib/toast'
import { api } from '@/lib/api'
import { parseCommand } from '@/lib/ai/nlp'
import { VoiceInput } from '@/components/ai/VoiceInput'

/* ───────────────────────────────────────────────
   Types
   ─────────────────────────────────────────────── */

interface CommandItem {
  id: string
  label: string
  description?: string
  icon: React.ElementType
  action: string
  category: string
  tags?: string[]
}

interface UniversalResult {
  id: string
  type: string
  label: string
  description?: string
  icon: React.ElementType
  category?: string
  tags?: string[]
}

interface RecentActivityItem {
  id: string
  label: string
  time: string
  icon?: React.ElementType
}

interface NavigationItem {
  id: string
  label: string
  icon: React.ElementType
  route: string
}

interface SelectableItem {
  id: string
  label: string
  action?: string
  section: 'ai' | 'universal' | 'command' | 'recent' | 'navigation'
  callback?: () => void
}

/* ───────────────────────────────────────────────
   Operators
   ─────────────────────────────────────────────── */

interface Operator {
  command: string
  label: string
  description: string
  icon: React.ElementType
  execute: () => void
}

/* ───────────────────────────────────────────────
   Static Data
   ─────────────────────────────────────────────── */

const commands: CommandItem[] = [
  { id: 'dash', label: 'Go to Dashboard', icon: LayoutDashboard, action: '/dashboard', category: 'navigation', tags: ['dashboard', 'home'] },
  { id: 'tasks', label: 'Go to Tasks', icon: CheckSquare, action: '/tasks', category: 'navigation', tags: ['tasks', 'todo'] },
  { id: 'courses', label: 'Go to Courses', icon: BookOpen, action: '/courses', category: 'navigation', tags: ['courses', 'study'] },
  { id: 'goals', label: 'Go to Goals', icon: Target, action: '/goals', category: 'navigation', tags: ['goals', 'objectives'] },
  { id: 'chat', label: 'Open ARIA Chat', icon: MessageCircle, action: '/chat', category: 'ai', tags: ['chat', 'aria', 'ai'] },
  { id: 'habits', label: 'Go to Habits', icon: Moon, action: '/habits', category: 'navigation', tags: ['habits', 'tracking'] },
  { id: 'projects', label: 'Go to Projects', icon: FolderKanban, action: '/projects', category: 'navigation', tags: ['projects'] },
  { id: 'opportunities', label: 'Go to Opportunities', icon: Radar, action: '/opportunities', category: 'navigation', tags: ['opportunities', 'radar'] },
]

const universalResults: UniversalResult[] = [
  { id: 'r1', type: 'Task', label: 'Review design tokens', description: 'Update color variables in globals.css', icon: FileText, category: 'design', tags: ['design', 'tokens'] },
  { id: 'r2', type: 'Project', label: 'Project Apollo Redesign', description: 'Full UI overhaul for Q3', icon: FolderKanban, category: 'projects', tags: ['project', 'redesign'] },
  { id: 'r3', type: 'Note', label: 'Design System Guidelines', description: 'Component usage and best practices', icon: BookOpen, category: 'design', tags: ['design', 'guidelines'] },
  { id: 'r4', type: 'Task', label: 'Fix login flow validation', description: 'Email regex edge cases', icon: CheckSquare, category: 'bugs', tags: ['bug', 'login'] },
  { id: 'r5', type: 'Goal', label: 'Complete React Mastery', description: 'Advanced patterns course', icon: Target, category: 'learning', tags: ['learning', 'react'] },
]

const navigationItems: NavigationItem[] = [
  { id: 'nav1', label: 'Dashboard', icon: LayoutDashboard, route: '/dashboard' },
  { id: 'nav2', label: 'Tasks', icon: CheckSquare, route: '/tasks' },
  { id: 'nav3', label: 'Courses', icon: BookOpen, route: '/courses' },
  { id: 'nav4', label: 'Goals', icon: Target, route: '/goals' },
  { id: 'nav5', label: 'Habits', icon: Moon, route: '/habits' },
  { id: 'nav6', label: 'Projects', icon: FolderKanban, route: '/projects' },
  { id: 'nav7', label: 'Opportunities', icon: Radar, route: '/opportunities' },
  { id: 'nav8', label: 'ARIA Chat', icon: MessageCircle, route: '/chat' },
]

const recentActivity: RecentActivityItem[] = [
  { id: 'ra1', label: 'Viewed Dashboard', time: '2m ago', icon: LayoutDashboard },
  { id: 'ra2', label: 'Edited design tokens', time: '1h ago', icon: FileText },
  { id: 'ra3', label: 'Created task "Review PR"', time: '3h ago', icon: CheckSquare },
  { id: 'ra4', label: 'Completed habit: Morning run', time: '5h ago', icon: Moon },
  { id: 'ra5', label: 'Updated project timeline', time: '1d ago', icon: FolderKanban },
]

const aiSearchResults: UniversalResult[] = [
  { id: 'ai1', type: 'AI Suggestion', label: 'You have 3 overdue tasks', description: 'Focus on high-priority items first', icon: Bot, tags: ['overdue', 'priority'] },
  { id: 'ai2', type: 'AI Insight', label: 'Best time for deep work is 9-11 AM', description: 'Based on your completion history', icon: Bot, tags: ['deep work', 'productivity'] },
  { id: 'ai3', type: 'AI Suggestion', label: 'Consider breaking down "Project Apollo"', description: 'Large projects are 40% more likely to complete with sub-tasks', icon: Bot, tags: ['project', 'suggestion'] },
]

const operatorsList: Operator[] = [
  {
    command: '/new task', label: 'New Task', description: 'Add a task using natural language — e.g. /new task review PR by Friday',
    icon: Plus, execute: async () => {},
  },
  {
    command: '/go', label: 'Navigate', description: 'Open a page — e.g. /go tasks, /go habits',
    icon: Navigation, execute: async () => {},
  },
  {
    command: '/help', label: 'Help', description: 'Show available operators',
    icon: HelpCircle, execute: () => {},
  },
]

/* ───────────────────────────────────────────────
   Fuse.js instance
   ─────────────────────────────────────────────── */

const allSearchable = [
  ...universalResults.map((r) => ({ ...r, __type: 'universal' as const })),
  ...commands.map((c) => ({ ...c, __type: 'command' as const })),
  ...navigationItems.map((n) => ({ ...n, __type: 'navigation' as const })),
]

const fuse = new Fuse(allSearchable, {
  keys: [
    { name: 'label', weight: 2 },
    { name: 'description', weight: 1 },
    { name: 'type', weight: 0.5 },
    { name: 'tags', weight: 1.5 },
    { name: 'category', weight: 0.5 },
  ],
  threshold: 0.4,
  includeScore: true,
})

/* ───────────────────────────────────────────────
   Kbd — keyboard shortcut badge
   ─────────────────────────────────────────────── */

function Kbd({ label, note }: { label: string; note: string }) {
  return (
    <kbd
      className="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-mono leading-none"
      style={{ background: 'rgba(70,70,79,0.3)' }}
    >
      <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
      <span style={{ color: 'var(--text-tertiary)' }}>{note}</span>
    </kbd>
  )
}

/* ───────────────────────────────────────────────
   Section Header
   ─────────────────────────────────────────────── */

function SectionHeader({ label }: { label: string }) {
  return (
    <div
      className="px-5 pt-4 pb-2 text-xs font-medium tracking-wider uppercase"
      style={{ color: 'var(--text-tertiary)', fontFamily: 'var(--font-jetbrains), JetBrains Mono, monospace' }}
    >
      {label}
    </div>
  )
}

/* ───────────────────────────────────────────────
   Props
   ─────────────────────────────────────────────── */

interface CommandCenterProps {
  isOpen: boolean
  onClose: () => void
}

/* ───────────────────────────────────────────────
   CommandCenter Component
   ─────────────────────────────────────────────── */

export function CommandCenter({ isOpen, onClose }: CommandCenterProps) {
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [nlLoading, setNlLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  /* ── Detect operator mode ── */
  const isOperator = query.startsWith('/')
  const operatorQuery = isOperator ? query.slice(1).toLowerCase() : ''

  const matchedOperators = useMemo(() => {
    if (!isOperator) return []
    return operatorsList.filter(
      (op) => op.command.slice(1).toLowerCase().includes(operatorQuery) || op.label.toLowerCase().includes(operatorQuery),
    )
  }, [isOperator, operatorQuery])

  /* ── Fuse fuzzy search results ── */
  const fuseResults = useMemo(() => {
    if (!query || isOperator) return { universal: [], ai: [], commands: [], navigation: [] }
    const results = fuse.search(query)

    const universal: UniversalResult[] = []
    const ai: UniversalResult[] = []
    const commandsResult: CommandItem[] = []
    const navigation: NavigationItem[] = []

    results.forEach(({ item }) => {
      if (item.__type === 'universal') {
        universal.push(item as unknown as UniversalResult)
      } else if (item.__type === 'command') {
        commandsResult.push(item as unknown as CommandItem)
      } else if (item.__type === 'navigation') {
        navigation.push(item as unknown as NavigationItem)
      }
    })

    const aiFiltered = aiSearchResults.filter(
      (r) =>
        r.label.toLowerCase().includes(query.toLowerCase()) ||
        r.description?.toLowerCase().includes(query.toLowerCase()),
    )

    return { universal, ai: aiFiltered, commands: commandsResult, navigation }
  }, [query, isOperator])

  /* ── Derive selectable items for keyboard navigation ── */
  const selectableItems: SelectableItem[] = useMemo(() => {
    const items: SelectableItem[] = []

    if (isOperator) {
      matchedOperators.forEach((op) =>
        items.push({ id: `op-${op.command}`, label: op.label, section: 'universal', callback: op.execute }),
      )
      return items
    }

    if (query) {
      fuseResults.ai.forEach((r) => items.push({ id: r.id, label: r.label, section: 'ai' }))
      fuseResults.universal.forEach((r) => items.push({ id: r.id, label: r.label, section: 'universal' }))
      fuseResults.commands.forEach((c) => items.push({ id: c.id, label: c.label, action: c.action, section: 'command' }))
      fuseResults.navigation.forEach((n) => items.push({ id: n.id, label: n.label, action: n.route, section: 'navigation' }))
    } else {
      recentActivity.forEach((ra) => items.push({ id: ra.id, label: ra.label, section: 'recent' }))
      navigationItems.slice(0, 5).forEach((n) => items.push({ id: n.id, label: n.label, action: n.route, section: 'navigation' }))
    }

    return items
  }, [query, isOperator, matchedOperators, fuseResults])

  const counts = useMemo(() => {
    if (isOperator) return { operators: matchedOperators.length, universal: 0, ai: 0, commands: 0, recent: 0, navigation: 0 }
    return {
      operators: 0,
      ai: fuseResults.ai.length,
      universal: fuseResults.universal.length,
      commands: fuseResults.commands.length,
      recent: !query ? recentActivity.length : 0,
      navigation: query ? fuseResults.navigation.length : navigationItems.slice(0, 5).length,
    }
  }, [query, isOperator, matchedOperators.length, fuseResults])

  /* ── Reset state on open/close ── */
  useEffect(() => {
    if (isOpen) {
      setQuery('')
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  /* ── Actions ── */
  const handleSelect = useCallback(
    (index: number) => {
      const item = selectableItems[index]
      if (!item) return
      if (item.callback) {
        item.callback()
        if (item.id === 'op-/help') return
        onClose()
        return
      }
      if (item.action) {
        router.push(item.action)
        onClose()
        return
      }
    },
    [selectableItems, router, onClose],
  )

  const handleBackdropClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === e.currentTarget) onClose()
    },
    [onClose],
  )

  const handleInputKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (['ArrowDown', 'ArrowUp'].includes(e.key)) {
        e.preventDefault()
      }
      if (e.key === 'Enter' && query && !isOperator && !nlLoading) {
        e.preventDefault()
        const parsed = parseCommand(query)
        if (parsed.type !== 'unknown' && parsed.confidence >= 0.7) {
          setNlLoading(true)
          ;(async () => {
            try {
              if (parsed.type === 'navigate' || parsed.type === 'create_task') {
                const res = await api.post<{ success: boolean; message: string; redirect_url?: string }>('/api/v1/nlp/execute', {
                  type: parsed.type,
                  task: parsed.task,
                  navigation: parsed.navigation,
                })
                if (res.success) {
                  showSuccess(res.message)
                  if (res.redirect_url) {
                    router.push(res.redirect_url)
                  }
                }
              }
            } catch {
              showError('Failed to execute command. Try again.')
            } finally {
              setNlLoading(false)
              onClose()
            }
          })()
        } else if (selectableItems.length > 0) {
          handleSelect(selectedIndex)
        }
        return
      }
    },
    [query, isOperator, nlLoading, selectableItems, selectedIndex, handleSelect, router, onClose],
  )

  /* ── Window-level keyboard navigation ── */
  useEffect(() => {
    if (!isOpen) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Enter' || e.key === 'Escape') {
        e.preventDefault()
      }
      switch (e.key) {
        case 'ArrowDown':
          setSelectedIndex((prev) => (prev + 1) % Math.max(selectableItems.length, 1))
          break
        case 'ArrowUp':
          setSelectedIndex((prev) => (prev - 1 + Math.max(selectableItems.length, 1)) % Math.max(selectableItems.length, 1))
          break
        case 'Enter':
          handleSelect(selectedIndex)
          break
        case 'Escape':
          onClose()
          break
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen, selectableItems.length, selectedIndex, handleSelect, onClose])

  /* ── Scroll selected item into view ── */
  useEffect(() => {
    if (!listRef.current || selectableItems.length === 0) return
    const el = listRef.current.querySelector(`[data-index="${selectedIndex}"]`)
    if (el) el.scrollIntoView({ block: 'nearest' })
  }, [selectedIndex, selectableItems.length])

  /* ── No render when closed ── */
  if (!isOpen) return null

  /* ── Derived render flags ── */
  const showOperatorsSection = isOperator && matchedOperators.length > 0
  const showAiSection = counts.ai > 0
  const showUniversalSection = counts.universal > 0
  const showCommandsSection = counts.commands > 0
  const showNavigationSection = counts.navigation > 0
  const showRecentSection = counts.recent > 0
  const isEmpty = selectableItems.length === 0 && !showOperatorsSection

  let flatOffset = 0

  return (
    <div
      className="fixed inset-0 z-modal flex items-start justify-center"
      style={{ background: 'rgba(10,11,15,0.7)', paddingTop: '12vh' }}
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-label="Command center"
    >
      {/* Radial gradient glow behind panel */}
      <div
        className="absolute pointer-events-none"
        style={{
          width: '672px',
          height: '400px',
          top: '8vh',
          background:
            'radial-gradient(ellipse 60% 50% at 50% 0%, rgba(99,102,241,0.12) 0%, rgba(0,255,163,0.04) 60%, transparent 100%)',
        }}
        aria-hidden="true"
      />

      {/* Panel */}
      <div
        className="relative flex flex-col w-full animate-scale-in"
        style={{ maxWidth: '672px', maxHeight: '80vh' }}
      >
        <div
          className="flex flex-col rounded-xl overflow-hidden"
          style={{
            background: 'rgba(42,41,45,0.85)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            border: '1px solid var(--border)',
            boxShadow:
              '0 0 40px var(--accent-glow-color-soft), 0 25px 50px rgba(0,0,0,0.4)',
          }}
        >
          {/* ── Search Input ── */}
          <div
            className="flex items-center gap-3 px-5"
            style={{
              borderBottom: '1px solid rgba(70,70,79,0.3)',
              minHeight: '56px',
            }}
          >
            <Sparkles
              size={20}
              style={{ color: 'var(--accent-neon)', flexShrink: 0 }}
              aria-hidden="true"
            />
            <input
              ref={inputRef}
              id="command-center-input"
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                setSelectedIndex(0)
              }}
              onKeyDown={handleInputKeyDown}
              placeholder="Type a command, search, or use / for operators..."
              className="flex-1 bg-transparent border-none outline-none"
              style={{
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-syne), Syne, sans-serif',
                fontSize: '18px',
              }}
              aria-label="Search commands"
              role="combobox"
              aria-expanded="true"
              aria-controls="command-list"
              aria-autocomplete="list"
              aria-activedescendant={
                selectableItems[selectedIndex]
                  ? `cmd-item-${selectableItems[selectedIndex].id}`
                  : undefined
              }
            />
            <VoiceInput
              onTranscript={(text) => {
                setQuery(text)
                setSelectedIndex(0)
              }}
            />
            <button
              onClick={onClose}
              className="flex items-center justify-center rounded-md transition-colors touch-target"
              style={{
                width: '32px',
                height: '32px',
                color: 'var(--text-tertiary)',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.color = 'var(--text-primary)'
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.color = 'var(--text-tertiary)'
              }}
              aria-label="Close command center"
              type="button"
            >
              <X size={18} />
            </button>
          </div>

          {/* ── Results ── */}
          <div
            ref={listRef}
            id="command-list"
            className="overflow-y-auto no-scrollbar"
            style={{ maxHeight: 'calc(80vh - 56px - 40px)' }}
            role="listbox"
          >
            {/* Operator Results */}
            {showOperatorsSection && (
              <div role="presentation">
                <SectionHeader label="Operators" />
                {matchedOperators.map((op, i) => {
                  const flatIndex = i
                  const isSelected = selectedIndex === flatIndex
                  const Icon = op.icon
                  return (
                    <button
                      key={op.command}
                      id={`cmd-item-op-${op.command}`}
                      role="option"
                      aria-selected={isSelected}
                      data-index={flatIndex}
                      className="flex items-center gap-3 w-full px-5 py-2.5 text-left transition-colors"
                      style={{
                        background: isSelected ? 'var(--glass-heavy)' : 'transparent',
                        minHeight: '44px',
                      }}
                      onMouseEnter={() => setSelectedIndex(flatIndex)}
                      onClick={() => handleSelect(flatIndex)}
                      type="button"
                    >
                      <Icon size={16} style={{ color: 'var(--accent-primary)', flexShrink: 0 }} />
                      <div className="flex-1">
                        <span className="text-sm block" style={{ color: 'var(--text-primary)' }}>
                          {op.label}
                        </span>
                        <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                          {op.command} — {op.description}
                        </span>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}

            {/* AI Search */}
            {showAiSection && (
              <div role="presentation">
                <SectionHeader label="AI Search" />
                {fuseResults.ai.map((result, i) => {
                  const flatIndex = (flatOffset = matchedOperators.length) + i
                  const isSelected = selectedIndex === flatIndex
                  const Icon = result.icon
                  return (
                    <button
                      key={result.id}
                      id={`cmd-item-${result.id}`}
                      role="option"
                      aria-selected={isSelected}
                      data-index={flatIndex}
                      className="flex items-center gap-3 w-full px-5 py-2.5 text-left transition-colors"
                      style={{
                        background: isSelected ? 'var(--glass-heavy)' : 'transparent',
                        minHeight: '44px',
                      }}
                      onMouseEnter={() => setSelectedIndex(flatIndex)}
                      onClick={() => handleSelect(flatIndex)}
                      type="button"
                    >
                      <Icon size={16} style={{ color: 'var(--accent-neon)', flexShrink: 0 }} />
                      <div className="flex-1">
                        <span className="text-sm block" style={{ color: 'var(--text-primary)' }}>
                          {result.label}
                        </span>
                        {result.description && (
                          <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                            {result.description}
                          </span>
                        )}
                      </div>
                      <span
                        className="inline-flex items-center rounded px-2 py-0.5 text-xs font-medium font-mono"
                        style={{
                          background: 'rgba(0,255,163,0.15)',
                          color: 'var(--accent-neon)',
                          border: '1px solid rgba(0,255,163,0.2)',
                        }}
                      >
                        {result.type}
                      </span>
                    </button>
                  )
                })}
              </div>
            )}

            {/* Universal Search */}
            {showUniversalSection && (
              <div role="presentation">
                <SectionHeader label="Universal Search" />
                {fuseResults.universal.map((result, i) => {
                  const flatIndex = (flatOffset = matchedOperators.length + fuseResults.ai.length) + i
                  const isSelected = selectedIndex === flatIndex
                  const Icon = result.icon
                  return (
                    <button
                      key={result.id}
                      id={`cmd-item-${result.id}`}
                      role="option"
                      aria-selected={isSelected}
                      data-index={flatIndex}
                      className="flex items-center gap-3 w-full px-5 py-2.5 text-left transition-colors"
                      style={{
                        background: isSelected ? 'var(--glass-heavy)' : 'transparent',
                        minHeight: '44px',
                      }}
                      onMouseEnter={() => setSelectedIndex(flatIndex)}
                      onClick={() => handleSelect(flatIndex)}
                      type="button"
                    >
                      <Icon size={16} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
                      <div className="flex-1">
                        <span className="text-sm block" style={{ color: 'var(--text-primary)' }}>
                          {result.label}
                        </span>
                        {result.description && (
                          <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                            {result.description}
                          </span>
                        )}
                      </div>
                      <span
                        className="inline-flex items-center rounded px-2 py-0.5 text-xs font-medium font-mono"
                        style={{
                          background: 'rgba(99,102,241,0.15)',
                          color: 'var(--accent-primary)',
                          border: '1px solid rgba(99,102,241,0.2)',
                        }}
                      >
                        {result.type}
                      </span>
                    </button>
                  )
                })}
              </div>
            )}

            {/* Commands */}
            {showCommandsSection && (
              <div role="presentation">
                <SectionHeader label="Commands" />
                {fuseResults.commands.map((cmd, i) => {
                  const flatIndex = (flatOffset = matchedOperators.length + fuseResults.ai.length + fuseResults.universal.length) + i
                  const isSelected = selectedIndex === flatIndex
                  const Icon = cmd.icon
                  return (
                    <button
                      key={cmd.id}
                      id={`cmd-item-${cmd.id}`}
                      role="option"
                      aria-selected={isSelected}
                      data-index={flatIndex}
                      className="flex items-center gap-3 w-full px-5 py-2.5 text-left transition-colors"
                      style={{
                        background: isSelected ? 'var(--glass-heavy)' : 'transparent',
                        minHeight: '44px',
                      }}
                      onMouseEnter={() => setSelectedIndex(flatIndex)}
                      onClick={() => handleSelect(flatIndex)}
                      type="button"
                    >
                      <Icon size={16} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
                      <span className="flex-1 text-sm" style={{ color: 'var(--text-primary)' }}>
                        {cmd.label}
                      </span>
                      <Kbd label="⌘" note={String(i + 1)} />
                    </button>
                  )
                })}
              </div>
            )}

            {/* Recent Activity */}
            {showRecentSection && (
              <div role="presentation">
                <SectionHeader label="Recent Activity" />
                {recentActivity.map((item, i) => {
                  const flatIndex = (flatOffset = matchedOperators.length + fuseResults.ai.length + fuseResults.universal.length + fuseResults.commands.length) + i
                  const isSelected = selectedIndex === flatIndex
                  const Icon = item.icon || Clock
                  return (
                    <button
                      key={item.id}
                      id={`cmd-item-${item.id}`}
                      role="option"
                      aria-selected={isSelected}
                      data-index={flatIndex}
                      className="flex items-center gap-3 w-full px-5 py-2.5 text-left transition-colors"
                      style={{
                        background: isSelected ? 'var(--glass-heavy)' : 'transparent',
                        minHeight: '44px',
                      }}
                      onMouseEnter={() => setSelectedIndex(flatIndex)}
                      onClick={() => handleSelect(flatIndex)}
                      type="button"
                    >
                      <Icon size={16} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
                      <span className="flex-1 text-sm" style={{ color: 'var(--text-primary)' }}>
                        {item.label}
                      </span>
                      <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                        {item.time}
                      </span>
                    </button>
                  )
                })}
              </div>
            )}

            {/* Navigation */}
            {showNavigationSection && (
              <div role="presentation">
                <SectionHeader label="Navigation" />
                {(query ? fuseResults.navigation : navigationItems.slice(0, 5)).map((item, i) => {
                  const baseOffset = matchedOperators.length + fuseResults.ai.length + fuseResults.universal.length + fuseResults.commands.length + recentActivity.length
                  const flatIndex = (flatOffset = (!query ? 0 : 0) + baseOffset) + i
                  const isSelected = selectedIndex === flatIndex
                  const navItem = 'route' in item ? item as NavigationItem : null
                  const Icon = navItem?.icon || Command
                  const route = navItem?.route || ''
                  return (
                    <button
                      key={item.id}
                      id={`cmd-item-${item.id}`}
                      role="option"
                      aria-selected={isSelected}
                      data-index={flatIndex}
                      className="flex items-center gap-3 w-full px-5 py-2.5 text-left transition-colors"
                      style={{
                        background: isSelected ? 'var(--glass-heavy)' : 'transparent',
                        minHeight: '44px',
                      }}
                      onMouseEnter={() => setSelectedIndex(flatIndex)}
                      onClick={() => {
                        if (route) router.push(route)
                        onClose()
                      }}
                      type="button"
                    >
                      <Icon size={16} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
                      <span className="flex-1 text-sm" style={{ color: 'var(--text-primary)' }}>
                        {item.label}
                      </span>
                      <span className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                        {route}
                      </span>
                    </button>
                  )
                })}
              </div>
            )}

            {/* Empty State */}
            {isEmpty && (
              <div
                className="px-5 py-8 text-center text-sm"
                style={{ color: 'var(--text-tertiary)' }}
              >
                No results found for &ldquo;{query}&rdquo;
                {isOperator && (
                  <div className="mt-2">
                    Try: /new task, /go tasks, /go habits, /help
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ── Footer ── */}
          <div
            className="flex items-center gap-4 px-5 py-3"
            style={{
              background: 'var(--surface-tertiary)',
              borderTop: '1px solid rgba(70,70,79,0.3)',
            }}
          >
            <Kbd label="Esc" note="Close" />
            <Kbd label="↑↓" note="Navigate" />
            <Kbd label="↵" note="Select" />
            <div className="flex-1" />
            <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
              Type <kbd className="px-1 rounded" style={{ background: 'rgba(70,70,79,0.3)' }}>/</kbd> for operators
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
