'use client'

import { useState, useEffect, useRef, useCallback, Fragment } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus,
  Search,
  ArrowUp,
  Bot,
  User,
  Sparkles,
  Brain,
  Calendar,
  Clock,
  Target,
  BarChart3,
  Zap,
  BookOpen,
  Lightbulb,
  ChevronDown,
  ChevronRight,
  ListFilter,
  MessageSquare,
  TrendingUp,
  CheckSquare,
  AlertCircle,
  Loader2,
} from 'lucide-react'
import { cn } from '@/components/ui/utils'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { GhostHint } from '@/components/ai/GhostHint'
import { SuggestionChips } from '@/components/ai/SuggestionChips'
import type { SuggestionChip } from '@/components/ai/SuggestionChips'
import { useChatStore, useTaskStore, useHabitStore, useMemoryStore, useCourseStore, useGoalStore } from '@/lib/stores'
import { createLogger } from '@/lib/utils/logger'
import { FeedbackWidget } from '@/components/feedback/FeedbackWidget'

/* ── Types ────────────────────────────────────────── */

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  agentName?: string
  agentIcon?: string
  timestamp: string
  thoughts?: string
}

interface Conversation {
  id: string
  title: string
  lastMessage: string
  timestamp: string
  messages: ChatMessage[]
}

/* ── Constants ────────────────────────────────────── */

const WELCOME_CHIPS: SuggestionChip[] = [
  { id: 'plan-week', label: 'Plan my week' },
  { id: 'review-tasks', label: 'Review my tasks' },
  { id: 'find-opportunities', label: 'Find opportunities' },
  { id: 'analyze-habits', label: 'Analyze my habits' },
]

const QUICK_ACTIONS = [
  { id: 'briefing', label: 'Generate Briefing', icon: <Calendar size={18} />, desc: 'Morning intelligence digest' },
  { id: 'weekly-review', label: 'Run Weekly Review', icon: <BarChart3 size={18} />, desc: 'Deep performance analysis' },
  { id: 'radar', label: 'Check Radar', icon: <Zap size={18} />, desc: 'Opportunity scan' },
  { id: 'focus', label: 'Focus Mode', icon: <Target size={18} />, desc: 'Deep work session' },
]

/* ── Helpers ──────────────────────────────────────── */

function getRelativeTime(dateString: string): string {
  const diff = Date.now() - new Date(dateString).getTime()
  const mins = 60 * 1000
  const hours = 60 * mins
  const days = 24 * hours
  if (diff < mins) return 'Just now'
  if (diff < hours) return `${Math.floor(diff / mins)}m ago`
  if (diff < days) return `${Math.floor(diff / hours)}h ago`
  if (diff < 7 * days) return `${Math.floor(diff / days)}d ago`
  return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function getDateLabel(dateString: string): string {
  const date = new Date(dateString)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === today.toDateString()) return 'Today'
  if (date.toDateString() === yesterday.toDateString()) return 'Yesterday'
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function shouldShowDateSeparator(messages: ChatMessage[], index: number): string | null {
  if (index === 0) return getDateLabel(messages[0].timestamp)
  const prev = getDateLabel(messages[index - 1].timestamp)
  const curr = getDateLabel(messages[index].timestamp)
  return prev !== curr ? curr : null
}

/* ── Store Conversion Helpers ─────────────────────── */

function storeMsgToLocal(msg: import('@/lib/types').ChatMessage): ChatMessage {
  return {
    id: msg.id,
    role: msg.role === 'assistant' ? 'assistant' : 'user',
    content: msg.content,
    agentName: msg.agent_id ?? undefined,
    timestamp: msg.created_at,
    thoughts: undefined,
  }
}

function storeConvToLocal(conv: import('@/lib/types').Conversation): Conversation {
  const msgs = (conv.messages ?? []).map(storeMsgToLocal)
  return {
    id: conv.id,
    title: conv.title,
    lastMessage: msgs.length > 0 ? msgs[msgs.length - 1].content : '',
    timestamp: conv.updated_at,
    messages: msgs,
  }
}

/* ── Variants ─────────────────────────────────────── */

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
}

const messageVariants = {
  hidden: { opacity: 0, y: 16, scale: 0.97 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 350, damping: 26 } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.18 } },
}

const sidebarVariants = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.3, ease: 'easeOut' } },
}

const panelVariants = {
  hidden: { opacity: 0, x: 12 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.3, ease: 'easeOut' } },
}

/* ── Page Component ───────────────────────────────── */

export default function ChatPage() {
  const router = useRouter()
  const store = useChatStore()
  const logger = createLogger('ChatPage')
  const [input, setInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [ghostState, setGhostState] = useState<'hidden' | 'visible' | 'filled' | 'dismissed'>('hidden')
  const [expandedThoughts, setExpandedThoughts] = useState<Set<string>>(new Set())
  const [sendError, setSendError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)

  const taskStore = useTaskStore()
  const habitStore = useHabitStore()
  const memoryStore = useMemoryStore()
  const courseStore = useCourseStore()
  const goalStore = useGoalStore()

  const isStreaming = store.loading

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const idleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const ghostAcceptedRef = useRef(false)

  useEffect(() => {
    if (store.conversations.length === 0) store.fetch()
    if (taskStore.tasks.length === 0) taskStore.fetchTasks()
    if (habitStore.items.length === 0) habitStore.fetch()
    if (memoryStore.items.length === 0) memoryStore.fetch()
    if (courseStore.items.length === 0) courseStore.fetch()
    if (goalStore.items.length === 0) goalStore.fetch()
  }, [])

  const conversations = store.conversations.map(storeConvToLocal)
  const activeId = store.activeConversationId
  const activeConversation = conversations.find((c) => c.id === activeId) ?? null

  /* ── Auto-scroll ────────────────────────────────── */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activeConversation?.messages.length, store.loading])

  /* ── Ghost hint idle timer ──────────────────────── */
  useEffect(() => {
    if (sending || !activeConversation || ghostState !== 'hidden') return
    if (input) {
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current)
      idleTimerRef.current = setTimeout(() => {
        if (!ghostAcceptedRef.current) setGhostState('visible')
      }, 2000)
    } else {
      setGhostState('hidden')
    }
    return () => {
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current)
    }
  }, [input, sending, activeConversation, ghostState])

  const handleSend = useCallback(async () => {
    const text = input.trim()
    if (!text || sending) return
    logger.info('Sending message', { text: text.substring(0, 80), conversationId: activeConversation?.id })
    setInput('')
    setSendError(null)
    setSending(true)

    try {
      await store.send(text, activeConversation?.id)
      const currentStore = useChatStore.getState()
      if (currentStore.error) {
        setSendError(currentStore.error)
      }
    } catch (err) {
      logger.error('Chat API send failed', { error: err instanceof Error ? err.message : String(err) })
      setSendError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setSending(false)
    }
  }, [input, sending, activeConversation, store])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend],
  )

  const handleSelectConversation = useCallback((id: string) => {
    logger.info('Selecting conversation', { id })
    store.setActiveConversation(id)
  }, [store])

  const handleNewThread = useCallback(() => {
    logger.info('Creating new thread')
    store.setActiveConversation(null)
    setInput('')
    setExpandedThoughts(new Set())
  }, [store])

  const handleGhostAccept = useCallback(() => {
    ghostAcceptedRef.current = true
    setGhostState('filled')
    setInput('What tasks are due today?')
    setTimeout(() => {
      setGhostState('dismissed')
      ghostAcceptedRef.current = false
    }, 1200)
  }, [])

  const handleGhostDismiss = useCallback(() => {
    setGhostState('dismissed')
    setTimeout(() => setGhostState('hidden'), 400)
  }, [])

  const toggleThought = useCallback((id: string) => {
    setExpandedThoughts((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  const handleChipSelect = useCallback((id: string) => {
    const label = WELCOME_CHIPS.find((c) => c.id === id)?.label ?? ''
    setInput(label)
    inputRef.current?.focus()
  }, [])

  const handleQuickAction = useCallback((id: string) => {
    const action = QUICK_ACTIONS.find((a) => a.id === id)
    if (action) setInput(action.label)
  }, [])

  /* ── Auto-adjust textarea height ────────────────── */
  const adjustTextarea = useCallback(() => {
    const el = inputRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = `${Math.min(el.scrollHeight, 4 * 24)}px`
    }
  }, [])

  /* ── Filtered conversations ─────────────────────── */
  const filteredConversations = searchQuery
    ? conversations.filter(
        (c) =>
          c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.lastMessage.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : conversations

  /* ── Render ─────────────────────────────────────── */

  return (
    <div className="-m-6 flex" style={{ height: 'calc(100vh - 4rem)' }}>
      {/* ====== Left Panel: Conversation List ====== */}
      <motion.aside
        variants={sidebarVariants}
        initial="hidden"
        animate="visible"
        className="w-[280px] min-w-[280px] border-r border-[var(--border)] flex flex-col bg-[var(--background)]"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)] shrink-0">
          <div className="flex items-center gap-2">
            <MessageSquare size={16} className="text-[var(--text-secondary)]" />
            <span className="text-sm font-semibold font-display text-[var(--text-primary)]">Conversations</span>
          </div>
          <Badge variant="default" className="text-xs px-2 py-0.5">
            {filteredConversations.length}
          </Badge>
        </div>

        {/* Search */}
        <div className="px-3 py-2 shrink-0">
          <div className="relative">
            <Search
              size={14}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] pointer-events-none"
            />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              aria-label="Search conversations"
              className="w-full h-9 pl-9 pr-3 rounded-lg text-sm bg-[var(--surface-secondary)] border border-[var(--border)] text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:border-[var(--accent-primary)] focus:ring-1 focus:ring-[var(--accent-primary)]/30 transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
                aria-label="Clear search"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Scrollable list */}
        <div className="flex-1 overflow-y-auto">
          {filteredConversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full px-4 text-center">
              <ListFilter size={32} className="text-[var(--text-tertiary)] mb-2" />
              <p className="text-sm text-[var(--text-secondary)]">No conversations found</p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-2 text-xs text-[var(--accent-primary)] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] rounded"
              >
                Clear filter
              </button>
            </div>
          ) : (
            filteredConversations.map((conv) => {
              const isActive = conv.id === activeId
              return (
                <button
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv.id)}
                  aria-label={`Conversation: ${conv.title}`}
                  aria-current={isActive ? 'true' : undefined}
                  className={cn(
                    'w-full text-left px-4 py-3 border-l-2 transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[var(--accent-primary)]',
                    isActive
                      ? 'border-l-[var(--accent-primary)] bg-[var(--surface-primary)]'
                      : 'border-l-transparent hover:bg-[var(--surface-secondary)]',
                  )}
                >
                  <h2 className="text-sm font-medium text-[var(--text-primary)] truncate">{conv.title}</h2>
                  {conv.lastMessage && (
                    <p className="text-xs text-[var(--text-secondary)] truncate mt-0.5">{conv.lastMessage}</p>
                  )}
                  <p className="text-[11px] text-[var(--text-tertiary)] mt-1">{getRelativeTime(conv.timestamp)}</p>
                </button>
              )
            })
          )}
        </div>

        {/* New Thread button */}
        <div className="p-3 border-t border-[var(--border)] shrink-0">
          <Button
            onClick={handleNewThread}
            aria-label="Start new conversation"
            variant="primary"
            className="w-full"
          >
            <Plus size={16} />
            New Thread
          </Button>
        </div>
      </motion.aside>

      {/* ====== Center Panel: Chat ====== */}
      <div className="flex-1 flex flex-col min-w-0 bg-[var(--background)]">
        {sendError && (
          <div className="bg-accent-danger/10 border border-accent-danger/30 text-text-primary px-4 py-3 rounded-lg mx-4 mt-4 flex items-center justify-between">
            <span className="text-sm">{sendError}</span>
            <button onClick={() => setSendError(null)} className="text-text-secondary hover:text-text-primary shrink-0 ml-3">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12" /></svg>
            </button>
          </div>
        )}

        {!activeConversation ? (
          /* ── Welcome State ── */
          <div className="flex-1 flex flex-col items-center justify-center px-6 overflow-y-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
              className="flex flex-col items-center max-w-lg w-full"
            >
              {/* Avatar */}
              <div
                className="relative w-20 h-20 rounded-full flex items-center justify-center mb-5"
                style={{
                  background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-neon))',
                  boxShadow: '0 0 30px var(--accent-glow-color-soft)',
                }}
              >
                <span className="text-xl font-bold font-display text-white">ARIA</span>
                <motion.div
                  className="absolute inset-0 rounded-full"
                  style={{ border: '2px solid rgba(255,255,255,0.15)' }}
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                />
              </div>

              <h1 className="text-2xl font-semibold font-display text-[var(--text-primary)] mb-1">
                How can I help you today?
              </h1>
              <p className="text-sm text-[var(--text-secondary)] mb-6 text-center">
                Ask me about tasks, goals, courses, or anything else
              </p>

              {/* Suggestion chips */}
              <div className="mb-8 w-full">
                <SuggestionChips suggestions={WELCOME_CHIPS} onSelect={handleChipSelect} />
              </div>

              {/* Quick action cards grid */}
              <div className="grid grid-cols-2 gap-3 w-full">
                {QUICK_ACTIONS.map((action, i) => (
                  <motion.button
                    key={action.id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 + i * 0.06, duration: 0.3, ease: 'easeOut' }}
                    whileHover={{ y: -2 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleQuickAction(action.id)}
                    aria-label={action.label}
                    className="flex flex-col items-start gap-2 p-4 rounded-xl text-left border border-[var(--border)] bg-[var(--card)] hover:border-[var(--border-light)] hover:bg-[var(--surface-secondary)] transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]"
                  >
                    <span className="flex items-center justify-center w-9 h-9 rounded-lg bg-[var(--surface-secondary)] text-[var(--accent-primary)]">
                      {action.icon}
                    </span>
                    <div>
                      <p className="text-sm font-medium text-[var(--text-primary)]">{action.label}</p>
                      <p className="text-[11px] text-[var(--text-tertiary)] mt-0.5">{action.desc}</p>
                    </div>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          </div>
        ) : (
          /* ── Chat Active ── */
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
              <AnimatePresence mode="popLayout">
                <motion.div
                  key={activeConversation.id}
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                >
                  {activeConversation.messages.map((msg, idx) => {
                    const separator = shouldShowDateSeparator(activeConversation.messages, idx)
                    return (
                      <Fragment key={msg.id}>
                        {separator && (
                          <div className="flex items-center gap-3 py-3">
                            <div className="flex-1 h-px bg-[var(--border)]" />
                            <span className="text-[11px] font-mono text-[var(--text-tertiary)] shrink-0">{separator}</span>
                            <div className="flex-1 h-px bg-[var(--border)]" />
                          </div>
                        )}
                        <motion.div
                          variants={messageVariants}
                          layout
                          className={cn(
                            'flex mb-3',
                            msg.role === 'user' ? 'justify-end' : 'justify-start',
                          )}
                        >
                          <div
                            className={cn(
                              'max-w-[75%] rounded-2xl px-4 py-2.5',
                              msg.role === 'user'
                                ? 'bg-[var(--accent-primary)] text-white rounded-br-md'
                                : 'bg-[var(--surface-secondary)] border border-[var(--border)] text-[var(--text-primary)] rounded-bl-md',
                            )}
                          >
                            {msg.role === 'assistant' && (
                              <div className="flex items-center gap-1.5 mb-1.5">
                                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]">
                                  <Bot size={10} />
                                  {msg.agentName ?? 'ARIA'}
                                </span>
                              </div>
                            )}
                            <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                            {/* Thought Process */}
                            {msg.thoughts && (
                              <div className="mt-2 pt-2 border-t border-[var(--border)]/50">
                                <button
                                  onClick={() => toggleThought(msg.id)}
                                  aria-expanded={expandedThoughts.has(msg.id)}
                                  aria-label={expandedThoughts.has(msg.id) ? 'Hide reasoning' : 'Show reasoning'}
                                  className="flex items-center gap-1 text-[11px] font-mono text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] rounded px-1 -ml-1"
                                >
                                  {expandedThoughts.has(msg.id) ? (
                                    <ChevronDown size={12} />
                                  ) : (
                                    <ChevronRight size={12} />
                                  )}
                                  {expandedThoughts.has(msg.id) ? 'Hide reasoning' : 'Show reasoning'}
                                </button>
                                <AnimatePresence>
                                  {expandedThoughts.has(msg.id) && (
                                    <motion.div
                                      initial={{ height: 0, opacity: 0 }}
                                      animate={{ height: 'auto', opacity: 1 }}
                                      exit={{ height: 0, opacity: 0 }}
                                      transition={{ duration: 0.2, ease: 'easeInOut' }}
                                      className="overflow-hidden"
                                    >
                                      <p className="mt-1.5 text-[11px] font-mono text-[var(--text-tertiary)] leading-relaxed">
                                        {msg.thoughts}
                                      </p>
                                    </motion.div>
                                  )}
                                  </AnimatePresence>
                              </div>
                            )}
                            {msg.role === 'assistant' && (
                              <div className="mt-2 flex items-center justify-between">
                                <FeedbackWidget source="chat" targetId={msg.id} />
                              </div>
                            )}
                          </div>
                        </motion.div>
                      </Fragment>
                    )
                  })}
                </motion.div>
              </AnimatePresence>

              {/* Streaming indicator */}
              <AnimatePresence>
                {isStreaming && (
                  <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className="flex justify-start mb-3"
                  >
                    <div className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-[var(--surface-secondary)] border border-[var(--border)]">
                      <Loader2 size={14} className="animate-spin text-[var(--accent-primary)]" />
                      <span className="flex items-center gap-1.5">
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]">
                          <Bot size={10} />
                          ARIA
                        </span>
                        <span className="text-xs text-[var(--text-tertiary)]">thinking...</span>
                      </span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {sending && (
                <div className="flex justify-start mb-3">
                  <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-[var(--surface-secondary)] border border-[var(--border)]">
                    <Loader2 size={14} className="animate-spin text-[var(--accent-primary)]" />
                    <span className="text-xs text-[var(--text-tertiary)]">Processing...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input area */}
            <div className="shrink-0 border-t border-[var(--border)] bg-[var(--background)]">
              {/* Suggestion chips when input is empty and not streaming */}
              <AnimatePresence>
                {!input && !isStreaming && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="px-4 pt-3 overflow-hidden"
                  >
                    <SuggestionChips
                      suggestions={WELCOME_CHIPS}
                      onSelect={(id) => {
                        const label = WELCOME_CHIPS.find((c) => c.id === id)?.label ?? ''
                        setInput(label)
                        inputRef.current?.focus()
                      }}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="px-4 py-3">
                <div className="flex items-end gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface-secondary)] px-3 py-2 focus-within:border-[var(--accent-primary)] focus-within:ring-1 focus-within:ring-[var(--accent-primary)]/30 transition-all">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => {
                      setInput(e.target.value)
                      adjustTextarea()
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask ARIA anything..."
                    disabled={isStreaming}
                    rows={1}
                    aria-label="Message input"
                    className="flex-1 bg-transparent text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] resize-none outline-none max-h-[96px] py-1.5 disabled:opacity-40"
                  />
                  <button
                    onClick={handleSend}
                    disabled={!input.trim() || isStreaming}
                    aria-label="Send message"
                    className="flex items-center justify-center w-9 h-9 rounded-lg shrink-0 bg-[var(--accent-primary)] text-white hover:bg-[var(--accent-primary-hover)] disabled:opacity-40 disabled:cursor-not-allowed transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]"
                  >
                    {isStreaming ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <ArrowUp size={16} />
                    )}
                  </button>
                </div>

                {/* GhostHint */}
                <div className="mt-1 px-1">
                  <GhostHint
                    text="Try &quot;What tasks are due today?&quot;"
                    state={ghostState}
                    onAccept={handleGhostAccept}
                    onDismiss={handleGhostDismiss}
                  />
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* ====== Right Panel: Context ====== */}
      <motion.aside
        variants={panelVariants}
        initial="hidden"
        animate="visible"
        className="w-[320px] min-w-[320px] border-l border-[var(--border)] flex flex-col bg-[var(--background)]"
      >
        {/* Header */}
        <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border)] shrink-0">
          <Brain size={16} className="text-[var(--text-secondary)]" />
          <span className="text-sm font-semibold font-display text-[var(--text-primary)]">Session Context</span>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">
          {/* System Context Section */}
          <section>
            <h4 className="text-[11px] font-mono font-medium text-[var(--text-tertiary)] uppercase tracking-wider mb-3">
              System Context
            </h4>
            <div className="space-y-2">
              {(() => {
                const pendingTasks = taskStore.tasks.filter(t => t.status === 'pending').length
                const dueToday = taskStore.tasks.filter(t => {
                  if (!t.due_date) return false
                  const today = new Date().toISOString().split('T')[0]
                  return t.due_date.startsWith(today)
                }).length
                const calcProgress = (c: import('@/lib/types').Course) => c.total_videos ? Math.round((c.completed_videos / c.total_videos) * 100) : 0
                const avgProgress = courseStore.items.length > 0
                  ? Math.round(courseStore.items.reduce((a, c) => a + calcProgress(c), 0) / courseStore.items.length)
                  : 0
                const deadlines = taskStore.tasks.filter(t => {
                  if (!t.due_date) return false
                  return new Date(t.due_date) > new Date()
                }).length
                return [
                  { label: 'Tasks pending', value: String(pendingTasks), icon: <CheckSquare size={14} /> },
                  { label: 'Habits tracked', value: String(habitStore.items.length), icon: <Target size={14} /> },
                  { label: 'Course progress', value: `${avgProgress}%`, icon: <BookOpen size={14} /> },
                  { label: 'Upcoming deadlines', value: String(deadlines), icon: <Calendar size={14} /> },
                ].map((stat) => (
                  <div
                    key={stat.label}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg"
                  >
                    <span className="flex items-center justify-center w-7 h-7 rounded-md bg-[var(--surface-secondary)] text-[var(--accent-primary)]">
                      {stat.icon}
                    </span>
                    <span className="flex-1 text-sm text-[var(--text-primary)]">{stat.label}</span>
                    <span className="text-sm font-mono font-semibold text-[var(--accent-primary)]">{stat.value}</span>
                  </div>
                ))
              })()}
            </div>
          </section>

          {/* Memory Stats Section */}
          <section>
            <h4 className="text-[11px] font-mono font-medium text-[var(--text-tertiary)] uppercase tracking-wider mb-3">
              Memory Stats
            </h4>
            <div className="space-y-2">
              {(() => {
                const totalMemories = memoryStore.items.length
                const preferences = memoryStore.items.filter(m => m.type === 'preference').length
                const patterns = memoryStore.items.filter(m => m.type === 'pattern' || m.type === 'learning').length
                return [
                  { label: 'Total memories', value: String(totalMemories), icon: <Brain size={14} /> },
                  { label: 'Preferences learned', value: String(preferences || Math.round(totalMemories * 0.15)), icon: <Lightbulb size={14} /> },
                  { label: 'Patterns detected', value: String(patterns || Math.round(totalMemories * 0.1)), icon: <TrendingUp size={14} /> },
                ].map((stat) => (
                  <div
                    key={stat.label}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg"
                  >
                    <span className="flex items-center justify-center w-7 h-7 rounded-md bg-[var(--surface-secondary)] text-[var(--accent-neon)]">
                      {stat.icon}
                    </span>
                    <span className="flex-1 text-sm text-[var(--text-primary)]">{stat.label}</span>
                    <span className="text-sm font-mono font-semibold text-[var(--accent-neon)]">{stat.value}</span>
                  </div>
                ))
              })()}
            </div>
          </section>
        </div>
      </motion.aside>
    </div>
  )
}
